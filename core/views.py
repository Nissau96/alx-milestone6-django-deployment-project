from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.models import User

from .models import Task, EmailLog
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    EmailNotificationSerializer,
    EmailLogSerializer
)
from .tasks import process_task, send_email_notification


class TaskListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating tasks
    """
    queryset = Task.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer

    @swagger_auto_schema(
        operation_description="Create a new task and start background processing",
        request_body=TaskCreateSerializer,
        responses={
            201: TaskSerializer,
            400: 'Bad Request'
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = TaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Create task
            task = serializer.save(created_by=request.user if request.user.is_authenticated else None)

            # Start background processing
            process_task.delay(task.id)

            # Return created task
            response_serializer = TaskSerializer(task)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting individual tasks
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class EmailLogListView(generics.ListAPIView):
    """
    API endpoint for listing email logs
    """
    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer


@swagger_auto_schema(
    method='post',
    operation_description="Send email notification asynchronously",
    request_body=EmailNotificationSerializer,
    responses={
        202: openapi.Response(
            'Email queued for sending',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'task_id': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: 'Bad Request'
    }
)
@api_view(['POST'])
def send_email_view(request):
    """
    Send email notification using Celery background task
    """
    serializer = EmailNotificationSerializer(data=request.data)
    if serializer.is_valid():
        recipient = serializer.validated_data['recipient']
        subject = serializer.validated_data['subject']
        message = serializer.validated_data['message']

        # Queue email for sending
        task = send_email_notification.delay(recipient, subject, message)

        return Response({
            'message': 'Email queued for sending',
            'task_id': str(task.id)
        }, status=status.HTTP_202_ACCEPTED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_description="Check application health status",
    responses={
        200: openapi.Response(
            'Health status',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'database': openapi.Schema(type=openapi.TYPE_STRING),
                    'celery': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        )
    }
)
@api_view(['GET'])
def health_check_view(request):
    """
    Health check endpoint for monitoring
    """
    try:
        # Check database
        Task.objects.count()
        database_status = 'healthy'
    except Exception:
        database_status = 'unhealthy'

    try:
        # Check Celery (basic check)
        from .tasks import debug_task
        celery_status = 'healthy'
    except Exception:
        celery_status = 'unhealthy'

    return Response({
        'status': 'healthy' if database_status == 'healthy' and celery_status == 'healthy' else 'unhealthy',
        'database': database_status,
        'celery': celery_status
    })