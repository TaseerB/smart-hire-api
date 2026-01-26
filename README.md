# Smart Hire API

A production-ready backend server for managing job applications and candidate workflows, built with FastAPI, PostgreSQL, and SQLAlchemy.

## Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.11+**
- **Docker & Docker Compose**
- **PostgreSQL** (if running locally without Docker)
- **Git**

---

## 🚀 Quick Start (Docker)

The easiest way to get the project running is using Docker Compose.

```bash
# 1. Clone the repository
git clone <repository-url>
cd smart-hire-api

# 2. Build and start the services
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

--- 

## 💻 Local Setup

If you prefer to run the project locally without Docker, follow these steps:

### 1. Environment Setup

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the root directory and configure your database settings:

```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=smart_hire
```

### 3. Database Migrations

Ensure your PostgreSQL server is running and the database specified in `.env` exists. Then, run the migrations:

```bash
alembic upgrade head
```

### 4. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

---

## 📖 API Documentation

Once the server is running, you can access the interactive API documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🧪 Running Tests

```bash
pytest
```
