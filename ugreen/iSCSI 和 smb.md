# iSCSI 和 smb

iSCSI 的全称是 Internet Small Computer System
Interface（互联网小型计算机系统接口）。

一句话解释：

通过网络（IP/以太网）传输 SCSI 命令协议，让服务器把远端 NAS
上的一个"块设备"当作本地硬盘来使用。

通俗类比：

SCSI 原本是计算机内部连接硬盘的电缆协议。

iSCSI 就是把这条"电缆"换成 IP 网络（网线、交换机、光纤）。

服务器通过网络访问 NAS 上划分出的一个
LUN（逻辑单元号），看起来就像插了一块新硬盘（需要格式化、挂载、分区）。

关键特点：

块级访问（像本地磁盘，不是文件共享如 SMB/NFS）。

常见于 虚拟化环境（ESXi、Hyper-V），把 VM 的虚拟磁盘放在 iSCSI LUN 上。

需要 initiator（客户端，如 ESXi）和 target（服务器端，如 UGREEN NAS）。

与 NAS 日常文件共享的区别：

---

协议                    访问层级                典型用途

SMB/NFS                 文件级                  共享文档、媒体文件

iSCSI                   块级                    虚拟机磁盘、数据库裸设备

---

简单记忆：

iSCSI = "网线版的硬盘线" + SCSI 命令。

---

特性                    iSCSI                                                                 SMB

工作层级                块级（Block-Level）                                                   文件级（File-Level）

客户端看到的样子        一块未格式化的"虚拟硬盘"，需要自己分区、格式化（如NTFS、APFS）        一个带有文件夹和文件的网络共享目录（如 \\\\nas\\share）

典型用途                数据库、虚拟机硬盘、游戏存储（需要底层磁盘访问）                      日常文件拷贝、文档编辑、多媒体共享

多用户同时写入          不支持（默认情况下一个LUN只能给一个客户端独占访问，否则会损坏数据）   原生支持（多用户可以同时打开、编辑同一文件，有锁机制）

共享粒度                整个LUN（虚拟磁盘）作为一个整体共享                                   单个文件或子文件夹，权限控制更精细

性能                    延迟更低，适合小块随机读写（如数据库、虚拟机）                        大文件顺序读写不错，但小文件随机读写开销较高

可引导性                支持（可从iSCSI磁盘启动操作系统）                                     不支持（无法通过网络文件夹启动系统）

---

iSCSI：就像一根延长线，把NAS上的"一块硬盘"直接连到你电脑上。这块盘只属于你一个人，你可以对它随意分区、格式化、装系统。别人如果同时连上来，就像两个人同时抢一根水管，数据会乱套。

SMB：就像一个自动化的共享仓库。你进去只能看到管理员摆好的文件柜和文件夹，不能自己在地上划块地盘。但好处是多人可以同时在仓库里工作，管理员可以给不同人发不同的钥匙（权限）。

环境：

UGREEN NASync DXP4800，RAID 10（4×4TB），iSCSI 服务

两台 ESXi 主机（主机 A、主机 B），通过 10GbE 交换机连接同一 iSCSI 目标

存放虚拟机磁盘（包括一个生产数据库 VM）

故障现象：

主机 B 连接 iSCSI 目标后，主机 A 的 IO 延迟从 5ms 涨到 500ms+

主机 B 自身正常

重启 NAS 或重连 iSCSI 后短暂恢复，几小时后复现

网络无丢包、延迟正常

NAS CPU/内存占用不高

日志出现：iscsi_trgt: connection reset、session re-login

一、现象关键点（重新确认）

主机 B 连接后，主机 A 延迟升高 → 说明不是主机 A 自身问题，而是 B
的加入触发了异常。

重启 NAS 或重连会话可暂时恢复 →
说明存在累积性触发条件（如缓存、锁、会话数量）。

日志有 connection reset、session re-login → 会话被反复重置。

