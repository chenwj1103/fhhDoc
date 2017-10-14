### Cookie 和Session

#### 一、JSP和Servlet中的Cookie 

 由于HTTP协议是无状态协议（虽然Socket连接是有状态的，但每次用HTTP协议进行数据传输后就关闭的Socket连接，因此，HTTP协议并不会保存上一次的状态），
 如果要保存某些HTTP请求过程中所产生的数据，就必须要有一种类似全局变量的机制保证数据在不同的HTTP请求之间共享。这就是下面要讲的Session和Cookie。

 Cookie是通过将数据保存在客户端的硬盘（永久Cookie）或内存（临时Cookie）中来实现数据共享的一种机制。每一个Cookie有一个超时时间，如果超过了这个时间，
 Cookie将自动失效。可按如下方法来设置Cookie的超时时间：

     Cookie cookie = new Cookie("key","value");
     cookie.setMaxAge(3600);  // Cookie的超时间为3600秒，也就是1小时
     response.addCookie(cookie);

如果不使用setMaxAge方法，Cookie的超时时间为-1，在这种情况下，Cookie就是临时Cookie，也就是说这种Cookie实际上并不保存在客户端硬盘上，而是保存在客户端内存中的。
读者可以在JSP中运行如下代码，看看是否会在上面提到的保存cookie的目录中生成cookie文件：

  Cookie cookie = new Cookie("key","value");
response.addCookie(cookie);

实际上使用setMaxAge将超时时间设为任意的负数都会被客户端浏览器认为是临时
Cookie，如下面的代码将在客户端内存中保存一个临时Cookie：

     Cookie cookie = new Cookie("key","value");
     cookie.setMaxAge(-100);  // 将cookie设为临时Cookie
     response.addCookie(cookie);

如果第一次将Cookie写入客户端（不管是硬盘还是内存），在同一台机器上第二次访问
该网站的jsp页面时，会自动将客户端的cookie作为HTTP请求头的Cookie字段值传给服务端，如果有多个Cookie，中间用";"隔开。如下面的HTTP请求头所示：
 
     GET /test/First.jsp HTTP/1.1

     HOST:localhost

     ...
     Cookie:key1=value1;key2=value2
     ...
     ...

|首部字段名称|说明|首部类型|
|---|---|---|
|set cookie|开始状态管理所使用的Cookie信息|响应首部字段|
|cookie |服务器收到的Cookie信息|请求首部字段|	

Cookie 是Web 服务器向用户的浏览器发送的一段ASCII码文本。一旦收到Cookie，浏览器会把Cookie的信息片断以"名/值"对(name-value pairs)的形式储存保存在本地。
这以后，每当向同一个Web 服务器请求一个新的文档时，Web 浏览器都会发送之站点以前存储在本地的Cookie。

Set-Cookie：customer=huangxp; path=/foo; domain=.ibm.com; 
expires= Wednesday, 19-OCT-05 23:12:40 GMT; [secure]

expires 有效期

path 制定发送范围的文件目录

domain 制定尾部匹配

secure 仅在htts发送

httpOnly禁止js获取 

虽然永久Cookie和临时Cookie在第二次向服务端发出HTTP请求时生成Cookie字段，但它们还是有一定的区别的。永久Cookie在任意新开启的IE窗口都可以生成Cookie。而临时Cookie由于只保存在当前IE窗口。

###Cookie的加密

    cookie有多种加密方式如
    1.借助证书中的私钥和公钥进行加密解密
    
    2.对cookie中的name=value中value进行md5进行加密，在服务端发送前进行一分md5的保存查看二者是否一致（可以多重方式）

### 任何私密数据都不应保存在cookie中无论是明文还是md5或可逆加密。在cookie只保留一个session id。

#### 二、Tomcat中的Servlet和Session

由于Cookie数存在保存在客户端，这样对于一些敏感数据会带来一些风险。而且Cookie一般只能保存字符串等简单数据。并且大小限制在4KB。如果要保存比较复杂的数据，Cookie可能显得有些不合适。基于这些原因，我们自然会想到在服务端采用这种类似Cookie的机制来存储数据。这就是我们这节要讲的会话(Session)。而在一个客户端和服务端的会话中所有的页面可以共享为这个会话所建立的Session。

