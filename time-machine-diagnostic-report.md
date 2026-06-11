# time-machine-diagnostic-report

# macOS Time Machine 备份失败 (-6606) 诊断报告

**设备**: UGOS Pro NAS (FAE-TEST)
**系统版本**: UGOS Pro 1.16.0.0085 (Debian 12)
**诊断包**: diag_HB670EE242539D16_2606050849
**报告日期**: 2026-06-05

---

## 一、问题概述

macOS Tahoe 26.6 Time Machine 备份失败，错误码 `-6606`（kNAFileAccessFailedError），
表示 macOS 无法访问或挂载 SMB Time Machine 卷。

---

## 二、SMB 配置状态

**配置文件**: `samba/testparm.log`

### 相关共享配置

**TM_MacBookAir**（配置正确）:

```
fruit:time machine = yes
vfs objects = catia fruit full_audit recycle streams_xattr ug_xattr_filter
valid users = @admin tmbackup Schedlbauer
```

**TimeMachineBackupMacMini**（**缺少 Time Machine 标记**）:

```
→ 没有 fruit:time machine = yes
```

> **关联日志**: `samba/testparm.log` 中搜索 `[TM_MacBookAir]` 和 `[TimeMachineBackupMacMini]`

---

## 三、根因 1：BTRFS 配额查询失败

### 严重性

🔴 **高** — 直接导致 macOS 无法完成卷挂载验证

### 错误日志

文件: `samba/log.mac` (行号约 50-60)

```
ERROR: quota query failed: Operation not permitted
[2026/06/05 08:48:44.157770] 
../../source3/lib/sysquotas_btrfs.c:121(sys_get_btrfs_quota)
Failed to get btrfs qgroup infor. 
  path[/volume1/TM_MacBookAir] 
  bdev[/dev/mapper/ug_7AA017_1755341522_pool1-volume1] 
  uid[4294967295] 
  ret[-1]
```

### 原因分析

- UGOS Pro 使用 LVM + BTRFS 存储架构
- Samba 进程（运行为 root）尝试查询 BTRFS qgroup 配额信息
- 系统返回 `Operation not permitted`，配额查询被拒绝
- `uid[4294967295]` 表示未映射到有效用户 ID
- macOS 的 backupd 在挂载 Time Machine 卷时需要读取卷的可用空间和配额信息，
  当配额查询失败时，macOS 判定该卷不可用

---

## 四、根因 2：#recycle 目录 ACL 拒绝

### 严重性

🟡 **中** — 可能导致备份过程中断或文件访问失败

### 错误日志

文件: `samba/log.mac` (行号约 65-70)

```
[2026/06/05 08:48:44.303669]
../../source3/modules/vfs_ugacl.c:494(ugacl_aget_acl)
ugacl_aget_acl: ERR_ACCESS_DENIE

[2026/06/05 08:48:44.303745]
../../source3/modules/vfs_ugacl.c:889(ugvfs_acl_fget_nt_acl)
ugvfs_acl_fget_nt_acl: 
  fget_nt_acl(real_path:/volume1/TM_MacBookAir/#recycle, stream:(null))
  ugacl_agent_acl fail, ret:-1073741790
```

### 原因分析

- UGOS Pro 的自定义 VFS 模块 `ug_xattr_filter` + `ugacl` 在处理 `#recycle` 目录时
  返回 `ERR_ACCESS_DENIE`
- macOS 在扫描 Time Machine 卷时会列举所有文件和目录，
  遇到权限拒绝的目录后中断操作
- `ret:-1073741790` 对应 `STATUS_ACCESS_DENIED`（NT 状态码）

---

## 五、根因 3：TimeMachineBackupMacMini 缺少 Time Machine 标记

### 严重性

🟡 **中** — 该共享无法被 macOS 识别为 Time Machine 目标

### 配置对比

|共享|fruit:time machine|状态|
| ------------------------| ------------------| -----------------|
|TM_MacBookAir|`yes`|✅ 正常|
|TimeMachineBackupMacMini|**未设置**|❌ macOS 无法发现|

**关联日志**: `samba/testparm.log` 中搜索 `[TimeMachineBackupMacMini]`

---

## 六、Samba 版本信息

文件: `samba/log.nmbd` (行号 30-32)

```
nmbd version 4.17.12-Debian
Copyright Andrew Tridgell and the Samba Team 1992-2022
```

Samba 4.17.12 对 macOS Tahoe 26.6 的 SMB 3.x 扩展支持存在已知兼容性问题。

---

## 七、建议修复方案

### 方案 A：修复 BTRFS 配额（优先）

```
btrfs quota enable /volume1/TM_MacBookAir
btrfs quota rescan /volume1/TM_MacBookAir
```

### 方案 B：修复回收站权限

```
chmod -R 755 /volume1/TM_MacBookAir/#recycle
chown tmbackup:admin /volume1/TM_MacBookAir/#recycle
setfacl -m g:admin:rwx /volume1/TM_MacBookAir/#recycle
```

### 方案 C：补全 TimeMachineBackupMacMini 配置

在 SMB 共享配置中添加：

```
fruit:time machine = yes
```

### 方案 D：重启 SMB 服务

```
systemctl restart smbd
```

---

## 八、日志索引

|日志文件|路径|关键内容|
| ----------------| ----| --------------------------|
|SMB 配置|`samba/testparm.log`|完整共享配置|
|macOS 连接日志|`samba/log.mac`|BTRFS quota 错误、ACL 拒绝|
|macOS 历史日志|`samba/log.mac-96de48`|历史连接记录|
|SMB 守护进程日志|`samba/log.smbd`|SMB 通用错误|
|Samba 版本|`samba/log.nmbd`|版本 4.17.12-Debian|
