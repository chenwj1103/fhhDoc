## 查询  
根据id查询 _id=234 _index=penghb _type=test  
curl -XGET http://localhost:9201/penghb/test/234   
```json
{
  "_index": "penghb",
  "_type": "test",
  "_id": "234",
  "_version": 1,
  "found": true,
  "_source": {
    "peng": "penghaibin",
    "age": 632452,
    "num": 632452
  }
}
```
如果记录不存在则返回  
```json
{
  "_index" : "website",
  "_type" :  "blog",
  "_id" :    "124",
  "found" :  false
}
```

指定返回字段 指定返回age和num字段  
curl -XGET http://192.168.66.128:9201/penghb/test/632452?_source=age,num  

只想得到 _source 字段，不需要任何元数据  
curl -XGET http://192.168.66.128:9201/penghb/test/632452/\_source  

检查文档是否存在  
curl -i -XHEAD http://localhost:9200/penghb/test/123  
如果存在返回200状态码，如果不存在返回404状态码   

## 搜索
 curl -XGET http://localhost:9201/_search搜索  
```json
{
    "took": 299,
    "timed_out": false,
    "_shards": {
        "total": 20,
        "successful": 20,
        "failed": 0
    },
    "hits": {
        "total": 2000025,
        "max_score": 1.0,
        "hits": [
            {
                "_index": "peng",
                "_type": "test",
                "_id": "14",
                "_score": 1.0,
                "_source": {
                    "peng": "penghaibin",
                    "age": 14,
                    "num": 14
                }
            },
          ......
        ]
    }
}
```
### hits
>返回结果中最重要的部分是hits ，它包含 total字段来表示匹配到的文档总数，并且一个 hits 数组包含所查询结果的前十个文档。
>在 hits 数组中每个结果包含文档的 _index 、 _type 、 _id ，加上 _source 字段。这意味着我们可以直接从返回的搜索结果中使用整个文档。这不像其他的搜索引擎，仅仅返回文档的ID，需要你单独去获取文档。
每个结果还有一个 _score ，它衡量了文档与查询的匹配程度。默认情况下，首先返回最相关的文档结果，就是说，返回的文档是按照 _score 降序排列的。在这个例子中，我们没有指定任何查询，故所有的文档具有相同的相关性，因此对所有的结果而言 1 是中性的 _score 。

### max_score  
>是与查询所匹配文档的 _score 的最大值。  

### took  
>took 值告诉我们执行整个搜索请求耗费了多少毫秒。  

### shards  
>_shards 部分 告诉我们在查询中参与分片的总数，以及这些分片成功了多少个失败了多少个。正常情况下我们不希望分片失败，但是分片失败是可能发生的。如果我们遭遇到一种灾难级别的故障，在这个故障中丢失了相同分片的原始数据和副本，那么对这个分片将没有可用副本来对搜索请求作出响应。假若这样，Elasticsearch 将报告这个分片是失败的，但是会继续返回剩余分片的结果。

### timeout:  
timed_out 值告诉我们查询是否超时。默认情况下，搜索请求不会超时。 如果低响应时间比完成结果更重要，你可以指定 timeout 为 10 或者 10ms（10毫秒），或者 1s（1秒）：  
curl -XGET http://localhost:9201/_search?timeout=10ms  

### 多索引，多类型
想在一个或多个特殊的索引并且在一个或者多个特殊的类型中进行搜索。可以通过在URL中指定特殊的索引和类型达到这种效果，如下所示：  
/\_search  

>在所有的索引中搜索所有的类型  

/gb/\_search  

>在 gb 索引中搜索所有的类型  

/gb,us/\_search  

>在 gb 和 us 索引中搜索所有的文档  

/g*,u*/\_search  

>在任何以 g 或者 u 开头的索引中搜索所有的类型  

/gb/user/\_search  

>在 gb 索引中搜索 user 类型  

/gb,us/user,tweet/\_search  

>在 gb 和 us 索引中搜索 user 和 tweet 类型  

