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
- 区分 evaluator replay[^evaluator-replay]、checkpoint 指标复现和完整训练复现；
- 固定代码 revision、权重 hash、数据 split、seed 和评测协议；
- 保留失败运行、兼容性修改、资源干扰和被作废的结果；
- 缺少关键数据、权重或协议时明确停止，不做未经标注的替代；
- 在公开权重验证通过且训练 Gate 完整后，才启动昂贵训练。

## 论文指标的链路完整度评级

评级对象不是整篇论文，而是论文表格中的一个<strong>原子指标主张</strong>。例如：

| 模型 | 数据集 1 | 数据集 2 |
|---|---:|---:|
| SOTA1 | a1 | a2 |
| Ours | b1 | b2 |

这里共有四个主张：

- `b1`、`b2` 是论文对自身模型作出的两个<strong>本模型主张</strong>；
- `a1`、`a2` 是论文引用或重新测量的两个<strong>其他模型主张</strong>。

一篇论文可能包含许多实验表格。通常先选择最重要的若干表格，例如主结果、关键消融和核心泛化实验，再将其中每个关键单元格登记成独立主张。不要用一个总评级覆盖整篇论文。

<sub>消融实验按复现成本排序：若需要增删模型模块、重新训练或重新发布权重，通常优先级低于主结果；若只需改变测试时设置、推理参数、输入条件或 evaluator 开关，且可以复用同一公开权重，则属于低成本、可控的消融，可优先验证。任何测试时变更仍须单独冻结协议，不能与主结果混成同一条指标链路。</sub>

### 两类、四个独立评级

每个主张分别记录：

1. <strong>交付完整度</strong>：作者公开了什么。
   - <strong>TD（Test Delivery Completeness，测试交付完整度）</strong>：作者是否交付了验证该数值所需的权重、测试代码、测试数据及划分和评测协议。
   - <strong>RD（Training Delivery Completeness，训练交付完整度）</strong>：作者是否交付了产生该权重所需的训练代码、训练数据及划分、训练设置和依赖权重。
2. <strong>复现完整度</strong>：复现者实际验证到哪里。
   - <strong>TR（Test Reproduction Completeness，测试复现完整度）</strong>：复现者是否实际运行并审计了权重到指标的测试链路。
   - <strong>RR（Training Reproduction Completeness，训练复现完整度）</strong>：复现者是否实际运行并审计了数据到训练权重再到指标的完整链路。

交付评级描述“作者公开了什么”；复现评级描述“复现者实际验证到哪里”。四个评级不能互相替代。

### 等级定义

下面用一个贯穿示例说明：假设 `Paper X` 的表 1 声称其模型在 `Dataset 1` 上得到 `b1=82.7`。例子描述的是同一主张在不同公开材料和执行状态下的评级。

| 等级 | 链路完整度 | 含义 | 以 `Paper X / b1=82.7` 为例 |
|---|---|---|---|
| <strong>AAA</strong> | 完整闭环 | 所需工件、身份、协议、划分和聚合均明确；复现评级为 AAA 时还要求完整执行、全量审计和必要的重复/不确定性分析。 | 对应 checkpoint、完整测试划分、测试代码、seed 和聚合方式均已固定；全量重跑得到 `82.6`，落在预先规定的容差内，逐样本结果也已保存。 |
| <strong>AA</strong> | 基本闭环 | 主链路完整，只有不改变科学含义的少量可追溯兼容处理或确定性重建步骤。 | 全部官方工件可用，但旧版 API 无法在当前环境运行；记录并应用只修改 API 调用[^api-call]、不改变模型与协议[^protocol]的兼容补丁后得到 `82.6`。 |
| <strong>A</strong> | 可执行但有重要限制 | 可以进行主张级验证，但缺少 seed、精确版本、checkpoint 选择或统计细节等重要信息，不能称严格复现。 | checkpoint、测试代码和数据可用，但作者没有公开 seed；采用复现者自行选用的 seed[^independent-seed] 得到 `82.5`，因此只能说明固定独立协议的结果是可靠的。 |
| <strong>BBB</strong> | 部分链路 | 能完成 evaluator replay、固定子集或独立协议验证，但无法闭合论文原指标。 | 作者未公开 checkpoint，只公开测试集上的现成预测文件和评分代码。复现者不加载模型，只把这些预测送进评分脚本，即可重新算出 `82.7`（evaluator replay[^evaluator-replay]）。这只验证打分链路，不能证明模型会生成这些预测。 |
| <strong>BB</strong> | 冒烟级 | 只能证明代码导入、权重加载、单样本生成或 evaluator 接口可运行。 | checkpoint 可以加载，并在 `Dataset 1` 的一个样本上输出预测；尚未运行完整测试集，不能与 `82.7` 比较。 |
| <strong>B</strong> | 仅工件追踪 | 找到部分代码、权重或数据入口，但尚不能形成可执行的指标链路。 | 找到了代码仓库和一个权重下载链接，但尚不能确认该权重是否对应表 1，也没有找到可执行的测试命令。 |
| <strong>CCC</strong> | 严重缺失 | 关键权重、代码、数据、划分、配对键或 evaluator 缺失，公开材料不足以测试主张。 | 论文只写出 `82.7`；没有对应权重，测试划分或指标实现也未公开，无法测试该主张。 |
| <strong>D</strong> | 无效链路 | 工件身份错误、协议被静默替换、结果已作废，或证据不能归属于目标主张。 | 运行后才发现下载的是另一个模型变体，或使用了不同的 `Dataset 1` 划分；所得数字不能归属于 `b1`，该次结果作废。 |
| <strong>NR</strong> | 未评级/不适用 | 尚未审计，或该维度对当前主张不适用。 | 已登记 `b1=82.7`，但尚未检查代码、权重、数据或评测材料。 |

