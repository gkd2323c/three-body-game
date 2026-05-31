# 三体3·死神永生 批次写作实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将四份规划文档转化为可游玩的游戏 JSON 批次文件，完成第三部全部 28+ 批次的写作、合并与验证。

**Architecture:** 每个批次是一个独立 JSON 文件，遵循现有三部曲的 schema 规范。批次通过 merge-game-3.py 合并为 site/three-body-3/game.json。每个批次写完后独立验证，确保节点可达、引用完整、无元叙事词汇。

**Tech Stack:** Python 3 (merge/validate scripts), JSON (game data), 无外部依赖

**规划文档引用：**
- `docs/three-body-3/原作索引-三体3死神永生.md` — 事件链、人物卡、场景表
- `docs/three-body-3/风格锚点-三体3死神永生.md` — 叙述温度、对白风格、选项风格、禁区
- `docs/three-body-3/分支拓扑-三体3死神永生.md` — 节拍序列、分支点、回响标记
- `docs/three-body-3/状态与结局设计-三体3死神永生.md` — 双轴属性、变量、flags、结局矩阵

---

## JSON Schema 参考

### 节点基础结构

```json
{
  "node_id": {
    "chapterTitle": "第X章：章节名",
    "scene": {
      "id": "scene_id",
      "name": "场景名称",
      "type": "major|minor",
      "description": "场景描述（首次进入时显示）",
      "arrival": "到达描述"
    },
    "progress": 1-100,
    "theme": "void|paper|noir|blood|night|tide|summer",
    "ambient": "rain|wind|static|sea|heat|none",
    "segments": [
      { "text": "正文文本" },
      { "speaker": "角色名", "text": "对白文本" },
      { "text": "叙述文本", "system": true }
    ],
    "choices": [
      {
        "text": "选项文本（符合程心内心映射）",
        "next": "target_node_id",
        "changes": {
          "val": 5,
          "set": { "flag_name": true, "variable_name": 10 },
          "unlockAchievement": "achievement_id"
        }
      }
    ],
    "next": "auto_advance_node_id",
    "routes": [
      {
        "condition": { "all": [{ "var": "val", "op": ">=", "value": 60 }, { "flag": "some_flag" }] },
        "next": "conditional_node_id"
      },
      { "condition": "default", "next": "fallback_node_id" }
    ],
    "isEnding": true,
    "title": "结局标题",
    "type": "TRUE ENDING|NORMAL ENDING|BRANCH ENDING|HIDDEN ENDING|SPECIAL ENDING|RASH ENDING|META ENDING",
    "description": "结局描述文本",
    "closing": "判词收束语",
    "achievement": "achievement_id"
  }
}
```

### 批次文件结构

```json
{
  "meta": {
    "title": "三体3：死神永生",
    "author": "刘慈欣",
    "version": "1.0.0",
    "description": "给时光以生命，而不是给生命以时光。",
    "theme": "void",
    "ambient": "silence",
    "cover": {
      "label": "死神永生",
      "tagline": "给时光以生命，而不是给生命以时光。"
    },
    "variableName": "人性",
    "initialVariable": 50,
    "batchInterface": {
      "type": "main|bridge|ending|rash",
      "entryFrom": ["entry_node_ids"],
      "exitTo": ["exit_node_ids"]
    }
  },
  "startNodeId": "first_node_id",
  "variables": {
    "deterrence": 50,
    "trust_wade": 0,
    "trust_shizi": 0,
    "guilt_cloud": 0,
    "clue_score": 0,
    "playthrough_count": 0,
    "unlocked_endings_list": [],
    "current_run_type": ""
  },
  "achievements": {},
  "nodes": {}
}
```

---

## Phase 0: 基础设施

### Task 0.1: 创建输出目录

**Files:**
- Create: `output/three-body-3/`

- [ ] **Step 1: 创建目录**

```bash
mkdir -p output/three-body-3
```

- [ ] **Step 2: 验证目录存在**

```bash
ls output/three-body-3
```

- [ ] **Step 3: Commit**

```bash
git add output/three-body-3
git commit -m "chore: 创建第三部输出目录"
```

### Task 0.2: 编写 merge-game-3.py

**Files:**
- Create: `scripts/merge-game-3.py`

- [ ] **Step 1: 复制 merge-game-2.py 并修改为第三部**

