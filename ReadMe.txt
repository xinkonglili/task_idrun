1、项目启动方式：同时启动fastapi_server.py、pika_server.py
2、test用来测试向这2个服务发起请求
 fastapi_server设计思路：
    1、启动了一个webserver，目前实现了一下接口: "/add"、"/setstatus"
    2、通过task_process.py:任务处理逻辑，比如加入task_id,timeout等
  pika_server设计思路：
    1、通过mq接收消息，协议目前是临时的
