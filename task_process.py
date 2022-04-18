import time
from threading import Timer

class task_info:
    def __init__(self):
        self.task_id = 0
        self.tasktime = time.time()
        self.task_timeout = 60 #30s
        self.status = 0  #0执行中，1执行完成，2检测超时

class Task_manager:

    def __init__(self):
        self.task_list1 = {}
        self.index = 0

    def start(self):
        t = Timer(1.0, self.update)
        t.start()

    def add_Task(self, task_id):
        if task_id in self.task_list1:
            pass
        task = task_info()
        task.task_id = task_id
        self.task_list1[task_id] = task
        #print("add task:",task_id,self)
        for kv in self.task_list1.items():
            print(kv)

    def remove_Task(self, task_id):
        if task_id in self.task_list1:
            self.task_list1.pop(task_id)

    def set_taskstatus(self, task_id, task_status): #fastapi--任务完成主动通知
        if task_id in self.task_list1:
            self.task_list1[task_id].status = task_status
            print("set_taskstatus ", task_id,task_status)
        else:
            print("set_taskstatus not find taskid,", task_id, task_status)


    def send_report(self, reason):
       print("send_report:", reason)

    def update(self):
        self.index += 1
        #print("update enter", self.index,self)
        for kv in self.task_list1.items():
            print(kv)

        current_time = time.time()
        for task in self.task_list1.values():
            print(" update task:", task.status)
            if task.status == 0 and current_time-task.tasktime >= task.task_timeout:
                task.status = 2  #报警

        remove_list = []
        for task_id, task in self.task_list1.items():
            if task.status == 1:
                remove_list.append(task_id)
                self.send_report("time finish,task_id: " + str(task.task_id) + ",starttime:" + str(task.tasktime))
            elif  task.status == 2:
                remove_list.append(task_id)
                self.send_report("time out!,task_id: " + str(task.task_id) + ",starttime:" + str(task.tasktime))

        for task_id in remove_list:
                del self.task_list1[task_id]

        print("----", len(self.task_list1))

        timer = Timer(1.0, self.update)
        timer.start()
