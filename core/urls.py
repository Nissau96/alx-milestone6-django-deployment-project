from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('tasks/', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('email-logs/', views.EmailLogListView.as_view(), name='email-log-list'),
    path('send-email/', views.send_email_view, name='send-email'),
    path('health/', views.health_check_view, name='health-check'),
]