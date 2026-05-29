# 分支剧情游戏 JSON 格式规范

本文档是 JSON 写作的速查手册。写作时遇到格式疑问，查阅本文档。

## 顶层结构

```json
{
  "meta": {},
  "startNodeId": "start",
  "variables": {},
  "achievements": {},
  "nodes": {}
}
```

## meta 字段

```json
{
  "meta": {
    "title": "作品标题",
    "author": "作者名",
    "version": "1.0.0",
    "description": "作品简介",
    "theme": "noir",
    "ambient": "rain",
    "cover": {
      "label": "封面短标签",
      "tagline": "作品气质短句"
    },
    "variableName": "主状态值名称",
    "initialVariable": 35
  }
}
```

不使用 `subtitle`。

### theme 可选值

| theme | 气质 |
|-------|------|
| `noir` | 黑色电影、悬疑、冷硬 |
| `paper` | 纸页、文学、安静 |
| `tide` | 海潮、湿冷、蓝灰 |
| `summer` | 闷热、南方、燥热 |
| `night` | 深夜、孤独、蓝黑 |
| `blood` | 危险、暗红、压迫 |
| `void` | 空白、虚无、极简 |

### ambient 可选值

| ambient | 效果 |
|---------|------|
| `none` | 无环境效果 |
| `rain` | 雨线、潮湿感 |
| `wind` | 风、横向流动 |
| `sea` | 海潮、水面呼吸 |
| `heat` | 热浪、闷热扭曲 |
| `static` | 电流、信号、档案噪声 |

## 节点 nodes

```json
{
  "nodes": {
    "node_id": {
      "chapterTitle": "章节标题",
      "title": "场景标题",
      "scene": {
        "id": "scene_id",
        "name": "场景名",
        "description": "场景环境描述",
        "arrival": "到达时的叙述"
      },
      "progress": 5,
      "theme": "noir",
      "ambient": "rain",
      "segments": [],
      "choices": [],
      "next": "next_node_id",
      "routes": [],
      "isEnding": false
    }
  }
}
```

节点 ID 使用英文、数字、下划线。

### scene 场景

`scene` 告诉玩家当前叙述发生在哪里。分为大场景和过场场景两种。

**简写形式**（仅场景名，默认按大场景处理）：
```json
{ "scene": "旧公寓门前" }
```

