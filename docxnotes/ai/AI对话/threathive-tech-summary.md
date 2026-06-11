# threathive-tech-summary

# ThreatHive 技术要点全景总结

> 覆盖简历中每条技术亮点的底层实现、设计决策、代码路径

---

## 一、多协议高交互蜜罐系统

### 1.1 SSH 蜜罐（asyncssh 全协议模拟）

|技术要点|实现细节|
| --------| ----------------------------------------------------------|
|**协议栈**|TCP → SSH Handshake → User Auth → Channel → Shell/Exec|
|**核心库**|`asyncssh`（Python 原生异步 SSH 实现，非 paramiko 的线程封装）|
|**服务端工厂**|`asyncssh.create_server(server_factory=...)` — 每连接实例化一个 `_SSHServer` 对象|
|**认证策略**|`validate_password()` 始终返回 `False`（诱导攻击者持续尝试更多凭据）|
|**凭据捕获**|在 `validate_password()` 中通过 `asyncio.create_task(self._report(...))` 异步上报，不阻塞协议状态机|
|**公钥捕获**|`validate_public_key(username, key)` 记录算法类型和指纹|
|**命令捕获**|`exec_requested(command)` 记录远程执行命令但拒绝执行|
|**会话追踪**|每个连接分配 UUID4 session_id，`connection_made` 中从 `conn.get_extra_info('peername')` 获取真实客户端 IP|
|**主机密钥**|RSA 密钥存储于 `%TEMP%/threathive_ssh_host_key`，首次自动生成，重启复用|
|**并发模型**|原生 asyncio 协程，单进程承载数百并发 SSH 连接|

**关键代码路径**: `src/threathive/honeypots/ssh_honeypot.py`

---

### 1.2 HTTP 蜜罐（aiohttp 虚假 Web 应用）

|技术要点|实现细节|
| --------| --------------------------------------------------------------------------------------------------------------|
|**服务器框架**|`aiohttp.web.Application` + `web.AppRunner` + `web.TCPSite`|
|**虚假端点（8个）**|`/`(nginx欢迎页), `/.env`(含假AWS/数据库凭据), `/wp-login.php`(WordPress登录页), `/admin.php`(管理面板), `/robots.txt`(含敏感路径), `/phpinfo.php`, `/.git/config`(假仓库地址), `/*`(Apache 404)|
|**全量请求记录**|`@web.middleware` 中间件，在任何路由处理前捕获 method/path/headers/query/body|
|**POST body 提取**|中间件中 `await request.read()` 读取表单/JSON payload|
|**敏感 Headers**|记录时自动脱敏 `Cookie` 和 `Authorization` 头|
|**类型检测**|通过 `content_type` 区分 form/json/xml/plain 请求|
|**服务器伪装**|不同端点返回不同 Server 头（nginx、Apache+PHP）|
|**并发模型**|aiohttp 异步事件循环，与 asyncio 原生集成|

**关键代码路径**: `src/threathive/honeypots/http_honeypot.py`

---

### 1.3 MySQL 蜜罐（手写 MySQL 线协议）