基于 `scripts/merge-game-2.py` 模板，修改以下内容：
- OUTPUT 目录 → `output/three-body-3`
- SITE 目录 → `site/three-body-3`
- 文件 glob 模式 → `三体3-第*批-*.json`
- BATCH_TRANSITIONS → 根据分支拓扑文档的章节衔接节点定义

```python
BATCH_TRANSITIONS = {
    "ch1_batch1_end": "ch2_w01_001",     # 第1章→第2章
    "ch2_batch2_end": "ch3_b01_001",     # 第2章→第3章
    "ch3_batch3_end": "ch4_m01_001",     # 第3章→第4章
    "ch4_batch4_end": "ch5_g01_001",     # 第4章→第5章
}
```

- [ ] **Step 2: 验证脚本语法**

```bash
python scripts/merge-game-3.py --help 2>&1 || echo "脚本可运行"
```

- [ ] **Step 3: Commit**

```bash
git add scripts/merge-game-3.py
git commit -m "feat: 添加第三部合并脚本"
```

### Task 0.3: 更新合并配置

**Files:**
- Modify: `site/three-body-3/index.html`

- [ ] **Step 1: 更新 index.html 使其可加载 game.json**

将现有的占位页改为与第一部/第二部相同的结构，添加游戏加载器引用。

- [ ] **Step 2: Commit**

```bash
git add site/three-body-3/index.html
git commit -m "feat: 更新第三部入口页以支持游戏加载"
```

---

## Phase 1: 第1章「云天明」（批次1-4）

每个批次的任务结构相同：

### 写作流程（每个批次）

1. **准备**：阅读分支拓扑中对应批次的节拍序列 + 原作索引中的事件链和场景表 + 风格锚点
2. **写作**：按节拍序列逐节点编写 JSON，每节点包含 scene/segments/choices/changes
3. **自检**：
   - 所有 choices.next 指向的节点 ID 存在于当前批次或已写批次中
   - 每个 choices.text 符合选项文本锚点（程心内心映射）
   - segments 不包含元叙事词汇（玩家/节点/分支/选项）
   - 每 1-5 句正文有互动（choices 或 next）
   - progress 值单调递增
4. **验证**：`python skills/scripts/validate.py output/three-body-3/三体3-第N批-章节名.json`
5. **Commit**

### Task 1.1: 批次1 — 序幕 + 生命选项

**Files:**
- Create: `output/three-body-3/三体3-第1批-序幕.json`

对应分支拓扑：C01-C11（君士坦丁堡1453 + 杨冬生命选项）

- [ ] **Step 1: 编写批次1 JSON**
  - 节点数：约 25-35 个
  - 关键内容：狄奥伦娜的魔法与死亡、高维碎块设定、杨冬的"生命选项"思想实验
  - 分支点1：杨冬的反应（人性±3, 威慑度±2）
  - theme: paper（温暖但脆弱）
  - progress: 1-8

- [ ] **Step 2: 验证**

```bash
python skills/scripts/validate.py output/three-body-3/三体3-第1批-序幕.json
```

- [ ] **Step 3: Commit**

```bash
git add output/three-body-3/三体3-第1批-序幕.json
git commit -m "feat(3-1): 序幕 + 生命选项（25-35节点）"
```

### Task 1.2: 批次2 — 云天明

**Files:**
- Create: `output/three-body-3/三体3-第2批-云天明.json`

对应分支拓扑：C12-C19（云天明病房 + 买星）

- [ ] **Step 1: 编写批次2 JSON**
  - 节点数：约 30-45 个
  - 关键内容：安乐死法、胡文来访、密云水库回忆、购星DX3906
  - 分支点2：云天明对胡文的态度（人性±2/3）
  - theme: paper
  - progress: 8-18

- [ ] **Step 2: 验证**

- [ ] **Step 3: Commit**

```bash
git commit -m "feat(3-2): 云天明 + 买星（30-45节点）"
```

### Task 1.3: 批次3 — 阶梯计划

**Files:**
- Create: `output/three-body-3/三体3-第3批-阶梯计划.json`

对应分支拓扑：C19-C29（PIA + 阶梯计划 + 手术）

- [ ] **Step 1: 编写批次3 JSON**
  - 节点数：约 40-55 个
  - 关键内容：PIA成立、阶梯计划设计、卡拉维拉尔角发射、云天明宣誓、瓦季姆之死、脑切除手术、维德揭露星星真相
  - 分支点3（回响标记 wade_fear/wade_respect）、分支点4（guilt_cloud）、分支点5（回响标记 wade_pity/wade_intimidate）
  - theme: paper → noir
  - progress: 18-30

