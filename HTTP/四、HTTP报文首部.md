### 报文结构
    报文首部
    空行
    报文主体

### 报文首部
	状态行
    响应首部字段
    通用首部字段
	实体首部字段
		
### 通用首部字段

|首部字段名|说明|
|---|---|
|Cache-Control|控制缓存行为|
|Connection|链接的管理| 
|Date|创建报文的日期和时间 |
|Tralier|报文末端的首部一览|
|Transfer-Encoding|指定报文主体的传输码方式|
|Upgrade|升级为其他协议| 
|Waming|错误通知| 

### 请求首部字段

|首部字段名|说明|
|---|---|
|Accept|用户代理可处理的媒体类型|
|Accept-Charset|优先的字符集| 
|Accept-Encoding|优先的内容编码 |
|Accept-Language|优先的语言（自然语言）| 
|Authorization|Web认证信息|
|Expect|期待服务器的特定行为|
|From|用户的电子邮箱地址| 
|if-Match|请求资源所在的服务器 |
|if-Modified-Since|比较资源的更新时间|
|if-None-Match|比较实体标记（与if—match相反）| 
|if-Range|资源未更新时发送实体Byte的范围请求 |
|if-Unmodified-Since|比较资源的更新时间（与if-Modified-Since相反）| 
|Max-Forwards|最大传输逐条数|
|Proxy-Authorization|代理服务器要求客户端认证信息|
|Range|实体的字段范围请求| 
|Referer|对请求中URI的原始获取方|
|TE|传输编码优先级|
|User-Agent|HTTP客户端程序的信息|

### 响应首部字段

|首部字段名|说明|
|---|---|
|Accept-Ranges|是否接受字节范围请求|
|Age|推算资源创建经过实践| 
|ETag|资源匹配信息 |
|Location|令客户端重定向至URI| 
|Prox-Authenticate|代理服务器对客户端的认证信息|
|Retry-After|对再次发起请求的时机要求|
|Server|HTTP服务器的安装信息| 
|Vary|代理服务器缓存的管理信息 |
|WWW-Authenticate|服务器对客户端的认证信息| 

### 实体首部字段

|首部字段名|说明|
|---|---|
|Allow|资源可支持的HTTP方法|
|Content-Encoding|实体主体使用的编码方式| 
|Content-Language|实体主题的自然语言 |
|ontent-Length|实体主体的大小（单位：字节）| 
|ontent-Location|替代对应的资源的URL|
|ontent-MD5|实体主体的报文摘要|
|ontent-Rang|试题主体的位置范围| 
|ontent-Type|试题主体的媒体类型|
|Expires|实体主体的过期日期时间| 
|Last-Modified|资源的最后修改日期|