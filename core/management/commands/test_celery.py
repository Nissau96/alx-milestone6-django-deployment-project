from django.core.management.base import BaseCommand
from core.tasks import process_task, send_email_notification
from core.models import Task


class Command(BaseCommand):
    help = 'Test Celery tasks functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test notification',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing Celery tasks...'))

        # Test task processing
        task = Task.objects.create(
            title='Test Task',
            description='This is a test task for Celery'
        )