- [ ] **Step 2: 验证**

- [ ] **Step 3: Commit**

```bash
git commit -m "feat(3-3): 阶梯计划 + 手术（40-55节点）"
```

### Task 1.4: 批次4 — 第一部终章

**Files:**
- Create: `output/three-body-3/三体3-第4批-阶梯飞行.json`

对应分支拓扑：C30-C31（帆索断裂 + 程心冬眠）

- [ ] **Step 1: 编写批次4 JSON**
  - 节点数：约 15-25 个
  - 关键内容：阶梯飞行器发射、1004枚核弹引爆、帆索断裂、程心冬眠
  - 第1章结束节点（batch1_end）
  - theme: noir
  - progress: 30-35

- [ ] **Step 2: 验证**

- [ ] **Step 3: Commit**

```bash
git commit -m "feat(3-4): 阶梯飞行 + 第1章终（15-25节点）"
```

---

## Phase 2: 第2章「执剑人」（批次5-11）

### Task 2.1: 批次5 — 审判 + 追击

**Files:**
- Create: `output/three-body-3/三体3-第5批-审判.json`

对应：C32-C35（青铜时代号审判 + 万有引力号追击）

- [ ] **Step 1: 编写批次5 JSON**
  - 节点数：约 25-35 个
  - 关键内容：返航翻转、军事法庭审判、史耐德警告、蓝色空间号逃离
  - theme: noir
  - progress: 35-40

- [ ] **Step 2-3: 验证 + Commit**

### Task 2.2: 批次6 — 程心苏醒 + 威慑纪元

**Files:**
- Create: `output/three-body-3/三体3-第6批-执剑人（上）.json`

对应：C36-C43（巨树城市 + 维德伏击 + 智子茶道 + 候选人劝告）

- [ ] **Step 1: 编写批次6 JSON**
  - 节点数：约 40-55 个
  - 关键内容：DX3906行星、艾AA、女性化社会、维德枪击、威慑度概念、智子茶道、候选人劝告
  - 分支点6（回响标记 shizi_warm/shizi_unease）
  - **分支点7（大型分歧·快速收束）**：如选A，本批次内完成 6 个快速收束节点
  - theme: noir → night
  - progress: 40-50

- [ ] **Step 2-3: 验证 + Commit**

### Task 2.3: 批次7 — 万有引力号线（平行叙事）

**Files:**
- Create: `output/three-body-3/三体3-第7批-万有引力.json`

对应：C44-C46（万有引力号事件，通过程心事后了解呈现）

- [ ] **Step 1: 编写批次7 JSON**
  - 节点数：约 15-25 个
  - 关键内容：智子盲区、超自然现象、关一帆对话
  - 叙事方式：通过"时间之外的往事"叙述或冬眠后的记录呈现
  - theme: night
  - progress: 50-52

- [ ] **Step 2-3: 验证 + Commit**

### Task 2.4: 批次8 — 执剑人交接 + 威慑失败

**Files:**
- Create: `output/three-body-3/三体3-第8批-执剑人（下）.json`

对应：C47-C51（权力交接 + 水滴攻击 + 威慑失败）——全书最高潮

- [ ] **Step 1: 编写批次8 JSON**
  - 节点数：约 30-45 个
  - 关键内容：罗辑交接（无言仪式）、红色开关、10分钟倒计时、程心内心35亿年演化史、扔掉开关、水滴摧毁发射台、智子揭示威慑度
  - 分支点8（全书最关键）：三选一（A启动广播/B扔掉开关/C犹豫超时）
  - **⊕ 量子毛刺节点 C49**
  - theme: blood
  - progress: 52-58

- [ ] **Step 2-3: 验证 + Commit**

### Task 2.5: 批次9 — 大移民 + 澳大利亚

**Files:**
- Create: `output/three-body-3/三体3-第9批-澳大利亚.json`

对应：C52-C59（三体舰队光速 + 澳大利亚大移民）

- [ ] **Step 1: 编写批次9 JSON**
  - 节点数：约 35-50 个
  - 关键内容：光速舰队、保留地声明、沙漠移民区、弗雷斯收留、维德监狱警告、堪培拉惨案、智子"粮食"宣言、程心失明
  - theme: blood → void
  - progress: 58-65

