- redis内存优化 (http://fex.staff.ifeng.com/fhh/fhh-doc/wikis/test)

> redisObject对象

>> Redis存储的数据都使用redisObject来封装

>> `type`:对象类型 （string,hash,list,set,zset)可以使用type key 命令查看

>> `encoding`:内部编码类型
```
    类型         | 编码方式                |   数据结构
    ----------- |------------------------|-----------------
    string      |raw                     |动态字符串编码
    		|embstr                  |优化内存分配的字符串编码
    		|int                     |整数编码
   -------------|------------------------|-----------------
    hash        |hashtable               |散列表编码
                |ziplist                 |压缩列表编码
    ------------|------------------------|-----------------
    list        |linkedlist              |双向链表编码
    		|ziplist                 |压缩列表编码'实际上一个字符串'
    		|quicklist               |3.2版本新的列表编码
    ------------|------------------------|-----------------
    set         |hashtable               |散列表编码
                |intset                  |整数集合编码'底层本质是一个有序的、不重复的、整型的数组'
    ------------|------------------------|-----------------
    zset        |skiplist                |跳跃表编码 `插入删除速度非常快`
                |ziplist                 |压缩列表编码
```
>> `lru字段`:

>> 记录对象最后一次被访问的时间，当配置了 maxmemory和maxmemory-policy=volatile-lru | allkeys-lru 时， 用于辅助LRU算法删除键数据。可以使用object idletime {key}命令在不更新lru字段情况下查看当前键的空闲时间.可以使用scan + object idletime  命令批量查询哪些键长时间未被访问
```
#内存容量超过maxmemory后的处理策略。
#volatile-lru：利用LRU算法移除设置过过期时间的key。
#volatile-random：随机移除设置过过期时间的key。
#volatile-ttl：移除即将过期的key，根据最近过期时间来删除（辅以TTL）
#allkeys-lru：利用LRU算法移除任何key。
#allkeys-random：随机移除任何key。
#noeviction：不移除任何key，只是返回一个写错误。
```

>> `refcount`

>> 记录当前对象被引用的次数，用于通过引用次数回收内存，当refcount=0时，可以安全回收当前对象空间。使用object refcount {key}获取当前对象引用

>> `*ptr字段`

>> 与对象的数据内容相关，如果是整数直接存储数据，否则表示指向数据的指针。

> String

>> 字符串对象的编码可以是 int 、 raw 或者 embstr

- 可以用 `long 类型保存的整数` int
- 如果字符串对象保存的是一个字符串值， 并且这个字符串值的`长度大于 39 字节`， 那么字符串对象将使用一个简单动态字符串（SDS）来保存这个字符串值， 并将对象的编码设置为 raw
- 如果字符串对象保存的是一个字符串值， 并且这个字符串值的`长度小于等于 39 字节`， 那么字符串对象将使用 embstr 编码的方式来保存这个字符串值
- embstr 编码是专门用于保存短字符串的一种优化编码方式， 这种编码和 raw 编码一样， 都使用 redisObject 结构和 sdshdr 结构来表示字符串对象， 但 raw 编码会调用两次内存分配函数来分别创建 redisObject 结构和 sdshdr 结构`字符串数据结构`， 而 embstr 编码则通过调用一次内存分配函数来分配一块连续的空间， 空间中依次包含 redisObject 和 sdshdr 两个结构

![image](/uploads/9cee2deee647c30964cf903eee1111dc/image.png)

![image](/uploads/3314d743591e6470dd976fb45b12d0ad/image.png)

> hash
>> 哈希对象的编码可以是 ziplist 或者 hashtable 。

```
HSET profile name "Tom" age 25 career "programmer"
```

- ziplist 编码的哈希对象使用压缩列表作为底层实现， 每当有新的键值对要加入到哈希对象时， 程序会先将保存了`键`的压缩列表节点推入到压缩列表表尾， 然后再将保存了`值`的压缩列表节点推入到压缩列表表尾。

