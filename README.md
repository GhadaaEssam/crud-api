# Tasks App

A simple RESTful Task API built with **FastAPI**. It allows you to create, read, update, and delete tasks (CRUD). The API also provides interactive documentation through Swagger UI.

## Features

* Create a new task
* Retrieve all tasks
* Retrieve a task by ID
* Update an existing task
* Delete a task
* Automatic interactive API documentation with Swagger UI

## Requirements

* Python 3.10+
* FastAPI
* Uvicorn/FastAPI CLI

## Installation & Run

1. Install the required packages.

2. Start the development server:

```bash
python -m fastapi dev main.py
```

The API will be available at:

* API: http://127.0.0.1:8000
* Swagger UI: http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint      | Description                                     |
| ------ | ------------- | ----------------------------------------------- |
| GET    | `/`           | Returns API information                         |
| GET    | `/tasks`      | Returns all tasks                               |
| GET    | `/tasks/{id}` | Returns a task by its ID                        |
| POST   | `/tasks`      | Creates a new task                              |
| PUT    | `/tasks/{id}` | Updates a task's title and/or completion status |
| DELETE | `/tasks/{id}` | Deletes a task                                  |
| GET    | `/health`     | Health check endpoint                           |

## Example Request

```bash
curl.exe -i -X POST "http://127.0.0.1:8000/tasks" -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
```

## Example Response

```text
HTTP/1.1 201 Created
content-type: application/json

{
  "id": 4,
  "title": "Buy milk",
  "done": false
}
```

## Swagger UI

FastAPI automatically generates interactive API documentation.

Open:

```
http://127.0.0.1:8000/docs
```

You can use **Try it out** to create, retrieve, update, and delete tasks directly from the browser.

### Screenshots

![Swagger UI](images/swagger-ui-1.png)
![Swagger UI](images/swagger-ui-3.png)
![Swagger UI](images/swagger-ui-2.png)


## Project Structure

```text
.
├── main.py
├── README.md
└── images
    └── swagger-ui.png
```

# AI vs. Me

Here's how the two codes compare:

|  | **AI Version**                                                                                                                                                                                                                    | **My Version**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Limitations** | • Swagger UI does not show a request body field for `POST`/`PUT` because using `request: Request` gives FastAPI no schema to generate.<br>• This makes the API less self-documenting and harder to test directly from Swagger UI. | • `id = len(tasks) + 1` can reuse IDs after deletion. For example, deleting task `2` from 3 tasks causes the next task to receive ID `3`, which already exists.<br>• `404` responses are wrapped as `{"detail": {...}}` instead of using a flat `{"error": ...}` structure, making error responses inconsistent with `400` responses.<br>• Malformed request bodies (invalid JSON or incorrect types such as `title: 123`) are not caught by the custom validation and fall through to FastAPI's default `422` response instead of returning the intended `400`. |

## Author

Created as part of a FastAPI REST API assignment.