|技术要点|实现细节|
| --------| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|**协议版本**|MySQL Protocol::HandshakeV10（MySQL 5.7+ 标准握手）|
|**握手包构造**|手动构建二进制包：protocol_version(1B) + server_version(null-term) + connection_id(4B LE) + auth_plugin_data(8+12B) + capability_flags(4B) + charset(1B) + status(2B) + auth_plugin_name(null-term)|
|**包格式**|MySQL Packet = 3字节长度(LE) + 1字节序列号 + payload|
|**能力标志**|`CLIENT_PROTOCOL_41|
|**认证捕获**|解析客户端握手响应：跳过4B能力标志→4B最大包→1B字符集→23B保留→null-term用户名→1B密码长度→密码哈希|
|**OK 包**|0x00 header + lenenc(affected_rows) + lenenc(last_insert_id) + status(2B) + warnings(2B)|
|**ERR 包**|0xFF header + error_code(2B) + '#' + sqlstate(5B) + message|
|**EOF 包**|0xFE header + warnings(2B) + status(2B)|
|**Resultset**|column_count → N×column_def → EOF → M×row_data → EOF|
|**长度编码整数**|<251:1B, <65536:0xFC+2B LE, <16M:0xFD+3B LE, else:0xFE+8B LE|
|**命令解析**|`COM_QUERY(0x03)`, `COM_QUIT(0x01)`, `COM_PING(0x0E)`|
|**查询记录**|记录 SQL 文本（如 `SELECT LOAD_FILE('/etc/passwd')`），回复 ERR(1045) 拒绝访问|

**关键代码路径**: `src/threathive/honeypots/mysql_honeypot.py`

---

### 1.4 Redis 蜜罐（手写 RESP 协议）

|技术要点|实现细节|
| --------| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|**协议解析**|支持两种模式：Inline（`CMD arg1 arg2\r\n`）和 Multi-bulk（`*N\r\n$len\r\narg\r\n...`）|
|**RESP 序列化**|`+OK\r\n`(Simple String), `-ERR msg\r\n`(Error), `:N\r\n`(Integer), `$len\r\nstr\r\n`(Bulk), `*N\r\n...`(Array)|
|**命令处理（20+）**|PING→PONG, INFO→伪造6.2.13信息, SET→OK+SSH key检测, CONFIG GET/SET→伪造+告警, KEYS→假键列表, SLAVEOF/REPLICAOF→告警, AUTH→ERR+记录密码, EVAL/EVALSHA→OK(Lua RCE诱饵), DEBUG→ERR|
|**SSH Key 注入检测**|检查 `SET` 命令的 key 参数是否包含 `ssh`/`cron`，触发 WARNING 级别日志|
|**CONFIG 滥用检测**|`CONFIG SET dir /root/.ssh` / `CONFIG SET dbfilename authorized_keys` 等模式告警|
|**会话保持**|循环读取命令直到 `QUIT` 或 60s 超时|
|**无认证模式**|模拟 Redis 默认无密码配置，吸引攻击者|

**关键代码路径**: `src/threathive/honeypots/redis_honeypot.py`

---

## 二、蜜罐基类框架（模板方法模式）

|技术要点|实现细节|
| --------| ----------------------------------------------------------------------------------------|
|**设计模式**|模板方法模式（Template Method）— 基类定义骨架，子类实现协议|
|**基类方法**|`start()`(asyncio.start_server)→`_handle_client()`→`handle_session()`(子类实现)|
|**连接管理**|自动提取 `peername`(IP+Port)、生成 UUID4 session_id、异常捕获(ConnectionResetError/CancelledError)|
|**事件上报**|`report_event()` 构造 `AttackEvent` dataclass → 调用 `on_event` 回调（依赖注入）|
|**资源清理**|`stop()` → `server.close()` + `wait_closed()` → writer.close()|
|**子类重写**|SSH 蜜罐重写 `start()` 用 asyncssh.create_server；HTTP 重写用 aiohttp；MySQL/Redis 重写 `handle_session()`|

**关键代码路径**: `src/threathive/honeypots/base_honeypot.py`

---

## 三、实时数据管道（Redis Pub/Sub + WebSocket）

### 3.1 事件收集器

|技术要点|实现细节|
| --------| ----------------------------------------------------------------------------------------|
|**数据流**|`add_event()` → aiosqlite INSERT(持久化) + `upsert_session()`(会话更新) + `RedisBridge.publish_event()`(实时广播)|
|**异步驱动**|`aiosqlite` — 异步 SQLite 驱动，避免阻塞事件循环|
|**数据库设计**|5表：attacks(主表+3索引) / sessions(IP+协议维度) / ip_intel(IP主键) / alerts(告警持久化)|
|**查询接口**|`get_attacks(limit, offset, protocol, ip)` 动态 WHERE 拼接；`get_stats()` 聚合查询（COUNT + GROUP BY）|

### 3.2 Redis 桥接

|技术要点|实现细节|
| --------| -----------------------------|
|**客户端**|`redis.asyncio.Redis` 异步客户端|
|**通道**|`threathive:events` 固定 Pub/Sub 通道|
|**序列化**|`json.dumps(data, ensure_ascii=False)` 发布|
|**订阅**|`client.pubsub()` → `subscribe(channel)` → `async for message in pubsub.listen()` 异步生成器|
|**缓存**|`cache_get/set(key, value, ttl)` — 用于威胁情报结果 24h 缓存|

### 3.3 WebSocket 广播

|技术要点|实现细节|
| --------| -----------------------------------------------|
|**架构**|FastAPI lifespan 中启动 `asyncio.create_task(broadcast_events())` 后台协程|
|**广播逻辑**|遍历 `ws_clients` set → `ws.send_json(event)` → 移除断连客户端|
|**客户端管理**|`ws_clients: set[WebSocket]` 全局集合，accept 时 add，disconnect 时 discard|

**关键代码路径**: `src/threathive/collector.py`, `src/threathive/redis_bridge.py`, `src/threathive/server.py:66-78`

---

## 四、行为分析引擎

### 4.1 攻击分类器

|分类|检测逻辑|置信度|示例|
| ----| ------------------------------------| ---------| --------------------------------------------------------|
|**scan**|同 IP 多端口/多路径短时命中|—|同一 IP 1分钟10+事件|
|**brute_force**|action 含 "login" + 同 IP 5次+/5分钟|0.8|SSH 连续密码尝试|
|**exploit**|payload 匹配 11 种漏洞特征正则|0.85-0.95|Log4Shell/SQL注入/路径穿越/命令注入/SSTI/XXE/PHP反序列化|
|**recon**|HTTP 敏感路径探测|0.6-0.8|/.env、/wp-admin、/phpinfo|
|**data_exfil**|MySQL SELECT 查询|0.5|SELECT * FROM users|
|**ssh_key_injection**|Redis SET + ssh 关键词|0.95|SET crackit ssh-rsa...|

**特征正则库（11种漏洞模式）** :

- `\$\{jndi:` — Log4Shell
- `union\s+select\|or\s+1=1` — SQL 注入
- `\.\./\.\./` — 路径穿越
- `[;&|`]\s*(id|whoami|uname|cat\s+/etc)` — 命令注入
- `\{\{.*\}\}` — SSTI
- `<!ENTITY` — XXE
- `O:\d+:"` — PHP 反序列化

### 4.2 扫描检测

```
detect_scanning(events, window=60s, threshold=10)
→ 返回 IP 列表（1分钟内产生10+事件的扫描器）
```

### 4.3 爆破检测

```
detect_brute_force(events, window=300s, threshold=5)
→ 返回 [{ip, count, protocol, window_seconds}] 列表
```

**关键代码路径**: `src/threathive/analyzer.py`

---

## 五、IOC 自动提取

|IOC 类型|正则模式|过滤策略|
| --------| --------| -------------------------------------|
|**IPv4**|`\b(?:(?:25[0-5]\|2[0-4]\d\|[01]?\d\d?)\.){3}(?:25[0-5]\|2[0-4]\d\|[01]?\d\d?)\b`|排除私有/回环/链路本地地址|
|**IPv6**|`\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b`|—|
|**域名**|`\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b`|排除 localhost/example.com 等虚假域名|
|**URL**|`https?://[^\s<>"'\|]+`|—|
|**MD5**|`\b[a-fA-F0-9]{32}\b`|—|
|**SHA1**|`\b[a-fA-F0-9]{40}\b`|去重 SHA256 重复|
|**SHA256**|`\b[a-fA-F0-9]{64}\b`|—|
|**Email**|`\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z\|a-z]{2,}\b`|—|
|**CVE**|`CVE-\d{4}-\d{4,7}`|—|

**聚合输出**: `extract_all(events) → {ip: IOCs{ipv4:[], domains:[], urls:[], hashes:{}, emails:[], cves:[]}}`

**关键代码路径**: `src/threathive/ioc_extractor.py`

---

## 六、威胁情报集成

### 6.1 AbuseIPDB 集成

|技术要点|实现细节|
| --------| ---------------------------------------------------------------|
|**API**|`GET https://api.abuseipdb.com/api/v2/check?ipAddress=X&maxAgeInDays=90&verbose=`|
|**认证**|Header `Key: <API_KEY>`|
|**异步请求**|`aiohttp.ClientSession` + `async with session.get()`|
|**缓存策略**|Redis 缓存 24 小时（`SETEX intel:ip:<ip> 86400 <json>`）|
|**速率限制**|429 状态码 → WARNING 日志，不崩溃|
|**私有 IP 过滤**|10.x/127.x/192.168.x/172.16-31.x 直接返回 None，不发起 API 请求|

### 6.2 IP 信誉评分

```
reputation_score = min(abuseipdb_score × 0.6, 60)    # AbuseIPDB 权重60%
                 + min(event_count × 2, 20)           # 本地频率权重20%
                 + min(severe_actions × 5, 20)        # 严重度权重20%

风险等级: ≥80 critical / ≥60 high / ≥30 medium / <30 low
```

**关键代码路径**: `src/threathive/intel_engine.py`

---

## 七、告警引擎

|规则|触发条件|严重度|去重策略|
| ----| ----------------------------------------------------------------------| --------| ------------|
|**high_frequency**|单 IP 在 300s 窗口内 ≥10 事件|HIGH|1 小时去重|
|**brute_force**|单 IP 在 600s 内 ≥5 次 login 动作|CRITICAL|1 小时去重|
|**critical_exploit**|payload 含 jndi:/ssh_key/config set//etc/passwd/union select/wget/curl|CRITICAL|不重复持久化|
|**multi_protocol_attack**|单 IP 在 3600s 内攻击 ≥3 种协议|HIGH|1 小时去重|

**持久化**: 告警写入 `alerts` 表（`INSERT INTO alerts (...) VALUES (...)`），支持后续审计

**关键代码路径**: `src/threathive/alert_engine.py`

---

## 八、攻击者画像

```
AttackerProfile.build_profile(events, reputation, country, isp)
→ {
    ip, total_attacks, first_seen, last_seen,
    protocols: ["ssh", "redis"],
    actions: ["login_attempt", "cmd:set", ...],
    ports_targeted: [2222, 6380],
    unique_sessions: 4,
    recent_payloads: [...最近10条独特payload],
    timeline: [...按时间排序的全部攻击行为],
    reputation_score: 8.0,
    risk_level: "low" | "medium" | "high" | "critical"
  }
```

**关键代码路径**: `src/threathive/profiler.py`

---

## 九、Vue3 仪表盘

### 9.1 技术架构

|技术|用途|
| ------| -----------------------------------------|
|**Vue3** (CDN)|Composition API + reactive/ref 响应式状态|
|**ECharts 5** (CDN)|世界地图（攻击散点）+ 饼图（协议分布）|
|**Element Plus** (CDN)|UI 组件风格|
|**WebSocket**|实时接收攻击事件推送|
|**REST API**|初始化加载 stats / attacks / alerts|

### 9.2 面板清单

|面板|实现|更新方式|
| ----| --------------------------------------------------| -------------------|
|**统计概览**|6 个 stat-box（Total/HTTP/SSH/MySQL/Redis/Alerts）|每 5s REST 轮询|
|**实时攻击地图**|ECharts world map + scatter series，按 IP 累积打点|WebSocket 实时更新|
|**协议分布饼图**|ECharts pie，四色（绿/蓝/黄/粉）|watch(stats) 响应式|
|**攻击时间线**|滚动列表，50 条，新事件 unshift 到顶部|WebSocket 实时|
|**蜜罐状态**|4 个状态指示器（Running/Down）|每 5s REST|
|**安全告警**|按严重度着色（红/黄/绿/灰），左边界色条|每 10s REST|

### 9.3 暗黑主题

- 背景 `#0d1117`（GitHub Dark 风格）
- 卡片 `#161b22` + 边框 `#30363d`
- 文本 `#c9d1d9` / 次要 `#8b949e`
- 自定义滚动条（6px 细滚动条）

**关键代码路径**: `dashboard/index.html`

---

## 十、部署与运维

### 10.1 Docker Compose 编排

```yaml
services:
  redis:       # redis:7-alpine + healthcheck(redis-cli ping)
  api:         # Python 3.12-slim + 依赖 Redis healthy
  ssh-honeypot # 同上，command: python -m threathive.run_honeypot ssh
```

**依赖链**: `ssh-honeypot → depends_on redis(healthy)` 确保 Redis 先就绪

### 10.2 配置管理

|方式|优先级|示例|
| --------| ------| -----------------------|
|默认值|最低|`config.py` 中定义|
|`.env` 文件|中|项目根目录|
|环境变量|最高|`THREATHIVE_REDIS_HOST=redis`（Docker Compose 注入）|
|前缀隔离|—|所有变量 `THREATHIVE_` 前缀|

### 10.3 开发模式

```
pip install -e .          # 可编辑安装，修改即生效
python -m threathive.server   # 启动 API
python -m threathive.run_honeypot <proto>  # 启动蜜罐
```

---

## 十一、设计模式与工程实践

|模式|应用场景|代码位置|
| ----| ---------------------------------------| --------|
|**模板方法**|蜜罐基类定义 TCP 生命周期，子类实现协议|`base_honeypot.py`|
|**依赖注入**|`on_event` 回调注入收集器|`BaseHoneypot.__init__`|
|**观察者**|Redis Pub/Sub → WebSocket 广播|`server.py`|
|**策略模式**|攻击分类器的多种检测策略|`analyzer.py`|
|**工厂模式**|`HONEYPOTS` 字典映射协议名 → (类, 端口)|`run_honeypot.py`|
|**单例（进程级）**|全局 `collector`/`redis_bridge`/`intel_engine` 实例|`server.py`|
|**异步上下文管理器**|FastAPI lifespan 管理资源生命周期|`server.py`|
|**数据类**|`AttackEvent`/`Alert`/`IOCs` 等纯数据结构|`models.py`|

---

## 十二、关键技术决策

|决策|选择|否决方案|理由|
| --------| ------------------| ------------------------| ------------------------------|
|蜜罐实现|纯 asyncio 手写|Cowrie/Honeyd 等现成框架|展示底层协议能力，零依赖|
|数据存储|SQLite|PostgreSQL/Elasticsearch|零配置，适合演示|
|消息队列|Redis Pub/Sub|Kafka/RabbitMQ|轻量，1 个容器搞定|
|前端方案|Vue3 CDN + 单 HTML|Vite + npm build|零构建，开浏览器即用|
|异步框架|FastAPI|Flask/Django|原生 async，WebSocket 原生支持|
|SSH 实现|asyncssh|paramiko + 线程池|纯异步，与 asyncio 一致|

---

## 十三、文件清单

```
threathive/
├── src/threathive/          # 16 个 Python 模块 (~2,500 行)
│   ├── server.py            # FastAPI 服务器 (290行, 10端点+WS)
│   ├── config.py            # Pydantic Settings (35行)
│   ├── models.py            # 数据模型 + SQLite schema (130行)
│   ├── collector.py         # 事件收集器 (140行)
│   ├── redis_bridge.py      # Redis 桥接 (80行)
│   ├── analyzer.py          # 攻击分类器 (210行, 6种分类+11种漏洞模式)
│   ├── ioc_extractor.py     # IOC 提取器 (150行, 9种IOC类型)
│   ├── intel_engine.py      # 威胁情报引擎 (170行, AbuseIPDB+评分)
│   ├── alert_engine.py      # 告警引擎 (160行, 4条规则)
│   ├── profiler.py          # 攻击者画像 (110行)
│   ├── run_honeypot.py      # 蜜罐控制台 (90行)
│   └── honeypots/           # 4个蜜罐实现 (~700行)
│       ├── base_honeypot.py # 基类 (110行)
│       ├── ssh_honeypot.py  # SSH协议 (145行)
│       ├── http_honeypot.py # HTTP协议 (250行)
│       ├── mysql_honeypot.py# MySQL线协议 (260行)
│       └── redis_honeypot.py# Redis RESP协议 (170行)
├── dashboard/index.html     # Vue3 仪表盘 (325行)
├── tools/
│   ├── verify_env.py        # 环境验证
│   └── demo_data.py         # 演示数据生成器
├── docker/Dockerfile        # 容器镜像
├── docker-compose.yml       # 一键部署
├── pyproject.toml           # 项目配置
├── .gitignore
└── README.md                # 完整文档 (150行)
```
