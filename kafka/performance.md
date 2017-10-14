# 相关参数介绍
>## kafka官方推荐使用最新的G1垃圾回收器。
>>G1相比较于CMS的优势：
>>>+ G1是一种适用于服务器端的垃圾回收器，很好的平衡了吞吐量和响应能力。
>>>+ 对于内存的划分方法不同，Eden, Survivor, Old区域不再固定，使用内存会更高效。G1通过对内存进行Region的划分，有效避免了内存碎片问题。
>>>+ G1可以指定GC时可用于暂停线程的时间（不保证严格遵守）。而CMS并不提供可控选项。
>>>+ CMS只有在FullGC之后会重新合并压缩内存，而G1把回收和合并集合在一起。
>>>+ CMS只能使用在Old区，在清理Young时一般是配合使用ParNew，而G1可以统一两类分区的回收算法。

>>G1的适用场景：
>>>+ JVM占用内存较大(At least 4G)。
>>>+ 应用本身频繁申请、释放内存，进而产生大量内存碎片时。
>>>+ 对于GC时间较为敏感的应用。

>## kafka可能对性能有影响的配置项
>### broker

>#### num.network.threads:3
>>用于接收并处理网络请求的线程数，默认为3。其内部实现是采用Selector模型。启动一个线程作为Acceptor
>>来负责建立连接，再配合启动num.network.threads个线程来轮流负责从Sockets里读取请求，一般无需改动，
>>除非上下游并发请求量过大。

>#### num.partitions:1
>>当Partition数量相对于流入流出的数据量显得较少，或由于业务逻辑和Partition数量没有匹配好造成个别
>>Partition读写数据量大，大量的读写请求集中落在一台或几台机器上时，很容易就会打满NIC的全部流量。
>>不难想象这时不仅这一个Partition的读写会出现性能瓶颈，同Broker上的其他Partition或服务都会陷入一
>>个网络资源匮乏的情况。

>#### queued.max.requests:500
>>这个参数是指定用于缓存网络请求的队列的最大容量，这个队列达到上限之后将不再接收新请求。一般不会
>>成为瓶颈点，除非I/O性能太差，这时需要配合num.io.threads等配置一同进行调整。

>### replica

>#### replica.lag.time.max.ms:10000
>#### num.replica.fetchers:1
>>num.replica.fetchers 参数是副本从leader拉取同步数据时开启的线程数量，replica.lag.time.max.ms是拉取
>>线程最大的空闲时间。这2个参数配合使用提高leader同步数据到副本的效率。

>#### default.replication.factor:1
>>这个参数指新创建一个topic时，默认的Replica数量。当Producer中的 acks!=0 && acks!=1时(即生产者要
>>确认副本同步数据响应)，Replica的大小可能会导致在Produce数据时的性能表现有很大不同。Replica过少
>>会影响数据的可用性，太多则会白白浪费存储资源，一般建议在2~3为宜。

>#### log.flush.interval.ms
>#### log.flush.scheduler.interval.ms
>#### log.flush.interval.messages
>>log.flush.interval.ms 消息从内存写到硬盘的最大间隔时间，log.flush.scheduler.interval.ms消息写盘定时
>>任务间隔时间，log.flush.interval.messages消息刷新到硬盘之前允许积累的最大消息数量。这些参数控制着
>>Broker写盘的频率，一般无需改动。如果topic的数据量较小可以考虑减少log.flush.interval.ms和log.flush.
>>interval.messages来强制刷写数据，减少可能由于缓存数据未写盘带来的不一致。

>#### min.insync.replicas:1
>>这个参数只能在topic层级配置，指定每次Producer写操作至少要保证有多少个在ISR的Replica确认，一般
>>配合request.required.acks使用。要注意，这个参数如果设置的过高可能会大幅降低吞吐量。

>#### compression.codec:none
>>Message落地时是否采用以及采用何种压缩算法。一般都是把Producer发过来Message直接保存，不再改变压
>>缩方式。

>### producer

>#### block.on.buffer
>>在Producer端用来存放尚未发送出去的Message的缓冲区大小。

>#### compression.type
>>默认发送不进行压缩，推荐配置一种适合的压缩算法，可以大幅度的减缓网络压力和Broker的存储压力。

>#### linger.ms
>>Producer默认会把两次发送时间间隔内收集到的所有Requests进行一次聚合然后再发送，以此提高吞吐量，
>>而linger.ms则更进一步，这个参数为每次发送增加一些delay，以此来聚合更多的Message。

>#### batch.size:16384
>>Producer会尝试去把发往同一个Partition的多个Requests进行合并，batch.size指明了一次Batch合并后
>>Requests总大小的上限。如果这个值设置的太小，可能会导致所有的Request都不进行Batch。

>#### acks:1
>>这个配置可以设定发送消息后是否需要Broker端返回确认。
>>>+ 0:不需要进行确认，速度最快。但是不能保证服务器端一定接收到数据。
>>>+ 1:仅需要Leader进行确认，不需要副本进行确认。是一种效率和安全折中的方式。
>>>+ all:需要ISR中所有的Replica给予接收确认，速度最慢，安全性最高，但是由于副本可能会缩小到仅
>>>包含一个Replica，所以设置参数为all并不能一定避免数据丢失。

