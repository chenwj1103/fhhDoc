#!/bin/sh

CONF_FILE=/home/fhh/kafka-connect/bin/connectors-config.conf

LINE_COUNT=`wc -l $CONF_FILE | awk '{print $1}'`

echo $"connectors total : $LINE_COUNT"

for(( i = 1 ; i <= $LINE_COUNT ; i++ ))
do
	NAME=`awk 'NR=='$i' {printf $1}' $CONF_FILE`
	
	echo ""
	echo "connector name : $NAME"
	
	RESPONSE=`curl -s -X GET 10.90.13.129:8083/connectors/$NAME/status`
	echo "response : $RESPONSE"
done


