### 1. 简介
   * 可基于内存的、也可以持久化的、key-value形式的非关系型数据库

### 2. 由来
   * 是意大利的一家做实时统计系统的公司在使用mysql时，创始人Salvatore Sanfilippo发现mysql的性能非常低下。于2009年开发完成的redis数据库，并将该数据库开源。VMware公司从2010年赞助redis的开发。

### 3.特点
*   读写性能：读110000/s  写 80000/s
*   value支持的类型：string 、hash 、list 、set、 zset  、BitMap、 HyperLogLog 、 geospatial
*   所有的操作是原子操作
*   支持数据库的备份，支持主从备份（master-slave）
*   支持订阅发布、通知以及key过期等特性

### 4.相同产品对比

![示例图片](http://fex.staff.ifeng.com/fhh/fhh-doc/blob/master/redis/doc/%E5%AF%B9%E6%AF%94.png "这个是对比")

### 5. 基本数据类型简介
#### String
- 字符串是一种最基本的Redis值类型。Redis字符串是二进制安全的，这意味着一个Redis字符串能包含任意类型的数据.
-  一个字符串类型的值最多能存储512M字节的内容
-  `二进制安全`：在 C 语言中，字符串可以用一个 \0 结尾的 char 数组来表示。比如说， hello world 在 C 语言中就可以表示为 "hello world\0" 。二进制安全就是，字符串不是根据某种特殊的标志来解析的，无论输入是什么，总能保证输出是处理的原始输入而不是根据某种特殊格式来处理。
- 常用命令 get、 set、 incr、 decr

#### list
- Redis列表是简单的字符串列表，按照插入顺序排序。 你可以添加一个元素到列表的头部（左边）或者尾部（右边）。
LPUSH 命令插入一个新元素到列表头部，而RPUSH命令 插入一个新元素到列表的尾部。当 对一个空key执行其中某个命令时，将会创建一个新表
- 一个列表最多可以包含2的32次方-1个元素
- 常用命令 lpush rpush lrange rpop等

#### hash
- Redis Hashes是字符串字段和字符串值之间的映射，是表示对象最好的数据类型。
- 一个hash最多可以包含2的32次方-1 个key-value键值对
- 常用命令 hset hget hmget hmset hgetall

#### set
- Redis集合是一个无序的字符串合集,不允许相同成员存在。向集合中多次添加同一元素，在集合中最终只会存在一个此元素.
- 一个集合最多可以包含2的32次方-1个元素
- 常用命令 sadd smembers srem scard

#### zset
- Redis有序集合和Redis集合类似，是不包含 相同字符串的合集。它们的差别是，每个有序集合 的成员都关联着一个评分，这个评分用于把有序集 合中的成员按最低分到最高分排列。是有序的。
- 常用命令 zadd zrange zcard

#### Bitmaps
- Bitmap是一串连续的2进制数字（0或1），每一位所在的位置为偏移(offset)，在bitmap上可执行AND,OR,XOR以及其它位操作。
- Redis从2.2.0版本开始新增了setbit,getbit,bitcount，BITOP等几个bitmap相关命令
- 使用场景 一个简单的例子：日活跃用户
- 为了统计今日登录的用户数，我们建立了一个bitmap,每一位标识一个用户ID。当某个用户访问我们的网页或执行了某个操作，就在bitmap中把标识此用户的位置为1。在Redis中获取此bitmap的key值是通过用户执行操作的类型和时间戳获得的。
- 这个简单的例子中，每次用户登录时会执行一次redis.setbit(daily_active_users, user_id, 1)。将bitmap中对应位置的位置为1，时间复杂度是O(1)。统计bitmap结果显示有今天有9个用户登录。Bitmap的key是daily_active_users，它的值是1011110100100101
-  因为日活跃用户每天都变化，所以需要每天创建一个新的bitmap。我们简单地把日期添加到key后面，实现了这个功能。



#### HyperLogLogs
- HyperLogLog（HLL）是一种基于概率的数据结构，用于统计集合中不同元素的个数。通常要完成这项工作所需的内存大小与集合中不同元素的个数成正比。不过，有一种使用精度换取空间的做法，也就是使用较小的内存完成工作，但得到的结果会有一定误差。对于redis来说，这个误差小于1%。这个做法的神奇之处在于，无论集合中有多少元素，你也至多只需要12k内存！

- 从概念上说，HLL的api和sets的api有些类似。在sets中，你可以使用SADD将元素加入集合，再使用SCARD来统计集合中不同元素的个数。
对于HLL来说，你并没有真的将元素加到集合中，而只是保存了一个标识位，所用的api是这样的：
- 每当遇到一个新元素，使用PFADD将其加入集合。
- 使用PFCOUNT，获取当前集合中不同元素个数的近似值。
````
> pfadd hll a b c d
(integer) 1
> pfcount hll
(integer) 4
````








### 6. incr的小demo

>     public static void main(String[] args) {
>         Jedis jedis = new Jedis("127.0.0.1", 6379);
>         System.out.println("connect success!");
>         jedis.del("testKey");
>         for (int i =0;i<10;i++){
>             long l = jedis.incr("testKey");
>             String value = jedis.get("testKey");
>             System.out.println(i+1+"次incr命令后，testKey对应的value是："+value);
>         }
>     }



