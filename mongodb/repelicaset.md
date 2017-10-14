1.复制集的搭建

    config={
        _id:"my_replica_set",
        members:[
        {_id:0,host:"192.168.1.129:27017"},
        {_id:1,host:"192.168.1.130:27017"},
        {_id:2,host:"192.168.1.131:27017"}
        ]
    }
    res.initiate(config)

res.initiate()命令进行初始化，初始化后各个成员之间开始发送心跳，并发起Primary选举操作，获得大多数成员投票的节点，会成为Primary,其余节点称为Secondary。

更详细的部署细节可以参考之前的[文档](http://fex.staff.ifeng.com/fhh/fhh-doc/wikis/mongodb-test)

2.大多数原则

假设复制集内投票成员数量为N，则大多数为N/2 +1,当复制集内存活成员数量不足大多数时，整个复制集无法选举出Primary,复制集将无法提供写服务，处于只读状态。

3.Secondary 节点

  正常情况下复制集的Secondary会参与Primary选举（自身也可能会被选为Primary），并从Primary同步最新的写入的数据，以保证与Primary存储相同的数据。Secondary可以提供读服务，增加Secondary节点可以提供复制集的的**读服务能力**，同时提升复制集的可用性。

4.Arbiter 节点

Arbiter节点只参与投票，不能被选为Primary，并且不从Primary同步数据。比如你部署了一个节点的复制集，1个Primary，1个Secondary，任意节点宕机，复制集将不能提供服务了（无选Primary），这时可以给复制集添加一个Arbiter节点，即使有节点宕机，仍能选Primary。
**Arbiter本身不存储数据，是非常轻量级的服务，当复制集成员为偶数时，最好加入一Arbiter点，以提升复制集可用性**。

5.Priority=0 属性

Priority 0节点的选举优先级为0，不会被选举为Primary，如果想被选为Primary，Priority至少为1

6.Vote=0 属性

Mongodb3.0里，复制集成员最多50个，参与Primary选举投票的成员最多7个，其他成员的vote属性必须设置为0，即不参与投票。

7.Hidden 节点

Hidden节点不能被选为主（Priority为0），并且对Driver不可见
因Hidden节点不会接受Driver的请求，可使用Hidden节点做一些数据备份、离线计算的任务，不会影响到复制集的服务。

8.Delayed 节点

Delayed 节点必须是Hidden节点，并且其数据落后于Primary一段时间。因delay节点的数据比Primary落后一段时间，当错误或者无效的数据写入Primary时，可通过Delayed节点的数据来恢复到之前的时间点。

9.数据同步

Primary与Secondary之间通过oplog来同步数据，Primary上的写操作完成后，会向特殊的local.oplog.rs特殊集合写入一条oplog，Secondary不断的从Primary取新的oplog并应用。
因oplog的数据会不断增加，local.oplog.rs被设置成为一个capped集合，当容量达到配置上限时，会将最旧的数据删除掉。

10.Primary选举除了在复制集初始化时发生，还有如下场景

* 复制集被recofig
* Secondary检测到Primary宕机时，会触发新Primary选举
* 当有Primary节点主动stepDown（主动降级为Secondary）时，也会触发新的Primary选举。


11.节点间心跳

复制集成员默认每2秒发送一次心跳信息，如果10s未收到某个节点的心跳，则认为该节点一宕机；如果宕机的节点为Primary，Secondary（前提是可被选为Primary）会发起新的Primary选举。

12.节点优先级

* 每个节点都倾向于投票给优先级最高的节点
* 优先级为0的节点不会主动发起Primary选举
* 当Primary发现有优先级更高的Secondary，并且该Secondary的数据落后在10s内，则Primary会主动降级，让优先级更高的Secondary有成为Primary的机会。


13.Optime

 拥有最新Optime（最近一条oplog的时间戳）的节点才能被选为主。
