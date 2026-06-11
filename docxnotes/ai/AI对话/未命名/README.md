# README

# ThreatHive — 多协议蜜罐集群与威胁狩猎平台

> Multi-Protocol Honeypot Cluster & Threat Hunting Platform

## 架构

```
SSH :2222 ─┐
HTTP :8080 ─┤                 ┌─→ SQLite
MySQL :3306 ─┼─→ Redis Pub/Sub ─┼─→ FastAPI :8000 ═══ WebSocket ═══→ Vue3 Dashboard
Redis :6380 ─┘                 └─→ Analysis + Threat Intel + Alerts
```

## 功能

|模块|功能|
| ----| --------------------------------------------|
|**蜜罐集群**|SSH / HTTP / MySQL / Redis 四协议高交互蜜罐|
|**事件管道**|Redis Pub/Sub 实时推送 → SQLite 持久化|
|**行为分析**|攻击分类（扫描/爆破/漏洞利用/侦察/数据窃取）|
|**IOC 提取**|IP、域名、URL、文件哈希、邮箱、CVE 自动提取|
|**威胁情报**|AbuseIPDB 集成 + IP 信誉评分（0-100）|
|**告警引擎**|高频攻击/暴力破解/多协议攻击/漏洞利用检测|
|**攻击者画像**|攻击时间线、协议分布、行为模式聚合|
|**实时仪表盘**|Vue3 + ECharts 攻击地图 + 时间线 + 统计面板|

## 快速开始

### 前置条件

- Python 3.10+
- Docker & Docker Compose
- Redis（Docker 自动启动）

### 1. 启动基础服务

```bash
cd threathive
docker compose up -d redis    # 启动 Redis
```

### 2. 启动 API 服务器

```bash
# Windows
.venv\Scripts\python.exe -m uvicorn threathive.server:app --host 0.0.0.0 --port 8000

# Linux/Mac
source .venv/bin/activate
python -m uvicorn threathive.server:app --host 0.0.0.0 --port 8000
```

### 3. 启动蜜罐（选择协议）

```bash
python -m threathive.run_honeypot ssh     # SSH 蜜罐 :2222
python -m threathive.run_honeypot http    # HTTP 蜜罐 :8080
python -m threathive.run_honeypot mysql   # MySQL 蜜罐 :3306
python -m threathive.run_honeypot redis   # Redis 蜜罐 :6380
python -m threathive.run_honeypot all     # 全部启动
```

### 4. 打开仪表盘

浏览器访问 `http://localhost:8000/`

### 5. 生成演示数据

```bash
python tools/demo_data.py
```

## API 端点

|端点|说明|
| ----| -----------------------------|
|`GET /api/health`|健康检查|
|`GET /api/attacks`|攻击事件列表（支持分页+过滤）|
|`GET /api/stats`|聚合统计|
|`GET /api/analyze`|行为分析（扫描/爆破/分类）|
|`GET /api/iocs`|IOC 提取|
|`GET /api/intel/{ip}`|威胁情报查询|
|`GET /api/reputation/{ip}`|IP 信誉评分|
|`GET /api/alerts`|安全告警|
|`GET /api/profile/{ip}`|攻击者画像|
|`WS /ws`|实时事件推送|

## Docker 一键部署

```bash
docker compose up -d
```

## 技术栈

|层级|技术|
| ----| ------------------------------------------|
|蜜罐|Python 3.12 / asyncio / asyncssh / aiohttp|
|数据|Redis (Pub/Sub) + SQLite|
|后端|FastAPI + WebSocket|
|分析|自研攻击分类 + IOC 提取 + AbuseIPDB 集成|
|前端|Vue3 + ECharts + Element Plus|
|部署|Docker Compose|

## 项目结构

```
threathive/
├── src/threathive/
│   ├── server.py              # FastAPI 服务器
│   ├── config.py              # 配置管理
│   ├── models.py              # 数据模型 + SQLite schema
│   ├── collector.py           # 事件收集器
│   ├── redis_bridge.py        # Redis 连接管理
│   ├── analyzer.py            # 行为分析引擎
│   ├── ioc_extractor.py       # IOC 提取器
│   ├── intel_engine.py        # 威胁情报引擎
│   ├── alert_engine.py        # 告警引擎
│   ├── profiler.py            # 攻击者画像
│   ├── run_honeypot.py        # 蜜罐启动入口
│   └── honeypots/
│       ├── base_honeypot.py   # 蜜罐基类
│       ├── ssh_honeypot.py    # SSH 蜜罐
│       ├── http_honeypot.py   # HTTP 蜜罐
│       ├── mysql_honeypot.py  # MySQL 蜜罐
│       └── redis_honeypot.py  # Redis 蜜罐
├── dashboard/
│   └── index.html             # Vue3 仪表盘
├── tools/
│   ├── verify_env.py          # 环境验证
│   └── demo_data.py           # 演示数据生成
├── docker/
│   └── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## 

```
ThreatHive — 多协议蜜罐集群与威胁狩猎平台                         2026.06

• 独立设计并实现了支持 SSH/HTTP/MySQL/Redis 四种协议的高交互蜜罐系统
• 基于 Python asyncio 手写 MySQL 线协议和 Redis RESP 协议，无需第三方蜜罐框架
• 构建 FastAPI + WebSocket + Redis Pub/Sub 实时数据管道，Vue3 + ECharts 可视化
• 集成 AbuseIPDB 威胁情报，实现 IP 信誉评分、IOC 自动提取、行为聚类分析
• 内置告警引擎（高频攻击/暴力破解/多协议检测），自动生成安全告警
• Docker Compose 一键部署，30 秒启动完整攻防演示环境
• 技术栈：Python 3.12 / FastAPI / asyncio / Redis / SQLite / Vue3 / Docker
```

## License

MIT
