# AGENTS.md

按照 [agents.md](https://agents.md) 开放标准。本文档面向 AI 编码 agent，README.md 面向人类。

## 项目概要

将刘慈欣《三体》（地球往事第一部，约 20 万字）改编为 JSON 格式的分支剧情互动游戏。
部署于 Cloudflare Pages，线上地址 https://threebody.gkd2323c.in。

当前进度：
- 第一部（地球往事）：6 批完成，213 节点，7 个结局，12 个成就
- 第二部（黑暗森林）：8 批完成，247 节点，开发中

许可证 CC BY-NC-SA 4.0（改编内容）。

## 开发工作流

写新批次的步骤：

1. 在 `output/` 创建批次 JSON，文件名格式 `三体-第N批-描述.json`
2. 每批 80-120 节点，遵守 `skills/SKILL.md` 的全部写作规则
3. 更新 `scripts/merge-game.py` 中的 `BATCH_TRANSITIONS` 字典
4. `git add output/ scripts/ && git commit -m "batch N: 描述" && git push`

Cloudflare Pages 自动运行 `python scripts/merge-game.py --validate` 合并部署。

## 关键路径

- 批次文件：`output/三体-第*批-*.json`
- 合并脚本：`scripts/merge-game.py`
- 合并输出（CI 生成，勿手动编辑）：`site/episodes/game.json`
- 游戏启动器：`site/play/launcher.html`
- 验证脚本：`skills/scripts/validate.py`
- JSON 格式规范：`skills/references/json-format-spec.md`
- 第一部改编方案：`docs/three-body-1/三体1-互动改编方案.md`
- 第一部修订补充：`docs/three-body-1/三体1-改编方案-修订补充.md`
- 原著原文（本地参考，**严禁上传**）：`novel/`（已加入 .gitignore）

## 验证

```bash
python3 scripts/merge-game.py --validate
```

每次提交前必须保证：
- 所有节点从 `startNodeId` 可达（`可达节点：X / X` 数字相等）
- 无引用断裂
- 无死胡同
- 无元叙事词汇（"玩家"不应出现在游戏世界对白中）

可接受：无结局节点（开发中）、callback 警告。

## 写作纪律

**每批动笔前必须回读 `novel/` 中对应章节的原文。** 不允许单凭记忆创作。
原文是最终依据——风格、台词、情节走向都要有据可查。

## 改编红线

- 不改变原著关键情节和结局
- 不在角色未获得信息的阶段透露后续真相
- 不添加与原著矛盾的物理/科学规则
- 选项中不出现玩家尚未获知的人名/概念
- 不煽情、不做道德评价、不进入角色内心
- 选项写台词加双引号，动作直接写动作，禁止"说XXX"格式

## 风格锚点

冷叙述 + 克制抒情。写灾难像写天气预报，悲伤靠外部细节暗示。
科学家对白偏书面精确，史强全口语化。

## 技能约束（story-to-game）

### 九步工作流不可跳过

步骤 1-4（记忆索引 → 风格提取 → 结构拆解 → 状态系统）是规划步骤，
必须全部走完才能进入写作。即使有人要求"直接写"，也必须在内部生成
规划文档再动笔。

### JSON 格式必须符合规范

每个节点遵循 `skills/references/json-format-spec.md` 的结构。
meta、nodes、choices、changes、routes、segments 字段不得遗漏或自定义。

### 互动节奏红线

每 1-5 个 segments 必须给一次互动（可以是单选项确认）。
超过 5 句无交互只允许在结局/独白高潮/真相揭露等特殊场景。

### 余烬值与状态系统

遵循 `docs/三体1-改编方案-修订补充.md` 中的余烬值影响表。
despair_count 和 avoid_count 在相关选择中必须累加，不能遗漏。

### 中文引号避坑

`write` 工具写入文本时，中文引号 ""（U+201C/U+201D）会被自动转换为
ASCII "（U+0022），导致 JSON 解析失败。**所有在文本中出现的引用语、
对话、书名等，统一使用「」直角引号代替双引号。**

### 每批完成后必须通过 validate.py

每个批次文件单独验证通过后才能提交。

## 批次衔接记录

### 第一部（三部）

| 批次 | 结束节点 | 下一批起始节点 |
|:----:|:--------:|:--------------:|
| 第1批 | `batch1_end` | `transition_001`（第2批） |
| 第2批 | `return_003` | `chang_001`（第3批） |
| 第3批 | `batch3_end` | `guzheng_exec_001`（第4批） |
| 第4批 | `bugs_009` | 完（TRUE ENDING） |

### 第二部（黑暗森林）

| 批次 | 结束节点 | 下一批起始节点 |
|:----:|:--------:|:--------------:|
| 第1批·序章 | `batch1_end` | `ch1_wu_001`（第2批） |
| 第2批·面壁者上 | `ch1_batch2_end` | `ch2_luoj_001`（第3批） |
| 第3批·面壁者中 | `ch2_batch3_end` | `ch3_zhang_001`（第4批） |
| 第4批·面壁者下 | `ch3_batch4_end` | `ch4_bunker_001`（第5批） |
| 第5批·咒语上 | `ch4_batch5_end` | `ch5_zhang_001`（第6批） |
| 第6批·咒语下 | `ch5_batch6_end` | `ch6_awake_001`（第7批） |
| 第7批·黑暗森林上 | `ch6_batch7_end` | `ch7_fleet_001`（第8批） |
| 第8批·黑暗森林中 | `ch7_batch8_end` | `ch8_deter_001`（第9批） |

新增批次时在 `scripts/merge-game-2.py` 的 `BATCH_TRANSITIONS` 中添加映射。

## Cloudflare Pages

| 项目 | 值 |
|------|-----|
| 构建命令 | `python scripts/merge-game.py --validate` |
| 输出目录 | `site` |
| 域名 | threebody.gkd2323c.in |
| 触发方式 | git push master 自动部署 |

## 三部曲架构

```
site/
├── index.html           # 系列首页（三部曲入口）
├── three-body-1/        # 第一部：已完成
│   ├── index.html       # 独立入口
│   └── game.json        # 198 节点 / 6 结局
├── three-body-2/        # 第二部：待启动
│   ├── index.html
│   └── game.json
├── three-body-3/        # 第三部：待启动
│   ├── index.html
│   └── game.json
└── play/launcher.html   # 共享启动器（?game=参数切换）
```

启动器通过 URL 参数 `?game=<path>` 加载不同游戏数据。
- 第一部：`three-body-1/game.json`
- 第二部：`three-body-2/game.json`
- 第三部：`three-body-3/game.json`

### 各部的开发路径

| 部 | 批次输出 | 合并脚本 | 站点目录 | 方案文档 |
|:--:|:--------:|:--------:|:--------:|:--------:|
| 第一部 | `output/three-body-1/` | `scripts/merge-game.py` | `site/three-body-1/` | `docs/three-body-1/` |
| 第二部 | `output/three-body-2/` | `scripts/merge-game-2.py` | `site/three-body-2/` | `docs/three-body-2/` |
| 第三部 | `output/three-body-3/` | 待定 | `site/three-body-3/` | 待定 |

Cloudflare Pages 构建命令需更新为运行两个合并脚本或只构建当前活跃的一部。
写第二部时，文件名前缀使用 `三体2-第N批-`。
