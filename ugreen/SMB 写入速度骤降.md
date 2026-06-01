SMB 写入速度骤降（10--15 MB/s），读取正常

一、故障现象

\- 设备：绿联 DXP4800，UGOS Pro，4×4TB RAID 5，千兆网络。

\- 原正常速度：从 Windows 电脑向 NAS 拷贝文件约 110 MB/s。

\- 当前异常：写入 NAS 只有 10--15 MB/s；从 NAS 读取 110
MB/s（正常）；其他电脑向该 NAS 写入正常（110 MB/s）；本机向其他 NAS
写入正常（110 MB/s）。

\- 已尝试无效操作：重启 NAS、重启电脑、更换交换机端口、更换网线。

\- NAS 状态：CPU/内存 \< 30%，硬盘无报错。

二、根本原因

Windows 与 NAS 之间协商的 SMB 协议版本降级为 SMB 2.0（而非 SMB
3.x），导致写入性能受限。具体触发原因可能是：

\- Windows 端误开启了 SMB 签名或加密（与某些 NAS
固件兼容性差，被迫降级）。

\- 网络中存在不支持 SMB 3.0
多通道或租约的设备（如老旧交换机或防火墙规则）。

\- Windows 策略或注册表强制最小 SMB 版本为 2.0。

为什么读取速度不受影响？

SMB 2.0 的写入性能远低于 SMB 3.0（尤其是对 RAID 5
的随机写入），但读取在单队列下差异不大，所以读取仍能接近线速。

三、排查步骤

第 1 步：确认当前 SMB 协议版本

在 Windows PowerShell（管理员）中运行：

Get-SmbConnection \| Format-List ServerName, Dialect

如果 Dialect 显示 2.0.2 或 2.1 -\> 确认为 SMB 2.0。

如果显示 3.0.0 或 3.1.1 -\> 排除版本问题，继续其他方向。

第 2 步：检查 SMB 签名/加密设置

运行：

Get-SmbServerConfiguration \| Select EnableSMB2Encryption,
RequireSecuritySignature

Get-SmbClientConfiguration \| Select RequireSecuritySignature,
EnableEncryption

若任何签名/加密选项为 True，先临时关闭测试：

Set-SmbClientConfiguration -RequireSecuritySignature \$false

Set-SmbClientConfiguration -EnableEncryption \$false

重启电脑后再测试写入速度。

第 3 步：检查 Windows 最小 SMB 版本策略

查看注册表：

Get-ItemProperty -Path
\"HKLM:\\SYSTEM\\CurrentControlSet\\Services\\LanmanWorkstation\\Parameters\"
\| Select MinSMB2Dialect, MaxSMB2Dialect

正常应为：MinSMB2Dialect Get-SmbConnection \| Format-List ServerName,
Dialect

= 2，MaxSMB2Dialect = 3。

若最小版本被设为 2 且最大版本也被限制为 2，则强制使用 SMB 2.0。

第 4 步：在 NAS 端检查 SMB 服务配置

登录绿联 NAS 网页 -\> 控制面板 -\> 文件服务 -\> SMB：

\- 确保最小 SMB 协议为 SMB2，最大 SMB 协议为 SMB3。

\- 关闭 SMB 加密（除非内网严格要求）。

\- 关闭 SMB 签名（或设为"客户端可选"）。

第 5 步：排查网络中间设备

\- 临时将电脑和 NAS
直连（不经过交换机）测试。若速度恢复，则交换机问题（可能不支持 SMB 3.0
的某些特性如租约）。

\- 检查路由器/交换机是否开启了流量整形或防火墙规则针对 SMB 端口。

第 6 步：尝试强制使用 SMB 3.0（仅测试）

在 Windows 上禁用 SMB 2.0（不推荐长期，仅定位问题）：

Set-SmbServerConfiguration -EnableSMB2Protocol \$false

测试后记得恢复：

Set-SmbServerConfiguration -EnableSMB2Protocol \$true

四、解决方案（根据定位到的根因）

根因：SMB 协议降级为 2.0

解决方案：关闭 Windows 或 NAS 端的 SMB
签名/加密；确保最大最小版本范围包含 3.0

**当只有单一客户端访问 NAS 变慢时，优先检查该客户端的 SMB
会话安全策略（尤其是签名与加密），而不是怀疑存储层------这是 SMB/NAS
支持中经过验证的高效定位方法。**

根因：交换机或防火墙阻塞 SMB 3.0 特性

解决方案：更换交换机，或更新固件；检查防火墙是否允许 SMB over QUIC
或多通道

根因：Windows 策略限制

解决方案：修改注册表 MaxSMB2Dialect 为 3，重启

根因：NAS 固件 Bug

解决方案：升级绿联 UGOS Pro 到最新版本（已知早期版本存在 SMB 协商问题）

五、验证恢复

\- 再次拷贝大文件（\>5GB），观察速度是否回到 100 MB/s 以上。

\- 运行 Get-SmbConnection 确认 Dialect 为 3.0.0 或 3.1.1。

\- 持续监控 1 小时，确保无波动。

六、预防措施

\- 定期检查 Windows SMB 配置，避免安全软件自动开启签名/加密。

\- 保持绿联 NAS 固件为最新。

\- 使用 iPerf3 测试网络基线（排除物理层问题后再排查 SMB 层）。
