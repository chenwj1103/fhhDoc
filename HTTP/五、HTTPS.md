### HTTP的缺点
	到现在为止我们都了解HTTP的优秀的地方，然而HTTP并非只有好的一面，事物都是具有两面性的，HTTP的主要不足如下：
	*明文通信，内容可能被窃听
	*不验证通讯fangs身份，有可能被伪装
	*无法证明报文的完整性，所以有可能遭篡改


### http+加密+认证+完整的保护=https
https并非是应用层的一总新协议，只是http通信接口部分用ssl和tls协议替代而已。通常http直接和tcp通信，当使用ssl时责演变成先和ssl通信，再由ssl和tcp通信。https就是披着ssl协议外壳的http。

HTTP协议中的请求和响应不会对通讯进行确认。也就行说存在“服务器是否就是发送请求中URI真正指定的主机，返回的响应是否真的返回到实际提出请求的客户端”由于HTTP不存在确认通信方的步骤，任何人都可以发起请求，不管对方是谁都返回一个响应。这个条件下，无法确认客户端或者服务端是否伪装，及是否有访问权限。

HTTP无法确定通信方，但是SSL可以，SSL不仅提供加密，而且还提供了一种称为证书的手段用于确定对方。证书由值得信任的第三方机构颁发，用以证明服务端和客户端身份。（证书难以伪造）


#### 加密方式

	*共享密匙:加密和解密用用同一个密匙的方式成为共享密匙也叫对称密匙加密。（如何发送密匙是一个问题）
	
	*公开密匙：公开密匙使用一个非对称密匙，一个是私有密匙一个是公开密匙。
	
	HTTPS采用混合加密机制，采用共享密匙和公开密匙混用机制，交换密匙环节使用公开加密方式，之后建立报文阶段使用共享密匙加密。

	公开密匙本身不是被伪装的问题，交给数字证书认证机构。
	
	2011年7月，荷兰一家认证机构被入侵。


IETF以SSL3为准制订了TLS1.0/1.1/1.2  主流1.0 


#### 对比

|HTTP|HTTPS|
|---|---|
|应用层HTTP|应用层HTTP|
| |SSL| 
|TCP|TCP|
|IP|IP|

### 由自认证机构颁发的证书成为自签名证书
	OpenSSL这套开源成勋，每人人都可以构建一套数据自己的认证机构，给自己颁发证书。
	java keytool

关于SSl链接可以确定做了三件事，网上说法有一些出入，但是可以确定做了三件事
	1.保护数据的算法达成一致，确认协议版本号
	2. 确立加密密钥
	3. 对客户端进行认证
