#!/usr/bin/env python
"""
Project validation script to ensure all components are properly configured
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deployment_project.settings')
django.setup()


def validate_models():
    """Validate that all models can be imported and used"""
    print("✓ Validating models...")
    try:
        from core.models import Task, EmailLog
        # Test model creation
        task_count = Task.objects.count()
        email_count = EmailLog.objects.count()
        print(f"  - Task model: {task_count} objects")
        print(f"  - EmailLog model: {email_count} objects")
        return True
    except Exception as e:
        print(f"  ✗ Model validation failed: {e}")
        return False


def validate_celery():
    """Validate Celery configuration"""
    print("✓ Validating Celery configuration...")
    try:
        from deployment_project.celery import app
        from core.tasks import process_task, send_email_notification
        print(f"  - Celery app: {app.main}")
        print(f"  - Registered tasks: {len(app.tasks)}")
        return True
    except Exception as e:
        print(f"  ✗ Celery validation failed: {e}")
        return False


def validate_api():
    """Validate API endpoints"""
    print("✓ Validating API configuration...")
    try:
        from django.urls import reverse
        from rest_framework.test import APIClient

        client = APIClient()

        # Test health endpoint
        health_url = reverse('core:health-check')
        health_response = client.get(health_url)

        if health_response.status_code == 200:
            print(f"  - Health check: {health_response.status_code}")
            return True
        else:
            print(f"  ✗ Health check failed: {health_response.status_code}")
            return False

    except Exception as e:
        print(f"  ✗ API validation failed: {e}")
        return False


def validate_environment():
    """Validate environment configuration"""
    print("✓ Validating environment...")
    try:
        from django.conf import settings
        print(f"  - Debug mode: {settings.DEBUG}")
        print(f"  - Database: {settings.DATABASES['default']['ENGINE']}")
        print(f"  - Celery broker: {settings.CELERY_BROKER_URL}")
        return True
    except Exception as e:
        print(f"  ✗ Environment validation failed: {e}")
        return False


def main():
    """Run all validations"""
    print("🔍 Validating Django Deployment Project Setup...\n")

    validations = [
        validate_environment,
        validate_models,
        validate_celery,
        validate_api,
    ]

    results = []
    for validation in validations:
        try:
            results.append(validation())
        except Exception as e:
            print(f"  ✗ Validation failed: {e}")
            results.append(False)
        print()

    if all(results):
        print("🎉 All validations passed! Project is ready for deployment.")
        return 0
    else:
        print("❌ Some validations failed. Please check the configuration.")
        return 1


if __name__ == '__main__':
    sys.exit(main())