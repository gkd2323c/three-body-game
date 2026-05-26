# 三体 · 互动文游 — 开发规则

> 本文档面向继任 AI Agent，明确本项目的开发规范、工作流与质量红线。
> 每次接手开发任务前，先读此文件。

---

## 一、项目概要

将刘慈欣《三体》（地球往事第一部）改编为可游玩的 JSON 格式分支剧情互动游戏。
使用 `story-to-game` 技能（九步工作流）进行改编。部署于 Cloudflare Pages。

| 项目 | 内容 |
|------|------|
| 原著 | 《三体》，刘慈欣，约 20 万字 |
| 预估规模 | 5000-6000 节点，10-12 批 |
| 当前进度 | 第 2 批完成，共 115 节点 |
| 许可证 | CC BY-NC-SA 4.0（改编内容）/ MIT（技能代码） |
| 线上地址 | https://threebody.gkd2323c.in |
| GitHub 仓库 | https://github.com/gkd2323c/three-body-game |

---

## 二、仓库结构

```
three-body-game/
├── AGENTS.md                 # 本文件
├── README.md                 # 项目说明
├── LICENSE                   # CC BY-NC-SA 4.0
├── .gitignore
├── scripts/
│   └── merge-game.py         # 批次合并脚本（Cloudflare 构建命令）
├── output/                   # 开发输出（分批 JSON）
│   ├── 三体-第一批-序幕+疯狂年代.json
│   └── 三体-第二批-三体游戏.json
├── site/                     # 网站根目录（Cloudflare Pages 输出目录）
│   ├── index.html            # 游戏菜单首页
│   ├── _redirects
│   ├── assets/
│   │   └── style.css
│   ├── episodes/
│   │   └── game.json         # 合并后的完整游戏（由 merge-game.py 生成，勿手动改）
│   └── play/
│       └── launcher.html     # 游戏启动器（山音原版 + URL 参数加载）
├── docs/
│   ├── 三体1-互动改编方案.md
│   └── 三体1-改编方案-修订补充.md
└── skills/                   # story-to-game 技能文件（来自 Shanyin-ai/Story-to-game）
    ├── SKILL.md
    ├── references/
    └── scripts/
        └── validate.py
```

---

## 三、开发工作流

### 3.1 写新批次

1. **在 `output/` 中创建批次 JSON 文件**
   - 文件名格式：`三体-第N批-内容描述.json`
   - 每个批次 80-120 节点
   - 遵循 `story-to-game` 技能的全部写作规则（见 `skills/SKILL.md`）

2. **更新 `scripts/merge-game.py` 中的 BATCH_TRANSITIONS**
   ```python
   BATCH_TRANSITIONS = {
       "batch1_end": "transition_001",          # 第1批 → 第2批
       "return_003": "<下一批起始节点ID>",        # 第2批 → 第3批
   }
   ```
   每个新批次添加一行：上一批的结束节点 → 本批的起始节点。

3. **提交并推送**
   ```bash
   git add output/ scripts/
   git commit -m "batch N: 内容描述"
   git push
   ```
   Cloudflare Pages 自动运行 `python scripts/merge-game.py --validate`，
   合并所有批次为 `site/episodes/game.json` 并部署。

### 3.2 批次文件结构要求

每个批次 JSON 必须包含：

```json
{
  "meta": { "title": "三体", "author": "刘慈欣", "variableName": "余烬", ... },
  "startNodeId": "...",
  "variables": { "wenjie_trust": 5, "game_depth": 0, ... },
  "achievements": { ... },
  "nodes": { ... }
}
```

- `meta.title` 在所有批次中保持一致（均为"三体"）
- 批次最后一个节点必须有 choices 自环作为"待续"占位（如 `return_003`）
- 节点 ID 使用英文、数字、下划线，不得跨批次冲突

### 3.3 合并不涉及的工作

- `site/episodes/game.json` 由 CI 自动生成，**不要手动编辑**
- `site/play/launcher.html` 只需在首次部署时修改（已改好）
- `site/index.html` 仅当需要修改菜单文案时更新

---

## 四、叙事与写作规范

### 4.1 改编边界

允许以下再创作：
- 为游戏体验补充过渡场景和衔接节点
- 在线性叙事基础上设计态度/路径/命运分支
- 为角色对白增加游戏互动性

