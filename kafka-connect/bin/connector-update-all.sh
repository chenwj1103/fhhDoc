#!/bin/sh

CONF_FILE=/home/fhh/kafka-connect/bin/connectors-config.conf

LINE_COUNT=`wc -l $CONF_FILE | awk '{print $1}'`

for(( i = 1 ; i <= $LINE_COUNT ; i++ ))
do
	NAME=`awk 'NR=='$i' {printf $1}' $CONF_FILE`
	CONFIG=`awk 'NR=='$i' {printf $2}' $CONF_FILE`
	
	echo ""
	echo "connector name : $NAME "
	echo "connector config : $CONFIG"
	echo ""

	RESPONSE=`curl -s -X PUT -H "Content-Type:application/json" --data "$CONFIG" 10.90.13.129:8083/connectors/$NAME/config`
	echo "response : $RESPONSE"
done

