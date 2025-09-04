# alx-milestone6-django-deployment-project

# Django Deployment Project with Celery and Swagger

This project is a demonstration of deploying a Django application to a production-ready cloud server. It includes features like background task processing with Celery and Redis, and interactive API documentation using Swagger (drf-yasg).

The application provides a single API endpoint to trigger a simulated email-sending task, which is handled asynchronously by a Celery worker.

## Features

-   **Django & Django REST Framework**: Robust backend and API development.
-   **Celery**: Asynchronous task queue for handling background jobs.
-   **Redis**: Message broker for Celery communication.
-   **Swagger UI**: Interactive API documentation, publicly accessible.
-   **Gunicorn**: Production-ready WSGI server.
-   **Render Deployment**: Configuration for seamless deployment on Render.

## Tech Stack

-   Python
-   Django
-   Django REST Framework
-   Celery
-   Redis
-   drf-yasg (Swagger)
-   Gunicorn
-   PostgreSQL (or SQLite for local)

## Local Setup Instructions

Follow these steps to run the project on your local machine.

### 1. Clone the Repository

```bash
git clone [https://github.com/Nissau96/alx-milestone6-django-deployment-project.git](https://github.com/Nissau96/alx-milestone6-django-deployment-project.git)
cd alx-milestone6-django-deployment-project
```

### 2. Create and Activate Virtual Environment

```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root and add the following variables:

```env
SECRET_KEY='your-django-secret-key'
DEBUG=True
```

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Start Required Services

You need three separate terminal windows for this.

-   **Terminal 1: Start Redis**
    If you have Docker, this is the easiest way:
    ```bash
    docker run -d -p 6379:6379 redis
    ```

-   **Terminal 2: Start the Celery Worker**
    (Make sure your virtual environment is active)
    ```bash
    celery -A core worker -l info
    ```

-   **Terminal 3: Start the Django Development Server**
    (Make sure your virtual environment is active)
    ```bash
    python manage.py runserver
    ```

### 7. Access the Application

-   **API**: `http://127.0.0.1:8000/api/`
-   **Swagger Docs**: `http://127.0.0.1:8000/swagger/`

## API Endpoint

### Trigger Email Task

-   **URL**: `/api/send-email/`
-   **Method**: `POST`
-   **Description**: Queues a background task to send a simulated email.
-   **Request Body**:
    ```json
    {
      "email": "recipient@example.com"
    }
    ```
-   **Success Response**: `202 ACCEPTED`
    ```json
    {
      "message": "Email sending task has been queued for recipient@example.com!"
    }
    ```

## Deployment

This application is configured for deployment on **Render**.

-   A **Web Service** is created for the Django application using `gunicorn core.wsgi` as the start command.
-   A **Background Worker** is created for the Celery process using `celery -A core worker -l info` as the start command.
-   A **Redis** instance is provisioned and linked to both services.
-   Environment variables from the `.env` file are added to the Render services' configuration.

**Live Application URL**: [Add your Render URL here]