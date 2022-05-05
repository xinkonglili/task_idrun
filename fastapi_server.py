#!/usr/bin/env python
from fastapi import FastAPI
import uvicorn
import task_process

app = FastAPI()

task_manager = task_process.Taskmanager()

@app.get("/")
async def root():
    task_manager.start()
    return {"message": "Hello World"}

@app.get("/add/{task_id}/")
async def item_id(task_id: int):
    task_manager.start()
    task_manager.add_task(task_id)
    return {'Add task_id:': task_id}

@app.get("/setstatus/{task_id}={task_status}/")
async def item_id(task_id: int, task_status: int):
    task_manager.set_task_status(task_id, task_status)
    return {'task_id': task_id, "task_status": task_status}

@app.get("/set_task_done/")
async def item_id(task_id: str):
    task_manager.set_task_status(int(task_id), 1)
    return {'task_id': task_id, "task_status": 1}

if __name__ == '__main__':
    # start fastapi
    uvicorn.run("fastapi_server:app", port=8000, reload=True)

