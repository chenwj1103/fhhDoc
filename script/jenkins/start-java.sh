#!/bin/sh


usage() {
    local prog=`basename $1`
    echo "Usage: $prog -d domain"
    echo "     -d doamin. i.e. b0fhh.ifeng.com"
    echo ""
    exit 1
}

DOMAIN=

while getopts "d:h" arg
do
    case $arg in
        d) DOMAIN=$OPTARG ;;
        h) usage $0 ;;
        ?) usage $0 ;;
    esac
done

[ -z "$DOMAIN" ] && usage $0

SERVICE_DIR=/home/fhh/fhh-user/$DOMAIN
JAR_FILE=$SERVICE_DIR/libs/running.jar
PID_FILE=$SERVICE_DIR/pid/service_pid
SERVICE_LOG_DIR=/data/logs/fhh-user-webserver/$DOMAIN
STD_LOG_FILE=$SERVICE_LOG_DIR/fhh-user-webserver-std.log
JMXPORT=889${DOMAIN:1:1}
FHH_SERVER_PORT=900${DOMAIN:1:1}
MEM_OPTIONS="-server -Xms500M -Xmx1G -XX:+UseG1GC -Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.port=$JMXPORT -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.authenticate=false -Dvertx.options.jmxEnabled=true"

if [ ! -d "$SERVICE_DIR" ]; then mkdir -p $SERVICE_DIR; fi
if [ ! -d "$SERVICE_DIR/libs" ]; then mkdir -p $SERVICE_DIR/libs; fi
if [ ! -d "$SERVICE_DIR/pid" ]; then mkdir -p $SERVICE_DIR/pid; fi
if [ ! -d "$SERVICE_LOG_DIR" ]; then mkdir -p $SERVICE_LOG_DIR; fi
if [ ! -d "$SERVICE_DIR" ]; then mkdir -p $SERVICE_DIR; fi

echo ""
echo "service home    : $SERVICE_DIR"
echo "jar path        : $JAR_FILE"
echo "mem_options     : $MEM_OPTIONS"
echo "pid file        : $PID_FILE"
echo "stdout log file : $STD_LOG_FILE"
echo "server port     : $FHH_SERVER_PORT"
echo ""

if [ -e "$PID_FILE" ]; then
    OLD_PID=`cat $PID_FILE`
    kill -9 $OLD_PID
fi
# 容错机制,如果这个端口的java存着,也kill
OLD_PID=`ps -ef | grep java | grep $JMXPORT | grep -v grep | awk '{print $2}'`
if [ ! -z "$OLD_PID" ]; then
    kill -9 $OLD_PID
fi

export FHH_SERVER_PORT=$FHH_SERVER_PORT
nohup  java $MEM_OPTIONS -jar $JAR_FILE >$STD_LOG_FILE 2>&1 &

echo $! > "$PID_FILE"
echo "fhh service server started pid : `cat $PID_FILE`"
echo "stdout -> $STD_LOG_FILE"

# 等待5秒验证是否启动
sleep 5
NEW_PID=`cat $PID_FILE`
NEW_PID1=`ps -ef | grep $NEW_PID | grep -v grep | awk '{print $2}'`
if [ "$NEW_PID" != "$NEW_PID1" ]; then
    echo "Failed to start...!!!!!!!!!!!"
    exit -1
fi


echo "=============== STD LOG========================"
cat $STD_LOG_FILE
echo "==============================================="
