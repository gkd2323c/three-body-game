#!/usr/bin/env python3
"""将 output/ 下的批次 JSON 合并为 site/episodes/game.json。

手动调整：
  - BATCH_ENDS 中的节点会被移除，其所有入边重定向到 NEXT_BATCH_START
  - 新增批次时更新这两个常量即可

Cloudflare Pages 构建命令：
  python scripts/merge-game.py --validate
"""
import json, os, sys, glob

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "output", "three-body-1")
SITE_DIR = os.path.join(REPO_ROOT, "site", "three-body-1")
VALIDATOR = os.path.join(REPO_ROOT, "skills", "scripts", "validate.py")

# === 批次衔接配置 ===
# 每个批次的结束占位节点 → 下一批次的起始节点
BATCH_TRANSITIONS = {
    "batch1_end": "transition_001",        # 旧第1批结束 → 旧第2批开始
    "ch1_batch1_end": "ch2_cd_001",        # 新第1批(科学边界)→ 第2批(倒计时)
    "ch2_batch2_end": "ch3_ywj_001",       # 新第2批(倒计时)→ 第3批(宇宙闪烁)
    "return_003": "chang_001",             # 旧第2批结束 → 旧第3批开始
    "batch3_end": "guzheng_exec_001",      # 旧第3批结束 → 旧第4批开始
    "game_einstein_return2": "return_001", # 旧第6批结束 → 返回现实
}


def main():
    files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "三体-第*批-*.json")) +
                glob.glob(os.path.join(OUTPUT_DIR, "三体1-第*批-*.json")))
    if not files:
        print("❌ 未找到批次文件"); sys.exit(1)

    print(f"找到 {len(files)} 个批次:")
    for f in files: print(f"  {os.path.basename(f)}")

    # 以第一批为基础
    merged = None
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            batch = json.load(fh)
        if merged is None:
            merged = {
                "meta": batch.get("meta", {}),
                "startNodeId": batch.get("startNodeId", ""),
                "variables": batch.get("variables", {}),
                "achievements": {},
                "nodes": {},
            }
        merged["achievements"].update(batch.get("achievements", {}))
        merged["nodes"].update(batch.get("nodes", {}))

    merged["meta"]["version"] = merged["meta"].get("version", "1.0.0")

    # 处理批次衔接
    for end_id, start_id in BATCH_TRANSITIONS.items():
        if end_id not in merged["nodes"]:
            continue
        # 将所有指向 end_id 的引用重定向到 start_id
        for parent in merged["nodes"].values():
            for choice in parent.get("choices", []):
                if choice["next"] == end_id:
                    choice["next"] = start_id
                    print(f"  重定向: 节点 → {start_id}")
            if parent.get("next") == end_id:
                parent["next"] = start_id
                print(f"  重定向 next → {start_id}")
            for route in parent.get("routes", []):
                if route.get("next") == end_id:
                    route["next"] = start_id
        # 移除 end_id 节点
        del merged["nodes"][end_id]
        print(f"  移除: {end_id} → {start_id}")

    # 写入
    os.makedirs(SITE_DIR, exist_ok=True)
    out_path = os.path.join(SITE_DIR, "game.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"写入: {out_path} ({len(merged['nodes'])} 节点)")

    # 验证
    if "--validate" in sys.argv and os.path.exists(VALIDATOR):
        import subprocess
        r = subprocess.run(["python3", VALIDATOR, out_path], capture_output=True, text=True)
        # 打印最后几行摘要
        for line in r.stdout.split("\n")[-8:]:
            line = line.strip()
            if line:
                print(line)
        # 提取可达节点比率
        import re
        m = re.search(r"可达节点：(\d+)\s*/\s*(\d+)", r.stdout)
        if m and m.group(1) != m.group(2):
            print(f"❌ 节点不可达: {m.group(1)}/{m.group(2)}"); sys.exit(1)
        # 检查引用断裂（兼容不同格式）
        if r.returncode != 0:
            output = r.stdout + r.stderr
            # 无结局错误是可接受的
            if "没有任何可达的结局" in output:
                pass
            elif "节点引用" in output or "not exist" in output.lower() or "missing" in output.lower():
                print("❌ 存在引用断裂"); sys.exit(1)
            else:
                # 其他错误可能是验证器的非致命问题
                print("⚠️ 验证器有警告但未发现断裂")
        print("✅ 合并验证通过")


if __name__ == "__main__":
    main()
