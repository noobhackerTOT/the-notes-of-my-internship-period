# kerberos 认证流程

Kerberos 是现代 Windows 域环境中的​**默认身份认证协议**，理解它对网络安全、域渗透、流量分析和应急响应都非常重要。

## Kerberos 是什么？

Kerberos 由 Massachusetts Institute of Technology 开发，微软将其作为 Active Directory 域环境的默认认证机制。

目标：

- 不在网络上传输明文密码
- 支持单点登录（SSO）
- 双向认证
- 防止重放攻击

---

## Kerberos 的核心角色

### Client（客户端）

用户电脑：

```text
WIN10-PC
```

---

### KDC（密钥分发中心）

通常运行在域控制器（DC）上。

KDC 包含：

```text
Authentication Server (AS)
Ticket Granting Server (TGS)
```

---

### Service（服务）

用户最终访问的资源：

```text
文件服务器
SQL Server
Web Server
Exchange
```

---

## 认证流程

可以记成：

```text
AS → TGS → Service
```

---

### 第一阶段：AS-REQ

用户登录：

```text
user: alice
password: ********
```

客户端向 KDC 发送：

```text
AS-REQ
```

Wireshark 过滤：

```wireshark
kerberos.msg_type == 10
```

---

### 第二阶段：AS-REP

KDC 返回：

```text
TGT
(Ticket Granting Ticket)
```

Wireshark：

```wireshark
kerberos.msg_type == 11
```

此时：

```text
用户获得 TGT
```

以后不用再输密码。

---

### 第三阶段：TGS-REQ

访问共享目录：

```text
\\fileserver\share
```

客户端拿着 TGT 请求：

```text
TGS-REQ
```

Wireshark：

```wireshark
kerberos.msg_type == 12
```

---

### 第四阶段：TGS-REP

KDC 返回：

```text
Service Ticket
```

Wireshark：

```wireshark
kerberos.msg_type == 13
```

---

### 第五阶段：AP-REQ

客户端向目标服务器发送：

```text
AP-REQ
```

Wireshark：

```wireshark
kerberos.msg_type == 14
```

---

### 第六阶段：AP-REP

服务器验证成功：

```text
AP-REP
```

Wireshark：

```wireshark
kerberos.msg_type == 15
```

认证完成。

---

## 一张图理解

```text
User
 │
 │ AS-REQ
 ▼
KDC(AS)
 │
 │ AS-REP(TGT)
 ▼
User
 │
 │ TGS-REQ(TGT)
 ▼
KDC(TGS)
 │
 │ TGS-REP(Service Ticket)
 ▼
User
 │
 │ AP-REQ
 ▼
Server
 │
 │ AP-REP
 ▼
Success
```

---

## Wireshark 中最重要的字段

### 用户名

过滤：

```wireshark
kerberos.CNameString
```

常见：

```text
alice
administrator
svc_backup
```

例如：

```text
kerberos.CNameString: administrator
```

---

### 服务名称（SPN）

过滤：

```wireshark
kerberos.SNameString
```

例如：

```text
cifs
host
ldap
http
mssqlsvc
```

---

### 域名

过滤：

```wireshark
kerberos.realm
```

例如：

```text
CORP.LOCAL
AD.COMPANY.COM
```

---

## 安全分析中的重点

### Kerberoasting

攻击者请求服务票据：

```text
TGS-REQ
```

获取：

```text
TGS-REP
```

离线爆破服务账户密码。

常见目标：

```text
MSSQLSvc
HTTP
CIFS
```

在 Wireshark 中会看到大量：

```wireshark
kerberos.msg_type == 13
```

---

### AS-REP Roasting

目标账户关闭预认证：

```text
Do not require Kerberos preauthentication
```

攻击者直接请求：

```text
AS-REP
```

然后离线爆破。

过滤：

```wireshark
kerberos.msg_type == 11
```

---

### 黄金票据（Golden Ticket）

伪造：

```text
krbtgt
```

账户签发的 TGT。

攻击者可以伪装成：

```text
administrator
```

访问整个域。

相关实体：Mimikatz

---

### 白银票据（Silver Ticket）

伪造：

```text
Service Ticket
```

只针对某个服务：

```text
CIFS
MSSQL
HTTP
```

无需联系域控。

---

## 流量分析时常用过滤器

全部 Kerberos：

```wireshark
kerberos
```

查看用户名：

```wireshark
kerberos.CNameString
```

查看服务：

```wireshark
kerberos.SNameString
```

查看 TGT 请求：

```wireshark
kerberos.msg_type == 10
```

查看 TGS 请求：

```wireshark
kerberos.msg_type == 12
```

查看服务票据：

```wireshark
kerberos.msg_type == 13
```

---

## 面试高频问题

**Q：Kerberos 和 NTLM 的区别？**

|Kerberos|NTLM|
| --------------------| ---------------------|
|默认用于 AD 域|较老协议|
|基于票据（Ticket）|Challenge-Response|
|支持 SSO|不支持真正 SSO|
|速度快|较慢|
|更安全|更容易被 Relay 利用|

简单记忆：

```text
NTLM = Hash认证
Kerberos = Ticket认证
```

如果你正在学域安全，建议下一步把 **Kerberos + LDAP + SMB + NTLM** 放在一起抓包分析。很多真实攻击链都会出现：

```text
Kerberos登录
    ↓
LDAP查询域信息
    ↓
SMB访问共享
    ↓
PsExec横向移动
```

能在 Wireshark 中识别这四类流量，已经具备较好的 Windows 域流量分析能力。
