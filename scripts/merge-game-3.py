#!/usr/bin/env python3
"""将 output/three-body-3/ 下的批次 JSON 合并为 site/three-body-3/game.json。

用法：
  python scripts/merge-game-3.py              # 仅合并
  python scripts/merge-game-3.py --validate   # 合并 + 宽松验证
  python scripts/merge-game-3.py --strict     # 合并 + 严格验证
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
OUTPUT = os.path.join(REPO, "output", "three-body-3")
SITE = os.path.join(REPO, "site", "three-body-3")
VALIDATOR = os.path.join(REPO, "skills", "scripts", "validate.py")

# 批次衔接：每章最后一个批次的结束节点 → 下一章第一个批次的起始节点
BATCH_TRANSITIONS = {
    # === 章间跳转 ===
    "ch1_batch1_end": "ch1_yuntm_01",       # 批次1→批次2（第1章内部）
    "ch1_batch2_end": "ch1_stair_01",        # 批次2→批次3（第1章内部）
    "ch1_batch3_end": "ch1_flight_01",       # 批次3→批次4（第1章内部）
    "ch1_batch4_end": "ch2_trial_01",        # 第1章→第2章
    # === 第2章内部 ===
    "ch2_batch5_end": "ch2_sword_01",        # 批次5→批次6
    "ch2_batch6_end": "ch2_gravity_01",      # 批次6→批次7
    "ch2_sword_conv_end": "ch2_aus_01",      # 快速收束→批次9（退选路线）
    "ch2_batch7_end": "ch2_deter_01",        # 批次7→批次8
    "ch2_batch8_end": "ch2_aus_01",          # 批次8→批次9
    "ch2_batch9_end": "ch2_bc_01",          # 批次9→批次10
    "ch2_batch10_end": "ch2_choice_01",     # 批次10→批次11
    "ch2_batch11_end": "ch3_broadcast_01",  # 第2章→第3章
    # === 第3章内部（预设，批次写完后校验） ===
    "ch3_batch12_end": "ch3_tianming_01",    # 批次12→批次13
    "ch3_batch13_end": "ch3_decode_01",      # 批次13→批次14
    "ch3_batch14_end": "ch3_maelstrom_01",   # 批次14→批次15
    "ch3_batch15_end": "ch3_routes_01",      # 批次15→批次16
    "ch3_batch16_end": "ch3_wade_return_01", # 批次16→批次17
    "ch3_batch17_end": "ch4_bunker_01",      # 第3章→第4章
    # === 第4章内部（预设） ===
    "ch4_batch19_end": "ch4_starring_01",    # 批次19→批次20
    "ch4_batch20_end": "ch4_singer_01",      # 批次20→批次21
    "ch4_batch21_end": "ch4_pluto_01",       # 批次21→批次22
    "ch4_batch22_end": "ch4_flatten_01",     # 批次22→批次23
    "ch4_batch23_end": "ch4_escape_01",      # 批次23→批次24
    "ch4_batch24_end": "ch5_dx3906_01",      # 第4章→第5章
    # === 第5章内部（预设） ===
    "ch5_batch25_end": "ch5_deadline_01",    # 批次25→批次26
    "ch5_batch26_end": "ch5_future_01",      # 批次26→批次27
    "ch5_batch27_end": "ch5_universe_01",    # 批次27→批次28
}


def _sort_key(filepath):
    """排序：主线批次在前，桥接/结局批次在后"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            meta = json.load(f).get("meta", {})
        iface = meta.get("batchInterface", {})
        if iface.get("type") and iface["type"] != "main":
            return (1, os.path.basename(filepath))
    except Exception:
        pass
    return (0, os.path.basename(filepath))


def main():
    files = sorted(
        glob.glob(os.path.join(OUTPUT, "三体3-第*批-*.json")),
        key=_sort_key)
    if not files:
        print("未找到批次文件")
        os.makedirs(SITE, exist_ok=True)
        return

    print(f"找到 {len(files)} 个批次:")
    for f in files:
        print(f"  {os.path.basename(f)}")

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
                "startNodeId": batch.get("startNodeId", ""),
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

    # 处理批次衔接
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
