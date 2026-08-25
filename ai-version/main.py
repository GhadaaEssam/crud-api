"""
Task Management API
--------------------
A simple in-memory task management API built with FastAPI.

Run with:
    uvicorn main:app --reload

Then visit http://127.0.0.1:8000/docs for interactive API docs.
"""

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.exceptions import RequestValidationError

app = FastAPI(title="Task API", version="1.0")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class Task(BaseModel):
    id: int
    title: str
    done: bool = False

class TaskCreate(BaseModel):
    title: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------

tasks: List[Task] = []
_next_id = 1


def _get_next_id() -> int:
    global _next_id
    current = _next_id
    _next_id += 1
    return current


def _find_task(task_id: int) -> Optional[Task]:
    return next((t for t in tasks if t.id == task_id), None)


def _error(message: str) -> Dict[str, str]:
    return {"error": message}


# ---------------------------------------------------------------------------
# Root & health
# ---------------------------------------------------------------------------

@app.get("/")
def read_root() -> Dict[str, Any]:
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"error": "Invalid request body"})


# ---------------------------------------------------------------------------
# List all tasks
# ---------------------------------------------------------------------------

@app.get("/tasks", response_model=List[Task])
def list_tasks() -> List[Task]:
    return tasks

# ---------------------------------------------------------------------------
# Get a single task
# ---------------------------------------------------------------------------

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = _find_task(task_id)
    if task is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=_error("Task not found"),
        )
    return task


# ---------------------------------------------------------------------------
# Create a task
# ---------------------------------------------------------------------------

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(request: TaskCreate):
    if request.title is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=_error("Title is required"),
        )

    if request.title.strip() == "":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=_error("Title cannot be empty"),
        )

    new_task = Task(id=_get_next_id(), title=request.title, done=False)
    tasks.append(new_task)
    return new_task


# ---------------------------------------------------------------------------
# Update a task
# ---------------------------------------------------------------------------

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, request: TaskUpdate):
    task = _find_task(task_id)
    if task is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=_error("Task not found"),
        )

    if request.title is None and request.done is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=_error("Request body must contain 'title' and/or 'done'"),
        )

    if request.title is not None and request.title.strip() == "":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=_error("Title must be a non-empty string"),
        )

    if request.title is not None:
        task.title = request.title
    if request.done is not None:
        task.done = request.done

    return task


# ---------------------------------------------------------------------------
# Delete a task
# ---------------------------------------------------------------------------

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    task = _find_task(task_id)
    if task is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=_error("Task not found"),
        )
    tasks.remove(task)
    return None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)