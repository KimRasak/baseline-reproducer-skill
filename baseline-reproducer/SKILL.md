---
name: baseline-reproducer
description: Audit and reproduce a published ML/AI baseline from official code, released weights, test data, and evaluators. Use when selecting reproducible baselines, validating a checkpoint, replaying a reported metric, restoring an environment, or deciding whether full training reproduction is justified. Do not use for ordinary literature summaries or new-method ideation before baseline evidence is closed.
---

# Baseline Reproducer

Reproduce the strongest claim supported by public artifacts without silently filling gaps. Prefer replaying an official checkpoint and evaluator over reimplementing the paper.

## Keep these outcomes separate

- Evaluate an atomic claim, not a paper's credibility as a whole.
- Separate deployment, inference, evaluator replay, released-checkpoint evaluation, and training reproduction.
- A runnable checkpoint is not a reproduced metric. A reproduced checkpoint metric is not reproduced training.
- Preserve reported values as claims; never copy them into local-result fields.
- Treat missing artifacts as `untestable` or `blocked`, not failed results.
- Never substitute data, weights, seeds, evaluator, model variant, or implementation without opening a separately labelled compatibility or independent-protocol lane.
- Retain failed attempts and deviations. Never overwrite prior run evidence.

Read [references/evidence-model.md](references/evidence-model.md) before assigning a state, [references/workflow.md](references/workflow.md) when executing, and [references/artifacts.md](references/artifacts.md) when creating the evidence package.

## Workflow

### 1. Define one claim

Freeze paper revision, table/figure row, model/config, dataset and split, inference protocol, evaluator revision, metric, aggregation, reported value, and tolerance. If these cannot be stated, do artifact discovery only.

### 2. Admit candidates by reproducibility

Among scientifically relevant baselines, prefer:

1. official training + evaluation code + paper-matching weights + reconstructable public data;
2. official evaluation code + paper-matching weights + reconstructable public test protocol;
3. official training/evaluation code without weights;
4. non-official implementation or paper only.

This order selects experimental baselines; it does not determine which relevant papers must be cited.

### 3. Audit before expensive execution

Record primary sources, immutable revisions, licenses, hashes, checkpoint-to-row identity, raw-data provenance, split, evaluator code/weights, environment, compute envelope, and missing fields. Inspect paper/code/config disagreements explicitly.

Create the evidence package from the layout in [references/artifacts.md](references/artifacts.md). Fill it from primary sources; do not infer absent values or overwrite existing case files.

### 4. Run cheapest-first gates

Advance only after the preceding result is terminal and audited:

```text
artifact identity
→ import/checkpoint-load smoke
→ one-sample inference smoke
→ evaluator self/interface smoke
→ frozen-subset run
→ full released-checkpoint evaluation
→ one-batch train/backward/save/resume smoke
→ full training reproduction
```

Do not train merely because compute is idle. Require a paper-matching endpoint, legally usable raw data, reconstructable preprocessing, complete training configuration, evaluator identity, and affordable compute.

### 5. Validate outputs before scoring

Check expected count, unique IDs/seeds, hashes, decode/readability, shape/schema, failures, duplicate outputs, input-output mapping, and denominator coverage. Exit code zero is insufficient.

For batch generation or source rewriting, assert every intended substitution occurred. If different inputs yield identical hashes or identical per-group statistics, stop and audit the input path before scoring.

### 6. Score independently

Run the evaluator separately over an immutable output set. Retain per-item scores before aggregation. Compare values using a declared deterministic rule; use the model only to explain discrepancies.

Compare a scalar with a declared absolute or relative tolerance recorded before the run. For stochastic metrics, predeclare seeds/runs and compare distributions or intervals rather than selecting a favorable run.

### 7. Report the exact level reached

State the tested claim, what ran, artifact/protocol identities, reported and fresh values, coverage, uncertainty, deviations, interference, failed attempts, narrow verdict, and next gate or stop decision.

## Stop conditions

Stop or downgrade scope when:

- released weights cannot be tied to the claimed row;
- raw data, pairing key, split, required per-sample weight, evaluator implementation, or license is missing;
- official config disables or differs from the headline method;
- only a miniature/different benchmark is available;
- a full run has no claim-level endpoint;
- repeated failure establishes a stable resource/protocol blocker;
- resource interference invalidates isolation;
- completion requires guessing a scientifically material choice.

A well-evidenced blocked decision is a successful audit.

## Safety

- Inspect shared accelerators and ports before launch. Readiness is not authorization to preempt a process.
- Isolate generated or legacy code. Put compatibility patches in a separate worktree and retain the diff.
- Do not expose credentials or redistribute artifacts beyond their licenses.
- Obtain explicit authorization before paid services, large downloads, expensive compute, remote mutations, or stopping processes.
