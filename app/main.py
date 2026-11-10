from fastapi import FastAPI, HTTPException, status, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.database.db import (createdb, 
    initialize_tasks_table, 
    insert_three_samples, 
    get_all_tasks, 
    get_task_by_id,
    insert_task,
    alter_task,
    remove_task
)

# run command: python -m fastapi dev main.py

app = FastAPI()

# Database initialization
con,cur = createdb()

if not cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'").fetchone():
    initialize_tasks_table(cur=cur)

if not cur.execute("SELECT * FROM tasks").fetchone():
    insert_three_samples(con, cur)

get_all_tasks(cur=cur)


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)

    # validator to ensure title is not empty or whitespace using field_validator decorator
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        v = v.strip()  
        if not v.strip():
            raise ValueError('Title must not be empty')
        return v
    
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

    # validator to ensure title is not empty or whitespace using field_validator decorator
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        v = v.strip()
        if v is not None and not v.strip():
            raise ValueError('Title must not be empty')
        return v

@app.get("/")
async def root():
    return { 
        "name": "Task API", 
        "version": "1.0", 
        "endpoints": ["/tasks"] 
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/tasks")
async def get_tasks():
    tasks_db = get_all_tasks(cur=cur)
    return tasks_db

@app.get("/tasks/{id}")
async def get_task(id: int):
    task = get_task_by_id(cur=cur, id=id)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail={"error": f"Task {id} not found"}
        )
    return task

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(new_task:TaskCreate):
    task_id = insert_task(con=con, cur=cur, title=new_task.title, done=False) 
    return get_task_by_id(cur=cur, id=task_id)

@app.patch("/tasks/{id}")
async def update_task(id:int, updated_task: TaskUpdate):

    # Check if the request body is empty (model_fields_set will be empty if no fields are provided or if fields are set to None)
    if updated_task.model_fields_set == set():
        raise HTTPException(
            status_code=400,
            detail={"error": "Request body must contain at least one of: title or done"}
        )

    task = alter_task(
        con=con, 
        cur=cur, id=id, 
        title=updated_task.title, 
        done=updated_task.done
    )

    # Check if the task was found and updated    
    if task is None:
        raise HTTPException(status_code=404,detail=f"Task {id} not found")

    return task

@app.delete("/tasks/{id}")
async def delete_task(id:int):
    success = remove_task(con=con, cur=cur, id=id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail={"error": f"Task id ({id}) not found"}
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)