>### consumer

>#### fetch.min.bytes:1 
>>每次请求拉取数据大小的最小值。一般保持默认值。

>#### fetch.max.bytes:52428800
>>服务器每次响应消费者请求数据的最大大小。设置太大可能降低消费者的读效率。

>#### max.poll.records:500
>>消费者请求一次拉取的最大消息数量。同样设置太大可能增加读数据效率，但是该参数受到fetch.max.
>>bytes限制。

>##### 注：kafka的参数随版本快速迭代变化较快，配置时一定要在官网确认对应版本的配置。

# 性能测试

>## 测试准备
>+ bootstrap-server 

>>10.21.7.21:9092,10.21.7.33:9092

>+ topic

>> performance_test

>+ partitions

>> 2

>+ replication-factor

>> 2

>## producer

> 测试使用官方提供的测试脚本

> kafka-producer-perf-test.sh
>+ --topic TOPIC

> 测试topic
>+ --num-records NUM-RECORDS

> 测试生产消息数量
>+ --record-size

> 测试生产每个消息的大小
>+ --throughput THROUGHPUT

> 单位时间吞吐记录数最大限制
>+ --producer-props PROP-NAME=PROP-VALUE [PROP-NAME=PROP-VALUE ...]

> 生产者配置(测试目标)

>### acks

>|record size|record num|acks|records/sec|MB/sec|
>|:----------|:---------|:---|:----------|:-----|
>|1024       |100000    |0   |80710.250202|78.82|
>|1024       |100000    |1   |72516.316171|70.82|
>|1024       |100000    |all |20833.333333|20.35|

>### record size

>|record size|record num|acks|records/sec|MB/sec|
>|:----------|:---------|:---|:----------|:-----|
>|512        |100000    |1   |99700.897308|48.68|
>|1024       |100000    |1   |74404.761905|72.66|
>|2048       |100000    |1   |39541.320680|77.23|
>|4096       |100000    |1   |21240.441801|82.97|
>|10240      |100000    |1   |8605.111436 |84.03|
>|102400     |100000    |1   |1347.037192 |131.55|

>### batch size

>|record size|record num|acks|batch size|records/sec|MB/sec|
>|:----------|:---------|:---|:---------|:----------|:-----|
>|1024       |100000    |1   |8192      |52164.840897|50.94|
>|1024       |100000    |1   |16384     |68073.519401|66.48|
>|1024       |100000    |1   |163840    |99601.593625|97.27|
>|1024       |100000    |1   |1638400   |83963.056255|82.00|

>## consumer
> 测试使用官方提供的测试脚本

> kafka-consumer-perf-test.sh
>+ --topic TOPIC

> 测试topic
>+ --broker-list

> 测试kafka集群节点列表
>+ --messages

> 测试消费消息总数
>+ --new-consumer

> 使用新的消费者设计算法
>+ --num-fetch-threads

> 消费者拉取数据的线程数
>+ fetch-size

> 一次请求拉取消息的最大大小
>+ socket-buffer-size

> tpc连接接收一次数据的最大大小

>### num-fetch-threads

>|num of fetch threads|messages|fetch size|socket-buffer-size|nMsg/sec|MB/sec|
>|:-------------------|:-------|:---------|:-----------------|:----------|:-----|
>|1                   |100000  |1048576   |2097152           |208958.2463|204.0608|
>|5                   |100000  |1048576   |2097152           |207227.7433|202.3708|
>|10                  |100000  |1048576   |2097152           |212057.2034|207.0871|
>|20                  |100000  |1048576   |2097152           |220951.4349|215.7729|
>|50                  |100000  |1048576   |2097152           |223417.4107|218.1811|
>|100                 |100000  |1048576   |2097152           |208089.3971|203.2123|

>### fetch-size

>|num of fetch threads|messages|fetch size|socket buffer size|nMsg/sec|MB/sec|
>|:-------------------|:-------|:---------|:-----------------|:----------|:-----|
>|10                  |100000  |32768     |2097152           |221440.2655|216.2503|
>|10                  |100000  |131072    |2097152           |207227.7433|202.3708|
>|10                  |100000  |524288    |2097152           |206373.1959|201.5363|
>|10                  |100000  |1048576   |2097152           |201796.3710|197.0668|
>|10                  |100000  |2097152   |2097152           |212057.2034|207.0871|
>|10                  |100000  |4194304   |2097152           |200583.1663|195.8820|

>### socket-buffer-size

>|num of fetch threads|messages|fetch size|socket-buffer-size|nMsg/sec|MB/sec|
>|:-------------------|:-------|:---------|:-----------------|:----------|:-----|
>|10                  |100000  |1048576   |262144            |244124.3902|238.4027|
>|10                  |100000  |1048576   |524288            |204267.3469|199.4798|
>|10                  |100000  |1048576   |1048576           |213869.6581|208.8571|
>|10                  |100000  |1048576   |2097152           |207657.6763|202.7907|
>|10                  |100000  |1048576   |4194304           |202613.3603|197.8646|
