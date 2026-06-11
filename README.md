# README

# CVE-2025-14187 — UGREEN DH2100+ NAS 缓冲区溢出

## 漏洞概要

- **CVE**: CVE-2025-14187
- **设备**: UGREEN DH2100+ (绿联私有云)
- **固件**: ≤ 5.3.0.251125
- **类型**: 栈缓冲区溢出 (CWE-120)
- **评分**: CVSS 3.1 7.2 (HIGH)
- **端点**: `POST /v1/file/backup/create` (path 参数)
- **组件**: nas_svr

## 文件说明

|文件|说明|
| ----| ---------------------------------------|
|`poc_cve_2025_14187.py`|PoC: 探测 + 认证 + 触发溢出 + fuzz 偏移|
|`exploit_skeleton_cve_2025_14187.py`|RCE skeleton: 需逆向固件后填入实际值|

## 利用步骤

### 阶段 1 — 验证漏洞存在

```bash
python3 poc_cve_2025_14187.py 192.168.1.100 443 admin admin
```

PoC 会自动:

1. 探测目标是否存活
2. 尝试登录
3. 发送超长 path 触发崩溃
4. 步进 fuzz 找到崩溃阈值

### 阶段 2 — 逆向固件 (获取精确 offset)

1. 从 UGREEN 官网下载固件 (`.swu` 包)
2. 解包: `binwalk -Me UGREEN_DH2100Plus_5.3.0.251125.swu`
3. 提取 rootfs (squashfs), 找到 `nas_svr` 二进制
4. 用 Ghidra/IDA 反汇编 `handler_file_backup_create`
5. 分析栈帧: 查看 `sub sp, sp, #0x??` → 确定缓冲区大小
6. 检查是否有 `__stack_chk_guard` → 是否启用 canary
7. 查找 ROP gadgets, system@plt 等地址

### 阶段 3 — 构建 RCE payload

将逆向得到的值填入 `exploit_skeleton_cve_2025_14187.py`:

```python
BUFFER_SIZE = 0x200  # 实际偏移
PLT_SYSTEM = 0x1234  # 实际地址
```

然后执行:

```bash
python3 exploit_skeleton_cve_2025_14187.py 192.168.1.100 'id'
```

## 修复

升级固件至 **5.3.0.251125 以上版本**。

---

 **⚠️ 免责声明**: 仅限安全研究和授权测试使用。
