## 字段数据类型
### 什么是映射
为了能够把日期字段处理成日期，把数字字段处理成数字，把字符串字段处理成全文本（Full-text）或精确（Exact-value）的字符串值，Elasticsearch需要知道每个字段里面都包含什么数据类型。这些类型和字段的信息存储在映射中  
创建索引的时候,可以预先定义字段的类型以及相关属性,相当于定义数据库字段的属性  


### 根对象
映射的最高一层被称为 根对象 ，它可能包含下面几项：  
一个 properties 节点，列出了文档中可能包含的每个字段的映射
各种元数据字段，它们都以一个下划线开头，例如 _type 、 _id 和 _source
设置项，控制如何动态处理新的字段，例如 analyzer 、 dynamic\_date\_formats 和 dynamic_templates
其他设置，可以同时应用在根对象和其他 object 类型的字段上，例如 enabled 、 dynamic 和 include\_in\_all

#### 字段类型
ELasticsearch 5.X之后的字段类型不再支持string，由text或keyword取代。  
text取代了string，当一个字段是要被全文搜索的，比如Email内容、产品描述，应该使用text类型。设置text类型以后，字段内容会被分析，在生成倒排索引以前，字符串会被分析器分成一个一个词项。text类型的字段不用于排序，很少用于聚合。

#### keyword类型
keyword类型适用于索引结构化的字段，比如email地址、主机名、状态码和标签。如果字段需要进行过滤(比如查找已发布博客中status属性为published的文章)、排序、聚合。keyword类型的字段只能通过精确值搜索到。

对于数字类型，ELasticsearch支持以下几种：  

    类型 | 取值范围        
    --- | ---
    long | -2^63至2^63-1|
    integer|-2^31至2^31-1
    short|-32,768至32768
    byte|-128至127
    double|64位双精度IEEE 754浮点类型
    float|32位单精度IEEE 754浮点类型
    half_float|16位半精度IEEE 754浮点类型
    scaled_float|缩放类型的的浮点数（比如价格只需要精确到分，price为57.34的字段缩放因子为100，存起来就是5734)

对于float、half_float和scaled_float,-0.0和+0.0是不同的值，使用term查询查找-0.0不会匹配+0.0，同样range查询中上边界是-0.0不会匹配+0.0，下边界是+0.0不会匹配-0.0。

对于数字类型的数据，选择以上数据类型的注意事项：

1.在满足需求的情况下，尽可能选择范围小的数据类型。比如，某个字段的取值最大值不会超过100，那么选择byte类型即可。迄今为止吉尼斯记录的人类的年龄的最大值为134岁，对于年龄字段，short足矣。字段的长度越短，索引和搜索的效率越高。  
2.优先考虑使用带缩放因子的浮点类型。

Object类型

JSON天生具有层级关系，文档会包含嵌套的对象：
```json
PUT my_index/my_type/1
{ 
  "region": "US",
  "manager": { 
    "age":     30,
    "name": { 
      "first": "John",
      "last":  "Smith"
    }
  }
}
```
上面的文档中，整体是一个JSON，JSON中包含一个manager,manager又包含一个name。最终，文档会被索引成一平的key-value对：
```json
{
  "region":             "US",
  "manager.age":        30,
  "manager.name.first": "John",
  "manager.name.last":  "Smith"
}
```
上面文档结构的Mapping如下：
```json
PUT my_index
{
  "mappings": {
    "my_type": { 
      "properties": {
        "region": {
          "type": "keyword"
        },
        "manager": { 
          "properties": {
            "age":  { "type": "integer" },
            "name": { 
              "properties": {
                "first": { "type": "text" },
                "last":  { "type": "text" }
              }
            }
          }
        }
      }
    }
  }
}
```
date类型

JSON中没有日期类型，所以在ELasticsearch中，日期类型可以是以下几种：

日期格式的字符串：e.g. “2015-01-01” or “2015/01/01 12:10:30”.
long类型的毫秒数( milliseconds-since-the-epoch)
integer的秒数(seconds-since-the-epoch)
日期格式可以自定义，如果没有自定义，默认格式如下：
"strict_date_optional_time||epoch_millis"

Array类型
ELasticsearch没有专用的数组类型，默认情况下任何字段都可以包含一个或者多个值，但是一个数组中的值要是同一种类型。

注意事项：

动态添加数据时，数组的第一个值的类型决定整个数组的类型
混合数组类型是不支持的，比如：[1,”abc”]
数组可以包含null值，空数组[]会被当做missing field对待。

