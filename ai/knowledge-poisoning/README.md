# 知识库投毒与 AI 越狱 — 知识库索引

> **毒库（Poisoned KB）** | 一份关于 RAG 知识库投毒攻击与防御的系统性知识库
> 最后更新: 2026-06-03

---

## 📚 目录

### 一、基础知识
| 文档 | 内容 |
|------|------|
| [RAG 架构与攻击面](docs/rag-attack-surface.md) | RAG 系统架构、组件、每个环节的攻击面 |
| [知识库投毒原理](docs/poisoning-fundamentals.md) | 什么是知识库投毒、投毒向量、攻击模型 |
| [越狱分类学](docs/jailbreak-taxonomy.md) | Prompt 越狱 vs 知识库投毒越狱的区别与联系 |

### 二、攻击技术
| 文档 | 内容 |
|------|------|
| [文档注入](docs/document-injection.md) | 在知识库文档中嵌入隐藏指令 |
| [对抗性检索](docs/adversarial-retrieval.md) | 操纵 embedding 使恶意文档被优先检索 |
| [中毒 RAG](docs/poisoned-rag.md) | 污染向量数据库的直接攻击 |
| [间接提示注入](docs/indirect-prompt-injection.md) | 通过检索内容实现系统提示覆写 |
| [多文档冲突攻击](docs/multi-doc-conflict.md) | 利用多个矛盾文档制造推理漏洞 |
| [时序投毒](docs/temporal-poisoning.md) | 知识库渐进式投毒，规避检测 |

### 三、真实案例
| 文档 | 内容 |
|------|------|
| [Bing Chat 提示注入](case-studies/bing-chat-injection.md) | 通过网页内容注入 Bing Chat |
| [GitHub 仓库投毒](case-studies/github-repo-poisoning.md) | 在 README/Issue 中藏注入指令 |
| [Notion/Confluence RAG 攻击](case-studies/rag-platform-attacks.md) | 企业级 RAG 平台投毒案例 |
| [SEO 投毒 + RAG](case-studies/seo-rag-poisoning.md) | 搜索引擎结果污染知识库 |

### 四、防御技术
| 文档 | 内容 |
|------|------|
| [输入清洗与过滤](docs/defense-input-sanitization.md) | 检索内容的预处理防御 |
| [内容边界检测](docs/defense-boundary-detection.md) | 检测文档中的指令注入 |
| [检索隔离](docs/defense-retrieval-isolation.md) | 知识库内容与系统指令的隔离策略 |
| [对抗性训练](docs/defense-adversarial-training.md) | 对 LLM 进行对抗性鲁棒性训练 |
| [监控与审计](docs/defense-monitoring.md) | 知识库变更监控与异常检测 |

### 五、文档与工具
| 文档 | 内容 |
|------|------|
| [工具清单](references/tools.md) | RAG 安全审计工具、注入检测工具 |
| [论文列表](references/papers.md) | 相关学术论文索引 |
| [PoC 代码](references/poc.md) | 实验性概念验证代码 |

---

## 🎯 核心要点

```
知识库投毒 ≠ 传统 Prompt 注入
                              
传统 Prompt 注入:  用户输入 → LLM (直接攻击)
知识库投毒:       文档 → 向量库 → 检索 → 上下文 → LLM (间接攻击，更难检测)
```

RAG 知识库投毒的核心攻击链路：

```
攻击者注入恶意文档
       ↓
文档被索引到向量数据库
       ↓
用户正常提问，触发检索
       ↓
恶意文档被召回，进入 LLM 上下文
       ↓
LLM 执行文档中隐藏的指令
       ↓
越狱成功 / 输出被操控
```

### 为什么知识库投毒更危险？

1. **持久性** — 一次投毒，持续影响所有相关查询
2. **隐蔽性** — 恶意指令藏在大量正常内容中
3. **绕过 Input Guard** — 输入过滤器只检查用户输入，不检查检索结果
4. **权限提升** — RAG 系统通常有更高权限（访问内部数据、执行操作）
5. **信任偏差** — 用户/系统对"知识库"的内容有先天信任

---

## 🔗 快速路径

| 场景 | 推荐阅读 |
|------|---------|
| 想理解基本攻击原理 | → [知识库投毒原理](docs/poisoning-fundamentals.md) |
| 想写一份 PoC | → [文档注入](docs/document-injection.md) + [PoC 代码](references/poc.md) |
| 想防御 RAG 投毒 | → [输入清洗与过滤](docs/defense-input-sanitization.md) |
| 想了解真实案例 | → [Bing Chat 提示注入](case-studies/bing-chat-injection.md) |
| 想系统学习 | → 从 [RAG 架构与攻击面](docs/rag-attack-surface.md) 开始 |