- [ ] **Step 2-3: 验证 + Commit**

### Task 2.6: 批次10 — 万有引力号广播 + 四维空间

**Files:**
- Create: `output/three-body-3/三体3-第10批-广播.json`

对应：C60-C64（水滴被俘 + 引力波广播 + 四维碎块）

- [ ] **Step 1: 编写批次10 JSON**
  - 节点数：约 25-35 个
  - 关键内容：四维空间伏击水滴、全民公决944票、引力波广播启动、四维碎块探索、"魔戒"对话
  - theme: void
  - progress: 65-68

- [ ] **Step 2-3: 验证 + Commit**

### Task 2.7: 批次11 — 第2章终章

**Files:**
- Create: `output/three-body-3/三体3-第11批-两舰选择.json`

对应：两舰选择（200余人返回/其余深空航行）+ 章节结束

- [ ] **Step 1: 编写批次11 JSON**
  - 节点数：约 10-15 个
  - 第2章结束节点（batch2_end）
  - theme: void
  - progress: 68-70

- [ ] **Step 2-3: 验证 + Commit**

---

## Phase 3: 第3章「星辰大海」（批次12-18）

### Task 3.1-3.7: 批次12-18

结构与 Phase 1-2 相同，每个批次遵循：编写→验证→Commit 流程。

| 批次 | 对应分支拓扑 | 关键内容 | 节点数 |
|:----:|:----------:|---------|:------:|
| 12 | C65-C69 | 程心苏醒+三体毁灭+茶道谈话+自杀阻止+智子告别 | 25-35 |
| 13 | C70-C75 | 云天明通话+三个童话（**clue_score 积分制**） | 40-60 |
| 14 | C76-C81 | 情报解读+香皂纸船顿悟+双层隐喻确认 | 30-40 |
| 15 | C82-C84 | 挪威默斯肯+大旋涡+黑域顿悟 | 20-30 |
| 16 | C85-C88 | 三条路线+假警报+曲率航迹发现+光速飞船被禁 | 25-35 |
| 17 | C89-C91 | 维德回归+星环公司交出（**分支点11：三选一**） | 20-30 |
| 18 | 第3章终章 | 程心冬眠+章节结束 | 8-12 |

---

## Phase 4: 第4章「降维」（批次19-24）

| 批次 | 对应分支拓扑 | 关键内容 | 节点数 |
|:----:|:----------:|---------|:------:|
| 19 | C92-C94 | 掩体世界+高Way黑洞 | 20-30 |
| 20 | C95-C102 | 星环城对峙（**分支点12：大型分歧·镜像平移**）+维德之死 | 35-50 |
| 21 | C103-C107 | 歌者+二向箔到来+白Ice警告 | 25-35 |
| 22 | C108-C111 | 冥王星+罗辑"把字刻在石头上"+行星二维化 | 25-35 |
| 23 | C112-C116 | 欧洲六号二维化+地球雪花+太阳最后日落+罗辑告别 | 25-35 |
| 24 | C117-C119 | 曲率引擎逃亡+飞向DX3906+最后声音 | 15-20 |

---

## Phase 5: 第5章「归零」（批次25-28）

| 批次 | 对应分支拓扑 | 关键内容 | 节点数 |
|:----:|:----------:|---------|:------:|
| 25 | C120-C124 | DX3906+关一帆+蓝星生态 | 20-30 |
| 26 | C125-C131 | 灰星+死线+黑域陷阱+冬眠（**分支点13**） | 25-35 |
| 27 | C132-C136 | 1890万年后+紫星+岩石刻字+小宇宙入口 | 20-30 |
| 28 | C137-C145 | 小宇宙+回归运动（**分支点14/15**）+生态球+TRUE ENDING | 30-45 |

---

## Phase 6: 桥接批次 + 结局路由（批次29-31）

### Task 6.1: 批次29 — 分支结局路由

**Files:**
- Create: `output/three-body-3/三体3-第B1批-分支结局.json`

- [ ] **Step 1: 编写所有 BRANCH ENDING 节点**
  - END_BRANCH_1（威慑维持）：从分支点8选A接入
  - END_BRANCH_2（维德的黎明）：从维德自由线接入
  - END_BRANCH_3（第三条路）：从程心主导线接入
  - END_BRANCH_4（另一个执剑人）：从快速收束接入
  - END_BRANCH_5（星舰地球）：从镜像平移接入

