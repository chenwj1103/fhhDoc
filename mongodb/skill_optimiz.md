### 一. MongoDB 使用优化
* 查询的优化

1. 根据业务查询建立合适的索引

        db.collection.createIndex({filed:1})

    **默认情况下建立索引，将阻塞其他所有的操作，直到索引建立完成。所以当数据量大时，这样建立索引将是一个漫长的过程，这对生产系统来说是个严重的问题**。所以我们MongoDB给我们提供了一些其他选项：

        db.collection.createIndex({filed:1},options)

    -- background : 设置该选项为true之后，数据库将采用"后台"模式创建索引,**这种模式不会阻塞数据库其他的操作**。MongoDB将采用一种增量的方式建立索引，这样比"前台"创建模式要慢一些。如果内存大小比要建立的索引小，这种模式可能比"前台"模式花费更长的时间。

    -- sparse : 设置该选项为true之后，将建立[稀疏索引](https://docs.mongodb.com/manual/core/index-sparse/)。这种索引类型将只包含该索引字段的文档(**即使该文档的这个字段为null**)，不包含没有索引字段的文档。相反，**普通的索引将包含所有的文档，对没有索引字段的文档将存储null值**。

    不过这种索引也会带来一些问题，[返回不完整的结果](https://docs.mongodb.com/manual/core/index-sparse/#sparse-index-incomplete-results)。MongoDB将不会使用这种索引，除非使用hint()方法指定该索引。

        //假设有一个scores集合
        { "_id" : ObjectId("523b6e32fb408eea0eec2647"), "userid" : "newbie" }
        { "_id" : ObjectId("523b6e61fb408eea0eec2648"), "userid" : "abby", "score" : 82 }
        { "_id" : ObjectId("523b6e6ffb408eea0eec2649"), "userid" : "nina", "score" : 90 }

        //在该集合上建立索引
        db.scores.createIndex( { score: 1 } , { sparse: true } ) 

        //下面这条查询命令将会返回'abby','nina'两条记录
        db.scores.find().sort( { score: -1 } ).hint( { score: 1 } )

        //而 db.scores.find().sort( { score: -1 } ) 命令将返回'newbie', 'abby','nina'这三条记录

    --partialFilterExpression : 3.2版本之后，索引又增加了一种属性--[部分索引](https://docs.mongodb.com/manual/core/index-partial/)。这个索引采用一个过滤条件，利用集合的一部分文档建立索引，缩小了建立和维护索引的性能损耗。可以看做稀疏索引的升级版，比稀疏索引的功能更强大。

        db.contacts.createIndex(
           { field: 1 },
           { partialFilterExpression: { field: { $exists: true } } }
        )
       // 这样就和稀疏索引的效果就一样了

    -- [其他的一些选项](https://docs.mongodb.com/manual/reference/method/db.collection.createIndex/) 



2. 限制返回的条数limit()

        db.wemedia_account.find({accountType:{$in:[1,2]},status:2}).select('weMediaName eAccount').limit(1000)

        db.wemedia_account.find({accountType:{$in:[1,2]},status:2}).select('weMediaName eAccount').limit(2000)

3. 返回自己需要的字段，减少网络传输流量

    db.collection.find({},{title:1,author:1...})

        //demo 
        db.wemedia_account.find({accountType:{$in:[1,2]},status:2}).select('weMediaName eAccount').limit(1000)

        db.wemedia_account.find({accountType:{$in:[1,2]},status:2}).limit(1000)

4. hint()方法,强制使用指定的索引

    **一般情况下数据库查询优化器已经帮我们优化的很好了**

5. 使用$inc在服务器端进行操作(逻辑锁)(**???不太明白官网为什么会把此当做优化**)

    [当查询的时候，使用某个数值字段作为查询条件，在服务器查询并使用$inc修改这个字段，这样有时可以解决竞态的情况](https://docs.mongodb.com/manual/tutorial/optimize-query-performance-with-indexes-and-projections/)。

    [查询优化](https://docs.mongodb.com/manual/core/query-optimization/)

    [正则表达式的查询](https://docs.mongodb.com/manual/reference/operator/query/regex/#regex-index-use 
)

* 写的优化
1. 索引的问题

    事物具有两面性：索引帮助我们提高了查询的性能，但是带来的问题时当我们insert或者delete写操作时，数据库相应的会insert或者delete一条和文档相关的记录在索引集合里面；update操作根据更新的字段有时也会影响到索引的更改。

    所以当我们考虑建一个新的索引时，我们要考虑是否现有的索引能够支撑业务，是否真的有必要建立这个索引，以免带来性能的损耗。    

2. 硬件的优化

   SSD硬盘比传统的HDD硬盘平均性能要好上100倍或者更多。

3. journal

    为了能在数据库出现故障的时候，仍然能够恢复数据。MongoDB采用[write ahead logging ](https://en.wikipedia.org/wiki/Write-ahead_logging)机制(修改数据库时，不直接修改数据库内容，而是将修改完的数据写入日志中)。
    
    为了保持数据的安全性和数据库的性能之间的平衡，可以参考下面的意见：

* 可以考虑把日志(journal)和数据文件（data file）保存在不同的设备上，这样data file 和journal 就不会因为有限的I/O资源而竞争了。
   * 停止mongodb实例，执行以下命令
    ```
     > cd /data/mongodb/dbpath 
     > mv ./journal ./journal_orig
     > ln -s /var/lib/mongo/journal .

    ```

* [write concerns](https://docs.mongodb.com/manual/reference/write-concern/) 中包含[ j option ](https://docs.mongodb.com/manual/reference/write-concern/#writeconcern.j) ,数据库实例将会缩短日志写的间隔，将会增加写的次数。

* 在数据库运行期间，日志写的时间间隔是可以用[commitIntervalMs](https://docs.mongodb.com/manual/reference/configuration-options/#storage.journal.commitIntervalMs)配置。缩短日志提交的间隔，将增加写的次数，这有可能降低数据库的写性能；增大日志写的间隔，可以降低日志写的次数，但是增加了数据库宕机时没有记录某一条写操作的概率。


    [journal 工作原理](http://blog.csdn.net/zhaowenzhong/article/details/50593894)

    [MongoDB journal 与 oplog，究竟谁先写入？](https://yq.aliyun.com/articles/73002?commentId=8939)

### 二. MongoDB的查询计划（explain)
 #### 命令
    db.collection.explain() 
    //or 
    cursor.explain()
这个命令返回执行计划及执行计划统计详情等。返回的是一个树形结构的对象。每一层返回他的结果给他的父节点。叶子节点直接访问的是集合或者索引表。中间的节点从他的子节点中获得结果，然后操作文档或者索引键。根节点是MongoDB返回最后结果集的阶段。

stage的类型的介绍：
   * __COLLSCAN: 集合扫描阶段__
   * __IXSCAN: 索引扫描阶段__
   * FETCH: 提取文档阶段
   * SHARD_MERGE: 从各个分片上合并结果的阶段
   * __SORT: 表明在内存中进行了排序（与前期版本的scanAndOrder:true一致）__
   * SORT_MERGE: 表明在内存中进行了排序后再合并
   * LIMIT: 使用limit限制返回数
   * SKIP: 使用skip进行跳过
   * __IDHACK: 针对_id进行查询__
   * SHARDING_FILTER: 通过mongos对分片数据进行查询
   * COUNT: 利用db.coll.count()之类进行count运算
   * __//COUNTSCAN: count不使用Index进行count时的stage返回__
   * __COUNT_SCAN: count使用了Index进行count时的stage返回__
   * SUBPLAN: 使用$or查询的stage返回
   * TEXT: 使用全文索引进行查询时候的stage返回
   * PROJECTION: 限定返回字段时候stage的返回

  #### 三种模式 (explain命令的参数)
* queryPlanner 模式(默认)

    MongoDB运行查询优化器对当前的查询进行评估并选择一个最佳的查询计划

* executionStats模式 

    MongoDB运行查询优化器对当前的查询进行评估并选择一个最佳的查询计划进行执行。在执行完毕后返回这个最佳执行计划执行完成时的相关统计信息

* allPlansExecution模式

    allPlansExecution模式是将所有的执行计划均进行executionStats模式的操作。

#### [返回结果](https://docs.mongodb.com/manual/reference/explain-results/#explain.queryPlanner)

 * queryPalnner 返回结果:

    explain.queryPlanner.namespace:该值返回的是该query所查询的表

    explain.queryPlanner.indexFilterSet:针对该query是否有indexfilter

    explain.queryPlanner.winningPlan:查询优化器针对该query所返回的最优执行计划的详细内容。

    explain.queryPlanner.winningPlan.stage:最优执行计划的stage。

    __explain.queryPlanner.winningPlan.inputStage:用来描述子stage，并且为其父stage提供文档和索引关键字。__

    __explain.queryPlanner.winningPlan.inputStages: 用一个数组来描述子stage,表示有多个子stage。__

    explain.queryPlanner.winningPlan.keyPattern:所扫描的index内容。

    explain.queryPlanner.winningPlan.indexName: winning plan所选用的index。

    explain.queryPlanner.winningPlan.isMultiKey: 是否是Multikey，此处返回是false，如果索引建立在array上，此处将是true。

    explain.queryPlanner.winningPlan.direction: 此query的查询顺序此处,forward(从小到大)，如果用了.sort({modify_time:-1})将显示backward。

    explain.queryPlanner.winningPlan.indexBounds:winningplan所扫描的索引范围,如果没有制定范围就是[MaxKey, MinKey]，这主要是直接定位到mongodb的chunck中去查找数据，加快数据读取。

    explain.queryPlanner.rejectedPlans：其他执行计划（非最优而被查询优化器reject的）的详细返回，其中具体信息与winningPlan的返回中意义相同。

* executionStats 返回结果:

    __executionStats.nReturned：满足查询条件的文档个数，即查询的返回条数;__

    executionStats.executionTimeMillis: 整体执行时间;

    __executionStats.totalKeysExamined: 索引整体扫描的文档个数，和早起版本的nscanned 是一样的;__

    __executionStats.totalDocsExamined: document扫描个数， 和早期版本中的nscannedObjects 是一样的;__

    executionStats.executionStages:整个winningPlan执行树的详细信息，一个executionStages包含一个或者多个inputStages;

    explain.executionStats.executionStages.works: 被查询执行阶段所操作的“工作单元(work units)”数;

    explain.executionStats.executionStages.advanced:返回给父stage的中间结果集中文档个数;

    explain.executionStats.executionStages.needTime: 没有给父stage返回结果工作周期(work cycles)的个数

    explain.executionStats.executionStages.needYield:表示存储层请求查询系统产生锁的次数。

    explain.executionStats.executionStages.isEOF:查询执行是否已经到了数据流的末尾
    这些值的初始值都是0。如果是true或者1，则执行阶段已经达到数据流的末尾；如果为false或0，则该阶段仍有结果要返回。

    explain.executionStats.executionStages.inputStage.keysExamined:[查询执行阶段，索引扫描检查范围内和范围外key的总数](https://docs.mongodb.com/manual/reference/explain-results/#explain.executionStats.executionStages.inputStage.keysExamined)。

    explain.executionStats.executionStages.inputStage.docsExamined:表示查询执行阶段扫描文档的个数。

    explain.executionStats.allPlansExecution:在选出最优计划和放弃的计划的选择阶段所捕获的部分信息。


        对于普通查询，我们最希望看到的组合有这些：

        Fetch+IDHACK

        Fetch+IXSCAN

        Limit+（Fetch+IXSCAN）

        PROJECTION+IXSCAN

        SHARDING_FILTER+IXSCAN

        不希望看到包含如下的stage：

        COLLSCAN（全表扫），SORT（使用sort但是无index），不合理的SKIP

        对于count查询，希望看到的有：COUNT_SCAN 不希望看到的有:  COUNTSCAN

查询计划分析实例：以我们现有系统账户表(wemedia_account)

        该表的索引字段有：_id online eId eAccountId updateTime weMediaName onlineTime auditTime applyTime operatorTelephone accountWeight 
        执行下面这条命令：
        db.wemedia_account.find({online:2}).explain('executionStats')   
        返回结果：
        {
            "queryPlanner" : {
            "mongosPlannerVersion" : 1,
            "winningPlan" : {
                "stage" : "SINGLE_SHARD",
                "shards" : [
                    {
                        "shardName" : "sharddbshardSvr1",
                        "connectionString" : "sharddbshardSvr1/10.90.34.36:27037,10.90.34.37:27037,10.90.34.38:27037",
                        "serverInfo" : {
                            "host" : "wemedia_test_db37v34_syq",
                            "port" : 27037,
                            "version" : "3.4.4",
                            "gitVersion" : "888390515874a9debd1b6c5d36559ca86b44babd"
                        },
                        "namespace" : "fhh_test.wemedia_account",
                        "indexFilterSet" : false,
                        "parsedQuery" : {
                            "accountType" : {
                                "$in" : [
                                    1,
                                    2
                                ]
                            }
                        },
                        "winningPlan" : {
                            "stage" : "COLLSCAN",
                            "filter" : {
                                "accountType" : {
                                    "$in" : [
                                        1,
                                        2
                                    ]
                                }
                            },
                            "direction" : "forward"
                        },
                        "rejectedPlans" : [ ]
                    }
                ]
            }
        },
        "executionStats" : {
            "nReturned" : 140305,
            "executionTimeMillis" : 364,
            "totalKeysExamined" : 0,
            "totalDocsExamined" : 369302,
            "executionStages" : {
                "stage" : "SINGLE_SHARD",
                "nReturned" : 140305,
                "executionTimeMillis" : 364,
                "totalKeysExamined" : 0,
                "totalDocsExamined" : 369302,
                "totalChildMillis" : 363,
                "shards" : [
                    {
                        "shardName" : "sharddbshardSvr1",
                        "executionSuccess" : true,
                        "executionStages" : {
                            "stage" : "COLLSCAN",
                            "filter" : {
                                "accountType" : {
                                    "$in" : [
                                        1,
                                        2
                                    ]
                                }
                            },
                            "nReturned" : 140305,
                            "executionTimeMillisEstimate" : 353,
                            "works" : 369304,
                            "advanced" : 140305,
                            "needTime" : 228998,
                            "needYield" : 0,
                            "isEOF" : 1,
                            "direction" : "forward",
                            "docsExamined" : 369302
                        }
                    }
                ]
            }
        },
        "ok" : 1
        }

    以下一些命令，自己在mongo shell中执行以下，自己对应着返回结果观察一下：
    db.wemedia_account.find({accountType:{$in:[1,2]}}).explain('executionStats')  //COLLSCAN

    db.wemedia_account.find({online:2}).explain('executionStats')   //FETCH +IXSCAN


    db.wemedia_account.find({accountType:{$in:[1,2]},online:2}).explain('executionStats')

    db.wemdia_account.explain('executionStats').count({accountType:{$in:[1,2]}})

    db.wemedia_account.explain('executionStats').count({online:2})  //COUNT_SCAN

    db.wemedia_account.explain('executionStats').count({status:2})

    db.wemedia_account.find({weMediaName:/弥音/}).explain('executionStats')

    db.wemedia_account.find().sort('-level').explain('executionStats')

    db.wemedia_account.find({_id:ObjectId("58576c67951f464ba7816720")}).explain('executionStats')




### 三.MongoDB 慢查询日志(profile)
   和MySQL一样，MongoDB也有慢查询日志。有下面两种方式开启MongoDB的慢查询日志。
   * 启动MongoDB时，加上profile=level 参数

   * 在mongodb shell 调用db.setProfilingLevel(level ,slowms)

   level : 0:关闭慢查询日志，1：只记录慢查询 2：记录所有的操作

   slowms :慢查询的时间标准，默认100ms

   与MySQL不同，MongoDB慢查询日志会保存在system.profile 集合中，我们要查找慢查询日志，只需要查询这个集合就行了。
   此外，当不开启慢查询日志的时候，MongoDB仍然会在log文件中记录超过慢查询时间标准的查询操作。

### 四.MongoDB 使用建议

1. 尽量不要使用$nin 和$ne ($exists,$not)

   在大多数情况下，使用这两个关键字查询，使用索引并不比不使用索引性能好多少。

        db.wemedia_account.find({ weMediaType: { $ne: 2 } }).select('weMediaName eAccountId').limit(1000)
        //测试库中做测试，账户表中weMediaType字段没有建立索引，你可以试一下在该字段上建立索引和不建索引查询时间对比

2. 正则表达式的使用

        { <field>: { $regex: /pattern/, $options: '<options>' } }
        { <field>: { $regex: 'pattern', $options: '<options>' } }
        { <field>: { $regex: /pattern/<options> } }
    option:

    i:大小写不敏感

    m:如果模式中包含(^ 或$)匹配开始或者末尾，有了此选项，将匹配多行的开始和结尾

        db.products.find( { description: { $regex: /^S/, $options: 'm' } } )

        // 将匹配下面的文档
        { "_id" : 100, "sku" : "abc123", "description" : "Single line description." }
        { "_id" : 101, "sku" : "abc789", "description" : "First line\nSecond line" }
        如果没有m选项，将只匹配
        { "_id" : 100, "sku" : "abc123", "description" : "Single line description." }

    x: 忽略空格和注释

        var pattern = "abc #category code\n123 #item number"
        db.products.find( { sku: { $regex: pattern, $options: "x" } } )
        //将匹配下面的文档
        { "_id" : 100, "sku" : "abc123", "description" : "Single line description." }


    s: [允许dot(.)匹配任何字符，包括新的一行的符号](https://docs.mongodb.com/manual/reference/operator/query/regex/#regex-dot-new-line)。
  
    正则表达式索引的使用: 如果查询的字段是索引字段，MongoDB 将在索引中匹配查询值。此外如果匹配模式是“prefix string”(前缀是某一个字符串)，MongoDB将根据这个前缀建立一个“范围“，然后从索引中匹配落到这个范围的值。

        /^a/ ,/^a.*/,/^a.*$/ 匹配相同的字符串，但是他们有着不同的性能。/^a.*/,/^a.*$/将会慢一些，因为/^a/匹配到前缀之后就会停止扫描。


3. 当同一字段的多个值时，用$in而不是$or 

        db.wemedia_account.find({accountType:{$in:[1,2]}})
        // don`t use 
        // db.wemedia_account.find({$or:[{accountType:1},{accountType:2}]})

4. batchSize()
        
        batchSize()的作用是设置从数据库每批次返回文件的的个数,当查询大量数据时，可以使用该方法。大多数情况下，修改该值对程序没有影响，因为大多说情况下客户端驱动程序都会把结果当做一个批次来发送。注意不要传参数为1或者负数，这样和limit()的作用一样了。
    [batchSize()](https://docs.mongodb.com/manual/reference/method/cursor.batchSize/)
   
5. mongoose 使用时可以采用lean()来优化

        lean() 的作用是：不把查询到的文档转成自定义的Schema类型,也就是返回原生的结果，mongoose不会为这个结果添加一些属性和方法，例如id属性，toObject(),toJson()方法。

6. 当使用聚合的时候尽量把match,sort等阶段放在前面，这样可以有效的利用索引


7. 当使用聚合查询的时候，如果使用ObjectId类型,mongoose 不会把字符串给我们转成ObjectId类型,而普通查询会帮我们做自动转换。

8. 当使用聚合查询，按时间聚合的时候，注意时区的问题。

        //假设有一article集合，有下面7条记录

        { title: 'hello java', author: 'java', createTime: new Date('2017-07-01 05:23:46') },
        { title: 'hello c#', author: 'csharp', createTime: new Date('2017-07-01 13:23:46') },

        { title: 'hello js', author: 'javascript', createTime: new Date('2017-07-02 07:23:46') },
        { title: 'hello python', author: 'python', createTime: new Date('2017-07-02 18:23:46') },

        { title: 'hello golang', author: 'golang', createTime: new Date('2017-07-05 02:23:46') },

        { title: 'hello c++', author: 'cpp', createTime: new Date('2016-12-31 05:23:46') },
        { title: 'hello object_c', author: 'iphone', createTime: new Date('2016-12-31 13:23:46') },

        { title: 'hello swift', author: 'apple', createTime: new Date('2017-01-01 19:23:46') },
        { title: 'hello swift', author: 'apple', createTime: new Date('2017-01-01 05:23:46') }


    现在我们想统计每天有多少篇文章，假设按createTime聚合,命令如下：

        db.article.aggregate([
            {
                $group: {
                    _id: {
                        year: { $year: '$createTime' },
                        month: { $month: '$createTime' },
                        day: { $dayOfMonth: '$createTime' }
                    },
                    count: { $sum: 1 },
                    createTime: { $first: '$createTime' }
                }
            },
            {
                $project: {
                    _id: 0,
                    count: 1,
                    createTime: 1
                }
            }
        ])

   将返回如下结果：

    {"count" : 1,"createTime" : ISODate("2017-01-01T11:23:46.000Z")},

    {"count" : 2,"createTime" : ISODate("2016-12-31T05:23:46.000Z")},

    {"count" : 1,"createTime" : ISODate("2016-12-30T21:23:46.000Z")},

    {"count" : 1,"createTime" : ISODate("2017-07-04T18:23:46.000Z")},

    {"count" : 1,"createTime" : ISODate("2017-07-02T10:23:46.000Z")},

    {"count" : 2,"createTime" : ISODate("2017-07-01T05:23:46.000Z")},

    {"count" : 1,"createTime" : ISODate("2017-06-30T21:23:46.000Z")}

   这貌似和我们预期的结果不太一样,再看这样的命令：

    db.article.aggregate([
        {
            $group: {
                _id: {
                    year: { $year: { $add: ['$createTime', 8 * 60 * 60 * 1000] } },
                    month: { $month: { $add: ['$createTime', 8 * 60 * 60 * 1000] } },
                    day: { $dayOfMonth: { $add: ['$createTime', 8 * 60 * 60 * 1000] } }
                },
                count: { $sum: 1 },
                createTime: { $first: '$createTime' }
            }
        },
        {
            $project: {
                _id: 0,
                count: 1,
                createTime: 1
            }
        }
    ])

    返回结果：

    {"count" : 2,"createTime" : ISODate("2016-12-31T21:23:46.000Z")},

    {"count" : 2,"createTime" : ISODate("2016-12-30T21:23:46.000Z")},

    {"count" : 1,"createTime" : ISODate("2017-07-04T18:23:46.000Z")},

    {"count" : 2,"createTime" : ISODate("2017-07-01T23:23:46.000Z")},

    {"count" : 2,"createTime" : ISODate("2017-06-30T21:23:46.000Z")}
