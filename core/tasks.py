from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Task, EmailLog
import time
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_task(self, task_id):
    """
    Background task to process a Task object
    """
    try:
        task = Task.objects.get(id=task_id)
        task.status = 'processing'
        task.save()

        # Simulate some processing time
        time.sleep(10)

        # Mark as completed
        task.status = 'completed'
        task.save()

        logger.info(f"Task {task_id} completed successfully")
        return f"Task {task_id} completed successfully"

    except Task.DoesNotExist:
        logger.error(f"Task {task_id} not found")
        return f"Task {task_id} not found"
    except Exception as exc:
        logger.error(f"Error processing task {task_id}: {str(exc)}")
        task = Task.objects.get(id=task_id)
        task.status = 'failed'
        task.save()
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task
def send_email_notification(recipient, subject, message):
    """
    Background task to send email notifications
    """
    email_log = EmailLog.objects.create(
        recipient=recipient,
        subject=subject,
        message=message
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )

        email_log.success = True
        email_log.save()

        logger.info(f"Email sent successfully to {recipient}")
        return f"Email sent successfully to {recipient}"

    except Exception as e:
        email_log.error_message = str(e)
        email_log.save()

        logger.error(f"Failed to send email to {recipient}: {str(e)}")
        raise e


@shared_task
def cleanup_old_tasks():
    """
    Periodic task to clean up old completed tasks
    """
    from django.utils import timezone
    from datetime import timedelta

    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count = Task.objects.filter(
        status='completed',
        updated_at__lt=cutoff_date
    ).delete()[0]

    logger.info(f"Cleaned up {deleted_count} old tasks")
    return f"Cleaned up {deleted_count} old tasks"