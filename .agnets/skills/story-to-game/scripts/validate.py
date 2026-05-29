#!/usr/bin/env python3
"""分支剧情游戏 JSON 验证器
用法：python validate.py <json文件路径>
"""
import json
import sys
from collections import deque


def validate(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    errors = []
    warnings = []
    nodes = data.get('nodes', {})
    achievements = data.get('achievements', {})
    variables = data.get('variables', {})
    start = data.get('startNodeId', '')

    # === 1. 基础结构 ===
    if 'meta' not in data:
        errors.append('缺少 meta 字段')
    if 'startNodeId' not in data:
        errors.append('缺少 startNodeId 字段')
    if 'nodes' not in data:
        errors.append('缺少 nodes 字段')
        return False
    if start not in nodes:
        errors.append(f'startNodeId "{start}" 不存在于 nodes 中')

    # === 2. 收集引用 ===
    referenced_nodes = set()
    referenced_achievements = set()
    endings = []
    non_endings = []

    for nid, node in nodes.items():
        if node.get('isEnding'):
            endings.append(nid)
            if node.get('achievement'):
                referenced_achievements.add(node['achievement'])
        else:
            non_endings.append(nid)

        if 'next' in node and isinstance(node['next'], str):
            referenced_nodes.add(node['next'])

        for choice in node.get('choices', []):
            if 'next' in choice:
                referenced_nodes.add(choice['next'])
            changes = choice.get('changes', {})
            if 'unlockAchievement' in changes:
                referenced_achievements.add(changes['unlockAchievement'])
            for a in changes.get('unlockAchievements', []):
                referenced_achievements.add(a)

        for route in node.get('routes', []):
            if 'next' in route:
                referenced_nodes.add(route['next'])

    # === 3. 引用完整性 ===
    for ref in referenced_nodes:
        if ref not in nodes:
            errors.append(f'节点引用 "{ref}" 不存在于 nodes 中')
    for ref in referenced_achievements:
        if ref not in achievements:
            errors.append(f'成就引用 "{ref}" 未在 achievements 中定义')

    # === 4. 节点可达性 (BFS) ===
    reachable = set()
    if start in nodes:
        queue = deque([start])
        while queue:
            nid = queue.popleft()
            if nid in reachable:
                continue
            reachable.add(nid)
            node = nodes.get(nid, {})
            if node.get('next') and node['next'] in nodes:
                queue.append(node['next'])
            for choice in node.get('choices', []):
                if choice.get('next') and choice['next'] in nodes:
                    queue.append(choice['next'])
            for route in node.get('routes', []):
                if route.get('next') and route['next'] in nodes:
                    queue.append(route['next'])

    unreachable = set(nodes.keys()) - reachable
    for nid in sorted(unreachable):
        warnings.append(f'节点 "{nid}" 不可达（从 startNodeId 无法到达）')

    # === 5. 死胡同检查 ===
    for nid in non_endings:
        node = nodes[nid]
        has_choices = bool(node.get('choices'))
        has_next = bool(node.get('next'))
        has_routes = bool(node.get('routes'))
        if not (has_choices or has_next or has_routes):
            errors.append(f'节点 "{nid}" 是死胡同（非结局但无 choices/next/routes）')

    # === 6. 结局可达性 ===
    reachable_endings = [e for e in endings if e in reachable]
    unreachable_endings = [e for e in endings if e not in reachable]
    for e in unreachable_endings:
        warnings.append(f'结局 "{e}" 不可达')
    if not reachable_endings:
        errors.append('没有任何可达的结局')

    # === 7. 成就 vs 结局数量 ===
    if len(achievements) <= len(endings):
        warnings.append(
            f'成就数量（{len(achievements)}）建议大于结局数量（{len(endings)}）'
        )

    # === 8. routes 兜底检查 ===
    for nid, node in nodes.items():
        routes = node.get('routes', [])
        if routes:
            has_default = any(
                r.get('condition') in ('default', None, True)
                for r in routes
            )
            if not has_default:
                errors.append(f'节点 "{nid}" 的 routes 没有 default 兜底（可能导致玩家无法到达任何结局）')

    # === 9. 结局节点完整性 ===
    for nid in endings:
        node = nodes[nid]
        if not node.get('description'):
            warnings.append(f'结局 "{nid}" 缺少 description')
        if not node.get('closing'):
            warnings.append(f'结局 "{nid}" 缺少 closing 收束语')
        if not node.get('title'):
            warnings.append(f'结局 "{nid}" 缺少 title')

    # === 10. 互动节奏检查 ===
    for nid in non_endings:
        node = nodes[nid]
        segments = node.get('segments', [])
        if len(segments) > 8:
            warnings.append(
                f'节点 "{nid}" 有 {len(segments)} 个 segments，'
                f'建议控制在 5 个以内以维持互动节奏'
            )

    # === 11. 同向选项 callback 检查（铁律） ===
    for nid, node in nodes.items():
        choices = node.get('choices', [])
        if len(choices) >= 2:
            # 按 next 分组
            from collections import defaultdict
            groups = defaultdict(list)
            for c in choices:
                groups[c.get('next', '')].append(c)

            for next_id, group in groups.items():
                if len(group) >= 2:
                    # 多个选项指向同一 next
                    # 检查目标节点是否是 callback（有 segments 且很快指向下一个节点）
                    # 如果直接指向同一节点且该节点无法区分来源 → 错误
                    target = nodes.get(next_id, {})
                    has_segments = bool(target.get('segments'))
                    # 如果目标有 segments 但没有 condition 或 routes → 可能是共享节点无差异化
                    if not has_segments:
                        errors.append(
                            f'节点 "{nid}" 有 {len(group)} 个选项指向 '
                            f'"{next_id}"，但目标节点无 segments——'
                            f'选择缺少文本 callback'
                        )
                    else:
                        # 有 segments 但仍然是多选项共享 → 警告（需人工确认差异化）
                        only_changes = all(
                            bool(c.get('changes')) and c.get('next') == next_id
                            for c in group
                        )
                        if only_changes:
                            warnings.append(
                                f'节点 "{nid}" 有 {len(group)} 个选项指向同一节点 '
                                f'"{next_id}" 且仅靠 changes 区分——'
                                f'建议为每个选项添加独立 callback 节点'
                            )

    # === 12. 选项直跳结局检查 ===
    for nid, node in nodes.items():
        for c in node.get('choices', []):
            target_id = c.get('next', '')
            target = nodes.get(target_id, {})
            if target.get('isEnding'):
                etype = target.get('type', '')
                if etype not in ('RASH ENDING', 'BAD ENDING'):
                    errors.append(
                        f'节点 "{nid}" 的选项直接跳到非草率结局 '
                        f'"{target_id}"——结局前必须有收束节点'
                    )
                # 草率结局也应该有过渡，但降为警告
                else:
                    target_segs = target.get('segments', [])
                    if not target.get('description'):
                        warnings.append(
                            f'草率结局 "{target_id}" 被直接跳入且缺少 description'
                        )

    # === 13. progress 检查 ===
    for nid, node in nodes.items():
        p = node.get('progress')
        if p is not None and (p < 0 or p > 100):
            errors.append(f'节点 "{nid}" 的 progress 值 {p} 超出 0-100 范围')

    # === 14. 模板痕迹检查 ===
    banned_phrases = [
        '把事情推到极端', '把话咽回去', '继续问', '的余劲',
        '关于.*的那句话', '这条支线', '这条线', '这个分支',
        '玩家', '节点', '分支点', '选项A', '选项B',
        '带着.*往后走', '带着.*继续',
    ]
    import re
    for nid, node in nodes.items():
        for c in node.get('choices', []):
            text = c.get('text', '')
            for phrase in banned_phrases:
                if re.search(phrase, text):
                    errors.append(
                        f'节点 "{nid}" 的选项 "{text[:20]}..." '
                        f'包含模板痕迹 "{phrase}"'
                    )
        for seg in node.get('segments', []):
            seg_text = seg.get('text', '')
            for phrase in ['玩家', '节点', '分支', '这条支线', '选项']:
                if phrase in seg_text:
                    errors.append(
                        f'节点 "{nid}" 的正文包含元叙事词汇 "{phrase}"'
                    )

    # === 15. 连续 next 链长度检查 ===
    for nid, node in nodes.items():
        if node.get('next') and not node.get('choices') and not node.get('isEnding'):
            chain_len = 1
            current = node.get('next')
            visited_chain = {nid}
            while current and current in nodes and current not in visited_chain:
                visited_chain.add(current)
                cn = nodes[current]
                if cn.get('choices') or cn.get('isEnding') or cn.get('routes'):
                    break
                if cn.get('next'):
                    chain_len += 1
                    current = cn['next']
                else:
                    break
            if chain_len > 10:
                warnings.append(
                    f'从节点 "{nid}" 开始有连续 {chain_len} 个 next 节点'
                    f'无任何互动——建议插入伪互动'
                )

    # === 报告 ===
    print(f'\n{"="*50}')
    print(f'验证结果：{path}')
    print(f'{"="*50}')
    print(f'节点总数：{len(nodes)}')
    print(f'  - 剧情节点：{len(non_endings)}')
    print(f'  - 结局节点：{len(endings)}')
    print(f'成就数量：{len(achievements)}')
    print(f'可达节点：{len(reachable)} / {len(nodes)}')
    print(f'自定义变量：{len(variables)}')

    if errors:
        print(f'\n❌ 错误（{len(errors)}）：')
        for e in errors:
            print(f'  ✗ {e}')
    if warnings:
        print(f'\n⚠️  警告（{len(warnings)}）：')
        for w in warnings:
            print(f'  △ {w}')
    if not errors and not warnings:
        print('\n✅ 验证通过，无错误无警告。')
    elif not errors:
        print('\n✅ 无致命错误（但有警告需关注）。')
    else:
        print(f'\n❌ 存在 {len(errors)} 个致命错误，需要修复。')

    return len(errors) == 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法：python validate.py <json文件路径>')
        sys.exit(1)
    ok = validate(sys.argv[1])
    sys.exit(0 if ok else 1)
