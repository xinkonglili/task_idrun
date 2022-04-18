#!/usr/bin/env python
from fastapi import FastAPI
import uvicorn
import task_process
#from main_fastapi import task_manager

app = FastAPI()

task_manager = task_process.Task_manager()

@app.get("/")
async def root():
    print("fast api task_manager pointer:", task_manager)# object at 0x7fe1aaa16910>
    return {"message": "Hello World"}

@app.get("/add/{task_id}/")
async def item_id(task_id: int):
    print("22 fast api task_manager pointer:", task_manager)
    task_manager.add_Task(task_id)
    return {'task_id----->': task_id}

@app.get("/query/{task_id}={task_status}/")
async def item_id(task_id: int, task_status: int):
    task_manager.set_taskstatus(task_id, task_status)
    return {'task_id': task_id, "task_status": task_status}

if __name__ == '__main__':
    task_manager.start()
    print("task_manager pointer:", task_manager)  #Task_manager object at 0x7f896296aac0>
    # start fastapi
    uvicorn.run("fastapi_server:app", port=8000, reload=True)
