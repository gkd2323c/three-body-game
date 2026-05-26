# 第八步：连通性验证与 JSON 输出

## 目标

确保最终 JSON 文件结构正确、逻辑自洽、可被启动器正常加载运行。

## 验证清单

### 一、JSON 格式合法性

1. JSON 可被标准解析器解析（无语法错误）
2. 顶层包含 `meta`、`startNodeId`、`nodes` 三个必填字段
3. `startNodeId` 指向的节点在 `nodes` 中存在
4. 所有节点 ID 只使用英文字母、数字、下划线

### 二、节点可达性

从 `startNodeId` 出发，通过 BFS/DFS 遍历所有可能的 `next`、`choices[].next`、`routes[].next`，检查：

1. 每个非 ending 节点都至少被一条路径到达
2. 不存在孤立节点（无法从起点到达的节点）
3. 如果存在孤立节点，报告其 ID

### 三、引用完整性

1. 所有 `choices[].next` 指向的节点 ID 都在 `nodes` 中存在
2. 所有 `routes[].next` 指向的节点 ID 都在 `nodes` 中存在
3. 所有 `node.next` 指向的节点 ID 都在 `nodes` 中存在
4. 所有 `unlockAchievement` / `unlockAchievements` 引用的成就 ID 都在 `achievements` 中定义
5. 所有结局节点的 `achievement` 引用的成就 ID 都在 `achievements` 中定义

### 四、无死胡同

每个非 ending 节点必须满足以下至少一个条件：
- 有 `choices`（且至少一个选项在任何条件下可见）
- 有 `next`
- 有 `routes`（且有 `default` 兜底或覆盖所有条件）

### 五、条件完备性

1. 有 `condition` 的选项：确保在所有可能的状态组合下，至少有一个选项可见
2. `routes` 数组：建议最后一条用 `"condition": "default"`
3. 所有 `condition` 引用的变量/flag，在之前的某条路径上有被 set/addFlag 的可能

### 六、结局可达性

1. 每个结局节点都至少从一条路径可达
2. 每条从 startNodeId 出发的主要路径都能到达至少一个结局
3. 不存在"走到某个分支后既不是结局也无法继续"的情况

### 七、进度一致性

1. 起始节点的 progress 接近 0（建议 5）
2. 所有结局节点的 progress 为 100
3. 在每条路径上，progress 大致单调递增（允许小范围波动）

### 八、成就与结局数量

1. 成就数量 ≥ 结局数量 + 2
2. 每个结局节点的 `achievement`（如果有）都已在 `achievements` 中定义
3. 不存在永远无法解锁的成就

## 自动验证脚本

以下 Python 脚本可以自动执行上述验证：

