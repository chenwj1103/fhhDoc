# kafka的安装与部署  

## 下载服务端代码

>[download](https://www.apache.org/dyn/closer.cgi?path=/kafka/0.11.0.0/kafka_2.11-0.11.0.0.tgz)  
>untar

## broker配置文件

>在kafka的config目录下，官方提供了很多默认配置文件，其中server.properties就是broker的配置文件。
>参考[Broker Configs](http://kafka.apache.org/documentation/#brokerconfigs)编辑该配置文件，下
>面是一些重要的配置说明  

+ broker.id  

>kafka节点的唯一标识，该配置必须是一个kafka集群中唯一的整数，使用server.properties启动的每一个
>进程都是一个唯一的broker，故每一次启动都是必须唯一的broker.id  

+ listeners  

>每一个broker都需要配置的监听地址  

>>FORMAT:

>>>listeners = security-protocol://host_name:port  

>>EXAMPLE:

>>>listeners = PLAINTEXT://myhost:9092,SSL://:9091 CLIENT://0.0.0.0:9092,REPLICATION://localhost:9093  

+ advertised.listeners  

>节点推送给zookeeper用来让client访问的监听地址,与listeners规则一致，没有设置则会使用listeners配置  

+ num.network.threads  

>broker用来接收和响应client请求的线程数  

+ num.io.threads  

>broker用来处理client请求(包含磁盘I/O操作)的线程数  

+ socket.send.buffer.bytes  

>socket发送缓冲区(SO_SNDBUF)的大小  

+ socket.receive.buffer.bytes  

>socket接收缓冲区(SO_RCVBUF)的大小  

+ socket.request.max.bytes  

>socket一次请求接收的数据最大字节数,该配置受业务数据大小影响，需谨慎设置，但是设置太大可能会造成OOM
>(内存溢出)  

+ log.dirs  

>broker保存消息文件的目录,可设置多个目录(逗号分隔)  

+ num.recovery.threads.per.data.dir  

>broker启动时恢复数据和shutdown时flush数据时的为每一个log.dir开启的线程数  

+ num.partitions  

>自动创建topic时使用的默认partition数量  

+ log.flush.interval.messages  

>每接收N条消息后刷新到磁盘一次(官方不建议设置，默认是每条消息立刻写盘)  

+ log.flush.interval.ms  

>每N ms刷新消息到磁盘一次(官方不建议设置，默认是每条消息立刻写盘)  

+ log.retention.hours  

>日志文件的最长保留时间，默认168小时  

+ log.retention.bytes  

>日志文件的最大保留体积(一般不设置)  

+ log.segment.bytes  

>日志分段文件的最大体积  

+ log.retention.check.interval.ms  

>日志文件保留策略的检查周期  

+ zookeeper.connect  

>kafka依赖的管理zookeeper的集群列表配置  

+ zookeeper.connection.timeout.ms  

>kafka节点与zookeeper通信超时时间  

+ auto.create.topics.enable = false  

>是否允许创建不存在的topic，测试环境中建议打开。生产环境强烈建议关闭。  

+ delete.topic.enable = true  

>是否允许删除topic  

+ message.max.bytes  

>每个消息的最大体积  

+ replica.fetch.max.bytes  

>副本每次拉取数据的最大体积  

## 启动broker节点

>使用bin/kafka-server-start.sh脚本启动broker  

	bin/kafka-server-start.sh config/server.properties &  

## 停止broker节点

>使用bin/kafka-server-stop.sh关闭节点   

	bin/kafka-server-stop.sh 
	
>建议并且应该使用该脚本停止broker节点，kafka会等待消息进行一些处理后安全关闭broker，直接
>kill进程会导致生产、消费、复制集复制突然中断，带来数据丢失，消费不完全，复制不完全等等
>可能性。