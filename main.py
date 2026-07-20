from ast import If

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

tasks = [
    {"id": 1, "title": "Task 1", "done": False},
    {"id": 2, "title": "Task 2", "done": True},
    {"id": 3, "title": "Task 3", "done": False}
]

class task(BaseModel):
    title: Optional[str] = None 

@app.get("/")
async def root():
    return { 
        "name": "Task API", 
        "version": "1.0", 
        "endpoints": ["/tasks"] 
    }

@app.get("/tasks")
async def get_tasks():
    return tasks

@app.get("/tasks/{id}")
async def get_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task
        
    raise HTTPException(
        status_code=404,
        detail={"error": f"Task {id} not found"}
    )

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(new_task:task):

    if new_task.title is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing required field: title"}
        )
    
    elif not new_task.title.strip():
        return JSONResponse(
            status_code=400,
            content ={"error": f"Empty title"}
        )
    
    else:
        task_data = {
            "id": len(tasks)+1 ,
            "title": new_task.title,
            "done":False }
        tasks.append(task_data)
        return task_data
    
@app.get("/health")
async def health_check():
    return {"status": "ok"}