```python
#!/usr/bin/env python3
"""分支剧情游戏 JSON 验证器"""
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
    start = data.get('startNodeId', '')

    # 1. 基础结构
    if 'meta' not in data:
        errors.append('缺少 meta 字段')
    if 'startNodeId' not in data:
        errors.append('缺少 startNodeId 字段')
    if 'nodes' not in data:
        errors.append('缺少 nodes 字段')
    if start not in nodes:
        errors.append(f'startNodeId "{start}" 不存在于 nodes 中')

    # 2. 收集所有引用的目标节点
    referenced = set()
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

        # 收集 next 引用
        if 'next' in node and isinstance(node['next'], str):
            referenced.add(node['next'])
        for choice in node.get('choices', []):
            if 'next' in choice:
                referenced.add(choice['next'])
            changes = choice.get('changes', {})
            if 'unlockAchievement' in changes:
                referenced_achievements.add(changes['unlockAchievement'])
            for a in changes.get('unlockAchievements', []):
                referenced_achievements.add(a)
        for route in node.get('routes', []):
            if 'next' in route:
                referenced.add(route['next'])

    # 3. 引用完整性
    for ref in referenced:
        if ref not in nodes:
            errors.append(f'节点引用 "{ref}" 不存在')
    for ref in referenced_achievements:
        if ref not in achievements:
            errors.append(f'成就引用 "{ref}" 未在 achievements 中定义')

    # 4. 节点可达性 (BFS)
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
    for nid in unreachable:
        warnings.append(f'节点 "{nid}" 不可达（从 startNodeId 无法到达）')

    # 5. 死胡同检查
    for nid in non_endings:
        node = nodes[nid]
        has_choices = bool(node.get('choices'))
        has_next = bool(node.get('next'))
        has_routes = bool(node.get('routes'))
        if not (has_choices or has_next or has_routes):
            errors.append(f'节点 "{nid}" 是死胡同（非结局但无 choices/next/routes）')

    # 6. 结局可达性
    reachable_endings = [e for e in endings if e in reachable]
    unreachable_endings = [e for e in endings if e not in reachable]
    for e in unreachable_endings:
        warnings.append(f'结局 "{e}" 不可达')
    if not reachable_endings:
        errors.append('没有任何可达的结局')

    # 7. 成就 vs 结局数量
    if len(achievements) <= len(endings):
        warnings.append(f'成就数量（{len(achievements)}）应大于结局数量（{len(endings)}）')

    # 8. routes 兜底检查
    for nid, node in nodes.items():
        routes = node.get('routes', [])
        if routes:
            has_default = any(
                r.get('condition') in ('default', None, True)
                for r in routes
            )
            if not has_default:
                warnings.append(f'节点 "{nid}" 的 routes 没有 default 兜底')

    # 报告
    print(f'\n验证结果：{path}')
    print(f'节点总数：{len(nodes)}')
    print(f'结局数量：{len(endings)}')
    print(f'成就数量：{len(achievements)}')
    print(f'可达节点：{len(reachable)} / {len(nodes)}')

    if errors:
        print(f'\n❌ 错误（{len(errors)}）：')
        for e in errors:
            print(f'  - {e}')
    if warnings:
        print(f'\n⚠️ 警告（{len(warnings)}）：')
        for w in warnings:
            print(f'  - {w}')
    if not errors and not warnings:
        print('\n✅ 验证通过，无错误无警告。')

    return len(errors) == 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法：python validate.py <json文件路径>')
        sys.exit(1)
    ok = validate(sys.argv[1])
    sys.exit(0 if ok else 1)
```

## 合并多章节 JSON

如果是分批写作的，最后需要合并：

1. 以第一章的 JSON 为基础
2. 将后续章节的 `nodes` 合并进去（确保没有 ID 冲突）
3. 合并所有章节的 `achievements`
4. `variables` 取第一章的定义（后续章节不应新增 variables 的定义）
5. 检查跨章节的 `next` 引用是否都已在合并后的 `nodes` 中
6. 运行验证脚本

## 总装后质检（铁律）

单批校验通过不等于总装合格。合并后必须额外检查：

**工程问题：**
- [ ] node id 是否有跨批次冲突？
- [ ] 是否残留工作流词汇（"checkpoint"、"batch"、"待续"等）？
- [ ] 跨批次的 next 引用是否全部正确？

**结局审计表：**

对每个结局逐条填写，任何一项不达标则修复：

```
| 结局ID | 类型 | 入口节点 | 收束节点数 | 后果维度覆盖 | ending页是否判词 | 通过? |
```

后果维度：家庭/亲密关系、社会/制度、生计/日常、关键人物态度、物件归处。RASH 至少覆盖 3 项，其他结局至少 4 项。

**文学质检（不可自动化，必须人工判断）：**
- [ ] 每条非原著分支线是否像原著世界可能长出来的？
- [ ] 每条结局线单独拿出来是否像完整短篇尾声？
- [ ] 有没有为了结局而结局（后果链不够就强行收束）？

## 最终输出

1. 将验证通过的 JSON 保存为 `{作品标题}.json` 并交付给用户
2. 同时交付验证脚本 `validate.py`（方便用户后续修改后自行验证）
3. 向用户报告：节点总数、结局数量、成就数量、验证结果
