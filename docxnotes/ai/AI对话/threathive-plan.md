# threathive-plan

# ThreatHive 实施计划 — 多协议蜜罐集群与威胁狩猎平台

> **For Hermes:**  使用 subagent-driven-development 逐步实施。

**目标**：构建一套支持 SSH/HTTP/MySQL/Redis 四种协议的高交互蜜罐集群，实时捕获攻击行为，通过仪表盘可视化攻击态势，集成威胁情报自动标记恶意 IP。

**架构**：Honeypot Cluster (Docker) → Log Collector → SQLite + Redis Pub/Sub → FastAPI + WebSocket → Vue3 Dashboard。各蜜罐独立运行，通过 Redis 实时推送攻击事件到前端仪表盘。

**技术栈**：Python 3.10+ (asyncio) · FastAPI · Vue3 + Vite + ECharts + Element Plus · Redis · SQLite · Docker Compose

**项目路径**：`D:\codingspace\threathive\`（即 `/mnt/d/codingspace/threathive/`）

---

## 总体架构

```
┌──────────────────────────────────────────────────────┐
│              Web Dashboard (Vue3 + ECharts)           │
│  实时攻击地图 │ 蜜罐状态 │ 攻击时间线 │ 攻击者画像   │
└────────────────────┬─────────────────────────────────┘
                     │ WebSocket (实时推送)
┌────────────────────┴─────────────────────────────────┐
│              API Server (FastAPI)                     │
│  REST CRUD │ WebSocket Hub │ 情报查询 │ 告警规则     │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────┴─────────────────────────────────┐
│          Redis (Pub/Sub + 缓存)                       │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────┴─────────────────────────────────┐
│          Core Services (Python asyncio)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐       │
│  │Collector │  │Analyzer  │  │Intel Engine  │       │
│  │日志收集  │  │行为分析  │  │威胁情报查询  │       │
│  └────┬─────┘  └────┬─────┘  └──────┬───────┘       │
│       └──────────────┴──────────────┘                │
│                      │                               │
│               ┌──────┴──────┐                        │
│               │   SQLite    │                        │
│               └─────────────┘                        │
└────────────────────┬─────────────────────────────────┘
                     │