/\_all/user,tweet/\_search  

>在所有的索引中搜索 user 和 tweet 类型

当在单一的索引下进行搜索的时候，Elasticsearch 转发请求到索引的每个分片中，可以是主分片也可以是副本分片，然后从每个分片中收集结果。多索引搜索恰好也是用相同的方式工作的--只是会涉及到更多的分片。

### 分页  
Elasticsearch 接受 from 和 size 参数：  
size  

>显示应该返回的结果数量，默认是 10  

from  

>显示应该跳过的初始结果数量，默认是 0  

 curl -XGET http://localhost:9201/_search?size=5&from=10
 
## 通过_mget和docs可以查询多个文档
curl -XGET http://localhost:9201/_mget?pretty -d '{"docs":[{"_index":"penghb","_type":"test","_id":2},{"_index":"penghb","_type":"test","_id":5555,"_source":"views"}]}'  
该响应体也包含一个 docs 数组 ， 对于每一个在请求中指定的文档，这个数组中都包含有一个对应的响应，且顺序与请求中的顺序相同。  
```json
{
  "docs" : [
    {
      "_index" : "penghb",
      "_type" : "test",
      "_id" : "2",
      "_version" : 1,
      "found" : true,
      "_source" : {
        "peng" : "penghaibin",
        "age" : 2,
        "num" : 2
      }
    },
    {
      "_index" : "penghb",
      "_type" : "test",
      "_id" : "5555",
      "_version" : 3,
      "found" : true,
      "_source" : {
        "views" : 1
      }
    }
  ]
}
```
如果想检索的数据都在相同的 \_index 中（甚至相同的 \_type 中），则可以在 URL 中指定默认的 /\_index 或者默认的 /\_index/\_type 。  
如果所有文档的 _index 和 _type 都是相同的，可以只传一个 ids 数组  
curl -XGET http://localhost:9201/penghb/test/\_mget?pretty -d '{"ids":["345","678","1111"]}'  

### 可以批量创建  
```json
 curl -XPOST http://localhost:9201/_bulk -d '
{ "delete": { "_index": "penghb", "_type": "test", "_id": 678 }} 
{ "create": { "_index": "website", "_type": "blog", "_id": 34 }} 
{ "title":    "My first blog post" }
{ "index":  { "_index": "penghb", "_type": "test" }}
{ "title":    "My index 1" }       
{ "update": { "_index": "penghb", "_type": "test", "_id": "333", "_retry_on_conflict" : 3} }
{ "doc" : {"peng" : "bulk update"} }
'
```
\_bluk命令也可以\_mget一样指定默认的_index或者\_index/\_type  

## 轻量搜索
>有两种形式的 搜索 API：一种是 “轻量的” 查询字符串 版本，要求在查询字符串中传递所有的 参数，另一种是更完整的 请求体 版本，要求使用 JSON 格式和更丰富的查询表达式作为搜索语言。
>查询字符串搜索非常适用于通过命令行做即席查询。  

### 根据字段查询
curl -XGET http://localhost:9201/_all/test/_search?q=num:1999999
根据num字段查询包含1999999的文档
curl -XGET http://localhost:9201/_all/test/_search?q=%2Bpeng%3Apenghaibin+%2Bviews%3A1
查询两个字段要url编码  

### _all 字段
这个简单搜索返回包含 elasticsearch 的所有文档：
curl -XGET http://localhost:9201/_search?q=elasticsearch  
查询peng包含penghaibin和aa的，并且age大于1999997的文档
curl -XGET http://localhost:9201/_all/test/_search?q=%2Bpeng%3A"(penghaibin+aa)"+%2Bage%3A%3E1999997

## 排序
为了按照相关性来排序，需要将相关性表示为一个数值。在Elasticsearch中， 相关性得分由一个浮点数进行表示，并在搜索结果中通过\_score 参数返回，默认排序是\_score降序。