禁止以下操作：
- **改变原著的关键情节和结局走向**
- **在角色未获得信息的阶段透露后续真相**（如叶文洁不能提前透露智子和舰队）
- 添加与原著设定矛盾的物理/科学规则
- 在选项中出现玩家尚未获知的人名/概念

### 4.2 风格锚点（刘慈欣《三体》）

| 维度 | 规则 |
|------|------|
| 叙述温度 | **冷叙述 + 克制抒情**。写灾难像写天气预报，悲伤靠细节暗示 |
| 对白 | 科学家对话偏书面精确，史强全口语化 |
| 科学概念 | 保持准确，不做简化歪曲 |
| 禁区 | 不煽情、不做道德评价、不进入角色内心做心理描写 |
| 选项格式 | 说话写台词加双引号，动作直接写动作，禁止"说XXX"格式 |

### 4.3 互动设计纪律

- 每 1-5 句正文必须给一次互动（可以是单选项确认）
- 选项字数：态度选项 2-6 字，行动选项 4-10 字
- 每个选择必须有回响（下一屏文字因选择不同而有变化）
- 态度选项不用「是/否」——用情境化的两个不同表达
- 三体游戏部分设计为"线性 + 关键选择"，而非网格式分支

### 4.4 状态系统（余烬值）

| 变量 | 类型 | 初始 | 说明 |
|------|------|:----:|------|
| 余烬 | int 0-100 | 35 | 对文明的信心 |
| wenjie_trust | int 0-10 | 5 | 与叶文洁的信任度 |
| game_depth | int 0-10 | 0 | 三体游戏探索深度 |
| know_truth | bool | false | 是否知晓三体文明真相 |
| eto_stance | str | "对抗" | 对ETO的立场 |
| shi_qiang_bond | int 0-10 | 3 | 与史强的默契度 |
| despair_count | int | 0 | 对人类失望的累计次数 |
| avoid_count | int | 0 | 选择逃避的累计次数 |

余烬值变化幅度：日常选择 ±2-5，重大事件 ±10-15。
despair_count 和 avoid_count 用于分支结局的宽松判定，不要忘记在相关选择中累加。

---

## 五、批次衔接规则

各批次的叙事流向必须形成一条连续的时间线。

当前已发布的批次衔接：

```
第1批（序幕+疯狂年代）               第2批（三体游戏）
  prologue_001 → ... → memory_end_004 → transition_001 → ... → return_003
```

新增第3批时：
1. 第2批的结束节点是 `return_003`（汪淼从三体游戏回到现实，去见常伟思的路上）
2. 第3批应从常伟思办公室开始（第2批结尾的"去见常伟思"自然延续到第3批）
3. 在 `merge-game.py` 中添加：`"return_003": "常伟思见面节点ID"`

---

## 六、质量红线

每次提交前必须确保：
- ✅ 所有节点从 `startNodeId` 可达
- ✅ 无引用断裂（所有 `next`/`choices[].next`/`routes[].next` 指向存在的节点）
- ✅ 无死胡同（每个非 ending 节点都有 choices 或 next 或 routes）
- ✅ 无元叙事词汇（"玩家"不应出现在游戏世界的对白中）
- 可接受的问题：无结局节点（批次开发中的正常状态）、callback 等警告

### 验证命令

```bash
python3 scripts/merge-game.py --validate
```

---

## 七、Cloudflare Pages

| 配置 | 值 |
|------|-----|
| 项目名 | three-body-game |
| 构建命令 | `python scripts/merge-game.py --validate` |
| 输出目录 | `site` |
| 根目录 | 留空 |
| 域名 | threebody.gkd2323c.in（自定义） |
| Pages 域名 | three-body-game.pages.dev |

GitHub 集成已就绪：每次 `git push master` 自动构建部署。

---

## 八、参考资料

- 完整改编方案：`docs/三体1-互动改编方案.md`
- 修订补充：`docs/三体1-改编方案-修订补充.md`
- story-to-game 工作流：`skills/SKILL.md`
- JSON 格式规范：`skills/references/json-format-spec.md`
- 写作规则：`skills/references/step5-writing.md`
- 验证脚本：`skills/scripts/validate.py`
