# Samba 如何工作

# Samba 如何工作

# Samba 如何工作

Samba 如何工作？

Samba 依赖两个核心守护进程来协同工作：

smbd：核心服务进程。负责处理来自客户端的文件、打印服务请求和用户身份验证，是
Samba 工作的关键。它默认监听 TCP 445 端口。

nmbd：NetBIOS 名称解析进程。负责将 Samba 服务器的主机名解析为 IP
地址，并支持网络浏览功能，让服务器能在"网上邻居"（或网络）中被发现。它主要使用
UDP 137/138 和 TCP 139 端口。

如果 nmbd 服务没有启动，用户将无法通过主机名浏览到该服务器，但可以通过
IP 地址直接访问共享资源。

核心配置文件：smb.conf

Samba
的所有配置都通过一个文件管理：/etc/samba/smb.conf。这个文件主要由两部分构成：

\[global\] 部分：用于设置全局参数，如工作组、安全模式等，影响整个 Samba
服务。

共享定义部分：形式如 \[sharename\]，用于定义一个个具体的共享资源。

关键配置参数说明

参数 作用 典型值示例 备注

workgroup 指定服务器要加入的 Windows 工作组名称。 WORKGROUP
与局域网内其他 Windows 机器保持一致。

security 定义安全认证模式。 user / share user 模式需用户密码验证，share
模式则为匿名访问。

passdb backend 指定 Samba 用户密码的存储后端。 tdbsam tdbsam
是目前常用的本地密码数据库。

path 指定要共享的本地目录的绝对路径。 /srv/samba/share 目录必须先存在。

browsable 控制共享资源是否在客户端"网络"视图中可见。 yes / no 设置为 no
是隐藏共享的一种方式。

read only 控制共享是否只读。 yes / no yes 表示只读，no 表示可读写。

guest ok 是否允许访客（无需密码）访问。 yes / no 通常与 security = user
模式配合使用。

valid users 指定允许访问此共享的用户或组列表。 \@smbgroup 支持用户列表
user1 user2 或组 \@groupname。

create mask 设定新建文件的权限掩码。 0664 相当于 Linux 的 umask 设置。

directory mask 设定新建目录的权限掩码。 0775 相当于 Linux 的 umask
设置。

🛠️ 主要服务与工具

Samba 软件包包含以下关键服务和工具：

服务/工具 描述

smbd / nmbd Samba 的核心守护进程，必须运行才能提供文件共享服务。

smbclient 命令行下的 FTP 风格客户端，用于访问 SMB/CIFS 资源，功能强大。

testparm 配置验证工具。用于检查 smb.conf 文件的语法正确性。

smbpasswd 管理 Samba 独立服务器用户密码的工具，用于添加或修改 Samba
用户。

重点关注日志：

硬盘健康日志
(S.M.A.R.T.)：这是硬盘的"体检报告"，包含重分配扇区计数、当前待映射扇区数、无法校正的扇区总数等核心指标。这些数值是预测硬盘故障的核心指标，只要出现增长趋势，就意味着硬盘可能存在问题。

RAID阵列日志：记录RAID的创建、同步、降级、重建等状态。这类日志中需要高度关注的关键词包括\"Mismatched
blocks
detected\"（不一致块被检测到）或\"Degraded\"（降级），这通常意味着阵列的健康状态存在风险。

磁盘错误日志：记录I/O（输入/输出）错误、超时、命令执行失败等。如果日志中出现大量与硬盘相关的I/O错误，说明硬盘可能已经出现物理故障。

如何排查：

监控SMART属性：重点关注重分配扇区计数、当前待映射扇区数等属性。任何数值的稳步增长都是一个强烈的警告信号，表明硬盘可能即将损坏。

解读RAID错误：RAID清理时出现\"inconsistent
blocks\"（不一致块）是常见现象，但如果频繁出现，则提示控制器或硬盘可能存在不稳定因素。

查看连接状态：检查磁盘与背板的连接日志，排查是否有物理接触不良或线缆故障。