binary类型
```json
PUT my_index
{
  "mappings": {
    "my_type": {
      "properties": {
        "name": {
          "type": "text"
        },
        "blob": {
          "type": "binary"
        }
      }
    }
  }
}
```
```json
PUT my_index/my_type/1
{
  "name": "Some binary blob",
  "blob": "U29tZSBiaW5hcnkgYmxvYg==" 
}
```
ip类型
ip类型的字段用于存储IPV4或者IPV6的地址。
```json
PUT my_index
{
  "mappings": {
    "my_type": {
      "properties": {
        "ip_addr": {
          "type": "ip"
        }
      }
    }
  }
}
```
```json
PUT my_index/my_type/1
{
  "ip_addr": "192.168.1.1"
}
```
```json
GET my_index/_search
{
  "query": {
    "term": {
      "ip_addr": "192.168.0.0/16"
    }
  }
}
```
range类型

range类型的使用场景：比如前端的时间选择表单、年龄范围选择表单等。 
```json
PUT range_index
{
  "mappings": {
    "my_type": {
      "properties": {
        "expected_attendees": {
          "type": "integer_range"
        },
        "time_frame": {
          "type": "date_range", 
          "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
        }
      }
    }
  }
}
```
```json
PUT range_index/my_type/1
{
  "expected_attendees" : { 
    "gte" : 10,
    "lte" : 20
  },
  "time_frame" : { 
    "gte" : "2015-10-31 12:00:00", 
    "lte" : "2015-11-01"
  }
}
```
nested类型
nested嵌套类型是object中的一个特例，可以让array类型的Object独立索引和查询。

token_count类型
token_count用于统计词频

geo_point类型
地理位置信息类型用于存储地理位置信息的经纬度

### 映射的分类

静态映射  动态映射  
什么是动态映射  
文档中碰到一个以前没见过的字段时,动态映射可以自动决定该字段的类型,并对该字段添加映射  
如何配置动态映射  
通过dynamic属性进行控制
true:默认值,动态添加字段; false:忽略新字段; strict:碰到陌生字段,抛出异常  
适用范围  
适用在根对象上或者object类型的任意字段上

### 动态模板
使用 dynamic_templates ，你可以完全控制 新检测生成字段的映射。你甚至可以通过字段名称或数据类型来应用不同的映射。
每个模板都有一个名称， 你可以用来描述这个模板的用途， 一个 mapping 来指定映射应该怎样使用，以及至少一个参数 (如 match) 来定义这个模板适用于哪个字段。
模板按照顺序来检测；第一个匹配的模板会被启用。例如，我们给 string 类型字段定义两个模板：  
es ：以 _es 结尾的字段名需要使用 spanish 分词器。  
en ：所有其他字段使用 english 分词器。  
我们将 es 模板放在第一位，因为它比匹配所有字符串字段的 en 模板更特殊：  
```json
PUT /my_index
{
    "mappings": {
        "my_type": {
            "dynamic_templates": [
                { "es": {
                      "match":              "*_es", 
                      "match_mapping_type": "string",
                      "mapping": {
                          "type":           "string",
                          "analyzer":       "spanish"
                      }
                }},
                { "en": {
                      "match":              "*", 
                      "match_mapping_type": "string",
                      "mapping": {
                          "type":           "string",
                          "analyzer":       "english"
                      }
                }}
            ]
}}}
```

下面是两个 最重要的设置：
number_of_shards
每个索引的主分片数，默认值是 5 。这个配置在索引创建后不能修改。
number_of_replicas
每个主分片的副本数，默认值是 1 。对于活动的索引库，这个配置可以随时修改。

### 配置分析器
standard 分析器是用于全文字段的默认分析器， 对于大部分西方语系来说是一个不错的选择。 它包括了以下几点：

standard 分词器，通过单词边界分割输入的文本。
standard 语汇单元过滤器，目的是整理分词器触发的语汇单元（但是目前什么都没做）。
lowercase 语汇单元过滤器，转换所有的语汇单元为小写。
stop 语汇单元过滤器，删除停用词--对搜索相关性影响不大的常用词，如 a ， the ， and ， is 。
默认情况下，停用词过滤器是被禁用的。如需启用它，你可以通过创建一个基于 standard 分析器的自定义分析器并设置 stopwords 参数。 可以给分析器提供一个停用词列表，或者告知使用一个基于特定语言的预定义停用词列表。
在下面的例子中，我们创建了一个新的分析器，叫做 es_std ， 并使用预定义的 西班牙语停用词列表：
PUT http://192.168.40.129:9200/spanish_docs
```json
{
    "settings": {
        "analysis": {
            "analyzer": {
                "es_std": {
                    "type":      "standard",
                    "stopwords": "_spanish_"
                }
            }
        }
    }
}
```
es_std 分析器不是全局的--它仅仅存在于我们定义的 spanish_docs 索引中。

