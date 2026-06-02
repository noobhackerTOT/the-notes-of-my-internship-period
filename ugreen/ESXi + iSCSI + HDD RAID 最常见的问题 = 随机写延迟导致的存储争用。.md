# ESXi + iSCSI + HDD RAID 最常见的问题 = 随机写延迟导致的存储争用。

# ESXi + iSCSI + HDD RAID 最常见的问题 = 随机写延迟导致的存储争用。

# ESXi + iSCSI + HDD RAID 最常见的问题 = 随机写延迟导致的存储争用。

## 环境

UGREEN NASync DXP4800，4×4TB HDD，RAID 10

iSCSI 提供给 3 台 ESXi，多 VM 共享同一 datastore

VM 包括：Windows Server、MySQL、Linux

10GbE 直连

## 背景知识介绍

**SCSI：就像是用网线给电脑“虚拟”接上一块远程硬盘。它把硬盘设备通过网络共享出来，让其它电脑能像使用本地硬盘一样，去分区和格式化，实现存储资源的网络共享**

**ESXi：虚拟机运行平台安装在物理服务器上，负责“运行”和“管”好单台服务器上的各个虚拟机。**

## 故障现象

每天下午 2 点，所有 VM 同时卡顿（延迟高、查询超时），持续 20-30
分钟后自动恢复

NAS CPU 飙到 90-100%，iSCSI 不掉线，网络正常

### 核心判断

存储层写争用（write contention），不是网络或单 VM 故障。所有 VM
同时受影响 → 底层共享 datastore 出现延迟尖峰。

### 根因

多个 VM 同时产生随机写、journal、metadata flush、fsync 等 IO

机械盘 RAID10 在高频随机写场景下，seek 激增、队列堵塞、延迟暴涨

固定时间触发说明存在后台任务（如 RAID scrub、snapshot consolidate、VM
快照、VSS 等）叠加 IO 压力

### 典型链路

后台任务启动 → HDD 顺序扫描/metadata rewrite → RAID seek 增加 → VM
随机写排队 → iSCSI 延迟升高 → ESXi datastore 卡顿 → 所有 VM 卡顿 →
后台结束恢复

### 验证方法

NAS：iostat -x 1 看 util 100%、await 高、avgqu-sz 暴涨

ESXi：esxtop 看 DAVG/GAVG \>50ms 表示 datastore 堵塞

## 解决方案

短期：错开 RAID scrub / SMART 测试时间，减少快照，分离高 IO VM

中长期：增加 NVMe 缓存（最有效）、拆分 datastore/LUN、换用 SSD

## 经验结论

ESXi + iSCSI + HDD RAID 最常见的问题 =
随机写延迟导致的存储争用。典型表现：固定时间点、所有 VM 一起卡、iSCSI
不掉线、网络正常、自动恢复。