那么什么是会话呢？有很多人认为会话就是在一台机器上客户端浏览器访问某个域名所指向的服务端程序，就建立了一个客户端到服务端的会话。然后关闭客户端浏览器，会话就结束。其实这并不准确。

首先让我们先来看看Session的原理。Session和Cookie类似。所不同的是它是建立在服务端的对象。每一个Session对象一个会话。也许很多读者看到这会有一个疑问。Session是如何同客户端联系在一起的呢？很多人在使用Session时并没有感觉到这一点。其实这一切都是Web服务器，如Tomcat一手包办的。那么Web服务器又是如何识别通过HTTP协议进行连接的客户端的呢？这就要用到第一节中所讲的Cookie。在一般情况下，Session使用了临时Cookie来识别某一个Session是否属于某一个会话。在本文中以Tomcat为例来说明Session是如何工作的。

让我们先假设某一个客户端第一次访问一个Servlet，在这个Servlet中使用了getSession来得到一个Session对象，也就是建立了一个会话，这个Servlet的代码如下：


    public class First extends HttpServlet{

    public void doGet(HttpServletRequest request, HttpServletResponse response)throws ServletException, IOException{

    response.setContentType("text/html");
     
    HttpSession session = request.getSession();
     
    session.setAttribute("key", "mySessionValue");
     
    PrintWriter out = response.getWriter();
     
    out.println("The session has been generated!");
     
    out.flush();

    out.close();}}

对于服务端的First来说，getSession方法主要做了两件事：

    从客户端的HTTP请求头的Cookie字段中获得一个寻找一个JSESSIONID的key，这个key的值是一个唯一字符串，类似于D5A5C79F3C8E8653BC8B4F0860BFDBCD 。
    
    如果Cookie中包含这个JSESSIONID，将key的值取出，在Tomcat的SessionMap（用于保存Tomcat自启动以来的所有创建的Session）中查找，如果找到，将这个Session取出，如果未找到，创建一个HttpSession对象，并保存在Session Map中，以便下一次使用这个Key来获得这个Session。
 
在服务器向客户端发送响应信息时，如果是新创建的HttpSession对象，在响应HTTP
头中加了一个Set-Cookie字段，并将JSESSIONID和相应的值反回给客户端。如下面的HTTP响应头：
 
    HTTP/1.1 200 OK
    ...
    Set-Cookie: JSESSIONID=D5A5C79F3C8E8653BC8B4F0860BFDBCD
    ...

对于客户端浏览器来说，并不认识哪个Cookie是用于Session的，它只是将相应的临时Cookie和永久Cookie原封不动地放到请求HTTP头的Cookie字段中，发送给服务器。如果在IE中首次访问服务端的First，这时在当前IE窗口并没有临时Cookie，因此，在请求HTTP头中就没有Cookie字段，所以First在调用getSession方法时就未找到JSESSIONID，因此，就会新建一个HttpSession对象。并在Set-Cookie中将这个JSESSIONID返回。接下来我们使用另外一个Servlet：Second来获得在First中所设置的Session数据。Second的代码如下：


    public class Second extends HttpServlet{
     
    public void doGet(HttpServletRequest request, HttpServletResponse response)throws ServletException, IOException{

    response.setContentType("text/html");

    HttpSession session = request.getSession();

    PrintWriter out = response.getWriter();
     
    out.println(session.getAttribute("key"));

    out.flush();

    out.close();}}

如果在同一个窗口来调用Second。这时客户端已经有了一个临时Cookie，就是JSESSIONID，因此，会将这个Cookie放到HTTP头的Cookie字段中发送给服务端。服务端在收到这个HTTP请求时就可以从Cookie中得到JSESSIONID的值，并从Session Map中找到这个Session对象，也就是getSession方法的返回值。因此，从技术层面上来说，所有拥有同一个Session ID的页面都应该属于同一个会话。