二、最可能的原因（按概率排序）

iSCSI 目标不支持多写者（multiple writers）

同一 LUN 被两台 ESXi 同时以读写方式挂载，且未使用集群文件系统（VMFS
本身支持，但需 SCSI-3 持久保留）。

当主机 B 尝试写入时，会触发 SCSI 冲突，导致主机 A 收到 BUSY 或重置。

iSCSI 会话数量或连接数超限

某些 NAS 对 iSCSI 并发会话有限制（如最多 2 个会话，或每个 LUN 只能 1
个写会话）。

主机 B 连接后，主机 A 的会话可能被踢掉或被限流。

网络层面的 iSCSI 流控或 offload 问题

主机 A 和主机 B 使用相同的 iSCSI 发起端名称或 ISID（导致会话冲突）。

交换机或 NAS 的 iSCSI 流控（如 DCB、PFC）配置不当，导致某条连接被降速。

NAS 端 iSCSI 锁或缓存一致性问题

如 ZFS 的 ZIL 或 L2ARC 在 iSCSI 目标实现中有 bug，多会话并发触发锁竞争。

三、具体排查步骤（从快到慢）

步骤 1：确认 ESXi 的路径策略和设备状态

在两台 ESXi 上分别执行（SSH）：

bash

esxcli storage core device list \| grep -A 10 \"naa.\"

查看同一 LUN 的 Multipathing → 是否为 VMW_PSP_RR 或 VMW_PSP_FIXED。

检查 Device State → 是否为 on。如果出现 dead 或
quiesced，说明有永久保留冲突。

步骤 2：查看 SCSI 预留和冲突

在主机 A 延迟高时执行：

bash

esxcli storage core device list -d naa.xxxx

\# 看是否有 \"Scsi Reservation\" 或 \"Reservation Conflict\"

或查看 vmkernel 日志：

bash

tail -f /var/log/vmkernel.log \| grep -i \"reservation\"

出现 RESERVATION CONFLICT 或 PR OUT 错误 → 确认为多写者冲突。

步骤 3：检查 NAS 端的 iSCSI 会话信息

SSH 到 UGREEN NAS（或通过 WebUI 查看）：

bash

cat /proc/net/iscsi/session \# 因系统不同，可能路径不同

\# 或使用 iscsiadm 命令

iscsiadm -m session

确认两台主机的 Initiator Name 是否相同（不应相同）。

确认同一 LUN 下有几个写会话。如果超过 1 且 NAS
文档未明确支持多并发写，则问题在此。

步骤 4：临时隔离测试

只让主机 A 连接 iSCSI 目标，主机 B 断开 → 观察主机 A 延迟是否恢复正常。

若 A 恢复，再单独让主机 B 连接（A 断开） → B 是否也正常。

若单独都正常，同时连就出问题 → 目标不支持并发写。

步骤 5：检查 iSCSI 目标配置

在 UGREEN NAS 上查看 iSCSI target 的高级参数：

MaxSessions 或 MaxConnections -- 是否设为 1。

AllowMultipleWriters -- 若为 false 或不存在，则不支持多主机同时读写。

四、解决方案建议

原因 解决办法

不支持多写者 改用 VMFS 集群 + SCSI-3 持久保留（ESXi
自带）；或仅用一台主机挂载，另一台走 NFS。

会话冲突（相同 InitiatorName） 修改其中一个 ESXi 的 iSCSI Initiator
名称，确保唯一。

NAS 会话数限制 升级 NAS 固件，或改用支持多会话的企业级 iSCSI 目标（如
TrueNAS、Windows Storage Server）。

网络流控问题 交换机上禁用 DCB / 优先级流控，或确认 iSCSI 的 CRC
校验是否正确。

五、一句话总结

现象本质是 iSCSI 多主机并发访问同一 LUN
时的写冲突或会话管理问题，优先检查 SCSI 预留冲突和 NAS 的并发会话限制。
