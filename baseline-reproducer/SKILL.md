---
name: baseline-reproducer
description: Audit delivery completeness and reproduce an atomic ML/AI paper claim using official code, weights, data, and evaluators. Use to assign TD/RD/TR/RR grades, replay a reported metric, validate a released checkpoint, or decide whether training reproduction is eligible. Do not use for ordinary literature summaries or new-method ideation.
---

# Baseline Reproducer

Audit and reproduce one atomic metric claim at a time. Treat the repository README as the canonical grading specification. Read [references/workflow.md](references/workflow.md) before execution.

## Required output

For each claim, report four independent dimensions:

- `TD` — Test Delivery Completeness: what the authors delivered for checkpoint-to-metric testing.
- `RD` — Training Delivery Completeness: what the authors delivered for data-to-checkpoint training.
- `TR` — Test Reproduction Completeness: what the reproducer actually ran and verified from checkpoint to metric.
- `RR` — Training Reproduction Completeness: what the reproducer actually ran and verified from model initialization through training to the tested metric.

Use base grades `O`, `E`, `M`, `I`, and `F`; use `E+` or `M+` only under the plus conditions in the README. Use `NR` for not rated or not applicable. Grade the highest level supported, subject to the weakest critical link.

## Non-negotiable distinctions

- Delivery and reproduction do not substitute for one another.
- Grade `TD` and `RD` only from the scope, specificity, availability, and claim linkage of author-released materials. Never use local execution success or numeric agreement to raise or lower a delivery grade.
- Grade `TR` and `RR` only from work actually executed and evidence actually retained.
- Reproduction is constrained by delivery. Missing author training code or unspecified material parameters remain missing; do not complete the code or guess the settings and call the result strict reproduction.
- You may locate a publicly available dataset and the exact paper-specified split, and may run author-specified deterministic preprocessing, without lowering a reproduction grade.
- Label reproducer-written implementations, guessed settings, substituted data, or materially changed protocols as independent implementation/protocol results.
- A nearby number cannot compensate for the wrong weights, data split, or protocol.

## Workflow

### 1. Freeze one atomic claim

Record paper revision, table/figure cell, model and configuration, checkpoint identity, training initialization, training and test data/splits, inference and training protocols, evaluator identity, metric, aggregation, reported value, and the decision tolerance.

### 2. Audit delivery

Use primary sources. Record immutable revisions, URLs, hashes, licenses, environment versions, artifact-to-claim mappings, missing fields, and paper/code/config conflicts.

Assign `TD` and `RD` before considering local run outcomes. Do not treat locally discovered author-specified public data or deterministic preprocessing as author delivery unless the authors actually linked or specified it.

### 3. Declare numeric agreement before running

Choose an absolute or relative tolerance from the paper's reporting precision, metric variability, and domain convention. Do not relax it after seeing results. Values within tolerance are consistent; where appropriate, equality after rounding to the paper's published precision may also count as consistent.

### 4. Run cheapest-first

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

Validate output count, identities, pairings, hashes, readability, duplicates, failures, and denominator coverage before scoring. Preserve commands, logs, per-item outputs, failed attempts, compatibility changes, and protocol deviations.

### 5. Apply the RR compute gate

Before training reproduction, compare locally available compute with the resources stated by the paper or official repository. If local compute is lower, skip training reproduction and assign `RR-NR`. Do not shrink the model, dataset, duration, or precision and retain an `RR` grade for the original claim.

### 6. Grade reproduction

- `TR-O` requires a strictly aligned or verified-equivalent environment, correct claim-matching weights, exact test split, specified execution/parameters/metric, a full test, and a value within the preregistered tiny tolerance.
- `RR-O` additionally requires the same initialization (from scratch or specified base weights), exact training data/split, claimed algorithm and full training configuration, a newly trained model, and evaluation within the preregistered tiny tolerance.
- A strictly aligned run outside tolerance cannot receive `O`; grade its execution/evidence at the applicable lower level and report `not_matched` or `contradicted_under_pinned_protocol` separately.

### 7. Report narrowly

For every claim, provide:

1. claim identity and paper-reported value;
2. `TD`, `RD`, `TR`, and `RR` grades with concrete reasons;
3. reported versus reproduced value and preregistered tolerance;
4. artifact/protocol identities and deviations;
5. what ran, coverage, uncertainty, failures, and blockers;
6. a narrow numeric verdict and the next permitted action.

## Stop conditions

Stop or reduce scope when required identity, data/split, pairing, code, weights, evaluator, training parameters, or legal access is missing; when completing the chain requires guessing a scientifically material choice; or when a run is invalidated by wrong artifacts, protocol substitution, output corruption, or resource interference.

## Safety

- Inspect shared accelerators and ports before launch; never preempt another process without authorization.
- Isolate compatibility changes and retain their diff.
- Do not expose credentials or redistribute artifacts beyond their licenses.
- Obtain explicit authorization before paid services, large downloads, expensive compute, remote mutations, or stopping processes.
