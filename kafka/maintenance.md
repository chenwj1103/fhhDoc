# topic管理

## kafka-topics.sh

>查看、修改、创建及删除topic。

### 脚本参数

+ --zookeeper  (required)  

>kafka依赖的zookeeper管理集群节点(因为zookeeper是集群，这里写列表或一个节点都可以)  

+ --create  

>创建topic  

+ --if-not-exists  

>create创建topic时，如果topic不存在执行create  

+ --alter  

>修改topic的partition数量，replication数量以及topic-level的configuration(修改configuration官方
>已建议使用kafka-configs.sh，后面再做介绍)  

+ --config <name=value>  

>[topic-level](http://kafka.apache.org/documentation/#topic-config)的配置  

+ --delete-config <name>  

>删除topic-level的配置  

+ --if-exists 

>alter修改topic时，如果topic存在执行alter  

+ --delete  

>删除topic  

+ --describe  

>topic详细信息列表  

+ --topics-with-overrides  

>describe查看topic详情列表时，只展示修改过topic-level的配置的topic  

+ --unavailable-partitions  

>describe查看topic详情列表时，只展示leader不可用的partition  

+ --under-replicated-partitions  

>describe查看topic详情列表时，只展示正在复制的partition    

+ --partitions  

>create创建、alter修改 topic 时，partition的数量  

+ --replication-factor  

>create创建 topic 时，副本的数量  

+ --replica-assignment  

>被人工分配过partition的topic列表  

+ --list  

>查看topic名称列表  

+ --topic  

>要操作的topic名称  

### 示例

#### 创建topic

>创建一个3个partition，每个partition2个副本的topic

	kafka-topics.sh --zookeeper 10.21.7.21:2181 --create --if-not-exists --topic test --partitions 3 --replication-factor 2

#### 查看topic列表

>查看所有topic的名称

	kafka-topics.sh --zookeeper 10.21.7.21:2181 --list

#### 查看topic信息

>topic信息列表

	kafka-topics.sh --zookeeper 10.21.7.21:2181 --describe

#### 修改topic

>修改topic的partition数量

	kafka-topics.sh --zookeeper 10.21.7.21:2181 --alter --if-exists --topic test --partitions 4

#### 删除topic

>删除一个topic

	kafka-topics.sh --zookeeper 10.21.7.21:2181 --delete --if-exists --topic test

## kafka-configs.sh

>添加/删除topics、client配置

### 脚本参数

+ --zookeeper  (required)  

>kafka依赖的zookeeper管理集群节点(因为zookeeper是集群，这里写列表或一个节点都可以)  

+ --entity-name

>topic名称/客户端id

+ --entity-type

>类型：topics/clients

+ --describe

>查看实体配置信息

+ --alter

>修改实体配置

+ --add-config

>添加配置参数

+ --delete-config

>删除配置参数

### 示例

#### 查看topic被修改过的配置参数

>查看人工修改的topic配置

	kafka-configs.sh --zookeeper 10.21.7.21:2181 --describe --entity-type topics --entity-name test

#### topic添加topic-level配置参数

>给topic添加cleanup.policy和delete.retention.ms

	kafka-configs.sh --zookeeper 10.21.7.21:2181 --alter --entity-type topics --entity-name test --add-config cleanup.policy=delete,delete.retention.ms=345600000

#### 删除topic的配置参数

>删除topic的配置参数delete.retention.ms

	kafka-configs.sh --zookeeper 10.21.7.21:2181 --alter --entity-type topics --entity-name test --delete-config delete.retention.ms

# producer 操作

## kafka-console-producer.sh

>控制台输入消息生产者

### 脚本参数

+ --batch-size

>生产者一次请求发送批量消息的体积大小

+ --broker-list (required)

>(新的生产者)kafka集群broker列表 (host1:port1,host2:port2,...)

+ --compression-codec [codec]

>消息压缩格式 codec : none、gzip、snappy、lz4。default：gzip

+ --key-serializer

>消息key序列化 default：kafka.serializer.DefaultEncoder

+ --value-serializer

消息value序列化 default : kafka.serializer.DefaultEncoder

+ --line-reader

>控制台输入消息处理 default：kafka.tools.ConsoleProducer$LineMessageReader

+ --max-block-ms

>生产者请求阻塞最大等待时间ms default：60000

+ --max-memory-bytes

>The total memory used by the producer to buffer records waiting to be sent to the server. 
>default: 33554432

+ --max-partition-memory-bytes

>The buffer size allocated for a partition. When records are received which are smaller than this size the producer will attempt to optimistically group them together until this size is reached.

+ --message-send-max-retries

>发送消息的最大尝试次数

+ --metadata-expiry-ms

>The period of time in milliseconds after which we force a refresh of metadata even if we 
>haven't seen any leadership changes. default:300000

+ --old-producer

>使用旧的生产者

+ --producer-property

>生产者配置key=value

+ --producer.config <file>

>生产者配置file (会被--producer-property覆盖)

+ --property

>A mechanism to pass user-defined properties in the form key=value to the message reader. This 
>allows custom configuration for a user-defined message reader.

+ --queue-enqueuetimeout-ms

>Timeout for event enqueue default:2147483647

+ --queue-size

>如果生产者以异步模式工作，该设置将控制消息等待队列的最大长度 default: 10000

+ --request-required-acks

>即生产者配置acks

+ --request-timeout-ms

>ack等待超时时间 default : 1500

+ --retry-backoff-ms

>重试等待时间 default : 100

+ --socket-buffer-size

>The size of the tcp RECV size.(default: 102400)

+ --sync

>生产者使用同步模式

+ --timeout

>异步模式时，消息在队列中等待的最大时间 default : 1000

+ --topic (required)

>目标topic名称

### 示例

#### 生产消息到topic

>控制台生产消息

	kafka-console-producer.sh --broker-list 10.21.7.33:9092,10.21.7.21:9092 --topic fhh_stream_test
	message1
	message2
	message3
	message4

>查看生产的消息

	kafka-console-consumer.sh --zookeeper 10.21.7.21:2181 --topic fhh_stream_test --from-beginning
	message1
	message2
	message3
	message4

# consumer 操作及管理

## kafka-console-consumer.sh

>控制台消费topic中的消息

### 脚本参数

+ --blacklist

>topic黑名单

+ --whitelist

>topic白名单

+ --new-consumer

>使用新的消费者

+ --bootstrap-server

>新消费者设置连接broker列表 

+ --consumer.config <file>

>消费者配置

+ --csv-reporter-enabled

>If set, the CSV metrics reporter will be enabled

+ --delete-consumer-offsets

>If specified, the consumer path in zookeeper is deleted when starting up

+ --enable-systest-events

>Log lifecycle events of the consumer in addition to logging consumed messages. (This is 
>specific for system tests.)

+ --formatter

>消息展示格式化 default : kafka.tools.DefaultMessageFormatter

+ --from-beginning

>从最早的消息开始消费

+ --key-deserializer

>消息key反序列化

+ --value-deserializer

>消息value反序列化

+ --max-messages

>最大消费的消息数，如果没有设置则不会停止

+ --metrics-dir

>如果csv-reporter-enable被设置，该参数就是report输出目录

+ --property <prop>

>The properties to initialize the message formatter.

+ --skip-message-on-error

>如果处理消息出错，则跳过继续消费，而不是停止

+ --timeout-ms

> 消费等待超时，timeout没有消息可以消费则退出

+ --zookeeper 

>使用旧消费者时，设置zookeeper集群节点列表

+ --topic

>topic名称

### 示例

#### 消费topic中的消息输出到控制台

>从队列尾部开始消费消息

	kafka-console-consumer.sh --zookeeper 10.21.7.21:2181 --topic fhh_stream_test
	abc
	acc
	adf

>从最早的消息开始消费

	kafka-console-consumer.sh --zookeeper 10.21.7.21:2181 --topic fhh_stream_test --from-beginning
	abcd
	weee
	qwo
	abc
	acc
	adf

## kafka-consumer-groups.sh

>查询消费者组列表、详情及删除消费者组

### 脚本参数

+ --new-consumer

>使用新的消费者

+ --bootstrap-server (required)

>使用新的消费者时，设置broker列表

+ --zookeeper (required)

>使用旧的消费者时，设置zookeeper节点列表

+ --list

>消费者组列表

+ --describe 

>消费者组详细信息，需要和--group一起使用

+ --group

>消费者组名称

+ --command-config <file>

>客户端及消费者配置

+ --delete

>删除消费者组(可以删除整个消费者组[--group]，可以删除消费者组在某个topic上的offset记录
>[--group --topic],可以删除某个topic的所有消费者组记录[--topic])  

>WARNING: Group deletion only works for old ZK-based consumer groups, and one has to use 
>it carefully to only delete groups that are not active.

+ --topic

>删除消费者组时可以设置关联topic

### 示例

#### 查看消费者组列表

>new consumer 列表

	kafka-consumer-groups.sh --new-consumer --bootstrap-server 10.21.7.33:9092,10.21.7.21:9092 --list
	connect-fhh_sink_searchEngine_data
	connect-fhh_stream_carchannel_article
	connect-fhh_stream_carchannel_article_status

>old consumer 列表

	kafka-consumer-groups.sh --zookeeper 10.21.7.21:2181 --list
	console-consumer-41633
	console-consumer-36187
	console-consumer-81492
	console-consumer-85880
	console-consumer-63321

#### 查看消费者组详情

>new consumer

	kafka-consumer-groups.sh --new-consumer --bootstrap-server 10.21.7.33:9092,10.21.7.21:9092 --describe --group connect-fhh_sink_searchEngine_data

|GROUP   |TOPIC    |PARTITION  |CURRENT-OFFSET  |LOG-END-OFFSET  |LAG  | OWNER|
|:-------|:--------|:----------|:---------------|:---------------|:----|:-----|
|connect-fhh_sink_searchEngine_data|fhh_stream_searchEngine_data|0|22398|22398|0|consumer-6_/10.21.7.28|

>old consumer

	kafka-consumer-groups.sh --zookeeper 10.21.7.21:2181 --describe --group console-consumer-36187

|GROUP   |TOPIC    |PARTITION  |CURRENT-OFFSET  |LOG-END-OFFSET  |LAG  | OWNER|
|:-------|:--------|:----------|:---------------|:---------------|:----|:-----|
|console-consumer-36187|fhh_stream_carchannel_article_status|0|61|105|44|none |

#### 删除消费者组

>删除old consumer 消费者组

	kafka-consumer-groups.sh --zookeeper 10.21.7.21:2181 --delete --group console-consumer-36187
	Deleted all consumer group information for group console-consumer-36187 in zookeeper.

# partiton、replication管理

## kafka-reassign-partitions.sh

>人工移动topic、partitons

### 脚本参数

+ --zookeeper  (required)  

>kafka依赖的zookeeper管理集群节点(因为zookeeper是集群，这里写列表或一个节点都可以) 

+ --generate

>生成转移计划(须配合topics-to-move-json-file参数使用)

+ --topics-to-move-json-file <json file>

>待转移的topic配置(须配合broker-list参数使用)，json文件示例
>>{
>>   "topics":[{"topic": "foo"},{"topic": "foo1"}],
>>   "version":1                           
>>}  

+ --broker-list

>转移topic的目标broker列表

+ --execute

>执行转移计划(须配合reassignment-json-file参数使用)

+ --reassignment-json-file

>执行计划时，该参数指定计划文件(即--generate命令生成的文件)

+ --disable-rack-aware

>禁用机架感知(没懂)

+ --verify

>验证转移进度和结果(须配合reassignment-json-file参数使用)

### 示例

#### 生成转移计划

>将topic test的唯一partition从broker 1转移到broker 0

	cat topic-move.json
	{
		"topics" : [
			{
				"topic" : "test"
			}
		],
		"version" : 1
	}

	kafka-reassign-partitions.sh --zookeeper 10.21.7.21:2181 --generate --topics-to-move-json-file topic-move.json --broker-list "0"

	Current partition replica assignment

	{"version":1,"partitions":[{"topic":"test","partition":0,"replicas":[1]}]}
	Proposed partition reassignment configuration

	{"version":1,"partitions":[{"topic":"test","partition":0,"replicas":[0]}]}

#### 执行转移计划

>执行生成计划产生的move-exe.json转移计划

	vi move-exe.json 

	{"version":1,"partitions":[{"topic":"test","partition":0,"replicas":[0]}]}

	kafka-reassign-partitions.sh --zookeeper 10.21.7.21:2181 --execute --reassignment-json-file move-exe.json

#### 检查转移进度和结果

	kafka-reassign-partitions.sh --zookeeper 10.21.7.21:2181 --verify --reassignment-json-file move-exe.json

	Status of partition reassignment:
	Reassignment of partition [test,0] completed successfully

## kafka-replica-verification.sh

>监控topic的partition副本同步数据状态

### 脚本参数

+ --broker-list (required)

>kafka集群broker列表

+ --fetch-size

>每次请求拉取的数据大小

+ --max-wait-ms 

>每次请求拉取数据等待的最大时间

+ --report-interval-ms

>生成报告的间隔时间，默认30秒

+ --time

>用于获取初始offsets的时间戳(可选特殊值-1[最早]，-2[最晚]) 默认 -1

+ --topic-white-list

>要监控的topic列表，支持正则表达式(java)

### 示例

#### 监控topic数据同步情况

>监控fhh_stream_searchEngine_data的数据同步情况

	kafka-replica-verification.sh --broker-list 10.21.7.21:9092,10.21.7.33:9092 --topic-white-list fhh_stream_searchEngine_data

	verification process is started.
	max lag is 1 for partition [fhh_stream_searchEngine_data,2] at offset 10230330 among 5 partitions
	max lag is 1 for partition [fhh_stream_searchEngine_data,0] at offset 10316596 among 5 partitions
	max lag is 1 for partition [fhh_stream_searchEngine_data,4] at offset 10260847 among 5 partitions

## kafka-mirror-maker.sh

>kafka数据镜像备份工具

### 脚本参数

+ --abort.on.send.failure

>发送数据失败一次后停止mirror-maker default : true

+ --blacklist

>topic黑名单，不镜像该参数指定的topic数据

+ --whitelist

>topic白名单，镜像该参数指定的topic数据

+ --consumer.config <config file>

>源kafka集群的消费者配置

+ --consumer.rebalance.listener

>自定义消费者重新负载的监听器

+ --rebalance.listener.args

>消费者重新负载的监听器参数

+ --message.handler

>自定义的消息处理器(consumer与producer之间)

+ --message.handler.args

>消息处理器的参数

+ --new.consumer

>使用新消费者

+ --num.streams

>消费-生产流线程数

+ --offset.commit.interval.ms

>自动提交offsets的时间间隔

+ --producer.config <config file>

>目标kafka集群的生产者配置

### 示例

#### 备份kafka集群数据到另一个集群

>演示正式环境到测试环境的备份

	vi source_consumer.conf
	bootstrap.servers=10.90.9.138:9092,10.90.9.164:9092,10.90.9.165:9092
	group.id=mirror-source-consumers
	key.deserializer=org.apache.kafka.common.serialization.StringDeserializer
	value.deserializer=org.apache.kafka.common.serialization.StringDeserializer

	vi target_producer.conf
	bootstrap.servers=10.21.7.21:9092,10.21.7.33:9092
	key.deserializer=org.apache.kafka.common.serialization.StringDeserializer
	value.deserializer=org.apache.kafka.common.serialization.StringDeserializer

	kafka-mirror-maker.sh --consumer.config source_consumer.conf --num.streams 1 --producer.config target_producer.conf --whitelist=".*"

	通过kafka-consumer-group工具可查看备份情况