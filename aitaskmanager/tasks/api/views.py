from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from tasks.models import Task, ProductivityInsight
from tasks.serializers import TaskSerializer, InsightSerializer
from tasks.ai_service import ai_service
import json

class TaskListAPI(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TaskDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

class InsightListAPI(generics.ListAPIView):
    serializer_class = InsightSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ProductivityInsight.objects.filter(user=self.request.user).order_by('-date')

class AIParseView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        text = request.data.get('text', '')
        if not text:
            return Response({'error': 'No text provided'}, status=400)
        
        parsed_data = ai_service.parse_natural_language(text)
        return Response(parsed_data)