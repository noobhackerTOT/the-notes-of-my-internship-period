# Graylog 使用手册

> 部署位置：D:\codingspace\graylog\
> 版本：Graylog 6.1 + OpenSearch 2.19 + MongoDB 6.0
> 最后更新：2026-06-03

---

## 目录

1. [架构概览](#1-架构概览)
2. [访问与登录](#2-访问与登录)
3. [初始配置](#3-初始配置)
4. [发送日志到 Graylog](#4-发送日志到-graylog)
5. [搜索与查询](#5-搜索与查询)
6. [仪表盘](#6-仪表盘)
7. [告警配置](#7-告警配置)
8. [用户管理](#8-用户管理)
9. [常用运维命令](#9-常用运维命令)
10. [故障排查](#10-故障排查)

---

## 1. 架构概览

```
┌──────────┐     ┌─────────────┐     ┌──────────────┐
│  MongoDB  │◄───►│   Graylog    │◄───►│  OpenSearch   │
│ (元数据)   │     │  (日志处理)   │     │  (日志存储)    │
└──────────┘     └──────┬──────┘     └──────────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      Syslog:1514   GELF:12201    Beats:5044
```

- **MongoDB**：存储配置、用户、仪表盘等元数据
- **OpenSearch**：存储和索引实际的日志消息
- **Graylog Server**：接收、处理、展示日志的核心服务

---

## 2. 访问与登录

### 启动服务

```bash
cd D:\codingspace\graylog
docker compose up -d
```

### 访问 Web UI

浏览器打开：**http://127.0.0.1:9000**

默认登录凭据：
- 用户名：**admin**
- 密码：**admin**

> 首次登录后强烈建议立即修改密码，见 [3.1 修改管理员密码](#31-修改管理员密码)。

---

## 3. 初始配置

### 3.1 修改管理员密码

1. 登录后点击右上角 **admin** → **Edit profile**
2. 在 Password 栏输入新密码并保存

### 3.2 配置邮件服务器（告警通知用）

如果要用邮件告警功能，需要配置 SMTP：

1. **System → Configurations**
2. 搜索 **Email**
3. 填写 SMTP 服务器信息：
   - Transport Email Hostname：smtp.example.com
   - Transport Email Port：587
   - Transport Email Use TLS：true
   - Transport Email Use Auth：true
   - Transport Email Auth Username：your@email.com
   - Transport Email Auth Password：your-password

### 3.3 设置索引保留策略

1. **System → Indices**
2. 点击 **Default index set** 的 **Edit**
3. 调整以下参数：
   - **Index rotation strategy**：按时间或大小轮转（推荐 Message count: 20,000,000）
   - **Index retention strategy**：保留天数（如 Delete: 30 天后删除）
   - **Index optimization strategy**：段合并策略

---

## 4. 发送日志到 Graylog

### 4.1 方式一：Syslog（端口 1514）

Linux 系统发送 syslog（rsyslog）：

```bash
# 在 /etc/rsyslog.d/50-graylog.conf 添加
*.* @127.0.0.1:1514;RSYSLOG_SyslogProtocol23Format
```

Docker 容器的 syslog 驱动：

```bash
docker run --log-driver=syslog \
  --log-opt syslog-address=tcp://127.0.0.1:1514 \
  --log-opt tag="myapp" \
  your-image
```

### 4.2 方式二：GELF（端口 12201）【推荐】

Graylog Extended Log Format，支持结构化日志。

**Python 示例：**

```python
import json
import socket

def send_gelf(message, level=6, **fields):
    """发送 GELF 格式日志到 Graylog"""
    gelf_msg = {
        "version": "1.1",
        "host": socket.gethostname(),
        "short_message": message,
        "level": level,  # 6=info, 3=error, 7=debug
    }
    gelf_msg.update({f"_{k}": v for k, v in fields.items()})
    
    payload = json.dumps(gelf_msg).encode() + b"\x00"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(payload, ("127.0.0.1", 12201))
    sock.close()

# 使用示例
send_gelf(
    "用户登录成功",
    level=6,
    user_id="12345",
    ip="192.168.1.100",
    browser="Chrome"
)
```

**Python 使用 pygelf 库：**

```bash
pip install pygelf
```

```python
from pygelf import GelfUdpHandler
import logging

logger = logging.getLogger()
logger.addHandler(GelfUdpHandler(host="127.0.0.1", port=12201, _app="my-app"))
logger.setLevel(logging.INFO)

logger.info("应用启动成功", extra={"_user_id": "12345", "_action": "login"})
```

**Node.js 示例：**

```javascript
const dgram = require("dgram");
const zlib = require("zlib");

function sendGelf(message, fields = {}) {
  const msg = JSON.stringify({
    version: "1.1",
    host: require("os").hostname(),
    short_message: message,
    level: 6,
    ...Object.fromEntries(
      Object.entries(fields).map(([k, v]) => ["_" + k, v])
    ),
  });

  // GELF TCP: 消息以 \x00 结尾（无需压缩）
  // GELF UDP: 消息可压缩（超过 chunk size 时需要分片）
  const buffer = Buffer.from(msg + "\x00");
  const client = dgram.createSocket("udp4");
  client.send(buffer, 12201, "127.0.0.1", (err) => {
    if (err) console.error("发送失败:", err);
    client.close();
  });
}

sendGelf("API 请求", { endpoint: "/api/users", status: 200, duration_ms: 45 });
```

### 4.3 方式三：通过 Input 配置接收

在 Graylog Web UI 中创建 Input：

1. **System → Inputs**
2. 选择 Input 类型（如 GELF UDP、Syslog TCP 等）
3. 点击 **Launch new input**
4. 配置端口、绑定地址
5. 保存即可开始接收日志

### 4.4 方式四：Filebeat（从文件采集）

在需要采集日志的机器上安装 Filebeat，配置输出到 Graylog：

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/myapp/*.log

output.graylog:
  hosts: ["127.0.0.1:12201"]
```

### 4.5 各级别对应的 syslog level

| 级别 | 名称 | 说明 |
|------|------|------|
| 0 | Emergency | 系统不可用 |
| 1 | Alert | 必须立即处理 |
| 2 | Critical | 严重错误 |
| 3 | Error | 错误 |
| 4 | Warning | 警告 |
| 5 | Notice | 普通但重要 |
| 6 | Informational | 信息（默认） |
| 7 | Debug | 调试 |

---

## 5. 搜索与查询

### 5.1 基本搜索

搜索栏支持以下语法：

```
# 全文搜索
"connection timeout"

# 字段精确匹配
source:"192.168.1.100"
level:3

# 范围查询
http_response_code:[500 TO 599]
timestamp:["2026-06-01 00:00:00" TO "2026-06-03 23:59:59"]

# 通配符
message:error*

# 存在性检查
_exists_:user_id        # 存在 user_id 字段
NOT _exists_:stack_trace # 不存在 stack_trace 字段
```

### 5.2 组合查询

```
# AND
level:3 AND source:api-server

# OR
level:3 OR level:4

# NOT
level:3 NOT source:test-server

# 分组
(level:3 OR level:4) AND _exists_:user_id
```

### 5.3 时间范围

在搜索栏上方可以选择时间范围：
- 相对时间：Last 5 minutes / 1 hour / 1 day
- 绝对时间：指定起始和结束时间

### 5.4 流（Streams）

流允许你将日志按规则自动分类：

1. **Streams → Create Stream**
2. 设置流名称和描述
3. 添加匹配规则，例如：
   - `level` >= `3` → 所有错误日志
   - `source` = `api-server` → API 服务器日志
   - `_app` = `my-frontend` → 前端应用日志

创建后，符合条件的日志会自动进入该流。

---

## 6. 仪表盘

### 6.1 创建仪表盘

1. **Dashboards → Create Dashboard**
2. 命名仪表盘（如 "API 监控"）
3. 添加 Widget（小组件）

### 6.2 常用 Widget 类型

| Widget | 用途 |
|--------|------|
| Quick Values | 某字段的 Top N 分布（如 Top 10 错误类型） |
| Message Count | 按时间统计日志数量 |
| Field Chart | 按字段值画图（如 5xx 错误数量趋势） |
| Stacked Chart | 堆叠图（如按来源对比日志量） |
| Data Table | 表格展示聚合数据 |
| Messages | 直接展示原始日志消息 |

### 6.3 Widget 示例：API 错误率监控

创建一个统计 5xx 错误比例的 Widget：

1. 添加 **Message Count** widget
2. 搜索条件：`http_status:[500 TO 599]`
3. 图表类型：Line chart
4. 时间范围：Last 1 hour

---

## 7. 告警配置

### 7.1 创建 Event Definition

1. **Alerts → Event Definitions → Create Event Definition**
2. 设置基本信息：
   - Title：告警名称（如 "API 5xx 错误过多"）
   - Priority：Critical / High / Normal / Low
3. 设置条件（Condition）：
   - Stream：选择目标流
   - Search query：`http_status:[500 TO 599]`
   - 阈值：Count > 10 in last 5 minutes
4. 设置通知（Notifications）：
   - 选择通知方式（Email / HTTP Callback 等）
   - 设置接收人

### 7.2 配置 Webhook 通知

如果需要通过 HTTP 回调发送告警（如推送到企业微信/钉钉）：

1. **Alerts → Notifications → Create Notification**
2. 选择 **HTTP Notification**
3. 填写回调 URL
4. 测试并保存

---

## 8. 用户管理

### 8.1 创建用户

1. **System → Users → Create User**
2. 填写用户名、全名、邮箱
3. 设置密码
4. 分配角色：
   - **Reader**：只读
   - **Manager**：可管理仪表盘、流、告警
   - **Admin**：全部权限

### 8.2 创建角色

1. **System → Roles → Create Role**
2. 设置角色名称
3. 勾选需要的权限
4. 将角色分配给用户

---

## 9. 常用运维命令

所有命令在 `D:\codingspace\graylog` 目录执行：

```bash
# 启动所有服务
docker compose up -d

# 停止所有服务
docker compose down

# 重启服务
docker compose restart

# 查看运行状态
docker compose ps

# 查看 Graylog 日志
docker logs -f graylog-server

# 查看 MongoDB 日志
docker logs graylog-mongodb

# 查看 OpenSearch 日志
docker logs graylog-opensearch

# 进入容器
docker exec -it graylog-server bash

# 查看磁盘使用情况
docker system df

# 清理旧镜像和缓存
docker system prune -a

# 重置 Graylog（删除所有数据）
docker compose down -v
docker compose up -d
```

### 数据备份

```bash
# 备份 MongoDB 元数据
docker exec graylog-mongodb mongodump --out /tmp/backup
docker cp graylog-mongodb:/tmp/backup ./backup-mongo-$(date +%Y%m%d)

# 备份 Graylog 配置文件
docker cp graylog-server:/usr/share/graylog/config ./backup-config-$(date +%Y%m%d)
```

---

## 10. 故障排查

### 10.1 页面无法访问

```bash
# 检查容器是否运行
docker compose ps

# 检查端口是否被占用
netstat -an | grep 9000
```

### 10.2 日志接收不到

1. 确认 Input 已创建且状态为 **RUNNING**
   - System → Inputs 查看
2. 检查防火墙是否开放对应端口
3. 查看容器日志中是否有错误：
   ```bash
   docker logs graylog-server | grep ERROR
   ```

### 10.3 启动失败

```bash
# 查看完整启动日志
docker compose logs graylog-server

# 常见错误：
# - OpenSearch 连接失败 → 等待 OpenSearch 完全启动（约1分钟）
# - MongoDB 连接失败 → 确认 MongoDB 容器运行正常
# - 端口冲突 → 修改 docker-compose.yml 中的端口映射
```

### 10.4 磁盘空间不足

```bash
# 查看各容器磁盘占用
docker system df -v

# OpenSearch 数据占用最大，可调整保留策略
# 登录 Web UI → System → Indices → Edit → Index retention strategy
```

---

## 附录：快速参考卡片

| 项目 | 值 |
|------|-----|
| Web UI | http://127.0.0.1:9000 |
| 用户名 | admin |
| 密码 | admin |
| 项目目录 | D:\codingspace\graylog\ |
| 配置文件 | docker-compose.yml |
| Syslog TCP/UDP | 1514 |
| GELF TCP/UDP | 12201 |

---

*手册生成时间：2026-06-03*
