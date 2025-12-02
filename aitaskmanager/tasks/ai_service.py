import openai
import os
from django.conf import settings
import json
from datetime import datetime, timedelta
import re

class AITaskService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        if self.api_key:
            openai.api_key = self.api_key
    
    def parse_natural_language(self, text):
        """Parse natural language to extract task details"""
        if not self.api_key:
            return self._fallback_parse(text)
        
        try:
            prompt = f"""
            Parse this task description and return JSON with:
            - title: A clear task title
            - description: Expanded description if needed
            - priority: LOW, MEDIUM, HIGH, or URGENT
            - estimated_duration: Estimated time in minutes
            - due_date: Date in YYYY-MM-DD format if mentioned
            - category_suggestion: Suggested category
            
            Text: "{text}"
            
            Return only JSON.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a task parsing assistant. Return only JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"AI parsing error: {e}")
            return self._fallback_parse(text)
    
    def _fallback_parse(self, text):
        """Fallback parsing without AI"""
        import random
        from datetime import datetime, timedelta
        
        # Simple keyword-based parsing
        text_lower = text.lower()
        
        # Priority detection
        priority_keywords = {
            'urgent': 'URGENT',
            'asap': 'URGENT',
            'important': 'HIGH',
            'high priority': 'HIGH',
            'medium': 'MEDIUM',
            'low': 'LOW',
            'whenever': 'LOW'
        }
        
        priority = 'MEDIUM'
        for keyword, pri in priority_keywords.items():
            if keyword in text_lower:
                priority = pri
                break
        
        # Duration estimation (simple heuristic)
        duration = 30  # default 30 minutes
        duration_patterns = [
            (r'(\d+)\s*hour', lambda x: int(x) * 60),
            (r'(\d+)\s*hr', lambda x: int(x) * 60),
            (r'(\d+)\s*min', lambda x: int(x)),
            (r'quick', lambda x: 15),
            (r'long', lambda x: 120),
        ]
        
        for pattern, converter in duration_patterns:
            match = re.search(pattern, text_lower)
            if match:
                duration = converter(match.group(1))
                break
        
        # Category suggestion
        categories = {
            'work': ['meeting', 'report', 'project', 'work', 'office'],
            'personal': ['buy', 'shopping', 'grocery', 'personal'],
            'health': ['exercise', 'gym', 'doctor', 'health', 'fitness'],
            'learning': ['study', 'read', 'learn', 'course', 'book'],
            'home': ['clean', 'home', 'house', 'repair']
        }
        
        category = 'General'
        for cat, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                category = cat.capitalize()
                break
        
        return {
            'title': text[:50] + ('...' if len(text) > 50 else ''),
            'description': text,
            'priority': priority,
            'estimated_duration': duration,
            'due_date': None,
            'category_suggestion': category
        }
    
    def get_productivity_recommendations(self, user_tasks):
        """Generate productivity recommendations based on user's tasks"""
        if not self.api_key:
            return self._fallback_recommendations(user_tasks)
        
        try:
            task_summary = "\n".join([
                f"- {task.title} (Priority: {task.priority}, Status: {task.status})"
                for task in user_tasks[:10]  # Limit to recent tasks
            ])
            
            prompt = f"""
            Based on these tasks, provide productivity recommendations:
            {task_summary}
            
            Return recommendations as a list of suggestions.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a productivity coach."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"AI recommendation error: {e}")
            return self._fallback_recommendations(user_tasks)
    
    def _fallback_recommendations(self, user_tasks):
        """Fallback recommendations without AI"""
        if not user_tasks:
            return "Start by adding some tasks to get personalized recommendations!"
        
        pending_tasks = [t for t in user_tasks if t.status != 'DONE']
        high_priority = [t for t in pending_tasks if t.priority in ['HIGH', 'URGENT']]
        
        recommendations = []
        
        if high_priority:
            recommendations.append(f"Focus on your {len(high_priority)} high-priority tasks first.")
        
        if len(pending_tasks) > 10:
            recommendations.append("Consider breaking down large tasks into smaller, manageable ones.")
        
        if any(t.is_overdue for t in pending_tasks):
            recommendations.append("Address overdue tasks to reduce stress.")
        
        return "\n".join(recommendations) if recommendations else "You're doing great! Keep up the good work."

# Singleton instance
ai_service = AITaskService()