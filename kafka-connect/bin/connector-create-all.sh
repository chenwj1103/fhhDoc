#!/bin/sh

CONF_FILE=./connectors-config.conf

LINE_COUNT=`wc -l $CONF_FILE | awk '{print $1}'`

for(( i = 1 ; i <= $LINE_COUNT ; i++ ))
do
	NAME=$(awk 'NR=='$i' {printf $1}' $CONF_FILE)
	CONFIG=$(awk 'NR=='$i' {printf $2}' $CONF_FILE)
	
	POST_BODY='{"name":"'${NAME}'","config":'${CONFIG}'}'

	echo ""
	echo "connector name : $NAME "
	echo "connector config : $CONFIG"
	echo "post_body : $POST_BODY"
	echo ""

	RESPONSE=`curl -s -X POST -H "Content-Type:application/json" --data "$POST_BODY" 10.90.13.129:8083/connectors`
	echo "response : $RESPONSE"
done

