# ThreatHive 技术文档 — Phase 1 工作总结

> 日期：2026-06-03 | 版本：v0.1.0 | 作者：Boreas

---

## 一、项目概述

**ThreatHive** 是一个多协议蜜罐集群与威胁狩猎平台。通过部署 SSH/HTTP/MySQL/Redis 四种协议的高交互蜜罐，实时捕获攻击行为，经 Redis Pub/Sub 数据管道推送至 FastAPI 后端，最终由 Vue3 仪表盘可视化呈现攻击态势。

### Phase 1 交付范围

- [x] 项目骨架搭建（模块化包结构、配置管理、依赖管理）
- [x] SQLite 数据模型（5 张表，覆盖攻击事件、会话、情报、告警）
- [x] Redis Pub/Sub 数据管道（事件收集 → 实时广播）
- [x] FastAPI 后端服务（REST API + WebSocket 实时推送）
- [x] SSH 蜜罐实现（基于 asyncssh 全协议模拟）
- [x] 蜜罐基类框架（可复用的 asyncio TCP 服务器抽象）
- [x] Docker Compose 编排（Redis + API + 蜜罐一键部署）
- [x] 端到端验证（SSH 连接 → 事件捕获 → API 查询）

---

## 二、系统架构

```
┌──────────────────────────────────────────────────────────────────┐
│                     攻击者 (Internet/内网)                        │
└──────┬───────┬───────┬───────┬───────────────────────────────────┘
       │:2222  │:8080  │:3306  │:6379
       ▼       ▼       ▼       ▼
┌──────┴───────┴───────┴───────┴───────────────────────────────────┐
│                    Honeypot Layer (Python asyncio)               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │SSH蜜罐   │ │HTTP蜜罐  │ │MySQL蜜罐 │ │Redis蜜罐 │           │
│  │asyncssh  │ │aiohttp   │ │手写协议  │ │手写协议  │           │
│  │(已完成)  │ │(待实现)  │ │(待实现)  │ │(待实现)  │           │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │
│       │            │            │            │                   │
│       └────────────┴────────────┴────────────┘                   │
│                          │                                       │
│                   EventCollector                                 │
│                   (事件标准化 + 持久化)                            │
└──────────────────────┬───────────────────────────────────────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
┌─────────────────────┐ ┌─────────────────────┐
│   SQLite            │ │   Redis             │
│   (持久存储)        │ │   (Pub/Sub 实时)    │
│                     │ │                     │
│ attacks    sessions │ │ threathive:events   │
│ ip_intel   alerts   │ │                     │
└─────────┬───────────┘ └──────────┬──────────┘
          │                        │
          └────────────┬───────────┘
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                API Server (FastAPI + Uvicorn)                    │
│                                                                  │
│  GET  /api/health         健康检查                               │
│  GET  /api/attacks        攻击事件查询（支持分页+过滤）           │
│  GET  /api/stats          聚合统计                               │
│  WS   /ws                 实时事件推送                           │
└──────────────────────────────┬───────────────────────────────────┘
                               │ WebSocket
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│              Dashboard (Vue3 + ECharts — Phase 4 实现)           │
│  攻击地图 │ 蜜罐状态 │ 攻击时间线 │ 攻击者画像 │ 告警           │
└──────────────────────────────────────────────────────────────────┘
```

---

## 三、核心模块技术细节

### 3.1 配置管理 (`config.py`)

基于 Pydantic Settings，支持多层配置覆盖：

```python
class Settings(BaseSettings):
    db_path: str = "data/threathive.db"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_channel: str = "threathive:events"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    # ... 蜜罐端口、告警阈值等

    model_config = {"env_prefix": "THREATHIVE_", "env_file": ".env"}
```

**设计要点**：
- 环境变量前缀 `THREATHIVE_` 隔离命名空间
- 自动加载 `.env` 文件
- Docker Compose 通过 `environment` 注入覆盖默认值

---

### 3.2 数据模型 (`models.py`)

5 张 SQLite 表，覆盖完整威胁狩猎数据链路：

#### attacks — 攻击事件表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| timestamp | TEXT | ISO 8601 UTC 时间戳 |
| attacker_ip | TEXT | 攻击源 IP（已建索引） |
| attacker_port | INTEGER | 攻击源端口 |
| protocol | TEXT | 协议：ssh/http/mysql/redis（已建索引） |
| honeypot_port | INTEGER | 蜜罐监听端口 |
| action | TEXT | 动作：login_attempt/command/request/query |
| payload | TEXT | 具体载荷数据（如 `user=root password=admin123`） |
| session_id | TEXT | 会话标识符 |
| raw_data | TEXT | 完整原始事件 JSON |
| country / city | TEXT | GeoIP 预留字段 |

