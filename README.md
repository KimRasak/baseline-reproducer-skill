# Baseline Reproducer Skill

中文 | [English](README.en.md)

一个用于审计和复现已发表 ML/AI 基线的证据门控 Agent Skill。

```text
工件审计 → checkpoint 冒烟测试 → evaluator 回放 → checkpoint 指标复现
→ 训练冒烟测试 → 完整训练复现
```

本 Skill 严格区分部署、推理、评测器、公开权重和训练流程的证据，并将证据充分的停止决定视为有效结果，而不是强行补齐缺失信息。

## 安装

将 `baseline-reproducer/` 复制或软链接到 Codex、Claude Code、Cursor 或其他兼容 Agent Skills 客户端的 Skill 目录。

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/baseline-reproducer" ~/.codex/skills/baseline-reproducer
```

然后可以这样调用：

> 使用 `$baseline-reproducer` 审计这篇论文的官方工件，并复现其公开材料能够支持的最强主张。

## 主要原则

- 优先运行官方代码、公开权重和官方评测器，而不是从论文重新生成实现；
- 将论文拆成原子主张，分别记录证据等级；
- 区分 evaluator replay、checkpoint 指标复现和完整训练复现；
- 固定代码 revision、权重 hash、数据 split、seed 和评测协议；
- 保留失败运行、兼容性修改、资源干扰和被作废的结果；
- 缺少关键数据、权重或协议时明确停止，不做未经标注的替代；
- 在公开权重验证通过且训练 Gate 完整后，才启动昂贵训练。

## 辅助工具

初始化一个非覆盖式的复现证据包：

```bash
python baseline-reproducer/scripts/repro_case.py init work/my-paper \
  --paper-id my-paper --title "My Paper baseline reproduction"
```

检查证据包结构和基本一致性：

```bash
python baseline-reproducer/scripts/repro_case.py validate work/my-paper
```

比较论文值和本地标量结果：

```bash
python baseline-reproducer/scripts/repro_case.py compare \
  81.01 81.02 --abs-tol 0.02
```

记录文件大小与 SHA-256：

```bash
python baseline-reproducer/scripts/repro_case.py hash checkpoint.pt
```

辅助工具只检查证据包结构和确定性的数值条件，不能替代科学判断。

## 证据包

默认结构包括：

```text
case/
├── REPRODUCTION_CARD.md
├── claim.json
├── source_manifest.jsonl
├── protocol.json
├── run_manifest.jsonl
├── reported_vs_reproduced.json
├── training_gate.json
├── commands.sh
├── patches/
├── logs/
└── outputs/
```

其中运行记录采用追加式保存，不覆盖失败或被作废的历史证据。

## 来源

该工作流提炼自一项长期论文复现实践，涉及公开视频生成 checkpoint、评测器、公开数据集和多 GPU 执行路径。Skill 泛化了其中关于身份冻结、协议分 lane、输出完整性审计、评测器回放、非覆盖式证据、结果作废和拒绝实质性协议替换的经验。

仓库不包含私有模型工件、凭证、机器路径或实验数据。

## 许可证

MIT