- zlbytes：表示ziplist占用的字符总数
- zllen： 表示ziplist中数据项（entry）的个数
- zltail: 表示ziplist表中最后一项（entry）在ziplist中的偏移字节数
- zlend : ziplist最后1个字节，是一个结束标记，值固定等于255

![ziplist](/uploads/e2a76aeb912239aa5f894c20cd8bbea5/ziplist.png)


- hashtable 编码的哈希对象使用字典作为底层实现，哈希对象中的每个键值对都使用一个字典键值对来保存。
- 字典的每个键都是一个字符串对象， 对象中保存了键值对的键；
- 字典的每个值都是一个字符串对象， 对象中保存了键值对的值。

![hashtable](/uploads/2d640b7de085873ebe201a77666f2fcb/hashtable.png)

- 当哈希对象可以`同时`满足以下两个条件时， 哈希对象使用 ziplist 编码：

- 哈希对象保存的所有键值对的`键`和`值`的字符串长度`都小于` 64 字节；
hash-max-ziplist-value
- 哈希对象保存的键值对数量`小于` 512 个；
hash-max-ziplist-entries

>list
>> 列表对象的编码可以是 ziplist 或者 linkedlist 。

- ziplist 编码的列表对象使用压缩列表作为底层实现， 每个压缩列表`节点（entry）`保存了一个列表元素。

```
RPUSH numbers 1 "three" 5

```


![ziplist2](/uploads/2a43ea20d6e5b6290c1061a65f5c19e2/ziplist2.png)


- linkedlist  编码的列表对象在底层的双端链表结构中包含了多个`字符串对象`


![linklist](/uploads/d964308069ccac65cdb5878d84ca99ef/linklist.png)
![stringObject](/uploads/8c001425801eed357a9d3a03e9a009c7/stringObject.png)

- redis3.2版本后废弃了废弃list-max-ziplist-entries和list-max-ziplist-entries配置

- 使用新配置:
- list-max-ziplist-size -2

```
当取正值的时候，表示按照数据项个数来限定每个quicklist节点上的ziplist长度。比如，当这个参数配置成5的时候，
表示每个quicklist节点的ziplist最多包含5个数据项。

当取负值的时候，表示按照占用字节数来限定每个quicklist节点上的ziplist长度。这时，它只能取-1到-5这五个值，每个值含义如下：
-5: 每个quicklist节点上的ziplist大小不能超过64 Kb。（注：1kb => 1024 bytes）
-4: 每个quicklist节点上的ziplist大小不能超过32 Kb。
-3: 每个quicklist节点上的ziplist大小不能超过16 Kb。
-2: 每个quicklist节点上的ziplist大小不能超过8 Kb。（-2是Redis给出的默认值）
-1: 每个quicklist节点上的ziplist大小不能超过4 Kb。
```
- list-compress-depth 0

```
0: 是个特殊值，表示都不压缩。这是Redis的默认值。` 由于经常访问两端的元素`
1: 表示quicklist两端各有1个节点不压缩，中间的节点压缩。
2: 表示quicklist两端各有2个节点不压缩，中间的节点压缩。
3: 表示quicklist两端各有3个节点不压缩，中间的节点压缩。
依此类推…
```
- quicklist 它是一个双向链表，每个节点都是一个ziplist

```
quicklist的结构是一个空间和时间的折中：

双向链表便于在表的两端进行push和pop操作，但是它的内存开销比较大。
首先，它在每个节点上除了要保存数据之外，
还要额外保存两个指针；其次，双向链表的各个节点是单独的内存块，
地址不连续，节点多了容易产生内存碎片。

ziplist由于是一整块连续内存，所以存储效率很高。但是，
它不利于修改操作，每次数据变动都会引发一次内存的realloc。
特别是当ziplist长度很长的时候，一次realloc可能会导致大批量的
数据拷贝，进一步降低性能。于是，结合了双向链表和ziplist的优点，
quicklist就应运而生了
```

