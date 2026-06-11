# ssdp

## SSDP 是什么？

**SSDP（Simple Service Discovery Protocol）**  是一种设备发现协议。

简单来说：

> 用于让局域网设备自动发现彼此。

例如：

- 智能电视
- 路由器
- NAS
- 打印机
- Xbox
- Windows

都会使用 SSDP。

---

## 它属于什么体系？

SSDP 是：

```text
UPnP（Universal Plug and Play）
```

的一部分。

流程类似：

```text
电脑
 ↓
谁是打印机？
 ↓
打印机回应
 ↓
建立连接
```

---

## 默认端口

```text
UDP 1900
```

组播地址：

```text
239.255.255.250
```

IPv6：

```text
FF02::C
```

---

## Wireshark 过滤

查看 SSDP：

```wireshark
ssdp
```

或者：

```wireshark
udp.port == 1900
```

---

## 常见报文

### M-SEARCH

设备搜索：

```http
M-SEARCH * HTTP/1.1
HOST:239.255.255.250:1900
MAN:"ssdp:discover"
MX:3
ST:ssdp:all
```

意思：

```text
局域网里有谁？
请回复我
```

---

### NOTIFY

设备主动广播：

```http
NOTIFY * HTTP/1.1
HOST:239.255.255.250:1900
NT:upnp:rootdevice
NTS:ssdp:alive
```

意思：

```text
我上线了
我是一个UPnP设备
```

---

## 在 Wireshark 中长什么样？

你会看到：

|Src|Dst|Info|
| --------------| -----------------| -----------------|
|192.168.1.10|239.255.255.250|M-SEARCH|
|192.168.1.1|239.255.255.250|NOTIFY|
|192.168.1.20|192.168.1.10|HTTP/1.1 200 OK|

---

## 为什么分析恶意流量时要过滤掉 SSDP？

回到你之前看到的过滤器：

```wireshark
(http.request or tls.handshake.type eq 1)
and !(ssdp)
and ip.addr eq 45.131.214.85
```

其中：

```wireshark
!(ssdp)
```

表示：

```text
排除 SSDP 流量
```

原因是 SSDP 很吵。

一个普通 Windows 电脑可能每分钟发很多：

```text
M-SEARCH
NOTIFY
```

这些和：

```text
NetSupport RAT
Cobalt Strike
Emotet
```

之类的恶意通信通常没关系。

分析师会把它们过滤掉，减少噪声。

---

## SSDP 的安全问题

虽然 SSDP 本身是正常协议，但存在一些风险：

### 1. UPnP 暴露端口

很多家用路由器：

```text
开启UPnP
↓
软件自动开端口
↓
外网可访问
```

NAS 用户经常遇到。

---

### 2. DDoS 反射放大

攻击者：

```text
伪造受害者IP
↓
向大量SSDP设备发请求
↓
设备回复给受害者
```

形成：

```text
SSDP Amplification Attack
```

放大倍数可达数十倍。

---

### 3. 资产发现

红队进入内网后：

```text
发送M-SEARCH
```

就能快速发现：

- NAS
- 摄像头
- 路由器
- 打印机
- IoT设备

---

## 在 NAS 环境里很常见

如果你抓绿联、群晖等 NAS 的包，经常会看到：

```text
UDP 1900
NOTIFY
M-SEARCH
```

因为 NAS 会向局域网广播：

```text
我是NAS
快来发现我
```

方便 Windows 资源管理器、手机 App 自动找到设备。

---

### 面试高频记忆

|项目|内容|
| ---------------| -----------------------------------|
|全称|Simple Service Discovery Protocol|
|属于|UPnP|
|端口|UDP 1900|
|地址|239.255.255.250|
|作用|自动发现设备|
|Wireshark过滤|​`ssdp`|
|常见报文|M-SEARCH、NOTIFY|
|安全风险|UPnP暴露、DDoS放大、资产发现|

做 PCAP 分析时，如果你发现大量 `M-SEARCH`​ 和 `NOTIFY`​，通常先判断为正常局域网发现流量；而像你正在分析的 ​**45.131.214.85 上的 HTTP POST 心跳流量**​，与 SSDP 的行为模式完全不同，所以分析师会专门用 `!(ssdp)` 把它们排除掉。