┌────────────────────┴─────────────────────────────────┐
│         Honeypot Cluster (Docker Compose)             │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │
│  │SSH蜜罐 │ │HTTP蜜罐│ │MySQL蜜罐│ │Redis蜜罐│       │
│  │:2222   │ │:8080   │ │:3306   │ │:6379   │        │
│  └────────┘ └────────┘ └────────┘ └────────┘        │
└──────────────────────────────────────────────────────┘
```

## 分阶段计划

### Phase 1: 基础框架（第 1 周）

**目标**：跑通项目骨架、一个可用蜜罐、数据流向

|##|任务|产出|
| ---| --------------------------------------------------------------------| ------------------|
|1.1|项目初始化：目录结构、pyproject.toml、Dockerfile 模板|项目骨架|
|1.2|数据库模型：SQLite schema（attacks, sessions, ip_intel）|models.py|
|1.3|日志收集器（Collector）：接收蜜罐事件、写入 SQLite、发 Redis Pub/Sub|collector.py|
|1.4|Redis 集成：Pub/Sub 通道 `threathive:events`|redis_bridge.py|
|1.5|第一个蜜罐 — SSH：模拟 SSH 服务、记录登录尝试、捕获命令|ssh_honeypot.py|
|1.6|FastAPI 骨架：/api/attacks 查询接口 + WebSocket 端点|server.py|
|1.7|Docker Compose 编排：SSH蜜罐 + Redis + API|docker-compose.yml|
|1.8|端到端验证：docker-compose up → ssh 连接 → API 查到数据|集成测试|

### Phase 2: 蜜罐矩阵（第 2 周）

**目标**：四个协议蜜罐全部就绪，覆盖主要攻击面

|##|任务|产出|
| ---| --------------------------------------------------------| ------------------|
|2.1|HTTP 蜜罐：伪装 WordPress 登录页 / .env 泄露 / admin.php|http_honeypot.py|
|2.2|MySQL 蜜罐：模拟握手、记录查询、捕获数据窃取|mysql_honeypot.py|
|2.3|Redis 蜜罐：模拟 Redis 协议、捕获写 SSH key 攻击|redis_honeypot.py|
|2.4|蜜罐基类重构：提取公共逻辑（连接管理、日志、心跳）|base_honeypot.py|
|2.5|多蜜罐并行启动脚本|run_all.py|
|2.6|攻击 Session 追踪：同一 IP 跨协议行为关联|session_tracker.py|

### Phase 3: 分析与情报（第 2-3 周）

**目标**：不只记录，还要分析攻击行为、自动查威胁情报

|##|任务|产出|
| ---| --------------------------------------------------| ----------------|
|3.1|行为分析引擎：攻击模式识别（扫描、爆破、漏洞利用）|analyzer.py|
|3.2|IOC 自动提取：IP、域名、URL、文件哈希|ioc_extractor.py|
|3.3|威胁情报集成：AbuseIPDB API 查询 + 本地缓存|intel_engine.py|
|3.4|IP 信誉评分：综合来源、频率、情报数据|reputation.py|
|3.5|告警规则引擎：高频攻击/新漏洞利用/已知恶意 IP 触发|alert_engine.py|
|3.6|攻击者画像聚合：按 IP 聚合所有行为、时间线|profiler.py|

### Phase 4: 可视化仪表盘（第 3-4 周）

**目标**：Vue3 前端，实时推送，面试能秀

|##|任务|产出|
| ---| ---------------------------------------------------| -------------------|
|4.1|Vue3 项目初始化：Vite + Element Plus + ECharts|前端骨架|
|4.2|实时攻击地图：ECharts 世界地图 + WebSocket 实时打点|AttackMap.vue|
|4.3|攻击时间线：实时滚动攻击事件流|AttackTimeline.vue|
|4.4|蜜罐状态面板：各蜜罐连接数、运行状态|HoneypotPanel.vue|
|4.5|攻击者详情页：IP 画像、攻击历史、威胁情报|AttackerProfile.vue|
|4.6|统计面板：攻击趋势图、协议分布饼图、Top攻击源|StatsPanel.vue|
|4.7|告警面板：实时告警 + 历史告警列表|AlertPanel.vue|
|4.8|暗色主题 + 响应式布局（面试演示用）|样式打磨|

### Phase 5: 打磨交付（第 4 周）

**目标**：文档、演示、部署一键化

|##|任务|产出|
| ---| -----------------------------------------------------| ------------|
|5.1|一键部署：`docker-compose up -d` 启动全部服务|部署脚本|
|5.2|README：架构图、快速开始、API 文档、截图|README.md|
|5.3|演示数据生成器：模拟真实攻击流量供演示|demo_data.py|
|5.4|最终集成测试 + bug 修复|稳定版本|
|5.5|GitHub 仓库准备：License、.gitignore、commit 历史整理|开源就绪|

---

## 关键技术决策

|决策|选择|理由|
| ------------| --------------------------| ------------------------------------------|
|蜜罐协议实现|纯 asyncio 手写协议模拟|展示底层网络编程能力，不依赖第三方蜜罐框架|
|数据存储|SQLite（生产可换 PG）|零配置，适合演示，代码层面抽象了存储接口|
|实时推送|Redis Pub/Sub → WebSocket|轻量、可靠，攻防演练场景延迟低|
|前端图表|ECharts|攻击地图效果好，中文社区资料多|
|部署|Docker Compose|面试官一键启动，不用配环境|

## 简历描述模板

```
ThreatHive — 多协议蜜罐集群与威胁狩猎平台                                    2026.06
• 独立设计并实现了支持 SSH/HTTP/MySQL/Redis 四种协议的高交互蜜罐系统
• 基于 Python asyncio 手写协议模拟，无需第三方蜜罐框架，单机承载 1000+ 并发连接
• 构建 FastAPI + WebSocket + Redis Pub/Sub 实时数据管道，前端 Vue3 + ECharts 可视化
• 集成 AbuseIPDB 威胁情报，实现 IP 信誉评分、IOC 自动提取、攻击行为聚类分析
• Docker Compose 一键部署，30 秒启动完整攻防演示环境
```

---

## 开发约定

- **语言**：Python 3.10+（asyncio 异步）、Vue3 Composition API
- **代码风格**：Black格式化、mypy类型检查
- **提交规范**：`feat:` / `fix:` / `refactor:` / `docs:`
- **测试**：pytest + pytest-asyncio，核心模块覆盖率 >80%
- **工作目录**：`/mnt/d/codingspace/threathive/`