```
list-max-ziplist-size的配置是一个需要找平衡点的难题。我们只从存储效率上
分析一下：

每个quicklist节点上的ziplist越短，则内存碎片越多。内存碎片多了，
有可能在内存中产生很多无法被利用的小碎片，从而降低存储效率。
这种情况的极端是每个quicklist节点上的ziplist只包含一个数据项，
这就蜕化成一个普通的双向链表了。

每个quicklist节点上的ziplist越长，则为ziplist分配大块连续内存
空间的难度就越大。有可能出现内存里有很多小块的空闲空间（它们加起来很多），
但却找不到一块足够大的空闲空间分配给ziplist的情况。这同样会降低存储效率。
这种情况的极端是整个quicklist只有一个节点，
所有的数据项都分配在这仅有的一个节点的ziplist里面。
这其实蜕化成一个ziplist了。
```

>set
>> 集合对象的编码可以是 intset 或者 hashtable

```
SADD numbers 1 3 5
```
- intset 编码的集合对象使用整数集合作为底层实现， 集合对象包含的所有元素都被保存在整数集合里面。


![inset](/uploads/c0340b8bfef42666f6e3dfaed237fe44/inset.png)

```
SADD fruits "apple" "banana" "cherry"
```

-  hashtable 编码的集合对象使用字典作为底层实现， 字典的每个键都是一个`字符串对象`， 每个字符串对象包含了一个集合元素， 而字典的值则全部被设置为 `NULL `

![hashtable2](/uploads/12d07415be78a445f95402d8ada9ff35/hashtable2.png)

 - set-max-intset-entries  512(默认)
 - 元素都是整数值


>zset(sorted set)
>> 有序集合的编码可以是 ziplist 或者 skiplist
- ziplist 编码的有序集合对象使用压缩列表作为底层实现， 每个集合元素使用两个紧挨在一起的压缩列表节点来保存， 第一个节点保存元素的成员（member）， 而第二个元素则保存元素的分值（score）
- 压缩列表内的集合元素按分值从小到大进行排序， 分值较小的元素被放置在靠近表头的方向， 而分值较大的元素则被放置在靠近表尾的方向。

```
ZADD price 8.5 apple 5.0 banana 6.0 cherry
```

![ziplist3](/uploads/f1a2bc70dac71e65e737dbda16c9d9cd/ziplist3.png)


- skiplist 编码的有序集合对象使用 zset 结构作为底层实现， 一个 zset 结构同时包含一个字典和一个跳跃表：

```
typedef struct zset {

    zskiplist *zsl;

    dict *dict;

} zset;

set 结构中的 zsl 跳跃表按分值从小到大保存了所有集合元素， 每个跳跃表节点都保存了一个集合元素：
跳跃表节点的 object 属性保存了元素的成员， 而跳跃表节点的 score 属性则保存了元素的分值。
通过这个跳跃表， 程序可以对有序集合进行范围型操作，
比如 ZRANK 、 ZRANGE 等命令就是基于跳跃表 API 来实现的。

除此之外， zset 结构中的 dict 字典为有序集合创建了一个从成员到分值的映射，
字典中的每个键值对都保存了一个集合元素： 字典的键保存了元素的成员， 而字典的值则保存了元素的分值。
通过这个字典， 程序可以用 O(1) 复杂度查找给定成员的分值，
ZSCORE 命令就是根据这一特性实现的， 而很多其他有序集合命令都在实现的内部用到了这一特性。

有序集合每个元素的成员都是一个字符串对象，
而每个元素的分值都是一个 double 类型的浮点数。
值得一提的是， 虽然 zset 结构同时使用跳跃表和字典来保存有序集合元素，
但这两种数据结构都会通过指针来共享相同元素的成员和分值，
所以同时使用跳跃表和字典来保存集合元素不会产生任何重复成员或者分值， 也不会因此而浪费额外的内存。
```


![skiplist](/uploads/f2a4261e7705e312e87acc80dc699bd3/skiplist.png)



![zset](/uploads/4da874e05f1d78bc4daf23ad6ab41383/zset.png)





- http://redisbook.com/preview/object/sorted_set.html
- http://zhangtielei.com/posts/server.html

