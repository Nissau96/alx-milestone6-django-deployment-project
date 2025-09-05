from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from .models import Task, EmailLog
from .tasks import process_task, send_email_notification


class TaskModelTest(TestCase):
    """Test Task model functionality"""

    def setUp(self):
        self.task = Task.objects.create(
            title="Test Task",
            description="This is a test task"
        )

    def test_task_creation(self):
        """Test that task is created correctly"""
        self.assertEqual(self.task.title, "Test Task")
        self.assertEqual(self.task.status, "pending")
        self.assertIsNotNone(self.task.created_at)

    def test_task_str_method(self):
        """Test task string representation"""
        self.assertEqual(str(self.task), "Test Task")


class TaskAPITest(APITestCase):
    """Test Task API endpoints"""

    def setUp(self):
        self.task_data = {
            "title": "API Test Task",
            "description": "Task created via API test"
        }

    def test_create_task(self):
        """Test task creation via API"""
        url = reverse('core:task-list-create')
        response = self.client.post(url, self.task_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.get().title, "API Test Task")

    def test_list_tasks(self):
        """Test listing tasks via API"""
        Task.objects.create(**self.task_data)
        url = reverse('core:task-list-create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_task_detail(self):
        """Test retrieving single task"""
        task = Task.objects.create(**self.task_data)
        url = reverse('core:task-detail', kwargs={'pk': task.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], task.title)


class EmailAPITest(APITestCase):
    """Test email notification API"""

    def setUp(self):
        self.email_data = {
            "recipient": "test@example.com",
            "subject": "Test Email",
            "message": "This is a test message"
        }

    @patch('core.tasks.send_email_notification.delay')
    def test_send_email_api(self, mock_delay):
        """Test email sending API endpoint"""
        mock_delay.return_value.id = "test-task-id"

        url = reverse('core:send-email')
        response = self.client.post(url, self.email_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('task_id', response.data)
        mock_delay.assert_called_once()


class CeleryTaskTest(TestCase):
    """Test Celery tasks"""

    def setUp(self):
        self.task = Task.objects.create(
            title="Celery Test Task",
            description="Task for testing Celery"
        )

    @patch('time.sleep')  # Mock sleep to speed up test
    def test_process_task(self, mock_sleep):
        """Test task processing"""
        result = process_task(self.task.id)

        # Refresh from database
        self.task.refresh_from_db()

        self.assertEqual(self.task.status, "completed")
        self.assertIn("completed successfully", result)

    @patch('django.core.mail.send_mail')
    def test_send_email_notification(self, mock_send_mail):
        """Test email notification task"""
        mock_send_mail.return_value = True

        result = send_email_notification(
            "test@example.com",
            "Test Subject",
            "Test message"
        )

        # Check email log was created
        email_log = EmailLog.objects.get()
        self.assertEqual(email_log.recipient, "test@example.com")
        self.assertEqual(email_log.success, True)

        mock_send_mail.assert_called_once()
        self.assertIn("sent successfully", result)


class HealthCheckTest(APITestCase):
    """Test health check endpoint"""

    def test_health_check(self):
        """Test health check returns status"""
        url = reverse('core:health-check')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('database', response.data)
        self.assertIn('celery', response.data)