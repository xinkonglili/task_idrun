import time
from threading import Timer
import redis

class task_info:
    def __init__(self):
        self.task_id = 0
        self.task_time = time.time()
        self.task_timeout = 60 #30s
        self.status = 0  #0执行中，1执行完成，2检测超时

class Taskmanager:
    bStart = False

    def __init__(self):
        self.task_list1 = {}
        self.index = 0
        self.redis_con = None

    def start(self):
        if not Taskmanager.bStart:
            Taskmanager.bStart = True

            pool = redis.ConnectionPool(host='127.0.0.1')
            self.redis_con = redis.Redis(connection_pool=pool)

            t = Timer(1.0, self.update)#启动调用update
            t.start()

    def add_Task(self, task_id):
        if task_id in self.task_list1:
            pass
        task = task_info()
        task.task_id = task_id
        self.task_list1[task_id] = task
        print("def add_Task's---> taskid:", task_id)

    def remove_Task(self, task_id):
        if task_id in self.task_list1:
            self.task_list1.pop(task_id)

    def set_taskstatus(self, task_id, task_status): #fastapi--任务完成主动通知
        if task_id in self.task_list1:
            self.task_list1[task_id].status = task_status
            print("def set_task_status's---> task_id:", task_id, ", status:", task_status)
        else:
            print("set_task_status not find taskid,", task_id, task_status)

    def send_report(self, reason):
       print("send_report:", reason)

    def update(self):
        self.index += 1
        #print("update enter", self.index,self)
        self.search_redis()
        current_time = time.time()
        for task in self.task_list1.values():
            #print(" update task:", task.status)
            if task.status == 0 and current_time-task.task_time >= task.task_timeout:
                task.status = 2  #报警

        remove_list = []
        for task_id, task in self.task_list1.items():
            if task.status == 1:
                remove_list.append(task_id)
                self.send_report("time finish,task_id: " + str(task.task_id) + ",start_time:" + str(task.task_time))
            elif task.status == 2:
                remove_list.append(task_id)
                self.send_report("time out!,task_id: " + str(task.task_id) + ",start_time:" + str(task.task_time))

        for task_id in remove_list:
            del self.task_list1[task_id]
        timer = Timer(1.0, self.update)
        timer.start()

    def search_redis(self):
        if self.redis_con == None:
            pass
        #查到新增的task
        keyname = "pika_redis_add_key"
        pika_redis_value = self.redis_con.get(keyname)
        #print("pika_redis_value:",pika_redis_value)
        if len(pika_redis_value.decode()) > 0:
            msg_split = pika_redis_value.decode().split(";", -1)
            for i in range(len(msg_split)):
                self.add_Task(int(msg_split[i]))
            self.redis_con.set(keyname, "")
        #查找状态　
        for task_id, task in self.task_list1.items():
            if self.redis_con.exists(str(task_id)):
                task_status = self.redis_con.get(str(task_id))
                self.set_taskstatus(task_id, int(task_status.decode()))





