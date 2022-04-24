import time
from threading import Timer
import redis
import requests
import json

Redis_taskAdd_keyname = "pika_redis_add_key"
#report url
dingding_report_url = "https://oapi.dingtalk.com/robot/send?access_token=" \
                                 "8bd600ae38ececa20cdde5e6d9768e13fcd58e17a5fa1eb5b5cc899f4dd596e7"
class task_info:
    def __init__(self):
        self.task_id = 0
        self.task_time = time.time()
        self.task_timeout = 30 #30s
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

    # 报警
    def send_report(self, taskid, status, reason):
        #timeout
        if status == 2 :
            self.send_task_timeout(taskid, reason)

    def send_task_timeout(self, taskid, reason):
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
                print("time finish,task_id: " + str(task.task_id) + ",start_time:" + str(task.task_time) + " ,end_time:" +
                      str(current_time))
            elif task.status == 2:
                remove_list.append(task_id)
                print("time out!,task_id: " + str(task.task_id) + ",start_time:" + str(task.task_time) + " ,end_time:" +
                      str(current_time))
                reason = "Timeout Duration: " + str(task.task_timeout) + "s"
                self.send_report(task_id, task.status, reason)

        for task_id in remove_list:
            del self.task_list1[task_id]
        timer = Timer(1.0, self.update)
        timer.start()

    def search_redis(self):
        if self.redis_con == "None":
            pass
        #查到新增的task
        pika_redis_value = self.redis_con.lrange(Redis_taskAdd_keyname, 0, -1)
        if len(pika_redis_value) > 0:
            for index in range(len(pika_redis_value)):
                self.add_Task(int(pika_redis_value[index].decode()))
            self.redis_con.delete(Redis_taskAdd_keyname)
        #查找状态　
        for task_id, task in self.task_list1.items():
            if self.redis_con.exists(str(task_id)):
                task_status = self.redis_con.get(str(task_id))
                self.set_taskstatus(task_id, int(task_status.decode()))





