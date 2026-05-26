# 三体 · 互动文游

将刘慈欣《三体》三部曲改编为分支剧情互动游戏。纯前端，浏览器运行，无需部署。

**线上体验**：https://threebody.gkd2323c.in

---

## 当前状态

| 部 | 节点 | 结局 | 状态 |
|:--|:---:|:----:|:----|
| 第一部 · 三体 | **215** | **7** | ✅ 已完结 |
| 第二部 · 黑暗森林 | — | — | ⏳ 框架就绪 |
| 第三部 · 死神永生 | — | — | 📅 待启动 |

第一部已实现完整主线 + 7 个分支结局，可直接通关。

### 7 个结局

- 🌾 **虫子（从未被战胜）** — TRUE ENDING
- 📥 **降临（一厢情愿的救世）** — NORMAL ENDING
- ❄️ **冬眠（错过的时代）** — NORMAL ENDING
- 🔪 **切割（一线之隔）** — RASH ENDING
- 🎮 **无尽游戏（文明的抽屉）** — HIDDEN ENDING
- 🧩 **破壁人** — HIDDEN ENDING
- 🌑 **深渊（回响）** — BRANCH ENDING

---

## 项目结构

```
three-body-game/
├── AGENTS.md                    # AI 开发规则
├── README.md
├── LICENSE                      # CC BY-NC-SA 4.0
├── scripts/
│   ├── merge-game.py            # 第一部合并脚本（CI 自动运行）
│   └── merge-game-2.py          # 第二部合并脚本
├── output/
│   ├── three-body-1/            # 第一部批次 JSON（6 批）
│   └── three-body-2/            # 第二部（待写）
├── site/                        # 网站根目录（Cloudflare Pages）
│   ├── index.html               # 三部曲入口
│   ├── three-body-1/            # 第一部（game.json + 入口）
│   ├── three-body-2/            # 第二部
│   ├── three-body-3/            # 第三部
│   └── play/launcher.html       # 共享游戏启动器
├── docs/
│   ├── three-body-1/            # 第一部改编方案
│   └── three-body-2/            # 第二部（待写）
├── skills/                      # story-to-game 工作流
│   ├── SKILL.md                 # 九步写作规则
│   ├── references/              # 细分规则文档（7 份）
│   └── scripts/validate.py      # JSON 验证脚本
└── novel/                       # 原著原文（本地参考，不上传）
```

---

## 开发

### 写新批次

```bash
# 1. 在 output/three-body-1/ 创建批次 JSON
# 2. 更新 scripts/merge-game.py 的 BATCH_TRANSITIONS
# 3. 合并验证
python scripts/merge-game.py --validate
# 4. 提交（CI 自动部署）
git add output/ scripts/ site/ && git commit && git push
```

### 验证

```bash
python scripts/merge-game.py --validate
```

验证项：节点可达性、引用完整性、无死胡同、无元叙事词汇。

---

## 技术栈

- **游戏引擎**：山音 · 分支剧情游戏启动器（单文件 HTML/JS）
- **数据格式**：JSON 剧本（自定义 schema）
- **托管**：Cloudflare Pages（GitHub CI/CD 自动部署）
- **域名**：threebody.gkd2323c.in

---

## 许可证

- 改编内容（`docs/`、`output/`、`site/`）：**CC BY-NC-SA 4.0**
- 技能代码（`skills/`，来自 [Shanyin-ai/Story-to-game](https://github.com/Shanyin-ai/Story-to-game)）：**MIT**
- 原著版权归 **刘慈欣** 所有
