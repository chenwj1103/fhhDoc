# topic

>每条发布到kafka集群的消息都有一个类别，这个类别被称为topic。

## 相关配置

### broker-level

	auto.create.topics.enable

>broker配置，决定是否自动创建topic，生产环境不建议打开

	auto.leader.rebalance.enable

>broker配置，决定是否自动平衡topic的partition、replication，生产环境不建议打开

	compression.type

>topic的消息压缩格式，gzip,snappy,lz4.默认producer(意思是由生产者的压缩配置决定)

	delete.topic.enable

>broker配置，决定是否允许topic被删除，如果不打开只有修改一次配置重启kafka的broker之后才能删除
>topic，但是考虑到安全问题，生产环境还是不建议打开

### topic-level

	cleanup.policy [compact,delete(default)]

>partition的消息日志文件清理策略,delete：删除，compact：压缩，按照message的key保留最新的一条记录

![logical-structure](http://fex.staff.ifeng.com/fhh/fhh-doc/raw/64fc7537665d7bb97a4bb7080a116cb1a24362db/kafka/imgae/logical-structure.png)

![log-compaction](http://fex.staff.ifeng.com/fhh/fhh-doc/raw/64fc7537665d7bb97a4bb7080a116cb1a24362db/kafka/imgae/log-compaction.png)

# partition

>partition是有序不可变的消息序列，每一个消息对应一个数字id(offset)

![topic-partition](http://fex.staff.ifeng.com/fhh/fhh-doc/raw/b6e8cdc914415add9be5181f6491ae9717861c77/kafka/imgae/topic-partition.png)  

# producer

>负责发布消息到kafka broker，每一个消息都是键值对。
>生产者发送消息给topic，消息具备4个主要参数
>+ topic名称 (required)

>+ partition的id

>+ key

>+ value (required)

>partition的选择由以下顺序决定
>1. 指定partition的id
>2. 根据消息key值计算一个partition id
>3. 均衡负载

![producer-consumer](http://fex.staff.ifeng.com/fhh/fhh-doc/raw/a32f1cb9fdf464473784598a0d1a2bed3601bc87/kafka/imgae/producer-consumer.png)

# consumer

>消息消费者,从topic的partition中读取消息并处理。

>消费者是以Consumer Group分组的形式消费消息，topic中的一个partition只能被同一个Consumer
>Group中的某一个消费者消费。当group中的消费者数量与topic的partition数量相等时，资源利用最
>充分。

>每一个消费者的消费记录offset都被kafka集群记录在__consumer_offsets这个特殊的由kafka自行创
>建的特殊topic中，该topic可以由kafka自行管理。

>![consumer-group](http://fex.staff.ifeng.com/fhh/fhh-doc/raw/37ef4960d1c537b2184a68ba33671cb1d66364b2/kafka/imgae/consumer-group.png)