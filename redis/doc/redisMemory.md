

### 基于redis-3.2.9版本的默认配置文件
    redis服务器是8核 4G内存

1. 比较key值长和短的内存区别.

```
存500万数据的情况（key值较短）

127.0.0.1:6379> dbsize
(integer) 4974516
127.0.0.1:6379> scan 0 COUNT 20
1) "131072"
2)  1) "listKey:59486170"
    2) "listKey:28791958"
    3) "setKey:11354070"
    4) "mapKey:54303736"
    5) "zaddKey:97996283"
    6) "listKey:49883561"
    7) "mapKey:18328012"
    8) "num:87615610"
    9) "setKey:66520022"
   10) "mapKey:82866653"
   11) "listKey:78369193"
   12) "zaddKey:8000851"
   13) "zaddKey:76565413"
   14) "listKey:86673104"
   15) "zaddKey:86136620"
   16) "mapKey:59828160"
   17) "zaddKey:1337731"
   18) "listKey:13973556"
   19) "num:41374425"
   20) "mapKey:42556618"
127.0.0.1:6379> info Memory
# Memory
used_memory:558953888
used_memory_human:533.06M
used_memory_rss:649760768
used_memory_rss_human:619.66M
used_memory_peak:2986123072
used_memory_peak_human:2.78G
total_system_memory:4143886336
total_system_memory_human:3.86G
used_memory_lua:37888
used_memory_lua_human:37.00K
maxmemory:0
maxmemory_human:0B
maxmemory_policy:noeviction
mem_fragmentation_ratio:1.16
mem_allocator:jemalloc-4.0.3




存500万数据的情况（key值较长）
key的长度由原来的加上前缀'testKeyLength++++++++++++++++++++++++++++++++++'

127.0.0.1:6379> dbsize
(integer) 4980115
127.0.0.1:6379> scan 0 COUNT 20
1) "3801088"
2)  1) "testKeyLength++++++++++++++++++++++++++++++++++num:79637262"
    2) "testKeyLength++++++++++++++++++++++++++++++++++num:35885178"
    3) "testKeyLength++++++++++++++++++++++++++++++++++setKey:96883097"
    4) "testKeyLength++++++++++++++++++++++++++++++++++zaddKey:46220067"
    5) "testKeyLength++++++++++++++++++++++++++++++++++mapKey:28878542"
    6) "testKeyLength++++++++++++++++++++++++++++++++++setKey:31440872"
    7) "testKeyLength++++++++++++++++++++++++++++++++++mapKey:28120548"
    8) "testKeyLength++++++++++++++++++++++++++++++++++num:89373286"
    9) "testKeyLength++++++++++++++++++++++++++++++++++setKey:83873841"
   10) "testKeyLength++++++++++++++++++++++++++++++++++setKey:91661262"
   11) "testKeyLength++++++++++++++++++++++++++++++++++zaddKey:33829475"
   12) "testKeyLength++++++++++++++++++++++++++++++++++zaddKey:59643215"
   13) "testKeyLength++++++++++++++++++++++++++++++++++listKey:23629033"
   14) "testKeyLength++++++++++++++++++++++++++++++++++mapKey:96428506"
   15) "testKeyLength++++++++++++++++++++++++++++++++++listKey:69827524"
   16) "testKeyLength++++++++++++++++++++++++++++++++++zaddKey:68129964"
   17) "testKeyLength++++++++++++++++++++++++++++++++++mapKey:32472278"
   18) "testKeyLength++++++++++++++++++++++++++++++++++num:32012329"
   19) "testKeyLength++++++++++++++++++++++++++++++++++num:68696622"
   20) "testKeyLength++++++++++++++++++++++++++++++++++setKey:3665294"
127.0.0.1:6379> info MEMORY
# Memory
used_memory:831832512
used_memory_human:793.30M
used_memory_rss:857923584
used_memory_rss_human:818.18M
used_memory_peak:2986123072
used_memory_peak_human:2.78G
total_system_memory:4143886336
total_system_memory_human:3.86G
used_memory_lua:37888
used_memory_lua_human:37.00K
maxmemory:0
maxmemory_human:0B
maxmemory_policy:noeviction
mem_fragmentation_ratio:1.03
mem_allocator:jemalloc-4.0.3



2.高级一点的数据类型如set, sorted set,hash,他们在数据大小不同的情况下使用的存储结构是不同的.


HASH的内存优化实例

    数据：
    dbsize：10000
    entries: 515
    values:70

    结构：

    “mapKey:474006796”：{
    "474006830"：“test key length ,need length is 64 byte.it is too much long  474006830”，
    "474007246": "test key length ,need length is 64 byte.it is too much long  474007246"
    }


1) 条件：
   hash-max-ziplist-entries  512
   hash-max-ziplist-value  64

   结果：
   used_memory_human:866.18M
   object encoding :hashtable


2) 条件：
   hash-max-ziplist-entries  520
   hash-max-ziplist-value  64

   结果：
   used_memory_human:866.18M
   object encoding :hashtable


3) 条件：
  hash-max-ziplist-entries  512
  hash-max-ziplist-value  75

  结果：
  used_memory_human:785.43M
  object encoding :hashtable


4) 条件：
 hash-max-ziplist-entries  520
 hash-max-ziplist-value  75

 结果：
 used_memory_human:392.16M
 object encoding :ziplist

总结：
    1和4对比 减少了 474.02M   120.87%




 List的内存优化实例

    数据：
    dbsize：10000
    每个list的size: 10
    值大小:4.2K

    结构：

    “listKey:7158249”：{
    "test key length ,need length is gt 64 byte.it is too large ll  98711650test "(60*70)
    " ",
    " "
    }


1) 条件：
   list-max-ziplist-size -2
   list-compress-depth 0

   结果：
   used_memory_human:493.09M
   object encoding :quicklist

2) 条件：
   list-max-ziplist-size -1
   list-compress-depth 0

   结果：
   used_memory_human:493.05M
   object encoding :quicklist

3) 条件：
   list-max-ziplist-size -1
   list-compress-depth 1

   结果：
   used_memory_human:114.73M
   object encoding :quicklist

4) 条件：
   list-max-ziplist-size -2
   list-compress-depth 1

   结果：
   used_memory_human:114.80M
   object encoding :quicklist


5) 条件：
   list-max-ziplist-size 9
   list-compress-depth 0

   结果：
   used_memory_human:493.12M
   object encoding :quicklist

6) 条件：
   list-max-ziplist-size 12
   list-compress-depth 0

   结果：
   used_memory_human:493.10M
   object encoding :quicklist

7) 条件：
   list-max-ziplist-size 9
   list-compress-depth 1

   结果：
   used_memory_human:114.79M
   object encoding :quicklist

8) 条件：
   list-max-ziplist-size 12
   list-compress-depth 1

   结果：
   used_memory_human:114.81M
   object encoding :quicklist


分析：list-compress-depth 参数是决定内存大小的关键
      list-max-ziplist-size 参数是 quicklist介于链表结构和ziplist之间的折中，是一个空间和时间。

Set的内存优化实例


    数据1：
    dbsize：200
    entries: 520

    结构：

    “setKey:474006796”：{
        “51456284”，
        “51456367”，
        “51456116”，
        “51456178”
    }


1) 条件：
   set-max-intset-entries ：512

   结果：
   used_memory_human:6.39M
   object encoding :hashtable

2) 条件：
   set-max-intset-entries ：530

   结果：
   used_memory_human:1.30M
   object encoding :intset


1和2对比 内存减少了 5.09M  占391.5%


    数据2：
    dbsize：200
    entries: 520

    结构：

    “setKey:474006796”：{
        “9361286t”，
        “9361037t”，
        “9360982t”，
        “9360949t”
    }

1) 条件：
   set-max-intset-entries ：512

   结果：
   used_memory_human:8.73M
   object encoding :hashtable

2) 条件：
   set-max-intset-entries ：530

   结果：
   used_memory_human:8.73M
   object encoding :hashtable





zSet的内存优化实例



    数据：
    dbsize：1000
    entries: 140
    values:70

    结构：

    “zaddKey:86423545”：
        “test key length ,need length is gt 64 byte.it is too large ll86423614”，    0.97933775990216543
        “test key length ,need length is gt 64 byte.it is too large ll86423678”，    0.98476398325408232
        “test key length ,need length is gt 64 byte.it is too large ll86423547”，    0.99646509991322085
    }


1) 条件：
   zset-max-ziplist-entries 128
   zset-max-ziplist-value  64

   结果：
   used_memory_human:26.68M
   object encoding :skiplist

2) 条件：
  zset-max-ziplist-entries 150
  zset-max-ziplist-value  64

   结果：
   used_memory_human:26.69M
   object encoding :skiplist

3) 条件：
    zset-max-ziplist-entries 128
    zset-max-ziplist-value  80

  结果：
  used_memory_human:26.67M
  object encoding :skiplist

4) 条件：
  zset-max-ziplist-entries 150
  zset-max-ziplist-value  80

  结果：
  used_memory_human:14.54M
  object encoding :ziplist

 1和4 对比 减少了 12.14M 占 83.5%


 ```