如果我们在一个新的IE窗口调用Second，并不会得到mySessionValue。因为这时Second和First拥有了不同的Session ID，因此，它们并不属于同一个会话。既然拥有同一个Session ID，就可以共享Session对象，那么我们可不可以使用永久Cookie将这个Session ID保存在Cookie文件中，这样就算在新的IE窗口，也可以共享Session对象了。答案是肯定的。下面是新的First代码：

    public class First extends HttpServlet{
     
    public void doGet(HttpServletRequest request, HttpServletResponse response)throws ServletException, IOException{
     
    response.setContentType("text/html");
     
    HttpSession session = request.getSession();
     
    session.setMaxInactiveInterval(3600);
     
    Cookie cookie = new Cookie("JSESSIONID", session.getId());
     
    cookie.setMaxAge(3600);
     
    response.addCookie(cookie);
     
    session.setAttribute("key", "mySessionValue");
     
    PrintWriter out = response.getWriter();
     
    out.println("The session has been generated!");
     
    out.flush();
     
    out.close();}}

### 使用url传递session id

在上面讲过，在默认情况下session是依靠客户端的cookie来实现的。但如果客户端浏览器不支持cookie或将cookie功能关闭，那就就意味着无法通过cookie来实现session了。在这种情况下，我们还可以有另一种选择，就是通过url来传递session id。

    对于Tomcat来说，需要使用jsessionid作为key来传递session id。但具体如何传呢？可能有很多人认为会是如下的格式：
 
	http://localhost:8080/test/MyJSP.jsp;jsessionid= D5A5C79F3C8E8653BC8B4F0860BFDBCD
	
Session本身也是实现为一个HashMap，因为Session设计为存放key-value键值对，Tomcat里面Session实现类是StandardSession，里面一个attributes属性：
      private HashMap attributes = new HashMap();
      
所有会话信息的存取都是通过这个属性来实现的。Session会话信息不会一直在服务器端保存，超过一定的时间期限就会被删除，这个时间期限可以在web.xml中进行设置，不设置的话会有一个默认值，Tomcat的默认值是60。
原理服务器会启动一个线程，一直查询所有的Session对象，检查不活动的时间是否超过设定值，如果超过就将其删除。




### Tomcat是怎么实现
连接请求会交给HttpProcessor的process方法处理，在此方法有这么几句：
[java] view plain copy print?

    1. parseConnection(socket); 
    2. parseRequest(input, output);//解析请求行，如果有jessionid，会在方法里面解析jessionid 
    3. if (!request.getRequest().getProtocol() 
    4.     .startsWith("HTTP/0")) 
    5.     parseHeaders(input);//解析请求头部，如果有cookie字段，在方法里面会解析cookie， 

下面看parseRequest方法里面是怎么解析jessionid的，这种解析方式是针对url重写的：

    parseRequest方法： 
     int semicolon = uri.indexOf(match);//match是“;JSESSIONID=”，即在请求行查找字段JSESSIONID 
             if (semicolon >= 0) {                                   //如果有JSESSIONID字段，表示不是第一次访问 
                 String rest = uri.substring(semicolon + match.length()); 
                 int semicolon2 = rest.indexOf(';'); 
                 if (semicolon2 >= 0) { 
                    request.setRequestedSessionId(rest.substring(0, semicolon2));//设置sessionid 
                     rest = rest.substring(semicolon2); 
                 } else { 
                     request.setRequestedSessionId(rest); 
                     rest = ""; 
                 } 
                request.setRequestedSessionURL(true); 
                 uri = uri.substring(0, semicolon) + rest; 
                 if (debug >= 1) 
                   log(" Requested URL session id is " + 
                         ((HttpServletRequest) request.getRequest()) 
                         .getRequestedSessionId()); 
             } else {                               //如果请求行没有JSESSIONID字段，表示是第一次访问。 
                 request.setRequestedSessionId(null); 
                 request.setRequestedSessionURL(false); 
             } 

