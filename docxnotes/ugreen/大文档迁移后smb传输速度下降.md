# 大文档迁移后smb传输速度下降

硬盘smart测试的关键

crc

一、它代表什么？

全称：Cyclic Redundancy Check（循环冗余校验）错误计数。

作用：记录硬盘与主机之间（通过 SATA/SAS 接口）数据传输时发生的 CRC
校验失败次数。

通俗解释：每次硬盘通过数据线向主板/RAID卡传输一个数据块，都会附带一个
CRC
校验码。如果接收端计算的校验值与附带的不一致，就说明传输过程中数据被损坏，计数器
+1。

二、CRC 错误 ≠ 磁盘介质损坏

---

错误类型                根源                     典型故障

CRC 错误                接口 / 线缆 / 背板 /     数据线松动、线缆质量差、接触不良、SATA
外部干扰                 接口氧化、电磁干扰

介质错误                盘片/磁头/闪存物理缺陷   坏道、无法读取的扇区、重映射事件、UNC
错误

---

✅ 关键判断：如果 SMART 中 Reallocated_Sector_Ct（重映射）为零或很低，而
CRC 错误计数很高，基本可以断定不是硬盘本身坏了，而是接口/线缆/连接问题。

三、常见触发原因及解决方案

---

原因                    表现                           解决办法

SATA/SAS                CRC 缓慢增长，有时伴随系统日志 重新插拔数据线，或更换质量更好的线材（建议
数据线松动或损坏        ataX.00: status: { DRDY ERR }  50cm 以内带卡扣）

背板或扩展卡接触不良    多块硬盘同时出现 CRC 错误      清洁或更换背板 / 重新插拔硬盘托架

SATA 线弯曲过紧 /       CRC 偶发，但硬盘自检正常       缩短线长、理顺走线、避免与电源线紧贴
长度超 1m

电源供电不稳            多块盘同时增长，伴随电压波动   检查电源输出，避免劣质电源

接口速率协商问题        强制设为 SATA 3.0 (6Gbps)      更换线材或主板端口，锁定速率测试
后出现，降到 3Gbps 消失

主板或 RAID 卡 SATA     所有端口上的硬盘都出现 CRC     更换扩展卡 / 送修主板
控制器故障              增长

---

Bg

• UGREEN NAS RAID5 性能突然下降

• SMB 文件复制速度只有 5--10 MB/s

• 大文件操作明显变慢

• CPU / Memory usage 正常

• 所有磁盘 SMART 显示 Healthy

• 问题出现在一次约 2TB 文件迁移之后

根本原因

一块硬盘（/dev/sdc）的 SATA 线缆松动/接触不良，导致 UDMA_CRC_Error_Count
高达 1847。

Linux mdraid 检测到链路不稳定，自动触发 RAID 重建/恢复（/proc/mdstat
显示 recovery 进度）。

重建期间，内核强制降低 I/O 优先级以保证数据一致性，造成极端性能瓶颈。

解决方案

重新插拔并交换 SATA 线缆 → CRC 停止增长。

等待 RAID rebuild 完成（约 32.4% 时被用户发现）→ 性能恢复到 \~110 MB/s。

关键知识点

CRC 错误 ≠ 磁盘坏道，而是通信链路问题（线缆、背板、接口）。

单盘链路故障会连锁触发 RAID 保护机制，导致全局性能雪崩。

排查 NAS 性能问题时，必须检查 cat /proc/mdstat 确认是否在重建/校验。

健康指标（CPU 空闲、SMART 通过）不能直接排除 RAID 层 I/O 限流。

一句话避坑指南：

当 NAS 突然变慢且 CRC
计数异常时，先修链路、等重建完成，不要急着换盘或怀疑存储池损坏。

Smart 测试的关键参数

1\. UDMA CRC Error Count

作用：记录 SATA/IDE 传输中发生的 CRC 校验错误次数

诊断价值：

非零且持续增加 → 可能是 SATA 线松动、接口接触不良或电缆质量问题

高值但不增加 → 过去通信有错误，但现在稳定

典型表现：

单盘高，其他盘正常 → 可导致 RAID degraded 模式或性能下降

2\. Reallocated Sector Count

作用：记录已坏的物理扇区被替换的数量

诊断价值：

大于 0 且持续增加 → 硬盘可能开始物理损坏

单次高但稳定 → 盘仍可使用，但需监控

3\. Pending Sector Count

作用：待重映射的坏道数量（还没替换）

诊断价值：

非零 → 硬盘正在出现潜在坏道

RAID 在 rebuild 或 I/O 大负载下可能出现性能问题

4\. Offline Uncorrectable

作用：离线测试发现无法纠正的扇区数量

诊断价值：

非零 → 硬盘已经出现不可恢复的错误，可能导致 RAID 出错

5\. Temperature

作用：记录硬盘温度

诊断价值：

高温 → 会触发自动降速，影响 RAID 和 SMB 性能

稳定在 35--45°C → 正常

6\. Power-On Hours / Load Cycle Count

作用：硬盘使用寿命指标

诊断价值：

用于判断硬盘老化情况，但短期性能问题一般不由此引起

UDMA CRC Error Count 是企业 NAS 性能排障中最常忽略的指标。

高 CRC → NAS 认为链路不稳定 → RAID 降速 → SMB 速度低

SMART 的 Reallocated / Pending Sector Count
更适合判断硬盘本身是否需要更换

NAS Support 里为什么 SATA 很重要

因为很多"玄学问题"：

SMB慢

RAID卡

偶发掉盘

rebuild异常

最后根因其实是：

SATA链路不稳定

日志的关键

SMART

\+

kernel log

\+

RAID log

\+

I/O error log
