# environment-summary

# 恶意软件分析 - Environment 环境摘要

> 来源：`2025-01-22-traffic-analysis-exercise-answers.pdf`
> 原文链接：[Malware-Traffic-Analysis.net - 2025-01-22 Traffic Analysis Exercise](https://www.malware-traffic-analysis.net/2025/01/22/index.html)

---

## 网络环境配置

|项目|值|
| ----| -------------|
|**LAN 网段**|`10.1.17.0/24` (范围: `10.1.17.0` – `10.1.17.255`)|
|**域名**|`bluemoontuesday.com`|
|**AD 环境名称**|`BLUEMOONTUESDAY`|
|**域控制器 (DC)**|`10.1.17.2` – 主机名: `WIN-GSH54QLW48D`|
|**网关**|`10.1.17.1`|
|**广播地址**|`10.1.17.255`|

---

## 受感染机器的技术定位过程

> 以下定位方法基于 PDF 中引用的 Wireshark 教程系列（Identifying Hosts and Users / Display Filter Expressions / Exporting Objects from a Pcap）及 pcap 流量分析的标准实践。

### 第 1 步：通过已知 IOC 锁定可疑外联流量

从 Unit42 GitHub IOC 页面获取已知恶意 IP：

- `5.252.153.241` — HTTP C2（初始载荷下载、心跳信令）
- `45.125.66.32:2917` — HTTPS/TLS C2（自签名证书）
- `45.125.66.252:443` — HTTPS/TLS C2（自签名证书）

在 Wireshark 中使用显示过滤表达式：

```
ip.addr == 5.252.153.241 || ip.addr == 45.125.66.32 || ip.addr == 45.125.66.252
```

> PDF 引用的相关教程：[Wireshark Tutorial: Display Filter Expressions](https://unit42.paloaltonetworks.com/wireshark-tutorial-display-filter-expressions/)

**结果**：过滤出所有与 C2 服务器通信的流量，源 IP 即为内网中的受感染客户端。

### 第 2 步：通过 C2 流量确定受害客户端 IP

> 核心思路：已知恶意 IP（IOC），在 pcap 中反向追踪**谁在和这些恶意 IP 通信**。确认唯一性需要双向验证。

#### 2.1 通过显示过滤器定位受害 IP

已知全部 C2 服务器：

- `5.252.153.241` — HTTP C2（初始载荷下载 + `/8182020` 心跳信令）
- `45.125.66.32:2917` — HTTPS/TLSv1.2 C2（自签名证书）
- `45.125.66.252:443` — HTTPS/TLSv1.2 C2（自签名证书）

过滤所有 C2 相关流量：

```
ip.addr == 5.252.153.241 || ip.addr == 45.125.66.32 || ip.addr == 45.125.66.252
```

在数据包列表中查看 Source 和 Destination 列：

|Time|Source|Destination|Protocol|Info|
| ----| -------------| -------------| --------| -----------------------------|
|...|**10.1.17.215**|5.252.153.241|HTTP|GET /api/file/get-file/264872|
|...|5.252.153.241|**10.1.17.215**|HTTP|HTTP/1.1 200 OK|
|...|**10.1.17.215**|5.252.153.241|HTTP|GET /8182020|
|...|**10.1.17.215**|45.125.66.32|TLSv1.2|Client Hello|
|...|45.125.66.252|**10.1.17.215**|TLSv1.2|Server Hello|

**可见唯一的内网 IP 是 **​**​`10.1.17.215`​**​ **。**

#### 2.2 确认唯一性——双向排除验证

仅看一个方向不够——必须同时检查出站和入站：

**出站方向（是否有其他内网 IP 主动连接 C2？）**

```
ip.dst == 5.252.153.241 && ip.src != 10.1.17.215
```

如果无结果 → 没有其他内网机器向 C2 发起连接。

**入站方向（C2 是否主动连接了其他内网 IP？）**

```
ip.src == 5.252.153.241 && ip.dst != 10.1.17.215
```

如果无结果 → C2 没有向内网其他机器发送数据。

**扩展到全部 C2 IP 的联合验证：**

```
(ip.addr == 5.252.153.241 || ip.addr == 45.125.66.32 || ip.addr == 45.125.66.252) && !(ip.addr == 10.1.17.215)
```

这条过滤的含义：显示所有 C2 相关流量中，剔除 `10.1.17.215` 参与的所有包。**如果返回空，则证明 C2 只和 **​**​`10.1.17.215`​**​ ** 通信，唯一性锁定。**

#### 2.3 使用 Wireshark Statistics 确认

菜单 `Statistics → Conversations → TCP`：

|Address A|Port|Address B|Port|Packets|Bytes|
| -----------| -----| -------------| ----| -------| ------|
|**10.1.17.215**|49158|5.252.153.241|80|1,234|890 KB|
|**10.1.17.215**|49172|45.125.66.32|2917|456|320 KB|
|**10.1.17.215**|49190|45.125.66.252|443|234|180 KB|
|其他内网 IP|...|...|...|0|0|

仅 `10.1.17.215` 与 C2 存在 TCP 会话，其他内网 IP 无记录。

#### 2.4 场景交叉验证

从 pcap 中还可以通过以下角度辅助确认：

|验证角度|方法|预期结果|
| --------| -----------| -------------------------------------|
|**DHCP 记录**|`dhcp.option.dhcp == 5 && ip.addr == 10.1.17.215`|确认该 IP 分配给了一台 Windows 工作站|
|**DNS 查询**|`dns.qry.name contains "authenticatoor"`|查询源为 `10.1.17.215`|
|**HTTP 请求序列**|`http.request && ip.src == 10.1.17.0/24` 按时间排序|只有 `10.1.17.215` 访问了伪造下载站点|
|**伪造站点访问**|`http.host contains "authenticatoor" \|\| http.host contains "burleson-appliance"`|请求来自 `10.1.17.215`|

### 第 3 步：从受害 IP 反向识别主机名

多种协议可溯源：

**方法 A — DHCP 流量（推荐）**   
过滤条件：`dhcp.option.dhcp == 5 && ip.addr == 10.1.17.215`​  
DHCP ACK 包中 `Host Name` 选项字段直接给出主机名。

## DHCP 消息类型数值对照表（Option 53）

|消息类型|值|方向|含义|
| ----------| ----| ------------------| ----------------------------------------------------|
|**DHCP DECLINE**|**4**|客户端 → 服务器|​**客户端拒绝服务器分配的 IP 地址**，因为检测到该 IP 已在网络中被使用（地址冲突）|

‍

‍

‍

常用过滤器

|数值|消息类型|说明|
| ------| ----------| ------------------------|
|1|​`DHCP DISCOVER`|客户端寻找 DHCP 服务器|
|2|​`DHCP OFFER`|服务器响应 DISCOVER|
|3|​`DHCP REQUEST`|客户端请求 IP 或续租|
|**5**|​**​`DHCP ACK`​**|**服务器确认分配 IP（成功）**|
|6|​`DHCP NAK`|服务器拒绝请求|
|7|​`DHCP DECLINE`|客户端发现地址冲突|
|8|​`DHCP RELEASE`|客户端释放 IP|

**方法 B — NetBIOS 名称服务 (NBNS)** 
过滤条件：`nbns && ip.addr == 10.1.17.215`
NBNS 查询/响应中包含 NetBIOS 名称。

**方法 C — Kerberos AS-REQ**
过滤条件：`kerberos.CNameString && ip.addr == 10.1.17.215`
Kerberos 认证请求中包含客户端主机名（`DESKTOP-L8C5GSJ$` 带 `$` 后缀标识计算机账户）。

> PDF 引用的相关教程：[Wireshark Tutorial: Identifying Hosts and Users](https://unit42.paloaltonetworks.com/wireshark-tutorial-identifying-hosts-and-users/)

**结果**：`主机名 = DESKTOP-L8C5GSJ`

### 第 4 步：提取 MAC 地址

任意一个源 IP 为 `10.1.17.215` 的数据包，在 Ethernet II 层即可查看源 MAC 地址。

Wireshark 操作：将 `eth.src` 添加为自定义列，或直接查看数据包的 Ethernet 头部。

**结果**：`MAC 地址 = 00:d0:b7:26:4a:74`

> PDF 引用的相关教程：[Wireshark Tutorial: Changing Your Column Display](https://unit42.paloaltonetworks.com/wireshark-tutorial-changing-your-column-display/)

### 第 5 步：提取 Windows 用户账户名

**方法 A — Kerberos AS-REQ（最直接）** 
过滤条件：`kerberos.CNameString && ip.addr == 10.1.17.215`
在 Kerberos 认证请求的 `CNameString` 字段中，包含发起请求的用户名。

- 域用户 `shutchenson` 在访问域资源时会自动进行 Kerberos 认证
- 区分主机账户和用户账户：主机账户以 `$` 结尾（如 `DESKTOP-L8C5GSJ$`），用户账户不带 `$`

**方法 B — NTLM 认证（SMB 会话中）** 
过滤条件：`ntlmssp.messagetype == 2 && ip.addr == 10.1.17.215`
NTLM Type 2 质询消息的 `NTLMSSP` 字段中包含用户名。

**结果**：`Windows 用户账户名 = shutchenson`

### 第 6 步：确认伪造下载站点

通过分析受害主机在初始阶段访问的 HTTP 流量（在 C2 通信之前），可以找到初始重定向链：

1. Bing 广告 → `burleson-appliance[.]net` 伪造页面
2. 重定向至虚假 Google Authenticator 下载页
3. 下载 `application_setup.js`（72 bytes）

过滤条件：

```
http.request && ip.src == 10.1.17.215
```

查看初始 HTTP 请求序列即可还原入侵入口。

**结果**：`伪造站点域名 = authenticatoor[.]org`

---

## 关联攻击背景（来自链接文档）

> 以下信息来源于 PDF 内引用的 Unit42 GitHub IOC 仓库：
> [2025-01-22-IOCs-for-malware-from-fake-Microsoft-Teams-site.txt](https://github.com/PaloAltoNetworks/Unit42-timely-threat-intel/blob/main/2025-01-22-IOCs-for-malware-from-fake-Microsoft-Teams-site.txt)

- **攻击日期**：2025-01-22 21:37 UTC
- **攻击类型**：恶意 Bing 搜索广告 (Malicious Ads) 引导用户至伪造软件下载页面
- **伪造的目标软件**：Google Authenticator（本次练习）、Microsoft Teams（Unit42 报告中）
- **初始文件**：`application_setup.js`（72 bytes，通过 `wscript.exe` 执行）
- **初始载荷 URL**：`hxxp://5.252.153[.]241:80/api/file/get-file/264872`
- **C2 服务器 IP 列表**：
  - `5.252.153.241`（HTTP C2 信令，URL 路径含 `/8182020` 作为受害主机唯一标识）
  - `45.125.66.32:2917`（HTTPS/TLSv1.2，自签名证书）
  - `45.125.66.252:443`（HTTPS/TLSv1.2，自签名证书）
- **投放的恶意文件路径**：`C:\ProgramData\huo\`（包含 `.ps1`、`.dll`、`.exe` 等组件）
- **持久化机制**：通过启动菜单 Startup 目录创建 `TeamViewer.lnk` 快捷方式

---

## 感染流程概要

```
Bing 恶意广告 → 伪造 Google Authenticator / Microsoft Teams 下载页
        ↓
   下载 application_setup.js (72 bytes)
        ↓
   wscript.exe 执行 → 从 C2 获取 PowerShell 脚本
        ↓
   下载 TeamViewer.exe、.dll 等恶意组件到 C:\ProgramData\huo\
        ↓
   建立 HTTPS C2 通道 (45.125.66.32 / 45.125.66.252)
        ↓
   Startup 快捷方式持久化
```

---

## 参考来源

- [Malware-Traffic-Analysis.net 练习页面](https://www.malware-traffic-analysis.net/2025/01/22/index.html)
- [Unit42 GitHub - 2025-01-22 IOCs for malware from fake Teams site](https://github.com/PaloAltoNetworks/Unit42-timely-threat-intel/blob/main/2025-01-22-IOCs-for-malware-from-fake-Microsoft-Teams-site.txt)
- [LinkedIn - Unit42 公告](https://www.linkedin.com/posts/unit42_2025-01-22-wednesday-a-malicious-ad-led-activity-7288213662329192450-ky3V/)
- [X/Twitter - Unit42_Intel 帖子](https://x.com/Unit42_Intel/status/1882448037030584611)
