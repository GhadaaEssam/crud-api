from fastapi import FastAPI, HTTPException, status, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from data import createdb, initialize_tasks_table, insert_three_samples, get_all_tasks, get_task_by_id,insert_task

# run command: python -m fastapi dev main.py

app = FastAPI()

# Database initialization
con,cur = createdb()

if not cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'").fetchone():
    initialize_tasks_table(cur=cur)

if not cur.execute("SELECT * FROM tasks").fetchone():
    insert_three_samples(con, cur)

get_all_tasks(cur=cur)

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
        task_id = insert_task(con=con, cur=cur, title=new_task.title, done=False)
        task = get_task_by_id(cur=cur, id=task_id)
        return task

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
async def delete_task(id:int):
    for task in tasks:
        if task.id == id:
            tasks.remove(task)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    raise HTTPException(
            status_code=404,
            detail={"error": f"Task id ({id}) not found"}
        )    