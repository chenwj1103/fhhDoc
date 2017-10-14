#### OSI参考模型
未解决计算机厂商网络结构体系/各种协议不兼容，ISO制定了一个国际标准OSI，对通信系统进行了标准化。OSI并没有普及，但是OSI协议设计之初作为知道仿真的OSI参考模型却常被用于网络协议的制定中。
OSI参考模型中各个分层的作用
|---|---|
|分层名称|功能|
|应用层|针对特定应用的协议|
|表示层|设备固有数据格式和网络标准数据格式转换|
|会话层|通讯管理。负责建立和断开通讯链接|
|传输层|管理两个节点之间的数据传输|
|网络层|地址管理与路由选择|
|数据链路层|互连设备之间传送和识别数据帧|
|物理层|0/1代表电压高低和网线规格|

### TCP/IP协议族
从字面意义上讲，很多人可能会认为TCP/IP是TCP/IP这两种协议，而事实上它指利用IP进行通讯时所用到的协议群的统称。
TCP/IP协议由IETF讨论制定，需要标准化的协议被人们列入RFC（Request For Comment）文档并在互联网上公布。https://www.rfc-editor.org/retrieve/bulk/
HTTP是TCP/IP的一个子集

HTTP是WWW的基础协议。CERN(欧洲核子研究组织)的Tim Berners-Lee（被称为万维网之父）在1989-1991年创建了它，基本理念是借助多文档之间相互关联形成的超文本，连接成相互参阅的WWW。
其中提出了 3 中构建技术，分别是 HTML、HTTP、URL。
1990 年 11 月，CERN 成功研发出了世界上第一台 WEB 服务器和 WEB 浏览器。

### 浏览器大战

1993 年 1 月，现代浏览器的祖先 NCSA 研发的 Mosaic 问世。通过内联形式显示 HTML 的图像。

1994 年 12 月，网景通信公司发布了 Netscape Navigator 1.0。

1995 年微软公司发布了 Internet Explorer 1.0 和 2.0。

### 浏览器大战
#### 第一次浏览器大战爆发于 1995 至 1998 年，微软通过捆绑操作系统来推广 IE ，将当时占市场90%的网景 Netscape 浏览器彻底击败。这次大战微软留下三个隐患：

	为对抗 Netscape 微软在 IE 里加入了很多非标准的专属标签，致使后来的的 IE 6 成为开发者的噩梦，破坏了开放标准；
	捆绑销售 IE 的做法被指垄断，受到反垄断的压制；
	网景为吸引开发者开放源代码创造了Mozilla，虽未能挽回 Netscape 的市场占有率，但是它衍生出了Phoenix ，即现在的 Firefox 火狐浏览器。
	
#### 第二次浏览器大战	

由于第一次浏览器大战留下的隐患导致了 05 年到 07 年的第二轮浏览器大战。这次大战后 Firefox 在北美，欧洲等地区的占有率接近甚至超过了 20%，微软全球范围内的份额也从 IE 6 高峰时的 96% 先是下降到 85%，最后 07 年末的时候稳定在 60% 左右，不再是“唯一的浏览器”了。

HTTP协议在应用的早期阶段非常简单，后来被称为HTTP/0.9，有时候被视为单行(one-line)协议.
### HTTP/0.9 – 
单行协议最初版本的HTTPi协议并没有版本号; 它的版本号被定位0.9以区分后来的版本。 HTTP/0.9 极其简单： 一个请求由一个单行的指令构成，唯一的指令GET开头，后面跟一个资源的路径（一旦连接到服务器，协议、服务器、端口这些都不是必须的）。

GET /mypage.html

响应也是极其简单的： 只是包含文档本身。

<HTML>
这是一个非常简单的HTML页面
</HTML>

跟后来的版本不一样，响应内容并没有HTTP头，这意味着只有HTML文件可以传送，没法传送其他类型的文件。没有状态或者错误代码：一旦出了问题，一个特定的包含问题描述的HTML文件将被发送，供人们查看。


### HTTP/1.0 1996 年 5 月 HTTP/1.0。
构建可扩展性HTTP浏览器和服务器迅速扩展使其用途更广：

	* 版本信息现在会随着每个请求发送（HTTP1.0 被追加到GET行）
	* 状态代码行也会在响应开始时发送，允许浏览器本身了解请求的成功或失败
	* 引入了HTTP头的概念，无论是对于请求还是响应，允许传输元数据，并使协议非常灵活和可扩展。
	* 在新的HTTP头的帮助下，增加了传输除纯文本HTML文件外的其他类型文档的能力。

一个典型的请求看来就像这样：

GET /mypage.html HTTP/1.0
User-Agent: NCSA_Mosaic/2.0 (Windows 3.1)

200 OK
Date: Tue, 15 Nov 1994 08:12:31 GMT
Server: CERN/3.0 libwww/2.17
Content-Type: text/html
<HTML> 

一个包含图片的页面
接下来就是第二个连接，请求获取图片：

GET /myimage.gif HTTP/1.0
User-Agent: NCSA_Mosaic/2.0 (Windows 3.1)

200 OK
Date: Tue, 15 Nov 1994 08:12:32 GMT
Server: CERN/3.0 libwww/2.17
Content-Type: text/gif

HTTP/1.1 – HTTP1.1 在1997年1月，就在HTTP/1.0发布后的几个月后。

引入了许多改进：

	* 连接可以重复使用，节省了多次打开它的时间(一个TCP可以支持多个HTTP)。
	* 默认使用长链接,支持断点续传
	* 同时也支持更多的请求头和响应头（range头，其中HTTP1.0需要在request中增加”Connection： keep-alive“ header才能够支持，而HTTP1.1默认支持）
	* 可以不同的域名配置在同一个IP地址的服务器。

一个典型的请求流程， 所有请求都通过一个连接实现，看起来就像这样：

GET /en-US/docs/Glossary/Simple_header HTTP/1.1
Host: developer.mozilla.org
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:50.0) Gecko/20100101 Firefox/50.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: https://developer.mozilla.org/en-US/docs/Glossary/Simple_header

200 OK
Connection: Keep-Alive
Content-Encoding: gzip
Content-Type: text/html; charset=utf-8
Date: Wed, 20 Jul 2016 10:55:30 GMT
Etag: "547fa7e369ef56031dd3bff2ace9fc0832eb251a"
Keep-Alive: timeout=5, max=1000
Last-Modified: Tue, 19 Jul 2016 00:59:33 GMT
Server: Apache
Transfer-Encoding: chunked
Vary: Cookie, Accept-Encoding

(content)


### HTTP/2.0的特性
	*HTTP/2采用二进制格式而非文本格式
	*使用报头压缩，HTTP/2降低了开销
	*HTTP/2是完全多路复用的，而非有序并阻塞的——只需一个连接即可实现并行
	*HTTP/2让服务器可以将响应主动“推送”到客户端缓存中






