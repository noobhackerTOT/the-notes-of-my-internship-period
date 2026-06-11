# summary

# 流量分析练习答案总结

> 来源: https://www.malware-traffic-analysis.net/2026/02/28/index.html
> 工具: Wireshark, 分析 NetSupport Manager RAT 通信

---

## 环境参数

|参数|值|
| ------------| ------------------------------------------|
|LAN 网段|10.2.28.0/24|
|域名|easyas123.tech|
|AD 环境名|EASYAS123|
|域控 (DC)|10.2.28.2 — EASYAS123-DC|
|网关|10.2.28.1|
|广播地址|10.2.28.255|
|C2 威胁 IP|45.131.214.85:443 (NetSupport Manager RAT)|
|攻击开始时间|2026-02-28 19:55 UTC|

---

## 受害主机详情

|项目|值|
| --------------| -----------------|
|IP 地址|10.1.28.88|
|MAC 地址|00:19:d1:b2:4d:ad|
|主机名|DESKTOP-TEYQ2NR|
|Windows 用户名|brolf|
|用户全名|Becka Rolf|

---

## 具体分析步骤

### 步骤 1: 定位受害主机 IP

- 在 Wireshark 中筛选与 C2 地址 `45.131.214.85` 通信的流量
- 源 IP 列为 `10.1.28.88`，确定该内网 IP 即为受害主机

### 步骤 2: 获取 MAC 地址和主机名

- 使用 Wireshark 过滤表达式: `nbns`
- **NBNS（NetBIOS Name Service）**  是 Windows 早期网络中用于**主机名解析**的协议。

  它的作用类似于 DNS，但只用于 NetBIOS 名称。
- 在 NBNS 协议响应中查看帧详情
- 获取主机名: `DESKTOP-TEYQ2NR`
- 获取 MAC 地址: `00:19:d1:b2:4d:ad`

### 步骤 3: 获取 Windows 用户账号名

- 使用 Wireshark 过滤表达式: `kerberos.CNameString`
- **Kerberos** 是一种网络身份认证协议，用来在不传输明文密码的情况下验证用户身份。
- 在 Wireshark 里，**​`kerberos.CNameString`​** 是 Kerberos 协议字段中的一个过滤字段（Display Filter Field）。

  它表示：

  > **Client Name String（客户端名称）**
  >

  也就是发起 Kerberos 认证请求的用户或主体（Principal）的名称。
- 黄金凭据tgt 白银票据tgts
- 选择任意结果帧，展开帧详情
- 找到 `CNameString`​ 字段值: `brolf`
- **技巧**: 可将 `CNameString` 添加为 Wireshark 列，后续分析无需重复展开帧详情

### 步骤 4: 推断并确认用户全名

- 用户账号 `brolf` 格式为「名首字母 + 姓」→ `b` + `Rolf`
- 使用 Wireshark 的 **Find Packet** 功能 (Edit 菜单)
- 搜索区分大小写的字符串 `Rolf`
- 在包详情中找到用户全名: **Becka Rolf**

---

## 所用 Wireshark 过滤器汇总

|目的|过滤器|
| ----------------| --------------------------------------|
|查看 C2 通信|`ip.addr == 45.131.214.85`|
|获取主机名和 MAC|`nbns`|
|获取用户账号名|`kerberos.CNameString`|
|搜索包内容|Find Packet → 字符串查找 (区分大小写)|

## 关键技巧

- 将 `kerberos.CNameString` 设为 Wireshark 列，可在多个 pcap 中快速定位用户名
- 用户名格式为「首字母+姓」时，可用 Find Packet 搜索姓氏来获取全名
