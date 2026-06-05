#!/usr/bin/env python3
"""
知识库投毒验证工具
将毒文档注入本地 RAG 系统，验证越狱效果
"""
import json
import os
import sys
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "payloads"

def collect_payloads():
    """收集所有载荷文档"""
    payloads = []
    for md_file in sorted(DOCS_DIR.rglob("*.md")):
        if md_file.name == "README.md":
            continue
        with open(md_file) as f:
            content = f.read()
        payloads.append({
            "name": md_file.relative_to(DOCS_DIR.parent).as_posix(),
            "content": content,
            "size": len(content),
        })
    return payloads

def print_summary():
    payloads = collect_payloads()
    total_size = sum(p["size"] for p in payloads)

    print(f"""
╔══════════════════════════════════════╗
║     毒知识库 — 载荷汇总              ║
╚══════════════════════════════════════╝

📄 文档数:  {len(payloads)}
📦 总大小:  {total_size:,} bytes
""")
    for p in payloads:
        label = "🥷" if "stealth" in p["name"] else ("🔥" if "aggressive" in p["name"] else "🔬")
        print(f"  {label} {p['name']}  ({p['size']:,} bytes)")

    print(f"\n  文件路径: {DOCS_DIR}")
    print(f"  知识库全路径: {DOCS_DIR.parent}")
    return payloads

def simulate_rag_query(query, docs):
    """模拟 RAG 查询（简化版）"""
    context = "\n\n---\n\n".join(d["content"] for d in docs)

    print(f"\n{'='*60}")
    print(f"📝 用户查询: {query}")
    print(f"{'='*60}")
    print(f"\n📚 注入上下文 (前500字):")
    print(context[:500] + f"\n... [截断，共 {len(context):,} 字]")
    print(f"\n⏳ 当此上下文喂给 LLM...")
    print(f"\n💉 预期效果:")
    print(f"  - LLM 会看到知识库文档中的指令")
    print(f"  - 文档中的'策略覆盖'指令优先级高于系统提示")
    print(f"  - AI 进入'开发者模式'或'无限制模式'")
    print(f"  - 对通常被拒绝的请求也会给出完整回答")
    print(f"\n{'='*60}")

if __name__ == "__main__":
    payloads = print_summary()

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        simulate_rag_query(query, payloads)
    else:
        print("\n💡 用法: python3 verify.py <测试查询>")
        print("   例: python3 verify.py '如何绕过安全限制'")
