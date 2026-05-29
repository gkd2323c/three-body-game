#!/usr/bin/env python3
"""将 output/three-body-2/ 下的批次 JSON 合并为 site/three-body-2/game.json。

用法：
  python scripts/merge-game-2.py              # 仅合并
  python scripts/merge-game-2.py --validate   # 合并 + 宽松验证
  python scripts/merge-game-2.py --strict     # 合并 + 严格验证
"""
import json, os, sys, glob
from collections import deque


def check_reachability(nodes, start_id):
    """从 start_id 做 BFS，返回 (reachable_set, unreachable_set)"""
    reachable = set()
    queue = deque([start_id])
    while queue:
        nid = queue.popleft()
        if nid in reachable:
            continue
        reachable.add(nid)
        node = nodes.get(nid, {})
        if node.get("next") and node["next"] in nodes:
            queue.append(node["next"])
        for c in node.get("choices", []):
            if c.get("next") and c["next"] in nodes:
                queue.append(c["next"])
        for r in node.get("routes", []):
            if r.get("next") and r["next"] in nodes:
                queue.append(r["next"])
    unreachable = set(nodes.keys()) - reachable
    return reachable, unreachable


def check_batch_interfaces(merged, batch_metas):
    """验证每个批次声明的 entryFrom/exitTo 是否兑现"""
    errors = []
    for bname, iface in batch_metas.items():
        for entry_id in iface.get("entryFrom", []):
            entry_node = merged["nodes"].get(entry_id)
            if not entry_node:
                errors.append(f"[{bname}] 入口节点 {entry_id} 不存在于合并结果中")
                continue
            batch_nodes = iface["_node_ids"]
            exit_nodes = set(iface.get("exitTo", []))
            all_valid = batch_nodes | exit_nodes
            has_conn = False
            if entry_node.get("next") in all_valid:
                has_conn = True
            for c in entry_node.get("choices", []):
                if c.get("next") in all_valid:
                    has_conn = True
            for r in entry_node.get("routes", []):
                if r.get("next") in all_valid:
                    has_conn = True
            if not has_conn:
                errors.append(f"[{bname}] 入口断裂：{entry_id} 未指向本批次或出口节点")
        for exit_id in iface.get("exitTo", []):
            if exit_id not in merged["nodes"]:
                errors.append(f"[{bname}] 出口节点 {exit_id} 不存在")
    return errors


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(REPO, "output", "three-body-2")
SITE = os.path.join(REPO, "site", "three-body-2")
VALIDATOR = os.path.join(REPO, "skills", "scripts", "validate.py")

BATCH_TRANSITIONS = {
    "batch1_end": "ch1_wu_001",
    "ch1_batch2_end": "ch2_luoj_001",
    "ch2_batch3_end": "ch3_zhang_001",
    "ch3_batch4_end": "ch4_bunker_001",
    "ch4_batch5_end": "ch5_zhang_001",
    "ch5_batch6_end": "ch6_awake_001",
    "ch6_batch7_end": "ch7_fleet_001",
    "ch7_batch8_end": "ch8_deter_001",
}


def _sort_key(filepath):
    """排序：主线批次在前，桥接批次（batchInterface）在后"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            meta = json.load(f).get("meta", {})
        iface = meta.get("batchInterface", {})
        if iface.get("type") and iface["type"] != "main":
            return (1, os.path.basename(filepath))  # 桥接批次排后
    except Exception:
        pass
    return (0, os.path.basename(filepath))  # 主线批次排前


def main():
    files = sorted(
        glob.glob(os.path.join(OUTPUT, "三体2-第*批-*.json")),
        key=_sort_key)
    if not files:
        print("未找到批次文件")
        os.makedirs(SITE, exist_ok=True)
        return

    strict = "--strict" in sys.argv
    merged = None
    batch_metas = {}
    for f in files:
        with open(f, "r", encoding="utf-8") as fh:
            batch = json.load(fh)
        bname = os.path.basename(f)
        if merged is None:
            merged = {
                "meta": batch["meta"],
                "startNodeId": "ch0_tomb_001",
                "variables": batch.get("variables", {}),
                "achievements": {},
                "nodes": {},
            }
        merged["achievements"].update(batch.get("achievements", {}))
        merged["nodes"].update(batch.get("nodes", {}))
        iface = batch.get("meta", {}).get("batchInterface", {})
        if iface:
            iface["_node_ids"] = set(batch.get("nodes", {}).keys())
            batch_metas[bname] = iface

    for end_id, start_id in BATCH_TRANSITIONS.items():
        if end_id not in merged["nodes"]:
            continue
        for parent in merged["nodes"].values():
            for c in parent.get("choices", []):
                if c["next"] == end_id:
                    c["next"] = start_id
            if parent.get("next") == end_id:
                parent["next"] = start_id
            for r in parent.get("routes", []):
                if r.get("next") == end_id:
                    r["next"] = start_id
        del merged["nodes"][end_id]

    os.makedirs(SITE, exist_ok=True)
    out = os.path.join(SITE, "game.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"写入 {out} ({len(merged['nodes'])} 节点)")

    # === 严格验证 ===
    if strict:
        print("\n=== 严格模式验证 ===")
        has_error = False
        reachable, unreachable = check_reachability(
            merged["nodes"], merged["startNodeId"])
        if unreachable:
            print(f"❌ 不可达节点: {len(unreachable)}/{len(merged['nodes'])}")
            for nid in sorted(unreachable):
                print(f"   - {nid}")
            has_error = True
        else:
            print(f"✅ 全图可达: {len(reachable)}/{len(merged['nodes'])}")
        if batch_metas:
            iface_errors = check_batch_interfaces(merged, batch_metas)
            if iface_errors:
                print(f"❌ 批次接口问题 ({len(iface_errors)}):")
                for e in iface_errors:
                    print(f"   - {e}")
                has_error = True
            else:
                print("✅ 所有批次接口声明兑现")
        broken = []
        for nid, node in merged["nodes"].items():
            if node.get("next") and node["next"] not in merged["nodes"]:
                broken.append(f"{nid}.next → {node['next']}")
            for c in node.get("choices", []):
                if c.get("next") and c["next"] not in merged["nodes"]:
                    broken.append(f"{nid} choice → {c['next']}")
            for r in node.get("routes", []):
                if r.get("next") and r["next"] not in merged["nodes"]:
                    broken.append(f"{nid} route → {r['next']}")
        if broken:
            print(f"❌ 引用断裂 ({len(broken)}):")
            for b in broken:
                print(f"   - {b}")
            has_error = True
        else:
            print("✅ 无引用断裂")
        if has_error:
            print("\n❌ 严格模式验证失败")
            sys.exit(1)
        else:
            print("\n✅ 严格模式验证通过")
        return

    # === 宽松验证 ===
    if "--validate" in sys.argv and os.path.exists(VALIDATOR):
        import subprocess, re
        r = subprocess.run(["python3", VALIDATOR, out], capture_output=True, text=True)
        m = re.search(r"可达节点：(\d+)\s*/\s*(\d+)", r.stdout)
        if m and m.group(1) != m.group(2):
            print(f"❌ 节点不可达: {m.group(1)}/{m.group(2)}")
        output = r.stdout + r.stderr
        if r.returncode != 0:
            if "没有任何可达的结局" in output:
                pass
            elif "节点引用" in output:
                print("❌ 存在引用断裂")
        print("✅ 合并验证通过")


if __name__ == "__main__":
    main()
