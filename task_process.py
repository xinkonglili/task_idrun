import time
from threading import Timer
import redis
import requests
import json
import config
from enum import Enum


Redis_taskAdd_keyname = config.Redis_taskAdd_keyname
dingding_report_url = config.dingding_report_url

class ETaskStatus(Enum):
    EXECUTING = 0  #执行中
    FINISHED = 1  #执行完成
    TIMEOUT = 2  #超时


#report url
class TaskInfo:
    def __init__(self):
        self.task_id = 0
        self.task_time = time.time()
        self.task_timeout = 30 #30s
        self.status = ETaskStatus.EXECUTING  #0执行中，1执行完成，2检测超时

class Taskmanager:
    bStart = False

    def __init__(self):
        self.task_list1 = {}
        self.index = 0
        self.redis_con = None

    def start(self):
        if not Taskmanager.bStart:
            Taskmanager.bStart = True
            if config.Enable_Redis:
                pool = redis.ConnectionPool(host='127.0.0.1')
                self.redis_con = redis.Redis(connection_pool=pool)

            t = Timer(1.0, self.update)#启动调用update
            t.start()

    def add_task(self, task_id):
        if task_id in self.task_list1:
            pass
        task = TaskInfo()
        task.task_id = task_id
        self.task_list1[task_id] = task
        print("def add_Task's---> taskid:", task_id)

    def remove_task(self, task_id):
        if task_id in self.task_list1:
            self.task_list1.pop(task_id)

    def set_task_status(self, task_id, task_status): #fastapi--任务完成主动通知
        if task_id in self.task_list1:
            self.task_list1[task_id].status = task_status
            print("def set_task_status's---> task_id:", task_id, ", status:", task_status)
        else:
            print("set_task_status not find taskid,", task_id, task_status)

    # 报警
    def send_report(self, taskid, status, reason):
        #timeout
        if status == ETaskStatus.TIMEOUT:
            self.send_task_timeout(taskid, reason)

    @staticmethod
    def send_task_timeout(taskid, reason):
        data_title = "ASR-超时报警"
        data_content = "### ASR任务监控-超时报警\n\n"
        data_content = data_content + "> **Task_ID:** " + str(taskid) + "\n\n"
        data_content = data_content + "> **Name:** compute_04\n\n" #todo
        data_content = data_content + "> **Reason:** " + reason

        data_dict = {
            "msgtype": "markdown",
            "markdown": {
                "title": data_title,
                "text": data_content
            }
        }

        headers = {'Content-Type': 'application/json'}
        response = requests.post(dingding_report_url, data=json.dumps(data_dict), headers=headers)
        print(response.text)  # {"errcode":0,"errmsg":"ok"}

    def update(self):
        self.update_redis()
        self.update_task()
        timer = Timer(1.0, self.update)
        timer.start()

    def update_task(self):
        current_time = time.time()
        for task in self.task_list1.values():
            if task.status == ETaskStatus.EXECUTING and current_time - task.task_time >= task.task_timeout:
                task.status = ETaskStatus.TIMEOUT

        remove_list = []
        for task_id, task in self.task_list1.items():
            if task.status == ETaskStatus.FINISHED:
                remove_list.append(task_id)
                print(
                    "time finish,task_id: " + str(task.task_id) + ",start_time:" + str(task.task_time) + " ,end_time:" +
                    str(current_time))
            elif task.status == ETaskStatus.TIMEOUT:
                remove_list.append(task_id)
                print("time out!,task_id: " + str(task.task_id) + ",start_time:" + str(task.task_time) + " ,end_time:" +
                      str(current_time))
                reason = "Timeout Duration: " + str(task.task_timeout) + "s"
                self.send_report(task_id, task.status, reason)

        for task_id in remove_list:
            del self.task_list1[task_id]

    def update_redis(self):
        if not config.Enable_Redis or self.redis_con == "None":
            return
        #查到新增的task
        pika_redis_value = self.redis_con.lrange(Redis_taskAdd_keyname, 0, -1)
        if len(pika_redis_value) > 0:
            for index in range(len(pika_redis_value)):
                self.add_task(int(pika_redis_value[index].decode()))
            self.redis_con.delete(Redis_taskAdd_keyname)
        #查找状态　
        for task_id, task in self.task_list1.items():
            if self.redis_con.exists(str(task_id)):
                task_status = self.redis_con.get(str(task_id))
                self.set_task_status(task_id, int(task_status.decode()))