评级衡量的是<strong>链路完整度，不是数值表现或论文可信度</strong>。在完全固定的协议下稳定得到与论文不一致的结果，仍可能具有 `TR-AAA`（Test Reproduction Completeness AAA，测试复现完整度 AAA），同时数值结论记为 `not_matched` 或 `contradicted_under_pinned_protocol`。反之，只因本地数字接近论文值，不能获得高评级。

### 示例评级

假设对上述主结果表审计后得到：

| 主张 | 类型 | TD | RD | TR | RR | 数值结论 |
|---|---|:---:|:---:|:---:|:---:|---|
| `b1` | 本模型 | AAA | AA | AAA | BBB | matched |
| `b2` | 本模型 | A | CCC | A | NR | not_strictly_comparable |
| `a1` | 其他模型 | BBB | NR | BBB | NR | author_table_only |
| `a2` | 其他模型 | D | NR | D | NR | invalidated |

- **`b1`：** 精确权重、测试集和 evaluator 均公开并已复现；训练数据需按公开脚本重建，但尚只完成训练子集。
- **`b2`：** 权重公开，但作者未给 seed 和完整测试划分；训练数据未公开。只能报告固定独立协议结果。
- **`a1`：** 本文没有重新运行 SOTA1，只引用其原论文数值；可回到 SOTA1 原论文继续单独评级。
- **`a2`：** 论文使用的 SOTA1 数据划分与本表 Ours 不同，却放在同一列直接比较，该比较链路无效。

对于其他模型主张，要进一步记录数值来源：`cited_from_original_paper`、`rerun_by_current_authors` 或 `unclear`。只有当前论文确实使用同一协议重新运行了对方模型，`a1/a2` 才能直接继承当前表格的测试链路；单纯转抄原论文数字不能视为本文完成了复现。

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

[^evaluator-replay]: <strong>Evaluator replay（评测器回放）</strong>就是用作者公开的输出和评测代码，重新计算论文中的分数。例如，作者公开了 1,000 个生成视频和 VBench 代码；我们重新评分得到 `81.0`，论文也报告 `81.0`。这只能说明评分流程可以复现，不能说明模型生成或训练过程可以复现。

[^api-call]: <strong>修改 API 调用</strong>是为了适配新版依赖，只更换已经失效的函数名、参数名或调用写法。例如把旧参数 `torch_device="cuda"` 改成新版参数 `device="cuda"`；传入值和实际计算不变。

[^independent-seed]: <strong>复现者自行选用的 seed</strong>是指作者未公开原实验的随机种子时，复现者自己选择一组种子，例如 `42、43、44、45、46`。这些种子应在运行前固定并记录，避免看到结果后只挑表现好的种子。由于它们不是作者原来的种子，不能称为精确恢复作者实验。

[^protocol]: <strong>协议（protocol）</strong>是产生并计算这个指标时使用的一整套固定设置，例如测试集划分、输入预处理、推理步数、seed、样本数和评分方法。只把旧 API 参数名改成新名称不算改变协议；改用另一份测试集或不同推理步数则算。

## 许可证

MIT
