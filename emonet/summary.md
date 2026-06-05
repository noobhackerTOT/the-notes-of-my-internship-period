# Emotet Epoch 3 感染 + Spambot 流量分析结果

> **pcap 文件**: `2019-11-27-Emotet-epoch-3-infected-Windows-client-as-spambot.pcap`
> **来源**: Malware-Traffic-Analysis.net
> **捕获时长**: 约 361 秒（~6 分钟）

---

## 1. 环境概览

| 项目 | 值 |
|------|-----|
| **受害主机 IP** | `10.11.27.102` |
| **DNS/网关** | `10.11.27.1` |
| **网段** | `10.11.27.0/24` |
| **OS 指纹** | Windows NT 6.1 (Windows 7 / Server 2008 R2) |

---

## 2. Emotet C2 通信

### C2 服务器

| C2 服务器 | 端口 | 协议 | URL 路径示例 |
|-----------|------|------|-------------|
| `82.145.43.153` | 8080 | HTTP | `/forced/site/arizona/merge/` |
| `92.119.123.10` | 8080 | HTTP | `/enable/scripts/arizona/merge/` |
| `222.239.249.166` | 443 | HTTP (raw TCP, 非 TLS) | `/sFZSdbM0xoXf` |

### HTTP 请求特征
- **路径含 `arizona`** — Emotet epoch 3 的 campaign 标识
- **User-Agent**: `Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; ...)`
- 每个请求使用不同随机路径规避签名检测

### Payload 下载

| 响应帧 | 源 IP | 大小 | 用途 |
|--------|-------|------|------|
| #8526 | 82.145.43.153 | 339,684 B | Emotet 核心 DLL/配置 |
| #10856 | 82.145.43.153 | 339,684 B | 同上 |
| #13092 | 92.119.123.10 | 171,028 B | 模块加载 |
| #15313 | 92.119.123.10 | 171,156 B | 模块加载 |
| #17826 | 92.119.123.10 | 170,996 B | 模块加载 |
| **#24253** | 92.119.123.10 | **3,380,884 B** | 🚨 **Spam 模块** |
| **#34942** | 92.119.123.10 | **2,198,580 B** | 🚨 **Spam 模块/载荷** |

---

## 3. Spambot 行为

### 总体统计

| 指标 | 数值 |
|------|------|
| 连接的 SMTP 服务器 | **177 个** 唯一目标 |
| SMTP 帧总数 | 1,812 帧 |
| SMTP 命令总数 | 522 条 |
| TLS 加密连接数 | 374 次 Client Hello |
| 端口 | 25 (SMTP)、465 (SMTPS)、587 (Submission) |

### 被盗凭据

```
用户名: uhrcjinja@uhrc.ug
密码:   t3st@1234
```

### 垃圾邮件目标

| 类型 | 地址 |
|------|------|
| FROM (伪造发件人) | `anjelo.femi@in.cpm-int.com` |
| FROM (伪造发件人) | `b.hussin@brj-sy.com` |
| FROM (被盗账户) | `uhrcjinja@uhrc.ug` |
| TO (攻击目标) | `overseahtl_payment@trip.com` |
| TO (攻击目标) | `importaciones@dismaconcobre.com` |
| TO (攻击目标) | `victorvila@pereventura.com` |

### 特征
- 伪造 EHLO 主机名: `[10.0.0.121]`
- 使用 **AUTH PLAIN** base64 认证
- 发送含 **.docx 恶意附件** 的钓鱼邮件
- **并行连接**多台 SMTP 服务器（多线程异步 I/O）

---

## 4. IOC 汇总

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
