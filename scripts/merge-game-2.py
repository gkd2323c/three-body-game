#!/usr/bin/env python3
"""将 output/three-body-2/ 下的批次 JSON 合并为 site/three-body-2/game.json。"""
import json, os, sys, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(REPO, "output", "three-body-2")
SITE = os.path.join(REPO, "site", "three-body-2")
VALIDATOR = os.path.join(REPO, "skills", "scripts", "validate.py")

BATCH_TRANSITIONS = {
    "batch1_end": "ch1_wu_001",           # 第一批(序章)→第二批
    "ch1_batch2_end": "ch2_luoj_001",     # 第二批(上部·面壁者·上)→第三批
    "ch2_batch3_end": "ch3_zhang_001",    # 第三批(上部·面壁者·中)→第四批
    "ch3_batch4_end": "ch4_bunker_001",    # 第四批→第五批(咒语·上)
    "ch4_batch5_end": "ch5_zhang_001",
    "ch5_batch6_end": "ch6_awake_001",
    "ch6_batch7_end": "ch7_fleet_001",     # 第五批(咒语·上)→第六批
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
        import subprocess, re
        r = subprocess.run(["python3", VALIDATOR, out], capture_output=True, text=True)
        m = re.search(r"可达节点：(\d+)\s*/\s*(\d+)", r.stdout)
        if m and m.group(1) != m.group(2):
            print(f"❌ 节点不可达: {m.group(1)}/{m.group(2)}"); sys.exit(1)
        output = r.stdout + r.stderr
        if r.returncode != 0:
            if "没有任何可达的结局" in output:
                pass
            elif "节点引用" in output:
                print("❌ 存在引用断裂"); sys.exit(1)
        print("✅ 合并验证通过")


if __name__ == "__main__":
    main()
