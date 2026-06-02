# security1

一、Windows 关键事件 ID

---

事件ID                  含义                    关注点

4624                    登录成功                Account Name、Source Network
Address、Logon
Type（2本地/3网络/7解锁/10
RDP/11缓存）

4625                    登录失败                大量出现 → 暴力破解或密码攻击

4720                    创建用户                攻击者可能新建账户

4732                    添加组成员              重点监控加入
Administrators、Remote Desktop
Users

4672                    特殊权限分配            管理员登录成功（常跟在4624后）

---

二、Linux 关键日志（/var/log/auth.log）

命令/内容 含义

grep \"Failed password\" SSH 爆破尝试

grep \"Accepted password\" SSH 登录成功，需排查来源IP是否异常

grep sudo sudo 提权操作（如执行 /bin/bash → 获取root）

三、SMB / 网络登录

Logon Type 3 → 网络登录（SMB、NAS、文件服务器）

可疑现象：凌晨 + 境外IP + 4624(Logon Type 3)

四、RDP 入侵攻击链

大量 4625 (Logon Type 10) → 一次 4624 (Logon Type 10) → 4672 →
攻击者已获得管理员远程桌面权限

五、Sysmon（推荐安装）

Event ID 含义 用途

1 进程创建 记录 cmd.exe、powershell.exe 等

3 网络连接 发现进程连接可疑IP（C2通信）

11 文件创建 检测勒索软件生成加密文件

六、Wireshark 常用过滤器

过滤器 用途

dns DNS 查询

smb2 SMB/NAS 排障

http HTTP 流量

tcp.port==3389 RDP

tcp.port==22 SSH

tcp.flags.syn==1 &amp;&amp; tcp.flags.ack==0 端口扫描（SYN）

‍
