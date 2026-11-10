# Task Management API

A simple RESTful Task Management API built with **FastAPI** and **SQLite**. It supports creating, retrieving, updating, deleting, searching, and filtering tasks, with request validation using Pydantic.

## Features

- Create tasks with validated titles.
- Retrieve all tasks or a specific task by ID.
- Partially update task titles and completion status.
- Delete tasks.
- Search tasks by title using SQL's `LIKE` operator.
- Filter tasks by completion status.
- Combine search and filtering using query parameters.
- Return tasks ordered alphabetically by title.
- Retrieve task statistics using SQL aggregation functions.
- Track task creation and modification timestamps (`created_at` and `updated_at`).
- Automatically initialize the database and migrate existing tables.
- Manage database connections through FastAPI dependency injection.
- Return appropriate HTTP status codes and error responses.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| FastAPI | REST API framework |
| SQLite | Relational database |
| Pydantic | Request validation |
| Uvicorn | ASGI server |

SQLite is used because it is lightweight, serverless, and doesn't require a separate database server or configuration. It is suitable for this small project.

## Project Structure

```text
task-management-api/
├── app/
│   ├── database/
│   │   └── db.py
│   └── main.py
├── images/
├── .gitignore
├── README.md
├── requirements.txt
└── tasks.db
```

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
<<<<<<< HEAD
cd flyrank-be-w2
=======
cd task-management-api
cd app
>>>>>>> 3896dd5ddeb478ce47e8bf02daa09d3607e51961
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

Install all required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

SQLite is included with Python, so no separate database installation is required.

### 4. Start the API

Run the following command from the project root:

```bash
python -m fastapi dev app/main.py
```

The database is initialized automatically when the application starts. If the database or `tasks` table doesn't exist, it will be created automatically. Existing databases are also updated with missing timestamp columns.

The API will be available at:

```text
http://127.0.0.1:8000
```

### 5. Explore the API documentation

Open Swagger UI in your browser:

```text
http://127.0.0.1:8000/docs
```

You can explore and test all available endpoints directly from the interactive documentation.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/tasks` | Retrieve all tasks |
| GET | `/tasks/{id}` | Retrieve a task by ID |
| POST | `/tasks` | Create a new task |
| PATCH | `/tasks/{id}` | Partially update a task |
| DELETE | `/tasks/{id}` | Delete a task |
| GET | `/stats` | Retrieve task statistics |

## Search, Filtering & Sorting

The `GET /tasks` endpoint supports optional query parameters.

| Parameter | Description | Example |
|---|---|---|
| `search` | Search task titles using SQL `LIKE` | `?search=milk` |
| `done` | Filter by completion status | `?done=true` |

You can combine both parameters:

```text
GET /tasks?search=milk&done=true
```

This returns completed tasks whose titles contain "milk".

Tasks are returned in alphabetical order by title using SQL's `ORDER BY` clause.

## Example Requests

### Create a task

`POST /tasks`

```json
{
  "title": "Learn FastAPI"
}
```

### Update a task

`PATCH /tasks/1`

```json
{
  "done": true
}
```

### Search tasks

`GET /tasks?search=milk`

### Filter completed tasks

`GET /tasks?done=true`

### Delete a task

`DELETE /tasks/1`

## Task Statistics

The `GET /stats` endpoint returns statistics calculated directly in SQLite using SQL aggregation functions such as `COUNT()`.

Example response:

```json
{
  "total_tasks": 10,
  "completed_tasks": 4,
  "pending_tasks": 6,
  "done_percentage": 40.0
}
```

The statistics include:

- Total number of tasks.
- Number of completed tasks.
- Number of pending tasks.
- Percentage of completed tasks.

## Database Design

The application uses a SQLite database named `tasks.db`.

The `tasks` table contains:

| Column | Type | Description |
|---|---|---|
| id | INTEGER | Primary key, auto-incremented |
| title | TEXT | Task title, required |
| done | INTEGER | Completion status (0 or 1) |
| created_at | TEXT | Timestamp when the task was created |
| updated_at | TEXT | Timestamp of the last modification |

The `done` column has a default value of `0` and a CHECK constraint to ensure it only stores `0` or `1`.

Timestamps are stored in UTC using SQLite's `CURRENT_TIMESTAMP`.

- `created_at` is set when a task is inserted.
- `updated_at` is refreshed whenever a task is modified.
- Existing records receive timestamps during database initialization and migration.

### Example SQL Queries

Retrieve all tasks:

```sql
SELECT * FROM tasks;
```

Retrieve only completed tasks:

```sql
SELECT * FROM tasks WHERE done = 1;
```

Search tasks by title:

```sql
SELECT * FROM tasks WHERE title LIKE '%milk%';
```

Retrieve tasks alphabetically:

```sql
SELECT * FROM tasks ORDER BY title ASC;
```

Count completed tasks:

```sql
SELECT COUNT(*) FROM tasks WHERE done = 1;
```

### Inspecting the Database

You can open `tasks.db` using a SQLite database viewer, such as the SQLite Viewer extension in VS Code, to inspect the database, browse records, and execute SQL queries.

![Database Viewer](images/sqlite-viewer.png)

## Request Validation

Pydantic models validate incoming request bodies.

- `TaskCreate` ensures the title is not empty or whitespace.
- `TaskUpdate` validates provided fields and rejects invalid values.
- Empty PATCH requests are rejected.
- Explicit `null` values are rejected for fields that require actual values.
- Invalid request data is rejected before reaching database operations.

## Database Connection Management

The application uses FastAPI's dependency injection system with a generator dependency.

Each request that needs database access obtains a connection and cursor. The connection is closed automatically after the request finishes, including when an exception occurs.

Database initialization and schema migration are handled automatically when the application starts.

## Interactive API Documentation

FastAPI automatically generates interactive API documentation.

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

These interfaces allow you to explore endpoints and test requests directly from your browser.
