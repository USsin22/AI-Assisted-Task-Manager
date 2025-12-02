from django.urls import path
from . import views

urlpatterns = [
    path('tasks/', views.TaskListAPI.as_view(), name='api_task_list'),
    path('tasks/<int:pk>/', views.TaskDetailAPI.as_view(), name='api_task_detail'),
    path('insights/', views.InsightListAPI.as_view(), name='api_insight_list'),
    path('ai/parse/', views.AIParseView.as_view(), name='api_ai_parse'),
]