代码没什么说的，看url有没有JSESSIONID，有就设置request的sessionid，没有就设置为null。有再看parseHeaders方法：

    parseHeaders方法：
    else if (header.equals(DefaultHeaders.COOKIE_NAME)) { //COOKIE_NAME的值是cookie
                    Cookie cookies[] = RequestUtil.parseCookieHeader(value);
                    for (int i = 0; i < cookies.length; i++) {
                        if (cookies[i].getName().equals
                            (Globals.SESSION_COOKIE_NAME)) {
                            // Override anything requested in the URL
                            if (!request.isRequestedSessionIdFromCookie()) {
                                 // Accept only the first session id cookie
                                 request.setRequestedSessionId
                                     (cookies[i].getValue());//设置sessionid
                                 request.setRequestedSessionCookie(true);
                                 request.setRequestedSessionURL(false);
                                 if (debug >= 1)
                                     log(" Requested cookie session id is " +
                                         ((HttpServletRequest) request.getRequest())
                                         .getRequestedSessionId());
                             }
                         }
                         if (debug >= 1)
                             log(" Adding cookie " + cookies[i].getName() + "=" +
                                 cookies[i].getValue());
                         request.addCookie(cookies[i]);
                     }
                 }   
    
       代码主要就是从http请求头部的字段cookie得到JSESSIONID并设置到reqeust的sessionid，没有就不设置。这样客户端的JSESSIONID（cookie）就传到tomcat,tomcat把JSESSIONID的值赋给request了。这个request在Tomcat的唯一性就标识了。
     我们知道，Session只对应用有用，两个应用的Session一般不能共用，在Tomcat一个Context代表一个应用，所以一个应用应该有一套自己的Session，Tomcat使用Manager来管理各个应用的Session，Manager也是一个组件，跟Context是一一对应的关系。Manager的标准实现是StandardManager，由它统一管理Context的Session对象（标准实现是StandardSession），能够猜想，StandardManager一定能够创建Session对象和根据JSESSIONID从跟它关联的应用中查找Session对象。事实上StandardManager确实有这样的方法，但是StandardManager本身没有这两个方法，它的父类ManagerBase有这两个方法

    ManagerBase类的findSession和createSession()方法
     public Session findSession(String id) throws IOException {
              if (id == null)
                  return (null);
              synchronized (sessions) {
                  Session session = (Session) sessions.get(id);//根据sessionid（即<span style="font-family: Arial; ">JSESSIONID</span>）查找session对象。
                  return (session);
              }
          }
    public Session createSession() { //创建session对象
               // Recycle or create a Session instance
               Session session = null;
               synchronized (recycled) {
                   int size = recycled.size();
                   if (size > 0) {
                       session = (Session) recycled.get(size - 1);
                       recycled.remove(size - 1);
                   }
               }
               if (session != null)
                   session.setManager(this);
               else
                   session = new StandardSession(this); 

               // Initialize the properties of the new session and return it
               session.setNew(true);
               session.setValid(true);
               session.setCreationTime(System.currentTimeMillis());
               session.setMaxInactiveInterval(this.maxInactiveInterval);
               String sessionId = generateSessionId();//使用md5算法生成sessionId
               String jvmRoute = getJvmRoute();
               // @todo Move appending of jvmRoute generateSessionId()???
               if (jvmRoute != null) {
                   sessionId += '.' + jvmRoute;
                   session.setId(sessionId);
               }
               session.setId(sessionId);
               return (session);
           }    

StandardManager：
不用配置元素，当Tomcat正常关闭，重做或Web应用重新加载时，它会将內存中的Session序列化到Tomcat目录下的/work/Catalina/host_name/webapp_name/SESSIONS.ser文件中。當Tomcat重启或应用加载完成后，Tomcat会将文件中的Session重新还原到內存中。如果突然終止该服务器，則所有Session都将丟失，因为StandardManager沒有机会实现存盘处理。

Session的共享：
    1：Servlet自己的共享方案，如tomcat修改web.xml 中的Cluste

    2： 自己进行持久化一般自己处理后放在redis或者memcached

    3： 自己通过在不同Servlet间发送请求互相通知session变化  