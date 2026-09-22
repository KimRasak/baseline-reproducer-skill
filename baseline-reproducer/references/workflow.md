# Gated reproduction workflow

## Candidate admission

Confirm relevance, then record the exact claim, official revision, checkpoint-to-row identity, public raw data/pairing/split/license, official entrypoints, evaluator weights, and effective compute. Do not create an active case for a speculative candidate unless audit or execution begins.

## Freeze identity and protocol

Hash papers, configs, prompt lists, checkpoints, archives, evaluator weights and wrappers. Freeze input schema, sampler/steps, seeds, retries, evaluator preprocessing/aggregation, output count and decision rule. If author seeds are missing, choose a deterministic independent policy and label it accordingly.

## Separate environments

Use independent generation/training and evaluation environments when needed. Inspect entrypoints before treating `--help` as CPU-only; some tools import every model or initialize CUDA before argument parsing. Put compatibility changes in an alternate worktree and classify whether they are metadata-only, environment compatibility, implementation repair, or a scientifically material protocol change. The last creates a new lane.

## Smoke ladder

1. Files and hashes.
2. Imports and strict checkpoint load.
3. One readable output.
4. Evaluator reads a tiny valid input and emits per-item output.
5. Frozen subset has complete mappings and denominators.
6. Full checkpoint run reaches expected count.
7. Training reads a real batch, computes required losses/rewards, backpropagates, steps, saves and resumes.
8. Full training only after a claim-level endpoint exists.

Tiny-sample Fréchet metrics or aggregate scores are interface tests, not scientific results.

## Batch integrity

Validate planned vs observed IDs, intact prompt/condition passage, substitution counts, unique seeds, hashes/duplicates, decoding, schema, failed attempts, and raw-input → cache → score mapping.

Common traps:

- shell quoting splits one prompt into many inputs;
- source replacement matches zero times while the run completes;
- all ranks bind one GPU unless binding occurs before framework import;
- after `CUDA_VISIBLE_DEVICES=3`, use logical `cuda`, not necessarily `cuda:3`;
- mixed directories cause suffix-based evaluators to select JSON and emit NaN;
- aggregate agreement hides opposing component errors;
- feature caches do not replace raw-data provenance;
- a response from the wrong model identity is not target-model evidence;
- exit code zero does not establish output identity or scientific validity.

## Independent evaluation

Freeze outputs before scoring. Save evaluator command/environment, code and weight hashes, per-item output, coverage, logs, aggregation and result hash. When author media and scores exist, replay the evaluator first to separate evaluator drift from model differences.

## Statistical closure

Use the paper's unit of analysis. Pair by input/seed, retain repeated runs, uncertainty, denominators and missing items. Never compare one run with a paper's multi-run mean as equivalent. Keep an interference-affected run but do not pool it as isolated evidence.

## Training gate

Require a matching endpoint, legal raw data, enabled headline method, all auxiliary weights, optimizer/schedule/global batch/world size/seeds/checkpoint selection, save/resume smoke, closed evaluator, and approved compute. If per-item weights or a headline mechanism are missing, stop rather than manufacture them.

## Closeout

Publish a local metric only after execution, output audit and independent evaluation are terminal. Preserve supersession instead of rewriting invalidated history; update human and machine trackers together.
