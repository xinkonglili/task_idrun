#!/bin/bash
 #docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.9-management
 #docker build -t my_redis:6.2.0 -f ./redis_dockerfile .
my_echo()
{
    echo "$(date '+%Y-%m-%d %H:%M:%S') [info]: $1" # to console
    if [ ! -z $log_dir ]; then
       echo "$(date '+%Y-%m-%d %H:%M:%S') [info]: $1" >> $log_dir/${APP_NAME}-start.log 2>&1 #to file
    else
       echo "$(date '+%Y-%m-%d %H:%M:%S') [warn]: var logdir:$log_dir has not set yet, so won't save into file"
    fi
}

function check_and_mkdir() {
  dir_path=$1
  if [ ! -d "$dir_path" ];then
   mkdir -pv "$dir_path";
  else
     my_echo "dir_path:$dir_path already exist......";
  fi
}

if [ ! -z "${APPNAME}" ]; then
  APP_NAME="${APPNAME}"
else
  APP_NAME=task-idrun
fi

kill_name="${APP_NAME}"

set -e
umask 022
log_dir="/var/log/$APP_NAME" #yunxiao
check_and_mkdir $log_dir
my_echo "argc:$#, argv:$*; pwd:$(pwd)"

argv_1="nohup"
if [ $# -gt 1 ];then
  argv_1=$2
fi
my_echo "argv_1:$argv_1"


my_echo "[${APP_NAME}] is beginning......"
DIR="$(cd "$(dirname "$0")" && pwd)"
my_echo "cd dir:$DIR start ... "
cd $DIR

log_dir="/var/log/$APP_NAME" #yunxiao
# ai-cloud
if [ ! -z "${http_port}" ]; then
  export platform="aicloud"
  export flower_port=${mainstay_port}
  log_dir="/var/log/tfs-publish"
  check_and_mkdir $log_dir

  my_echo "set-env start....."

  port=$http_port
  if [ $http_port == 8080 ]; then #k8s always 8080
    export LOG_FILE_NAME="${APP_NAME}_`hostname`"
  else
    export LOG_FILE_NAME="${APP_NAME}_${port}"
  fi
  my_echo "env:$env, APP_MODE:${APP_MODE}, LOG_FILE_NAME:${LOG_FILE_NAME}"
elif [ ! -z "$WEB_PORT" ]; then
  echo "starting in yunxiao"
  export platform="yunxiao"
  export mainstay_port=8001
  export flower_port=${mainstay_port}
  export port=$WEB_PORT
  if [ "${ENVIRONMENT}" = "product" ]; then
    export env="prod"
  else
    export env=$ENVIRONMENT
  fi
  export NODE_IP="${CONSUL_CLIENT_HOST}"
else
  my_echo "unexpected deploy platform! neither aicloud nor yunxiao!"
  exit 55
#  my_echo "set-env start....."
#  port=$YX_HTTP_PORT
#  export HTTP_PORT=$port
fi

export APP_MODE="$env"
export http_port=$port
export LOG_DIR=$log_dir

#
my_echo "[${APP_NAME}] is starting......pwd:\"$(pwd)\", DIR:$DIR, port:${port}, LOG_DIR:${LOG_DIR}"

pidfile="/tmp/$APP_NAME.pid"
main_pid=$$
my_echo "main_pid:$main_pid"
kill_all() {
    arg=$1
    pids=($arg)
    # echo "arg: $arg, pids: $pids"
    pids_len=${#pids[@]}
    echo "pids size: $pids_len"
    for (( i=0; i<$pids_len; i++ ))
    do
        pid=${pids[i]}
        if [ $main_pid == $pid ];then
          continue;
        fi
        kill -9 $pid;
        ret=$?;
        echo "kill i:$i, pid:$pid, ret: $ret";
    done
}


failure() {
   ret=$?
   my_echo "failure......ret:$ret"
   set +e
   exit $ret
}

usage() {
   my_echo "usage:$0 start|stop|restart"
   set +e
   exit 1
}

[ $# -lt 1 ] && usage

_start() {
  my_echo "start is running......"
  if [ -f $pidfile ]; then
     my_echo "pid:$pid, app:$APP_NAME has already started."
     set +e
     exit 1
  fi


  nohup gunicorn task-idrun:app -w 2 -k uvicorn.workers.UvicornWorker --timeout 120 --bind 0.0.0.0:$port >> $log_dir/${APP_NAME}.log 2>&1 &
  my_echo "APP_NAME:${APP_NAME} started!"
  python ./pika_server.py
  #疑问
  my_echo "pika_server started!!!!"

  RETVAL=$?
  if [ "${platform}" == "yunxiao" ]; then
    my_echo "started & sleeping! ret:$RETVAL, platform:${platform}, port:${port}, env:${env}"
    # shellcheck disable=SC2160
    while true; do
        sleep 1800
    done
  else
    my_echo "start finished! ret:$RETVAL, platform:${platform}, port:${port}, env:${env}"
  fi
  #_pid=$!
  #my_echo $_pid > $DIR/asr.pid
  return $RETVAL
}

_stop() {
  my_echo "stop is starting......"
  pids=`ps -ef | grep "$kill_name" | grep -v grep | awk '{print $2}'`
  ps -ef | grep $kill_name >> $log_dir/${APP_NAME}.log 2>&1
  my_echo "${APP_NAME} pids:$pids is stopping..." >> $log_dir/${APP_NAME}.log 2>&1
  if [ -z "$pids" ]; then
    RETVAL=0
    my_echo "pids is none, maybe ${APP_NAME} is not running......"
  else
    #kill -9 $pids || failure
    kill_all "$pids" || failure
    RETVAL=$?
    my_echo "stop finished ret:$RETVAL"
  fi
  my_echo "stop is done."
  return $RETVAL
}

stop(){
  my_echo "cmd stop"
  _stop
}

start(){
  my_echo "cmd start"
  _stop #workaround with cmdb restart with no stop bug
  _start
}

restart(){
  my_echo "cmd restart"
  _stop
  _start
}

case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  restart)
    restart
    ;;
  *)
    usage
    ;;
esac

my_echo "[${APP_NAME}] is finished......"
set +e
exit 0
