# BankGPT Backend

![BankGPT Logo]([path/to/logo.png](https://lvpvdtjsjkjcteniapit.supabase.co/storage/v1/object/public/statics/Bankgpt.png))

## Overview

Welcome to the backend of **BankGPT**, an application designed to revolutionize your banking experience. This backend is built using FastAPI, providing a robust and efficient structure for our application.

## Technologies Used

- **FastAPI**: A modern, fast (high-performance), web framework for building APIs with Python 3.6+.
- **SQLAlchemy**: An SQL toolkit and Object-Relational Mapping (ORM) library for Python.
- **Alembic**: A database migration tool for SQLAlchemy.
- **Supabase**: Used for database hosting and authentication.
- **Google OAuth**: For user authentication via Google.
- **SMTP**: Our own setup for email services.

## Getting Started

### Running the Backend

To run the backend server, use the following command:

```bash
uvicorn app.main:app --reload
```

The app will start:

```bash
http://127.0.0.1:8000/
```

Once the application is running, you can access the API documentation provided by Swagger at:

```bash
http://127.0.0.1:8000/docs
```

Here, you can explore and interact with the various API endpoints.