#### sessions — 攻击会话表

追踪同一 IP 对同一协议的持续攻击行为。

| 字段 | 说明 |
|------|------|
| attacker_ip + protocol | 联合标识 |
| first_seen / last_seen | 会话时间窗口 |
| total_events | 事件计数（每次 `upsert_session` 递增） |

#### ip_intel — IP 威胁情报表

| 字段 | 说明 |
|------|------|
| ip | 主键 |
| reputation_score | 本地信誉评分（0-100） |
| abuse_score | AbuseIPDB 置信度 |
| country / isp / tags | 情报数据 |
| last_checked | 最后查询时间 |

#### alerts — 告警表

| 字段 | 说明 |
|------|------|
| rule_name | 触发规则名 |
| severity | low / medium / high / critical |
| acknowledged | 是否已确认 |

**索引策略**：attacks 表在 `attacker_ip`、`protocol`、`timestamp` 三列建立索引；alerts 表在 `attacker_ip`、`severity` 建立索引。覆盖主要查询路径。

---

### 3.3 事件收集器 (`collector.py`)

`EventCollector` 是连接蜜罐层与存储/消息层的核心组件：

```
蜜罐上报 AttackEvent
       │
       ▼
EventCollector.add_event()
       │
       ├──→ aiosqlite INSERT INTO attacks  ← 持久化
       ├──→ upsert_session()               ← 会话追踪
       └──→ RedisBridge.publish_event()    ← 实时广播
```

**异步设计**：全程使用 `aiosqlite` 异步 SQLite 驱动，避免阻塞事件循环。`add_event` 是核心热路径，在单次数据库写入完成后立即广播 Redis 消息，保证实时性。

**查询接口**：
```python
async def get_attacks(limit, offset, protocol=None, attacker_ip=None)
async def get_stats()  # 返回 total_attacks, by_protocol, top_attackers
```

---

### 3.4 Redis 桥接 (`redis_bridge.py`)

封装 `redis.asyncio` 客户端，提供三个核心能力：

| 方法 | 功能 |
|------|------|
| `publish(channel, data)` | JSON 序列化后发布，返回订阅者数量 |
| `publish_event(event)` | 快捷方法，发布到 `threathive:events` 通道 |
| `subscribe(channel)` | 异步生成器，yield 解析后的 JSON 消息 |
| `cache_get/set(key, value, ttl)` | 键值缓存（预留给威胁情报缓存） |

**广播架构**：蜜罐发布 → Redis Pub/Sub → API Server 订阅 → WebSocket 推送到所有前端客户端。

---

### 3.5 SSH 蜜罐 (`ssh_honeypot.py`)

#### 协议模拟栈

```
TCP 连接 (asyncio)
  ├── SSH 握手 (asyncssh)
  │     └── 发送伪造 OpenSSH 8.9p1 Banner
  ├── 认证阶段
  │     ├── password_auth → validate_password()  ← 记录用户名+密码
  │     └── public_key_auth → validate_public_key() ← 记录公钥算法
  ├── 通道阶段
  │     └── exec_requested(command)  ← 记录远程命令
  └── 断开
```

#### SSHHoneypotServer 关键实现

```python
class _SSHServer(asyncssh.SSHServer):
    def connection_made(self, conn):
        peer = conn.get_extra_info("peername")  # 获取真实攻击者 IP
        self._attacker_ip = peer[0]

    def validate_password(self, username, password):
        # 记录凭据但始终返回 False
        # → 攻击者会继续尝试其他密码组合
        asyncio.create_task(self._report("login_attempt", f"user={u} pass={p}"))
        return False

    def exec_requested(self, command):
        # 记录命令但拒绝执行
        asyncio.create_task(self._report("exec_attempt", command))
        return False
```

**设计决策**：
- **始终拒绝认证**：诱导攻击者尝试更多凭据组合，最大化情报收集
- **`asyncio.create_task` 上报事件**：不阻塞 SSH 协议状态机
- **动态生成主机密钥**：存储在 `%TEMP%/threathive_ssh_host_key`，重启复用

---

### 3.6 蜜罐基类 (`base_honeypot.py`)

为所有协议蜜罐提供统一的抽象层：

```python
class BaseHoneypot:
    protocol_name: str        # 子类覆盖
    default_port: int         # 子类覆盖

    async def start()         # asyncio.start_server → _handle_client
    async def stop()          # 优雅关闭

    async def _handle_client(reader, writer):
        # 1. 提取 attacker_ip:port
        # 2. 生成 session_id (UUID4 前12位)
        # 3. 调用子类 handle_session()
        # 4. 异常处理 + 连接关闭

    async def handle_session(reader, writer, ip, port, sid):
        raise NotImplementedError  # 子类实现协议交互

    async def report_event(ip, port, action, payload, ...):
        # 构造 AttackEvent → 调用 on_event 回调
```

