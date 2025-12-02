from django import forms
from .models import Task, Category
from .ai_service import ai_service
from django.utils import timezone

class TaskForm(forms.ModelForm):
    use_natural_language = forms.BooleanField(
        required=False,
        initial=False,
        label='Use natural language input'
    )
    natural_language_input = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Describe your task naturally'
    )
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'category', 'priority', 'status', 'due_date', 'estimated_duration']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['category'].queryset = Category.objects.filter(user=self.user)
        
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            if field_name not in ['use_natural_language']:
                field.widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        use_natural_language = cleaned_data.get('use_natural_language')
        natural_language_input = cleaned_data.get('natural_language_input')
        
        if use_natural_language and natural_language_input:
            # Parse natural language using AI
            parsed_data = ai_service.parse_natural_language(natural_language_input)
            
            # Update form fields with parsed data
            cleaned_data['title'] = parsed_data.get('title', cleaned_data.get('title'))
            cleaned_data['description'] = parsed_data.get('description', natural_language_input)
            cleaned_data['priority'] = parsed_data.get('priority', 'MEDIUM')
            
            # Set AI-generated fields (will be saved in view)
            self.ai_data = {
                'ai_priority_score': self._calculate_priority_score(parsed_data.get('priority')),
                'ai_category_suggestion': parsed_data.get('category_suggestion', ''),
                'ai_estimated_duration': parsed_data.get('estimated_duration')
            }
        
        return cleaned_data
    
    def _calculate_priority_score(self, priority):
        priority_scores = {
            'LOW': 0.25,
            'MEDIUM': 0.5,
            'HIGH': 0.75,
            'URGENT': 1.0
        }
        return priority_scores.get(priority, 0.5)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})