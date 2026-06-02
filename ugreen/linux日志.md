# linux日志

# linux日志

# linux日志

一、Linux日志体系概览

---

日志类别            文件路径（Ubuntu示例）                          主要记录内容                                      典型应用场景

‍

认证日志            /var/log/auth.log

CentOS:             SSH登录、sudo、su、用户创建/密码修改、PAM认证   检测爆破、异常登录、提权行为
/var/log/secure

系统日志            /var/log/syslog

CentOS:             系统服务启动/错误、守护进程、网络服务、cron等   NAS排障首选，查看整体运行状态
/var/log/messages

内核日志            dmesg -T 或 /var/log/kern.log                   驱动、磁盘、RAID、网卡、USB、内核异常             磁盘I/O错误、RAID降级、SATA链路问题

启动日志            /var/log/boot.log                               开机过程、服务启动、驱动加载                      启动慢、服务无法启动

定时任务日志        grep CRON /var/log/syslog

CentOS:             cron任务执行记录                                排查备份、rsync、快照脚本
/var/log/cron

Samba日志           /var/log/samba/log.smbd 等                      SMB用户认证、共享访问、文件操作、权限错误         解决访问拒绝、共享异常

NFS日志             journalctl -u nfs-server 或 grep nfs            挂载、权限、连接异常                              处理 mount denied、stale file handle
/var/log/syslog

统一日志            journalctl                                      systemd管理的所有日志，可过滤服务、启动、内核等   现代Linux首选，替代部分传统文本日志

审计日志            /var/log/audit/audit.log                        文件访问、命令执行、权限变更、用户行为            安全审计、合规要求

---

二、NAS工程师排查优先级（从高到低）

dmesg / kern.log -- 硬件与磁盘错误第一现场

syslog / messages -- 系统与服务整体状态

auth.log / secure -- 认证问题

Samba / NFS日志 -- 共享服务访问问题

journalctl -- 现代统一查看方式

三、典型故障排查流程（以"NAS变慢"为例）

bash

dmesg -T \# 检查磁盘/RAID错误

journalctl -p err \# 查看系统错误级别日志

tail -f /var/log/syslog \# 实时跟踪系统日志

iostat -x 1 \# 观察磁盘IO

sar -n DEV 1 \# 监控网络设备流量

重点确认：磁盘错误、RAID降级、网卡异常、文件系统错误。

四、关键关键词（出现即预警）

类别 关键词

存储 I/O error, reset link, timeout, sense key, medium error, mdadm,
raid degraded

认证 Failed password, Invalid user, authentication failure, sudo:
session opened

服务 NT_STATUS_ACCESS_DENIED, mount denied, stale file handle

五、面试常见问答

问：Linux里除了auth.log还有哪些重要日志？

答：

auth.log / secure -- 认证与登录

syslog / messages -- 系统与服务日志

kern.log / dmesg -- 内核与硬件日志

audit.log -- 安全审计日志

cron -- 定时任务日志

samba / nfs 相关日志 -- 共享服务日志

journalctl -- systemd统一日志

补充（存储/NAS场景）：

在存储和NAS场景下，我最常关注的是 dmesg、kern.log、syslog 和 Samba
日志，因为它们能快速定位磁盘、RAID、网络和共享服务问题。
