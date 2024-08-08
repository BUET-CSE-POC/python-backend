# BankGPT Backend

![BankGPT Logo](https://lvpvdtjsjkjcteniapit.supabase.co/storage/v1/object/public/statics/Bankgpt.png)

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

### Making the Environment

To make a virtual environment, use the following command:

```bash
python3 -m venv myvenv
```

Activate the virtual Environment:

```bash
source myvenv/bin/activate
```

### Install the Requirements:

Install The requirements with the following command:

```bash
pip install -r requirements.txt
```

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

## Database
The schemas are defined in /db. If you make any change (add/ edit),you need to change the models. Then You may need to add your model in base.py

The Database is hosted in supabase.
In order to make the changes visual in database, just run
```bash
./push.sh
```
Changes will migrate automatically

## Endpoints
Endpoints are defined in api/api_v1/endpoints/

## Helper functions
Helper functions are defined in /helpers. Most **LLM Tasks** will be performed here

## Environment File
It will be provided **Privately**

## Areas to focus-on / test
- **File_Parsing**: We have used unstructured local model here. We have used yolox and hi-res and some other configurations. Also We generated descriptions using the gpt-4o-mini model for cost minimization. These things are subjected to test and research for further betterment
- **Vector_db**: Still relying on cloud vector store. Have to study whether we can rely on alternatives like pinecone, chromadb, weaviate etc.
- **RAG Pipeline**: The vector points fetching and re-ranking and some other parts are subjected to study
- **REACT/other powerful prompting techniques**: These things has to be studied
- **Langsmith**: We have used traditional postgres db for storing the conversations. But it has to be studied whether we could use other framneworks like langsmith 