'''import uvicorn
import task_process

task_manager = task_process.Task_manager()

def main():
    task_manager.start()
    print("task_manager pointer:",task_manager) #object at 0x7f86c1aa1070>
    # start fastapi
    uvicorn.run("fastapi_server:app", port=8000, reload=True)


if __name__ == "__main__":
    main()'''