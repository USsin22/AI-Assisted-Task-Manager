
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
import json

from .models import Task, Category, ProductivityInsight
from .forms import TaskForm, CategoryForm
from .ai_service import ai_service

@login_required
def dashboard(request):
    """Main dashboard view"""
    # Get user's tasks
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    
    # Statistics
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='DONE').count()
    pending_tasks = tasks.filter(status__in=['TODO', 'IN_PROGRESS']).count()
    overdue_tasks = tasks.filter(status__in=['TODO', 'IN_PROGRESS']).filter(due_date__lt=timezone.now()).count()
    
    # Recent tasks
    recent_tasks = tasks[:5]
    
    # AI recommendations
    recommendations = ai_service.get_productivity_recommendations(tasks)
    
    # Productivity insights for last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    insights = ProductivityInsight.objects.filter(
        user=request.user,
        date__gte=seven_days_ago.date()
    ).order_by('date')
    
    # Prepare chart data
    dates = [insight.date.strftime('%Y-%m-%d') for insight in insights]
    completed_counts = [insight.tasks_completed for insight in insights]
    
    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'recent_tasks': recent_tasks,
        'recommendations': recommendations,
        'chart_data': {
            'dates': json.dumps(dates),
            'completed': json.dumps(completed_counts),
        }
    }
    
    return render(request, 'tasks/dashboard.html', context)

@login_required
def task_list(request):
    """List all tasks with filtering"""
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    category_filter = request.GET.get('category', '')
    
    tasks = Task.objects.filter(user=request.user)
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if category_filter:
        tasks = tasks.filter(category_id=category_filter)
    
    categories = Category.objects.filter(user=request.user)
    
    context = {
        'tasks': tasks,
        'categories': categories,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
    }
    
    return render(request, 'tasks/task_list.html', context)

@login_required
def task_create(request):
    """Create a new task"""
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            
            # Add AI data if available
            if hasattr(form, 'ai_data'):
                for key, value in form.ai_data.items():
                    setattr(task, key, value)
            
            task.save()
            messages.success(request, 'Task created successfully!')
            
            # Generate insight for today
            generate_daily_insight(request.user)
            
            return redirect('task_list')
    else:
        form = TaskForm(user=request.user)
    
    context = {'form': form}
    return render(request, 'tasks/task_form.html', context)

@login_required
def task_update(request, pk):
    """Update an existing task"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            
            # Generate insight for today
            generate_daily_insight(request.user)
            
            return redirect('task_list')
    else:
        form = TaskForm(instance=task, user=request.user)
    
    context = {'form': form, 'task': task}
    return render(request, 'tasks/task_form.html', context)

@login_required
def task_delete(request, pk):
    """Delete a task"""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('task_list')
    
    context = {'task': task}
    return render(request, 'tasks/task_confirm_delete.html', context)

@login_required
def category_list(request):
    """List all categories"""
    categories = Category.objects.filter(user=request.user)
    context = {'categories': categories}
    return render(request, 'tasks/category_list.html', context)

@login_required
def category_create(request):
    """Create a new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST, user=request.user)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(user=request.user)
    
    context = {'form': form}
    return render(request, 'tasks/category_form.html', context)

@login_required
def quick_add(request):
    """Quick add task using natural language"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        text = request.POST.get('text', '')
        
        if text:
            # Parse using AI
            parsed_data = ai_service.parse_natural_language(text)
            
            # Create task
            task = Task(
                title=parsed_data.get('title', text[:50]),
                description=parsed_data.get('description', text),
                user=request.user,
                priority=parsed_data.get('priority', 'MEDIUM'),
                ai_priority_score=parsed_data.get('priority_score', 0.5),
                ai_category_suggestion=parsed_data.get('category_suggestion', ''),
                ai_estimated_duration=parsed_data.get('estimated_duration')
            )
            
            # Try to find matching category
            category_suggestion = parsed_data.get('category_suggestion')
            if category_suggestion:
                category = Category.objects.filter(
                    user=request.user,
                    name__icontains=category_suggestion
                ).first()
                if category:
                    task.category = category
            
            task.save()
            
            return JsonResponse({
                'success': True,
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'priority': task.get_priority_display(),
                }
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def generate_daily_insight(user):
    """Generate daily productivity insight"""
    today = timezone.now().date()
    
    # Get today's tasks
    today_tasks = Task.objects.filter(
        user=user,
        updated_at__date=today
    )
    
    tasks_completed = today_tasks.filter(status='DONE').count()
    
    # Calculate total focus time (simplified)
    total_focus_time = sum(
        task.actual_duration or task.estimated_duration or 0
        for task in today_tasks.filter(status='DONE')
    )
    
    # Calculate average task duration
    completed_tasks_with_duration = today_tasks.filter(
        status='DONE',
        actual_duration__isnull=False
    )
    average_duration = completed_tasks_with_duration.aggregate(
        avg=Avg('actual_duration')
    )['avg'] or 0
    
    # Get AI recommendations
    recommendations = ai_service.get_productivity_recommendations(today_tasks)
    
    # Create or update insight
    insight, created = ProductivityInsight.objects.update_or_create(
        user=user,
        date=today,
        defaults={
            'tasks_completed': tasks_completed,
            'total_focus_time': total_focus_time,
            'average_task_duration': average_duration,
            'recommendations': recommendations,
        }
    )
    
    return insight