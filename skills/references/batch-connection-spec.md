# 新批次写作规范

每写一个新批次，必须完成以下检查清单后才能提交。

---

## 一、批次接口声明（必须）

在批次 JSON 的 `meta` 中添加 `batchInterface` 字段：

```json
{
  "meta": {
    "title": "三体1：地球往事",
    "batchInterface": {
      "entryFrom": ["ch6_raid_005"],
      "exitTo": ["ch6_confess_001"],
      "type": "side_branch"
    }
  }
}
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|:----:|------|
| `entryFrom` | 是 | 本批次的入口——主线中哪个节点应该有选项指向本批次的起始节点 |
| `exitTo` | 是 | 本批次的出口——本批次结束时应该指向哪个主线节点 |
| `type` | 是 | `main`（主线批次）/ `side_branch`（支线）/ `ending_pack`（结局补完）/ `rash`（草率结局） |

### type 的含义

- **main**：按顺序衔接的主线批次，通过 `BATCH_TRANSITIONS` 配置衔接
- **side_branch**：可选支线（红岸回忆、叶文洁心理管线等），需要在主线指定入口节点添加选项
- **ending_pack**：补充结局的批次，需要在主线关键分支点添加路由或选项
- **rash**：草率结局批次，需要在主线错误选择点添加短路选项

---

## 二、入口连接验证（必须）

写完批次后，**必须修改主线批次文件**，在 `entryFrom` 声明的节点中添加指向本批次的 choices 或 routes。

```python
# 验证方法
python scripts/merge-game.py --strict
```

严格模式会检查：
1. `entryFrom` 中的节点是否有 choices/next/routes 指向本批次
2. `exitTo` 中的节点在合并后是否存在
3. 全图可达性（从 startNodeId 出发所有节点可达）
4. 无引用断裂

---

## 三、禁止事项

- **不要创建自循环占位符节点**（`next` 指向自身且无 choices/routes）
- **中间章节不要用 `isEnding: true`**——如果玩家需要继续，用 `next` 或 `choices` 连接
- **不要引用不存在的节点 ID**——先确认目标节点在哪个批次中
- **不要只声明入口但不修改主线**——`batchInterface.entryFrom` 是承诺，必须兑现

---

## 四、提交检查清单

```
□ batchInterface 声明完整（entryFrom + exitTo + type）
□ 主线批次已修改：entryFrom 节点有指向本批次的 choices/routes
□ 无自循环占位符节点
□ exitTo 指向的节点在已有批次中存在
□ 运行 python scripts/merge-game.py --strict 通过
□ 所有节点可达
□ 无引用断裂
```

---

## 五、示例

### 正确做法

```json
// 三体1-第H1批-红岸（上）.json
{
  "meta": {
    "title": "三体1：地球往事",
    "batchInterface": {
      "entryFrom": ["ch6_raid_005"],
      "exitTo": ["hy_ye_013"],
      "type": "side_branch"
    }
  },
  "startNodeId": "hy_ye_001",
  "nodes": { ... }
}
```

同时修改 `三体1-第Y1批` 的 `ch6_raid_005`，添加：
```json
{ "text": "回忆她说过的话", "next": "hy_ye_001" }
```

### 错误做法

```json
// ❌ 声明了 entryFrom 但没有修改主线
"batchInterface": {
  "entryFrom": ["ch6_raid_005"],  // 声明了
  "exitTo": ["ch6_confess_001"]
}
// ch6_raid_005 实际上没有指向本批次的任何选项
```