### 自定义分析器
虽然Elasticsearch带有一些现成的分析器，然而在分析器上Elasticsearch真正的强大之处在于，你可以通过在一个适合你的特定数据的设置之中组合字符过滤器、分词器、词汇单元过滤器来创建自定义的分析器。
一个 分析器 就是在一个包里面组合了三种函数的一个包装器， 三种函数按照顺序被执行:  
字符过滤器
字符过滤器 用来 整理 一个尚未被分词的字符串。例如，如果我们的文本是HTML格式的，它会包含像 <p> 或者 <div> 这样的HTML标签，这些标签是我们不想索引的。我们可以使用 html清除 字符过滤器 来移除掉所有的HTML标签，并且像把 &Aacute; 转换为相对应的Unicode字符 Á 这样，转换HTML实体。
一个分析器可能有0个或者多个字符过滤器。

分词器
一个分析器 必须 有一个唯一的分词器。 分词器把字符串分解成单个词条或者词汇单元。 标准 分析器里使用的 标准 分词器 把一个字符串根据单词边界分解成单个词条，并且移除掉大部分的标点符号，然而还有其他不同行为的分词器存在。
例如， 关键词 分词器 完整地输出 接收到的同样的字符串，并不做任何分词。 空格 分词器 只根据空格分割文本 。 正则 分词器 根据匹配正则表达式来分割文本 。

词单元过滤器
经过分词，作为结果的 词单元流 会按照指定的顺序通过指定的词单元过滤器 。

词单元过滤器可以修改、添加或者移除词单元。我们已经提到过 lowercase 和 stop 词过滤器 ，但是在 Elasticsearch 里面还有很多可供选择的词单元过滤器。 词干过滤器 把单词 遏制 为 词干。 ascii_folding 过滤器移除变音符，把一个像 "très" 这样的词转换为 "tres" 。 ngram 和 edge_ngram 词单元过滤器 可以产生 适合用于部分匹配或者自动补全的词单元。  
使用 html清除 字符过滤器移除HTML部分。
使用一个自定义的 映射 字符过滤器把 & 替换为 " 和 " ：
```json
"char_filter": {
    "&_to_and": {
        "type":       "mapping",
        "mappings": [ "&=> and "]
    }
}
```
使用 标准 分词器分词。
小写词条，使用 小写 词过滤器处理。
使用自定义 停止 词过滤器移除自定义的停止词列表中包含的词：  
```json
"filter": {
    "my_stopwords": {
        "type":        "stop",
        "stopwords": [ "the", "a" ]
    }
}
```
我们的分析器定义用我们之前已经设置好的自定义过滤器组合了已经定义好的分词器和过滤器：
```json
"analyzer": {
    "my_analyzer": {
        "type":           "custom",
        "char_filter":  [ "html_strip", "&_to_and" ],
        "tokenizer":      "standard",
        "filter":       [ "lowercase", "my_stopwords" ]
    }
}
```
```json
PUT /my_index
{
    "settings": {
        "analysis": {
            "char_filter": {
                "&_to_and": {
                    "type":       "mapping",
                    "mappings": [ "&=> and "]
            }},
            "filter": {
                "my_stopwords": {
                    "type":       "stop",
                    "stopwords": [ "the", "a" ]
            }},
            "analyzer": {
                "my_analyzer": {
                    "type":         "custom",
                    "char_filter":  [ "html_strip", "&_to_and" ],
                    "tokenizer":    "standard",
                    "filter":       [ "lowercase", "my_stopwords" ]
            }}
}}}
```


http://192.168.40.129:9200/library
```json
{
    "settings":{
    "number_of_shards" : 5,
    "number_of_replicas" : 1
},
     "mappings":{
      "books":{
        "properties":{
            "title":{"type":"string"},
             "name":{"type":"string","index":"not_analyzed"},
            "publish_date":{"type":"date","index":"not_analyzed"},
            "price":{"type":"double"},
            "number":{
                "type":"object",
                "dynamic":true
    }
        }
     }
     }
}
```

curl -XPOST "http://127.0.0.1:9200/product"  
创建了一个索引，并没有设置mapping，查看一下索引mapping的内容：   
```json
curl -XGET "http://127.0.0.1:9200/product/_mapping?pretty" 
{
  "product" : {
    "mappings" : { }
  }
}
```
可以看到mapping为空，我们只创建了一个索引，并没有进行mapping配置，mapping自然为空。   
下面给product这个索引加一个type，type name为prod，并设置mapping：   
http://192.168.66.128:9201/product/prod/_mapping  
```json
{
    "prod": {
            "properties": {
                "title": {
                    "type": "string",
                    "store": "yes"
                },
                "description": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "price": {
                    "type": "double"
                },
                "onSale": {
                    "type": "boolean"
                },
                "type": {
                    "type": "integer"
                },
                "createDate": {
                    "type": "date"
                }
            }
        }
  }
 ```