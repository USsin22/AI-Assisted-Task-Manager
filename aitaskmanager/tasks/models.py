from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    
    class Meta:
        verbose_name_plural = 'Categories'
        unique_together = ['name', 'user']
    
    def __str__(self):
        return self.name

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('DONE', 'Done'),
        ('ARCHIVED', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    due_date = models.DateTimeField(null=True, blank=True)
    estimated_duration = models.IntegerField(help_text='Estimated duration in minutes', null=True, blank=True)
    actual_duration = models.IntegerField(help_text='Actual duration in minutes', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # AI-generated fields
    ai_priority_score = models.FloatField(null=True, blank=True)
    ai_category_suggestion = models.CharField(max_length=100, blank=True)
    ai_estimated_duration = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-priority', 'due_date', 'created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.status == 'DONE' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'DONE':
            self.completed_at = None
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        if self.due_date and self.status != 'DONE':
            return timezone.now() > self.due_date
        return False

class TaskLabel(models.Model):
    name = models.CharField(max_length=50)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='labels')
    
    def __str__(self):
        return self.name

class ProductivityInsight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='insights')
    date = models.DateField()
    tasks_completed = models.IntegerField(default=0)
    total_focus_time = models.IntegerField(default=0)  # in minutes
    average_task_duration = models.FloatField(default=0)
    peak_productivity_hour = models.IntegerField(null=True, blank=True)
    recommendations = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"