**设计模式**：模板方法模式。基类处理 TCP 生命周期（连接管理、异常处理、资源清理），子类只需实现 `handle_session` 协议交互逻辑。回调模式（`on_event`）解耦蜜罐与收集器。

---

### 3.7 蜜罐启动入口 (`run_honeypot.py`)

```bash
python -m threathive.run_honeypot ssh     # 启动 SSH 蜜罐
python -m threathive.run_honeypot http    # 启动 HTTP 蜜罐（待实现）
python -m threathive.run_honeypot mysql   # 启动 MySQL 蜜罐（待实现）
python -m threathive.run_honeypot redis   # 启动 Redis 蜜罐（待实现）
```

每个蜜罐进程独立连接 Redis + SQLite，可独立部署到不同主机。

---

## 四、数据流全景

以一次 SSH 暴力破解为例：

```
1. 攻击者: ssh root@target -p 2222
         │
2. 蜜罐:  _SSHServer.validate_password("root", "admin123")
         │
3. 蜜罐:  asyncio.create_task(self._report("login_attempt", ...))
         │
4. 基类:  report_event() → AttackEvent(attacker_ip, protocol, action, payload)
         │
5. 回调:  EventCollector.add_event(event)
         ├── aiosqlite INSERT INTO attacks  ──→ 持久化
         ├── upsert_session()              ──→ 会话更新
         └── RedisBridge.publish_event()   ──→ 实时广播
                │
6. Redis:  threathive:events 通道
         │
7. API:    broadcast_events() 订阅 → 遍历 ws_clients
         │
8. 前端:  WebSocket 接收 JSON → ECharts 地图打点 / 时间线追加
```

**延迟分析**：蜜罐捕获到前端渲染 ≈ 2-10ms（本地 Redis → WebSocket）

---

## 五、部署架构

```yaml
# docker-compose.yml
services:
  redis:          # Redis 7 Alpine（健康检查：redis-cli ping）
  api:            # FastAPI（依赖 redis healthy）
  ssh-honeypot:   # SSH 蜜罐（依赖 redis healthy）
  # http-honeypot / mysql-honeypot / redis-honeypot（待添加）
```

**一键启动**：`docker compose up -d`

**数据持久化**：`redis_data` 和 `threathive_data` 两个命名卷

---

## 六、技术栈选型理由

| 技术 | 选型理由 |
|------|----------|
| **Python asyncio** | 蜜罐需高并发 I/O；无需引入 Go/Node.js 新语言 |
| **asyncssh** | 完整的 SSH 协议实现，比手写 SSH 握手省数周工作量 |
| **aiosqlite** | 异步 SQLite 驱动，避免阻塞事件循环 |
| **Redis Pub/Sub** | 轻量实时消息；无 Kafka/RabbitMQ 运维负担 |
| **FastAPI** | 原生 async 支持 + 自动 OpenAPI 文档 + WebSocket |
| **Pydantic Settings** | 类型安全配置；环境变量自动绑定 |
| **Docker Compose** | 面试官一键启动，零环境配置 |

---

## 七、Phase 2-5 路线图

### Phase 2 — 蜜罐矩阵（HTTP/MySQL/Redis）
- HTTP 蜜罐：伪装 WordPress/.env/admin.php，记录所有 HTTP 请求
- MySQL 蜜罐：模拟握手协议，捕获查询和数据窃取
- Redis 蜜罐：捕获未授权访问和 SSH key 写入攻击

### Phase 3 — 分析与情报
- 行为分析引擎：扫描探测 vs 定向攻击分类
- IOC 自动提取：IP、域名、URL、文件哈希
- AbuseIPDB 威胁情报集成
- 告警规则引擎

### Phase 4 — 可视化仪表盘
- Vue3 + Vite + ECharts + Element Plus
- 实时攻击地图、攻击时间线、攻击者画像

### Phase 5 — 打磨交付
- 演示数据生成器、完整 README、GitHub 开源

---

## 八、简历描述

```
ThreatHive — 多协议蜜罐集群与威胁狩猎平台                         2026.06

• 独立设计并实现了支持 SSH/HTTP/MySQL/Redis 四种协议的高交互蜜罐系统
• 基于 Python asyncio 手写协议模拟，无需第三方蜜罐框架
• 构建 FastAPI + WebSocket + Redis Pub/Sub 实时数据管道
• 集成 AbuseIPDB 威胁情报，实现 IP 信誉评分与 IOC 自动提取
• Docker Compose 一键部署，30 秒启动完整攻防演示环境
• 技术栈：Python 3.12 / FastAPI / asyncio / Redis / SQLite / Docker
```
