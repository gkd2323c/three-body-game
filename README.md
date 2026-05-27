# 三体 · 互动文游

将刘慈欣《三体》三部曲改编为分支剧情互动游戏。纯前端，浏览器运行，无需部署。

**线上体验**：https://threebody.gkd2323c.in

---

## 当前状态

| 部 | 批次 | 节点 | 结局 | 成就 | 状态 |
|:--|:---:|:----:|:----:|:----:|:----|
| 第一部 · 地球往事 | **18** | **236** | **14** | **33** | ✅ 已完结 |
| 第二部 · 黑暗森林 | **13** | **322** | **12** | **35** | ✅ 已完结 |
| 第三部 · 死神永生 | — | — | — | — | 📅 待启动 |

### 第一部 · 14 结局

| 类型 | 结局 |
|:----|:------|
| 🎯 TRUE ENDING | 虫子（从未被战胜） |
| 👁️ SPECIAL ENDING | 射手与农场主 |
| 📥 NORMAL ENDING | 降临 / 冬眠 |
| 🌑 BRANCH ENDING | 深渊（回响） |
| 🧩 HIDDEN ENDING | 破壁人 |
| 💀 RASH ENDING | 第零日 / 崩坏 / 归零 / 无尽的游戏 / 暴露 / 切割 |

### 第二部 · 12 结局

| 类型 | 结局 |
|:----|:------|
| 🎯 TRUE ENDING | 黑暗森林 |
| 🐜 SPECIAL ENDING | 褐蚁 |
| 📥 NORMAL ENDING | 在末日等你 / 沉默的见证者 |
| 🌑 BRANCH ENDING | 星舰地球 / 阴影中的殉道者 / 钢印族 |
| 🧩 HIDDEN ENDING | 另一个伊文斯 |
| 💀 RASH ENDING | 第四位的陨落 / 过线 / 拒绝时间 / 太空遗骸 |

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
├── archive/                     # 旧批次存档（6 批）
├── output/
│   ├── three-body-1/            # 第一部批次 JSON（18 批纯新版）
│   └── three-body-2/            # 第二部批次 JSON（13 批）
├── site/                        # 网站根目录（Cloudflare Pages）
│   ├── index.html               # 三部曲入口
│   ├── three-body-1/            # 第一部（game.json + 入口）
│   ├── three-body-2/            # 第二部
│   ├── three-body-3/            # 第三部
│   └── play/launcher.html       # 共享游戏启动器
├── docs/
│   ├── three-body-1/            # 第一部规划文档（索引/风格/拓扑/状态）
│   └── three-body-2/            # 第二部规划文档
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
# 1. 在 output/three-body-1/ 或 output/three-body-2/ 创建批次 JSON
# 2. 更新对应合并脚本的 BATCH_TRANSITIONS
# 3. 合并验证
python scripts/merge-game.py --validate    # 第一部
python scripts/merge-game-2.py --validate  # 第二部
# 4. 提交（CI 自动部署）
git add output/ scripts/ site/ && git commit && git push
```

### 验证

```bash
python scripts/merge-game.py --validate     # 第一部
python scripts/merge-game-2.py --validate   # 第二部
```

Cloudflare Pages 构建命令已配置为自动运行 `python scripts/merge-game.py --validate && python scripts/merge-game-2.py --validate`。

验证项：节点可达性、引用完整性、无死胡同、无元叙事词汇。正文字数 ≥ 2000（长篇）或 ≥ 800（短篇）。

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
