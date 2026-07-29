from fastapi import FastAPI, HTTPException, status, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

# run command: python -m fastapi dev main.py

app = FastAPI()

class Task(BaseModel):
    id: int
    title: str
    done: bool

class TaskCreate(BaseModel):
    title: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

tasks = [
    Task(id=1, title="Task 1", done=False),
    Task(id=2, title="Task 2", done=True),
    Task(id=3, title="Task 3", done=False),
]

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
        if task.id == id:
            return task
        
    raise HTTPException(
        status_code=404,
        detail={"error": f"Task {id} not found"}
    )

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(new_task:TaskCreate):

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
        task_data = Task(
            id=len(tasks)+1 ,
            title=new_task.title,
            done=False )
        tasks.append(task_data)
        return task_data

@app.put("/tasks/{id}")
async def update_task(id:int, updated_task: TaskUpdate):
    if (updated_task.title is None) and (updated_task.done is None):
        return JSONResponse(
            status_code=400,
            content={"error": "Request body must contain at least one of: title or done"}
        )
    elif (updated_task.title is not None) and (not updated_task.title.strip()):
        return JSONResponse(
            status_code=400,
            content ={"error": f"Empty title"}
        )
    else:
        for task in tasks:
            if task.id == id:
                if updated_task.title is not None:
                    task.title = updated_task.title
                if updated_task.done is not None:
                    task.done = updated_task.done
                return task 
        
        raise HTTPException(
            status_code=404,
            detail={"error": f"Task {id} not found"}
            )

@app.delete("/tasks/{id}")
async def update_task(id:int):
    for task in tasks:
        if task.id == id:
            tasks.remove(task)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    raise HTTPException(
            status_code=404,
            detail={"error": f"Task id ({id}) not found"}
        )    

@app.get("/health")
async def health_check():
    return {"status": "ok"}