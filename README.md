# 三体 → 互动文游改编项目

基于 story-to-game 技能，将刘慈欣《三体》改编为分支剧情互动游戏（JSON 格式，
兼容「分支剧情游戏启动器」）。

## 项目结构

```
three-body-game/
├── README.md              # 本文件
├── .gitignore
├── docs/                  # 方案文档
│   ├── 三体1-互动改编方案.md       # 完整改编规划设计
│   └── 三体1-改编方案-修订补充.md  # 基于审查反馈的修订
├── output/                # 输出 JSON（分批）
│   └── 三体-第一批-序幕+疯狂年代.json  # 第一批 64 节点
└── skills/                # story-to-game 技能文件
    ├── SKILL.md
    ├── references/        # 细分规则文档（7 份）
    └── scripts/
        └── validate.py    # JSON 验证脚本
```

## 状态

- 改编对象：三体（地球往事第一部）
- 预估规模：5000-6000 节点，10-12 批
- 当前进度：第 1 批完成（序幕 + 疯狂年代前段，64 节点）

## 声明

本项目是刘慈欣《三体》（地球往事第一部）的衍生互动改编作品。

- 原著版权归 **刘慈欣** 所有。
- `docs/`、`output/` 目录下的改编方案文档与 JSON 叙事内容采用 **CC BY-NC-SA 4.0** 许可——您可以自由共享和改编，但须署名、非商业使用、以相同方式共享。
- `skills/` 目录下的 story-to-game 技能代码（来自 [Shanyin-ai/Story-to-game](https://github.com/Shanyin-ai/Story-to-game)）遵循其原有的 **MIT** 许可证。

## 使用方式

1. 下载 `故事剧情游戏启动器.html`（见原项目 Shanyin-ai/Story-to-game）
2. 用 Chrome/Edge 打开
3. 点击「插入JSON剧本」，选择 `output/` 下的 JSON 文件
4. 开始游玩

## 验证

```bash
python skills/scripts/validate.py output/三体-第一批-序幕+疯狂年代.json
```
