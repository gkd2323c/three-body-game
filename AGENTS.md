# AGENTS.md

按照 [agents.md](https://agents.md) 开放标准。本文档面向 AI 编码 agent，README.md 面向人类。

## 项目概要

将刘慈欣《三体》（地球往事第一部，约 20 万字）改编为 JSON 格式的分支剧情互动游戏。
部署于 Cloudflare Pages，线上地址 https://threebody.gkd2323c.in。

当前进度：2/12 批完成，115 节点。许可证 CC BY-NC-SA 4.0（改编内容）。

## 开发工作流

写新批次的步骤：

1. 在 `output/` 创建批次 JSON，文件名格式 `三体-第N批-描述.json`
2. 每批 80-120 节点，遵守 `skills/SKILL.md` 的全部写作规则
3. 更新 `scripts/merge-game.py` 中的 `BATCH_TRANSITIONS` 字典，添加上一批结束节点 → 本批起始节点的映射
4. `git add output/ scripts/ && git commit -m "batch N: 描述" && git push`

Cloudflare Pages 会自动运行 `python scripts/merge-game.py --validate` 合并所有批次为 `site/episodes/game.json` 并部署。

## 关键路径

- 批次 JSON 文件：`output/三体-第*批-*.json`
- 合并脚本：`scripts/merge-game.py`
- 合并输出（CI 生成，勿手动编辑）：`site/episodes/game.json`
- 网站首页：`site/index.html`
- 游戏启动器：`site/play/launcher.html`
- 验证脚本：`skills/scripts/validate.py`
- 完整改编方案：`docs/三体1-互动改编方案.md`

## 验证命令

```bash
python3 scripts/merge-game.py --validate
```

每次提交前必须保证：
- 所有节点从 `startNodeId` 可达（`可达节点：X / X`，两个数字相等）
- 无引用断裂（`node引用` 不在输出中）
- 无死胡同（每个非 ending 节点都有 choices/next/routes）
- 无元叙事词汇（"玩家"不应出现在游戏世界对白中）

可接受：无结局节点（批次开发中正常状态）、callback 警告。

## 改编红线

- 不改变原著关键情节和结局
- 不在角色未获得信息的阶段透露后续真相（如叶文洁不能提前透露智子和舰队）
- 不添加与原著矛盾的物理/科学规则
- 选项中不出现玩家尚未获知的人名/概念
- 不煽情、不做道德评价、不写角色内心心理描写
- 选项写台词加双引号，动作直接写动作，禁止"说XXX"格式

## 风格锚点

刘慈欣《三体》的叙述基调：冷叙述 + 克制抒情。写灾难像写天气预报，
悲伤靠外部细节暗示。科学家对白偏书面精确，史强全口语化。

## Cloudflare Pages 配置

| 项目 | 值 |
|------|-----|
| 构建命令 | `python scripts/merge-game.py --validate` |
| 输出目录 | `site` |
| 根目录 | 留空 |
| 域名 | threebody.gkd2323c.in |
| 触发方式 | git push master 自动部署 |
