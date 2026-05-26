#!/usr/bin/env python3
"""将 output/three-body-2/ 下的批次 JSON 合并为 site/three-body-2/game.json。"""
import json, os, sys, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(REPO, "output", "three-body-2")
SITE = os.path.join(REPO, "site", "three-body-2")
VALIDATOR = os.path.join(REPO, "skills", "scripts", "validate.py")

BATCH_TRANSITIONS = {
    # "end_node": "next_start_node",
}


def main():
    files = sorted(glob.glob(os.path.join(OUTPUT, "三体2-第*批-*.json")))
    if not files:
        print("未找到批次文件，生成占位 game.json")
        os.makedirs(SITE, exist_ok=True)
        src = os.path.join(SITE, "game.json")
        if os.path.exists(src):
            print("占位文件已存在")
        return

    merged = None
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            batch = json.load(fh)
        if merged is None:
            merged = {"meta": batch["meta"], "startNodeId": batch["startNodeId"],
                       "variables": batch.get("variables", {}),
                       "achievements": {}, "nodes": {}}
        merged["achievements"].update(batch.get("achievements", {}))
        merged["nodes"].update(batch.get("nodes", {}))

    for end_id, start_id in BATCH_TRANSITIONS.items():
        if end_id not in merged["nodes"]:
            continue
        for parent in merged["nodes"].values():
            for c in parent.get("choices", []):
                if c["next"] == end_id:
                    c["next"] = start_id
            if parent.get("next") == end_id:
                parent["next"] = start_id
        del merged["nodes"][end_id]

    os.makedirs(SITE, exist_ok=True)
    out = os.path.join(SITE, "game.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"写入 {out} ({len(merged['nodes'])} 节点)")

    if "--validate" in sys.argv and os.path.exists(VALIDATOR):
        import subprocess
        r = subprocess.run(["python3", VALIDATOR, out], capture_output=True, text=True)
        if "节点引用" in r.stdout:
            print("❌ 引用断裂"); sys.exit(1)
        print("✅ 合并验证通过")


if __name__ == "__main__":
    main()