## 按照字段的值排序
```json
{
    "query" : {
        "bool" : {
            "filter" : { "term" : { "user_id" : 1 }}
        }
    },
    "sort": { "date": { "order": "desc" }}
}
```
返回值：
```JSON
{
  "took" : 48,
  "timed_out" : false,
  "_shards" : {
    "total" : 10,
    "successful" : 10,
    "failed" : 0
  },
  "hits" : {
    "total" : 6,
    "max_score" : null,
    "hits" : [
      {
        "_index" : "us",
        "_type" : "tweet",
        "_id" : "14",
        "_score" : null,
        "_source" : {
          "date" : "2014-09-24",
          "name" : "John Smith",
          "tweet" : "How many more cheesy tweets do I have to write?",
          "user_id" : 1
        },
        "sort" : [
          1411516800000
        ]
      },
      ......
    ]
  }
}
```
_score 不被计算, 因为它并没有用于排序。
这里没有一个有意义的分数：因为我们使用的是 filter （过滤），这表明我们只希望获取匹配 user_id: 1 的文档，并没有试图确定这些文档的相关性。 实际上文档将按照随机顺序返回，并且每个文档都会评为零分。
其次 _score 和 max_score 字段都是 null 。 计算 _score 的花销巨大，通常仅用于排序； 我们并不根据相关性排序，所以记录 _score 是没有意义的。如果无论如何你都要计算 _score ， 你可以将 track_scores 参数设置为 true 。
constant_score
curl -XGET localhost:9201/_search?pretty -d '{"query":{"constant_score":{"filter":{"term":{"user_id":1}}}}}'
````json
{
  "took" : 37,
  "timed_out" : false,
  "_shards" : {
    "total" : 40,
    "successful" : 40,
    "failed" : 0
  },
  "hits" : {
    "total" : 6,
    "max_score" : 1.0,
    "hits" : [
      {
        "_index" : "us",
        "_type" : "tweet",
        "_id" : "14",
        "_score" : 1.0,
        "_source" : {
          "date" : "2014-09-24",
          "name" : "John Smith",
          "tweet" : "How many more cheesy tweets do I have to write?",
          "user_id" : 1
        }
      },
      ......
    ]
  }
}
```

### 多级排序
要结合使用 date 和 _score 进行查询，并且匹配的结果首先按照日期排序，然后按照相关性排序：
GET /_search
```json
{
    "query" : {
        "bool" : {
            "must":   { "match": { "tweet": "manage text search" }},
            "filter" : { "term" : { "user_id" : 2 }}
        }
    },
    "sort": [
        { "date":   { "order": "desc" }},
        { "_score": { "order": "desc" }}
    ]
}
```
排序条件的顺序是很重要的。结果首先按第一个条件排序，仅当结果集的第一个 sort 值完全相同时才会按照第二个条件进行排序，以此类推。

Query-string 搜索 也支持自定义排序，可以在查询字符串中使用 sort 参数：  
GET /_search?sort=date:desc&sort=_score&q=search  

### 字段多值排序
对于数字或日期，你可以将多值字段减为单值，这可以通过使用 min 、 max 、 avg 或是 sum 排序模式 。 例如你可以按照每个 date 字段中的最早日期进行排序，通过以下方法：  
curl -XGET localhost:9201/_search -d '{"sort":{"date":{"order":"asc","mode":"min"}}}'  

### 字符串排序和多字段
被解析的字符串字段也是多值字段， 但是很少会按照你想要的方式进行排序。如果你想分析一个字符串，如 fine old art ， 这包含 3 项。我们很可能想要按第一项的字母排序，然后按第二项的字母排序，诸如此类，但是 Elasticsearch 在排序过程中没有这样的信息。
你可以使用 min 和 max 排序模式（默认是 min ），但是这会导致排序以 art 或是 old ，任何一个都不是所希望的。
为了以字符串字段进行排序，这个字段应仅包含一项： 整个 not_analyzed 字符串。 但是我们仍需要 analyzed 字段，这样才能以全文进行查询
一个简单的方法是用两种方式对同一个字符串进行索引，这将在文档中包括两个字段： analyzed 用于搜索， not_analyzed 用于排序
但是保存相同的字符串两次在 _source 字段是浪费空间的。 我们真正想要做的是传递一个 单字段 但是却用两种方式索引它。所有的 _core_field 类型 (strings, numbers, Booleans, dates) 接收一个 fields 参数，该参数允许你转化一个简单的映射如：
"tweet": {
    "type":     "string",
    "analyzer": "english"
}

为一个多字段映射如：  
"tweet": { 
    "type":     "string",
    "analyzer": "english",
    "fields": {
        "raw": { 
            "type":  "string",
            "index": "not_analyzed"
        }
    }
}

现在，至少只要我们重新索引了我们的数据，使用 tweet 字段用于搜索，tweet.raw 字段用于排序：  
```json
{
    "query": {
        "match": {
            "tweet": "elasticsearch"
        }
    },
    "sort": "tweet.raw"
}
```

### 相关性

每个文档都有相关性评分，用一个正浮点数字段 _score 来表示 。 _score 的评分越高，相关性越高。

查询语句会为每个文档生成一个 _score 字段。评分的计算方式取决于查询类型 不同的查询语句用于不同的目的： fuzzy 查询会计算与关键词的拼写相似程度，terms 查询会计算 找到的内容与关键词组成部分匹配的百分比，但是通常我们说的 relevance 是我们用来计算全文本字段的值相对于全文本检索词相似程度的算法。
Elasticsearch 的相似度算法 被定义为检索词频率/反向文档频率， TF/IDF ，包括以下内容：  

检索词频率
检索词在该字段出现的频率？出现频率越高，相关性也越高。 字段中出现过 5 次要比只出现过 1 次的相关性高。
反向文档频率
每个检索词在索引中出现的频率？频率越高，相关性越低。检索词出现在多数文档中会比出现在少数文档中的权重更低。
字段长度准则
字段的长度是多少？长度越长，相关性越低。 检索词出现在一个短的 title 要比同样的词出现在一个长的 content 字段权重更大。

单个查询可以联合使用 TF/IDF 和其他方式，比如短语查询中检索词的距离或模糊查询里的检索词相似度。
相关性并不只是全文本检索的专利。也适用于 yes|no 的子句，匹配的子句越多，相关性评分越高。
如果多条查询子句被合并为一条复合查询语句 ，比如 bool 查询，则每个查询子句计算得出的评分会被合并到总的相关性评分中。

### 理解评分标准
当调试一条复杂的查询语句时， 想要理解 _score 究竟是如何计算是比较困难的。Elasticsearch 在 每个查询语句中都有一个 explain 参数，将 explain 设为 true 就可以得到更详细的信息。

curl -XGET localhost:9201/_search?pretty&explain=true -d '{"query":{"match":{"tweet":"honeymoon"}}}'
```json
{"took":23,"timed_out":false,"_shards":{"total":40,"successful":40,"failed":0},"hits":{"total":1,"max_score":0.5974999,"hits":[{"_shard":"[us][1]","_node":"tq1abqnjTzK7eiQynCOEZg","_index":"us","_type":"tweet","_id":"12","_score":0.5974999,"_source":{ "date" : "2014-09-22", "name" : "John Smith", "tweet" : "Elasticsearch and I have left the honeymoon stage, and I still love her.", "user_id" : 1 },"_explanation":{"value":0.5974999,"description":"weight(tweet:honeymoon in 2) [PerFieldSimilarity], result of:","details":[{"value":0.5974999,"description":"score(doc=2,freq=1.0 = termFreq=1.0\n), product of:","details":[{"value":0.6931472,"description":"idf, computed as log(1 + (docCount - docFreq + 0.5) / (docFreq + 0.5)) from:","details":[{"value":1.0,"description":"docFreq","details":[]},{"value":2.0,"description":"docCount","details":[]}]},{"value":0.8620102,"description":"tfNorm, computed as (freq * (k1 + 1)) / (freq + k1 * (1 - b + b * fieldLength / avgFieldLength)) from:","details":[{"value":1.0,"description":"termFreq=1.0","details":[]},{"value":1.2,"description":"parameter k1","details":[]},{"value":0.75,"description":"parameter b","details":[]},{"value":11.5,"description":"avgFieldLength","details":[]},{"value":16.0,"description":"fieldLength","details":[]}]}]}]}}]}}
```
词频率和 文档频率是在每个分片中计算出来的，而不是每个索引中：  
然后它提供了 _explanation 。每个 入口都包含一个 description 、 value 、 details 字段，它分别告诉你计算的类型、计算结果和任何我们需要的计算细节。

### Doc Values

当你对一个字段进行排序时，Elasticsearch 需要访问每个匹配到的文档得到相关的值。倒排索引的检索性能是非常快的，但是在字段值排序时却不是理想的结构。
在搜索的时候，我们能通过搜索关键词快速得到结果集。
当排序的时候，我们需要倒排索引里面某个字段值的集合。换句话说，我们需要 ``倒置`` 倒排索引。
``倒置`` 结构在其他系统中经常被称作 ``列存储`` 。实质上，它将所有单字段的值存储在单数据列中，这使得对其进行操作是十分高效的，例如排序。
在 Elasticsearch 中，doc values 就是一种列式存储结构，默认情况下每个字段的 doc values 都是激活的，doc values 是在索引时创建的，当字段索引时，Elasticsearch 为了能够快速检索，会把字段的值加入倒排索引中，同时它也会存储该字段的 doc values。  
Elasticsearch 中的 doc vaules 常被应用到以下场景：  
对一个字段进行排序
对一个字段进行聚合
某些过滤，比如地理位置过滤
某些与字段相关的脚本计算
因为文档值被序列化到磁盘，我们可以依靠操作系统的帮助来快速访问。当 working set 远小于节点的可用内存，系统会自动将所有的文档值保存在内存中，使得其读写十分高速； 当其远大于可用内存，操作系统会自动把 doc values 加载到系统的页缓存中，从而避免了 jvm 堆内存溢出异常。

## 空查询
这两个查询相等，返回所有索引的所有文档
curl -XGET localhost:9201/\_search -d '{}'  
curl -XGET localhost:9201/\_search  
可以在一个、多个或者 _all 索引库（indices）和一个、多个或者所有types中查询
es也支持post请求

## 查询表达式
查询表达式(Query DSL)是一种非常灵活又富有表现力的 查询语言。 Elasticsearch 使用它可以以简单的 JSON 接口来展现 Lucene 功能的绝大部分。在你的应用中，你应该用它来编写你的查询语句。它可以使你的查询语句更灵活、更精确、易读和易调试。  
要使用这种查询表达式，只需将查询语句传递给 query 参数：
空查询在功能上等价于使用 match_all 查询， 正如其名字一样，匹配所有文档：  
curl -XGET localhost:9201/_search -d '{"query": {"match\_all": {}}}'

### 查询语句的结构
一个查询语句的典型结构：  
```json
{
    QUERY_NAME: {
        ARGUMENT: VALUE,
        ARGUMENT: VALUE,...
    }
}
```
如果是针对某个字段，那么它的结构如下:
```json
{
    QUERY_NAME: {
        FIELD_NAME: {
            ARGUMENT: VALUE,
            ARGUMENT: VALUE,...
        }
    }
}
```
curl -XGET localhost:9201/_search?pretty -d '{"query":{"match":{"elasticsearch":"elasticsearch"}}}'

### 合并查询
查询语句(Query clauses) 就像一些简单的组合块 ，这些组合块可以彼此之间合并组成更复杂的查询。这些语句可以是如下形式：
叶子语句（Leaf clauses） (就像 match 语句) 被用于将查询字符串和一个字段（或者多个字段）对比。  
复合(Compound) 语句 主要用于 合并其它查询语句。 比如，一个 bool 语句 允许在你需要的时候组合其它语句，无论是 must 匹配、 must_not 匹配还是 should 匹配，同时它可以包含不评分的过滤器（filters）。
一条复合语句可以合并 任何 其它查询语句，包括复合语句，了解这一点是很重要的。这就意味着，复合语句之间可以互相嵌套，可以表达非常复杂的逻辑。

## 查询与过滤
Elasticsearch 使用的查询语言（DSL） 拥有一套查询组件，这些组件可以以无限组合的方式进行搭配。这套组件可以在以下两种情况下使用：  
过滤情况和查询情况。  
过滤情况：这个查询只是简单的问一个问题：“这篇文档是否匹配？”。回答也是非常的简单，yes 或者 no ，二者必居其一。
查询情况：查询就变成了一个“评分”的查询。和不评分的查询类似，也要去判断这个文档是否匹配，同时它还需要判断这个文档匹配的有 _多好_（匹配程度如何）。  

### 性能差异
过滤查询只是简单的检查包含或者排除，这就使得计算起来非常快。考虑到至少有一个过滤查询的结果是 “稀少的”（很少匹配的文档），并且经常使用不评分查询，结果会被缓存到内存中以便快速读取，所以有各种各样的手段来优化查询结果。
相反，评分查询不仅仅要找出匹配的文档，还要计算每个匹配文档的相关性，计算相关性使得它们比不评分查询费力的多。同时，查询结果并不缓存。
多亏倒排索引，一个简单的评分查询在匹配少量文档时可能与一个涵盖百万文档的filter表现的一样好，甚至会更好。但是在一般情况下，一个filter 会比一个评分的query性能更优异，并且每次都表现的很稳定。
过滤的目标是减少那些需要通过评分查询进行检查的文档。  


### 查询
match_all 查询简单的匹配所有文档。在没有指定查询方式时，它是默认的查询：
```json
{ "match_all": {}}
```

#### match查询
无论你在任何字段上进行的是全文搜索还是精确查询，match 查询是你可用的标准查询。
如果你在一个全文字段上使用 match 查询，在执行查询前，它将用正确的分析器去分析查询字符串.
如果在一个精确值的字段上使用它， 例如数字、日期、布尔或者一个 not_analyzed 字符串字段，那么它将会精确匹配给定的值.  
#### multi_match查询
```json
{
    "multi_match": {
        "query":    "full text search",
        "fields":   [ "title", "body" ]
    }
}
```
#### range查询
range 查询找出那些落在指定区间内的数字或者时间
```json
{
    "range": {
        "age": {
            "gte":  20,
            "lt":   30
        }
    }
}
```
被允许的操作符如下：
gt 大于 gte 大于等于 lt 小于 lte 小于等于

#### term查询
term 查询被用于精确值 匹配，这些精确值可能是数字、时间、布尔或者那些 not_analyzed 的字符串：
```json
{ "term": { "age":    26           }}
{ "term": { "date":   "2014-09-01" }}
{ "term": { "public": true         }}
{ "term": { "tag":    "full_text"  }}
```
term 查询对于输入的文本不 分析 ，所以它将给定的值进行精确查询。
#### terms查询
terms 查询和 term 查询一样，但它允许你指定多值进行匹配。如果这个字段包含了指定值中的任何一个值，那么这个文档满足条件：
```json
{ "terms": { "tag": [ "search", "full_text", "nosql" ] }}
```
和 term 查询一样，terms 查询对于输入的文本不分析。它查询那些精确匹配的值（包括在大小写、重音、空格等方面的差异）。  
#### exists查询和missing查询
exists查询和missing查询被用于查找那些指定字段中有值 (exists) 或无值 (missing) 的文档。这与SQL中的 IS_NULL (missing) 和 NOT IS_NULL (exists) 在本质上具有共性：
```json
{
    "exists":   {
        "field":    "title"
    }
}
```
这些查询经常用于某个字段有值的情况和某个字段缺值的情况。

## 组合多查询
#### bool查询
bool查询是一种能够将多查询组合成单一查询的查询方法。这种查询将多查询组合在一起，成为用户自己想要的布尔查询。它接收以下参数：  
must  
>文档必须匹配这些条件才能被包含进来。
must_not  
>文档必须不匹配这些条件才能被包含进来。
should  
>如果满足这些语句中的任意语句，将增加 \_score,否则,无任何影响。它们主要用于修正每个文档的相关性得分。
filter  
>必须匹配，但它以不评分、过滤模式来进行。这些语句对评分没有贡献，只是根据过滤标准来排除或包含文档。  
每一个子查询都独自地计算文档的相关性得分。一旦他们的得分被计算出来，bool查询就将这些得分进行合并并且返回一个代表整个布尔操作的得分。
下面的查询用于查找 title 字段匹配 how to make millions 并且不被标识为 spam 的文档。那些被标识为 starred 或在2014之后的文档，将比另外那些文档拥有更高的排名。如果 _两者_ 都满足，那么它排名将更高：
```json
{
    "bool": {
        "must":     { "match": { "title": "how to make millions" }},
        "must_not": { "match": { "tag":   "spam" }},
        "should": [
            { "match": { "tag": "starred" }},
            { "range": { "date": { "gte": "2014-01-01" }}}
        ]
    }
}
```
#### 增加过滤器查询
如果我们不想因为文档的时间而影响得分，可以用filter语句来重写前面的例子：
```json
{
    "bool": {
        "must":     { "match": { "title": "how to make millions" }},
        "must_not": { "match": { "tag":   "spam" }},
        "should": [
            { "match": { "tag": "starred" }}
        ],
        "filter": {
          "range": { "date": { "gte": "2014-01-01" }} 
        }
    }
}
```
通过将 range 查询移到 filter 语句中，我们将它转成不评分的查询，将不再影响文档的相关性排名。由于它现在是一个不评分的查询，可以使用各种对filter 查询有效的优化手段来提升性能。
所有查询都可以借鉴这种方式。将查询移到bool查询的filter语句中，这样它就自动的转成一个不评分的filter了。
如果你需要通过多个不同的标准来过滤你的文档，bool 查询本身也可以被用做不评分的查询。简单地将它放置到 filter 语句中并在内部构建布尔逻辑：  
```json
{
    "bool": {
        "must":     { "match": { "title": "how to make millions" }},
        "must_not": { "match": { "tag":   "spam" }},
        "should": [
            { "match": { "tag": "starred" }}
        ],
        "filter": {
          "bool": { 
              "must": [
                  { "range": { "date": { "gte": "2014-01-01" }}},
                  { "range": { "price": { "lte": 29.99 }}}
              ],
              "must_not": [
                  { "term": { "category": "ebooks" }}
              ]
          }
        }
    }
}
```

#### constant_score查询
它将一个不变的常量评分应用于所有匹配的文档。它被经常用于你只需要执行一个 filter 而没有其它查询（例如，评分查询）的情况下。
可以使用它来取代只有 filter 语句的 bool 查询。在性能上是完全相同的，但对于提高查询简洁性和清晰度有很大帮助。
```json
{
    "constant_score":   {
        "filter": {
            "term": { "category": "ebooks" } 
        }
    }
}
```
## 验证查询
查询可以变得非常的复杂，尤其和不同的分析器与不同的字段映射结合时，理解起来就有点困难了。不过 validate-query API 可以用来验证查询是否合法。  
GET /gb/tweet/_validate/query
{
   "query": {
      "tweet" : {
         "match" : "really powerful"
      }
   }
}
### 理解错误信息
为了找出 查询不合法的原因，可以将 explain 参数 加到查询字符串中：
GET /gb/tweet/_validate/query?explain 
{
   "query": {
      "tweet" : {
         "match" : "really powerful"
      }
   }
}


