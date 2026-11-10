from fastapi import FastAPI, HTTPException, status, Response, Depends
from pydantic import BaseModel, Field, field_validator
from contextlib import asynccontextmanager
from typing import Optional
from database.db import (
    initialize_database,
    get_task_by_id,
    insert_task,
    alter_task,
    remove_task,
    get_db_connection,
    get_filtered_tasks
)

# run command: python -m fastapi dev main.py

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database and create the tasks table if it doesn't exist
    initialize_database()
    yield

app = FastAPI(lifespan=lifespan)

class TaskCreate(BaseModel):
    title: str = Field(min_length=1)

    # validator to ensure title is not empty or whitespace using field_validator decorator
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        v = v.strip()  
        if not v:
            raise ValueError('Title must not be empty')
        return v
    
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

    # validator to ensure title is not empty or whitespace using field_validator decorator
    # validators only run when the fields are provided. If a field is omitted, its default None is not rejected
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Title must not be empty')
        return v

    @field_validator("done")
    @classmethod
    def validate_done(cls, v):
        if v is None: 
            raise ValueError("Done cannot be null")
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
def get_tasks(search: Optional[str] = None, done: Optional[bool] = None, db= Depends(get_db_connection)):
    con, cur = db
    return get_filtered_tasks(cur, name=search, done=done)

@app.get("/tasks/{id}")
def get_task(id: int, db= Depends(get_db_connection)):
    con, cur = db
    task = get_task_by_id(cur=cur, id=id)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail={"error": f"Task {id} not found"}
        )
    return task


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(new_task:TaskCreate, db= Depends(get_db_connection)):
    con, cur = db
    task_id = insert_task(con=con, cur=cur, title=new_task.title, done=False) 
    return get_task_by_id(cur=cur, id=task_id)

@app.patch("/tasks/{id}")
def update_task(id:int, updated_task: TaskUpdate, db= Depends(get_db_connection)):
    con, cur = db

    # Check if the request body is empty (model_fields_set tracks which fields were explicitly provided, even if their values are None)
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
def delete_task(id:int, db= Depends(get_db_connection)):
    con, cur = db
    success = remove_task(con=con, cur=cur, id=id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail={"error": f"Task id ({id}) not found"}
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)