**完整形式**：
```json
{
  "scene": {
    "id": "old_apartment",
    "name": "旧公寓门前",
    "type": "major",
    "description": "雨水沿着楼道边缘往下淌，门缝里压着一封没有署名的信。",
    "arrival": "你在这里停下脚步。",
    "duration": 1900
  }
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | 建议 | 场景唯一标识。同一场景跨多个节点时必须一致 |
| `name` | 是 | 场景名，转场主标题。写地点不写情绪 |
| `type` | 否 | `major`（大场景，切换时显示场景卡片）或 `transient`（过场，只更新位置不播动画）。默认 `major` |
| `description` | 建议 | 稳定环境描写（光线、声音、空间关系） |
| `arrival` | 否 | 本次进入场景的动作/叙述 |
| `duration` | 否 | 转场时长（毫秒），不写则用默认值 |

**大场景 major**：连续多个节点共用的稳定地点。切换时显示非全屏场景卡片。
```json
{
  "scene": {
    "id": "factory_clinic",
    "name": "厂医办公室",
    "type": "major",
    "description": "药柜贴着墙排开，窗外的厂区广播时断时续。",
    "arrival": "你推门进去，屋里的人同时抬头。"
  }
}
```

**过场场景 transient**：一闪而过的地点或瞬间。只更新当前位置标记，不播放转场动画。
```json
{
  "scene": {
    "id": "stairwell_flash",
    "name": "楼梯间",
    "type": "transient",
    "description": "灯管闪了一下。"
  }
}
```

**写作要求**：
- `name`：写地点，如"厂医办公室"、"大烟囱顶"、"旧公寓门前"
- `description`：写稳定不变的环境特征（光线、声音、空间）
- `arrival`：写本次来到这个地方时的动作或感受
- 场景 ≠ 章节。章节管结构，场景管空间和沉浸感
- 同一 `scene.id` 跨节点不重复触发转场
- 建议每个有正文的节点都写 scene

### chapterTitle 使用规则

`chapterTitle` 只在章节/幕的第一个节点设置，用于触发章节过渡动画。不要每个节点都写。

```json
{
  "chapter_02_start": {
    "chapterTitle": "第二章：潮声之前",
    "segments": [
      { "text": "第二天清晨，雨停了。" }
    ],
    "choices": [
      { "text": "走向车站", "next": "station_001" }
    ]
  }
}
```

当多条分支路径都可能进入新章节时，确保所有入口都指向同一个带 chapterTitle 的节点。

## 段落 segments

```json
{
  "segments": [
    { "speaker": "系统", "text": "旁白内容。", "effect": "breath" },
    { "text": "普通叙述。" },
    { "speaker": "角色名", "text": "对白内容。" },
    { "text": "多特效段落。", "effects": ["glitch", "noise"] }
  ]
}
```

- `speaker` 不写则为普通叙述
- `speaker` 为 `系统`、`System`、`旁白`、`Narrator` 时显示为旁白样式
- text 为纯文本，不支持 HTML

## 选项 choices

```json
{
  "choices": [
    {
      "text": "选项文本",
      "next": "目标节点ID",
      "condition": "val >= 60",
      "effect": "flash",
      "changes": {
        "val": 12,
        "valSet": 50,
        "set": { "key": "value" },
        "addFlag": "flag_name",
        "importantFlag": "key_decision",
        "importantFlag": { "flag": "key_decision", "label": "做出关键选择" },
        "removeFlag": "flag_name",
        "unlockAchievement": "achievement_id",
        "unlockAchievements": ["id1", "id2"]
      }
    }
  ]
}
```

## 主状态值 val

- 范围 0-100，自动钳制
- `"val": 10` 表示在当前值上 +10
- `"valSet": 50` 表示直接设为 50

## 条件 condition

字符串格式：
```
val >= 60
val <= 30
val > 50
val < 20
val == 80
val != 0
trust >= 2
route == 'true'
hasFlag 'flag_name'
!hasFlag 'flag_name'
default
```

对象格式：
```json
{ "all": [ { "var": "val", "op": ">=", "value": 55 }, { "flag": "checked_envelope" } ] }
{ "any": [ { "var": "val", "op": "<", "value": 20 }, { "flag": "panic" } ] }
{ "not": { "flag": "safe" } }
```

## 自动路由 routes

```json
{
  "routes": [
    { "condition": "val >= 70", "next": "ending_clear" },
    { "condition": "val < 30", "next": "ending_lost" },
    { "condition": "default", "next": "normal_path" }
  ]
}
```

按数组顺序判断，第一个满足的生效。建议最后放 `default`。

## 自动跳转 next

无选项时自动进入下一节点：
```json
{ "segments": [...], "next": "next_node" }
```

建议优先用单选项代替 next，维持参与感。

## 成就 achievements

定义：
```json
{
  "achievements": {
    "achievement_id": {
      "title": "成就标题",
      "description": "成就描述。"
    }
  }
}
```

选项中解锁：`"unlockAchievement": "id"` 或 `"unlockAchievements": ["id1", "id2"]`

## 结局 endings

```json
{
  "ending_id": {
    "isEnding": true,
    "title": "结局标题",
    "type": "TRUE ENDING",
    "progress": 100,
    "ambient": "sea",
    "achievement": "achievement_id",
    "description": "结局正文。",
    "closing": "最后留给玩家的收束语。",
    "effect": "breath",
    "effects": ["flash", "silence"]
  }
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `isEnding` | 是 | 必须为 `true` |
| `title` | 是 | 结局标题 |
| `type` | 否 | 结局类型 |
| `description` | 是 | 结局正文 |
| `closing` | 是 | 结局收束语。余韵、反讽、遗憾、确认、回声或一句落幕 |
| `progress` | 否 | 通常写 100 |
| `ambient` | 否 | 结局氛围 |
| `effect`/`effects` | 否 | 结局特效 |
| `achievement` | 否 | 抵达结局时解锁的成就 |

`description` 是结局的主体叙述（发生了什么），`closing` 是最后的余韵（留给玩家的感受）。播放器会将两者连接显示。

结局 type 可选值：
- `RASH ENDING` — 草率结局
- `BRANCH ENDING` — 分支结局
- `NORMAL ENDING` — 普通结局
- `TRUE ENDING` — 真结局
- `HIDDEN ENDING` — 隐藏结局
- `SPECIAL ENDING` — 特殊结局

## 特效 effect 可选值

| effect | 用途 |
|--------|------|
| `shake` | 震动、撞击、惊吓 |
| `blur` | 模糊、恍惚、失焦 |
| `noise` | 电流、录音、信号干扰 |
| `flash` | 闪白、瞬间冲击 |
| `blackout` | 黑屏、昏迷、切断 |
| `silence` | 静默、环境被抽空 |
| `pulse` | 心跳、压迫、紧张 |
| `breath` | 呼吸、微弱明暗变化 |
| `glitch` | 错位、系统错误、现实断裂 |
| `drown` | 水下、窒息、潮水涌入 |
| `heat` | 热浪、眩晕、闷热 |
| `cold` | 冷光、退色、寒意 |
| `blood` | 暗红压迫、危险 |

## Flags

**普通 flag：**
添加：`"addFlag": "flag_name"`
多个：`"addFlags": ["flag_a", "flag_b"]`
移除：`"removeFlag": "flag_name"`
判断：`"condition": "hasFlag 'flag_name'"` 或 `"condition": "!hasFlag 'flag_name'"`

**重要 flag（会显示浮动提示）：**

当一个 flag 标记的是影响结局走向的关键决定时，使用 importantFlag。播放器会短暂浮出提示"重要决定已记录"，让玩家意识到这个选择有分量。

```json
{ "changes": { "importantFlag": "saved_lin" } }
```

带标签（提示显示为"重要决定已记录：拆开信封"）：
```json
{ "changes": { "importantFlag": { "flag": "opened_letter", "label": "拆开信封" } } }
```

多个重要 flag：
```json
{ "changes": { "importantFlags": ["saved_lin", "found_truth"] } }
```

兼容写法（在普通 addFlag 中标记 important）：
```json
{ "changes": { "addFlag": "saved_lin", "important": true } }
```

**使用场景：**
- 决定结局走向的关键选择 → importantFlag
- 日常的状态记录（检查过抽屉、读过一封信）→ 普通 addFlag
- 不是每个 flag 都要标记为 important——只有真正影响结局分流的 2-5 个关键决定才用

## 自定义变量 variables

定义初始值：
```json
{ "variables": { "letterOpened": false, "trust": 0, "route": "normal" } }
```

赋值（直接赋值，非加减）：
```json
{ "changes": { "set": { "letterOpened": true, "trust": 2 } } }
```