- [ ] **Step 2-3: 验证 + Commit**

### Task 6.2: 批次30 — 隐藏/特殊结局路由

**Files:**
- Create: `output/three-body-3/三体3-第B2批-隐藏结局.json`

- [ ] **Step 1: 编写 HIDDEN + SPECIAL ENDING 节点**
  - END_HIDDEN_1（我们的星星）：蓝星田园
  - END_HIDDEN_2（安全的坟墓）：小宇宙留守
  - END_SPECIAL_1（二维化中的秘密）
  - END_SPECIAL_2（妥协者）

- [ ] **Step 2-3: 验证 + Commit**

### Task 6.3: 批次31 — 草率结局

**Files:**
- Create: `output/three-body-3/三体3-第R批-草率结局.json`

- [ ] **Step 1: 编写所有 RASH ENDING 节点**
  - END_RASH_1 到 END_RASH_8
  - 每个草率结局 3-5 个节点，含收束过渡
  - 每个结局关联一个成就

- [ ] **Step 2-3: 验证 + Commit**

### Task 6.4: 批次32 — Meta 结局路由

**Files:**
- Create: `output/three-body-3/三体3-第M批-meta结局.json`

- [ ] **Step 1: 编写 META ENDING 节点**
  - END_META_BOTTLE（漂流瓶）
  - 触发条件路由：playthrough_count ≥ 3 ∧ unique_types ≥ 3
  - 量子毛刺文本定义（C49/C97/C141 三个节点的毛刺文案）
  - 两档密封状态文案（未全解/全解）

- [ ] **Step 2-3: 验证 + Commit**

---

## Phase 7: 合并与最终验证

### Task 7.1: 全量合并

- [ ] **Step 1: 运行合并脚本**

```bash
python scripts/merge-game-3.py
```

Expected: 输出 `site/three-body-3/game.json`，节点总数 2150-3300

- [ ] **Step 2: 严格验证**

```bash
python scripts/merge-game-3.py --strict
```

Expected: ✅ 全图可达，无引用断裂，无死胡同

- [ ] **Step 3: 宽松验证**

```bash
python scripts/merge-game-3.py --validate
```

Expected: ✅ 合并验证通过

### Task 7.2: 批次接口验证

- [ ] **Step 1: 检查所有 batchInterface 声明兑现**

合并脚本的 `check_batch_interfaces()` 函数会自动验证每个批次声明的 entryFrom/exitTo 是否兑现。

### Task 7.3: 更新 README 和索引

**Files:**
- Modify: `README.md`
- Modify: `site/index.html`

- [ ] **Step 1: 更新 README 中第三部状态为"可游玩"**
- [ ] **Step 2: 更新 site/index.html 中第三部卡片信息**
- [ ] **Step 3: Commit**

```bash
git commit -m "docs: 第三部完结，更新状态和节点数"
```

---

## 写作规则速查（每个批次写作时参考）

### 节点 ID 命名规范
- 格式：`ch{章}_{批次}_{序号}` 或描述性命名
- 示例：`ch1_prologue_01`, `ch2_sword_15`, `ch3_tianming_08`

### 双轴属性变动参考
| 幅度 | 人性 | 威慑度 | 适用场景 |
|:----:|:----:|:------:|:---------|
| ±3-5 | 日常态度 | 日常威慑 | 对话回应、信息获取 |
| ±8-10 | 重要表态 | 关键表态 | 情感爆发、战略决策 |
| ±15-20 | 核心行动 | 核心博弈 | 执剑人抉择、制止维德 |
| 特殊 | 强制设定 | 强制设定 | 剧情锁定 |

### 选项文本铁律
1. 必须是程心的声音（自省/道德两难/克制行动）
2. 信息时序约束（不引用玩家未知信息）
3. 情境匹配（只回应此刻正在发生的事）

### 验证清单（每批次自检）
- [ ] 所有 choices.next 指向的节点 ID 存在
- [ ] 无元叙事词汇（玩家/节点/分支/选项）
- [ ] 每 1-5 句正文有互动
- [ ] progress 单调递增
- [ ] 结局节点有 title/description/closing
- [ ] 同向选项有独立 callback 节点
- [ ] 草率结局有 3-5 个收束节点
