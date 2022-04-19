一、使用方式：
    1、启动：fastapi_server.py和pika_server.py，完成了webserver和mq的启动
    2、web测试：
        1、在网页中通过：http://127.0.0.1:8000/add/1003/新增task
        2、通过：http://127.0.0.1:8000/setstatus/1003=1/ 改变task状态
    3、mq测试：
        参考test目录下的2个文件，启动后完成增加和修改

二、模块介绍：
     fastapi_server设计思路：
        1、启动了一个webserver，目前实现了一下接口: "/add"、"/setstatus"
        2、通过task_process.py:任务处理逻辑，比如加入task_id,timeout等
      pika_server设计思路：
        1、通过mq接收消息，协议目前是临时的
        2、收到消息并解析，解析后通过http协议回调fastapi_server

三、后续改进和拓展：
     1、确定mq的消息协议
     2、mq发送的http接口支持异步处理
     3、task管理器的数据接入数据库存储
     4、接入"报警"接口，确定报警的级别和文案

 更新日志 04/19：
  1、http接口支持异步处理：使用request+threading的方式修改成异步处理请求
  2、测试速度提升非常明显