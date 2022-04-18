#!/usr/bin/env python
from fastapi import FastAPI
import uvicorn
import task_process
#from main_fastapi import task_manager

app = FastAPI()

task_manager = task_process.Taskmanager()
print("start fast api task_manager pointer:", task_manager)

@app.get("/")
async def root():
    print("11 fast api task_manager pointer:", task_manager)
    return {"message": "Hello World"}

@app.get("/add/{task_id}/")
async def item_id(task_id: int):
    print("22 fast api task_manager pointer:", task_manager)
    task_manager.start()
    task_manager.add_Task(task_id)
    return {'task_id----->': task_id}

@app.get("/setstatus/{task_id}={task_status}/")
async def item_id(task_id: int, task_status: int):
    print("33 fast api task_manager pointer:", task_manager)
    task_manager.set_taskstatus(task_id, task_status)
    return {'task_id': task_id, "task_status": task_status}

if __name__ == '__main__':
    # start fastapi
    uvicorn.run("fastapi_server:app", port=8000, reload=True)
