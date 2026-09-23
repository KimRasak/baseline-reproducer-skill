# Baseline Reproducer Skill

[中文](README.md) | English

An evidence-gated Agent Skill for auditing and reproducing published ML/AI baselines.

```text
artifact audit → checkpoint smoke → evaluator replay → checkpoint metric
→ training smoke → full training reproduction
```

It keeps deployment, inference, evaluator, checkpoint and training evidence separate, and treats a well-supported stop decision as a valid outcome.

## Core principles

- Prefer official code, released weights, and official evaluators over generating a new implementation from the paper.
- Split a paper into atomic claims and track evidence for each claim separately.
- Distinguish evaluator replay[^evaluator-replay], released-checkpoint metric reproduction, and full training reproduction.
- Pin code revisions, artifact hashes, data splits, seeds, and evaluation protocols.
- Retain failed runs, compatibility changes, resource interference, and invalidated results.
- Stop explicitly when critical data, weights, or protocol details are missing; do not make an unlabelled substitution.
- Start expensive training only after checkpoint verification and the training gate are complete.

## Claim-chain completeness ratings

Rate an atomic metric claim—a table cell—not a paper as a whole. For example:

| Model | Dataset 1 | Dataset 2 |
|---|---:|---:|
| SOTA1 | a1 | a2 |
| Ours | b1 | b2 |

This table contains four claims. `b1` and `b2` are <strong>self-model claims</strong> made for the paper's model; `a1` and `a2` are <strong>other-model claims</strong> cited or remeasured by the paper.

A paper may contain many experimental tables. Start with the most important few—typically the main results, decisive ablations, and central generalization tests—and register each important cell independently. Do not assign one global rating to the paper.

<sub>Prioritize ablations by reproduction cost. Ablations that add or remove model modules and therefore require retraining or new weights are usually lower priority than the main result. Ablations produced by changing only test-time settings, inference parameters, input conditions, or evaluator switches while reusing the same released checkpoint are low-cost and controllable, so they may be tested earlier. Each test-time variation still needs its own frozen protocol and must not be merged into the main-result metric chain.</sub>

### Two categories, four independent ratings

1. <strong>Delivery completeness:</strong> what the authors made available.
   - <strong>TD (Test Delivery Completeness):</strong> whether the authors delivered the weights, evaluation code, test data/split, and protocol needed to verify the value.
   - <strong>RD (Training Delivery Completeness):</strong> whether the authors delivered the training code, training data/split, settings, and dependent weights needed to produce the evaluated checkpoint.
2. <strong>Reproduction completeness:</strong> what an independent reproducer actually verified.
   - <strong>TR (Test Reproduction Completeness):</strong> how far the reproducer executed and audited the checkpoint-to-metric path.
   - <strong>RR (Training Reproduction Completeness):</strong> how far the reproducer executed and audited the raw-data-to-trained-checkpoint-to-metric path.

Delivery describes what the authors made available; reproduction describes what an independent reproducer actually verified. The ratings do not substitute for one another.

### Grade definitions

Grade each of the four dimensions independently; one generic table cannot be used to infer the others. In ascending order, the grades are `F`, `I`, `M-`, `M`, `M+`, `E`, `E+`, and `O`. The labels follow the “Failed / Improving / Medium / Excellent / Outstanding” naming scheme[[1](https://www.zhihu.com/question/495085246), [2](https://www.dingteam.com/article/285)], but here they measure <strong>how much auditable evidence the released materials and actual reproduction provide for the claimed value</strong>. The grade therefore affects confidence in that value, but it does not judge whether the value is high or low, nor does it extend to an overall credibility rating for the entire paper. `NR` means Not Rated / Not Applicable and is not a grade on this scale.

Every definition applies to one frozen claim. For example, “the model scores `b1=82.7` on `Dataset 1` in Table 1 of `Paper X`” is one claim; other cells in the same paper are graded separately.

#### TD: Test Delivery Completeness

| Grade | Definition |
|---|---|
| **O** | In addition to `E+`, a durable one-command test workflow, locked environment, full provenance, and machine-checkable manifests are delivered with no scientific parameters left to guess. |
| **E+** | In addition to `E`, immutable revisions, hashes, per-item outputs, or equivalent audit materials allow independent artifact and result verification. |
| **E** | The matching checkpoint, full test split, inference and evaluation code, protocol parameters, seeds, and aggregation rules are all explicitly released. |
| **M+** | Main-chain test materials are complete and traceable; only minor deterministic reconstruction or scientifically neutral compatibility handling is needed. |
| **M** | Checkpoint, test code, data, and evaluator are broadly usable for claim-level testing, but seeds, exact versions, checkpoint selection, split, or aggregation have material gaps. |
| **M-** | The release supports import, weight loading, one-sample testing, or evaluator replay[^evaluator-replay], but not the complete metric run from the matching checkpoint. |
| **I** | Only the paper value, repository, or scattered entry points can be located; a key checkpoint, test dataset/split, inference path, or evaluator is missing, so no test chain can be formed. |
| **F** | Released artifacts have the wrong identity, the test protocol conflicts with the target claim, or the materials cannot be attributed to it. |

#### RD: Training Delivery Completeness

| Grade | Definition |
|---|---|
| **O** | In addition to `E+`, a durable one-command training workflow, full data provenance and processing lineage, resource specification, and machine-checkable manifests are delivered with no scientific parameters left to guess. |
| **E+** | In addition to `E`, data and weight hashes, a locked environment, training logs, and intermediate checkpoints make the training trajectory auditable. |
| **E** | Training data and split, code, full configuration, seeds, dependent weights, stopping rule, and checkpoint-selection rule are explicitly released. |
| **M+** | Main materials from raw data to target checkpoint are complete; only minor deterministic data reconstruction or scientifically neutral compatibility handling is needed. |
| **M** | Training code, primary data, and configuration are broadly usable and target training can start, but data version/split, seeds, hyperparameters, dependent weights, or checkpoint selection have material gaps. |
| **M-** | Training code can import, a small sample can be built, or a very short smoke run works, but full training under the paper's setup is not possible. |
| **I** | Only a paper description or scattered training code exists; raw training data, split, key dependent weights, configuration, or entry point is critically absent, preventing meaningful training. |
| **F** | Training artifacts belong to the wrong model, configuration, or data; the protocol is incorrectly substituted; or the materials cannot belong to the target checkpoint's training chain. |

#### TR: Test Reproduction Completeness

| Grade | Definition |
|---|---|
| **O** | In addition to `E+`, the chain was rebuilt end to end in a clean environment, with evidence, commands, logs, hashes, and deviations fully auditable by a third party. |
| **E+** | In addition to `E`, preregistered repetitions or uncertainty analysis are complete, and aggregation plus key artifact identities were independently checked. |
| **E** | Checkpoint, full split, protocol, and aggregation were frozen; the full run, integrity checks, and per-item result retention are complete. |
| **M+** | A full test under a substantially aligned protocol is complete and results are retained; only minor traceable compatibility handling remains, or required repetition/uncertainty analysis is absent. |
| **M** | A claim-level test produced a metric, but reproducer-chosen seeds[^independent-seed], substitute versions, or incomplete statistics prevent strict alignment with the paper. |
| **M-** | Only import, checkpoint loading, one-sample inference, or evaluator replay is complete; no full metric from the matching checkpoint exists. |
| **I** | The chain was audited or execution attempted, but a critical omission or error still blocks testing and no valid output exists. |
| **F** | The executed run used the wrong checkpoint, split, or protocol; its result is invalidated and cannot be attributed to the target claim. |

#### RR: Training Reproduction Completeness

| Grade | Definition |
|---|---|
| **O** | In addition to `E+`, the chain was fully rebuilt in a clean environment, retaining data lineage, commands, logs, intermediate checkpoints, resource use, hashes, and every deviation for direct third-party audit. |
| **E+** | In addition to `E`, preregistered independent training repetitions or uncertainty analysis are complete, with data, checkpoint, and aggregation identities checked. |
| **E** | Data and split, training configuration, seeds, dependent weights, and selection rules were frozen; end-to-end training, full testing, and training-trajectory audit are complete. |
| **M+** | One end-to-end training and full test under a substantially aligned protocol are complete; only minor traceable compatibility handling remains, or repeated training/uncertainty analysis is absent. |
| **M** | One training run and evaluation of its new checkpoint are complete, but data, seeds, scale, hyperparameters, or stopping rules differ materially from the paper. |
| **M-** | Only data loading, a short-step run, single-batch overfitting, or a training-subset smoke test is complete; no target checkpoint suitable for full evaluation was produced. |
| **I** | Training was audited or attempted but remains blocked by critical data, configuration, dependency, or resource problems; no valid trained checkpoint exists. |
| **F** | The executed training used the wrong data, model configuration, or protocol; the resulting checkpoint and result are invalidated and cannot be attributed to the target claim. |

High grades do not require a result close to the paper value. A complete pinned run that stably disagrees with the paper may still earn `TR-E+` or `TR-O`, while the numeric outcome is separately recorded as `not_matched` or `contradicted_under_pinned_protocol`. A nearby number alone never earns a high grade.

### Rating example

| Claim | Type | TD | RD | TR | RR | Outcome |
|---|---|:---:|:---:|:---:|:---:|---|
| `b1` | self-model | E | M+ | E+ | M- | matched |
| `b2` | self-model | M | I | M | NR | not_strictly_comparable |
| `a1` | other-model | M- | NR | M- | NR | author_table_only |
| `a2` | other-model | F | NR | F | NR | invalidated |

- **`b1`:** Exact weights, test set and evaluator were released and replayed; training data requires a public reconstruction script, and only a training subset has run.
- **`b2`:** Weights are public, but seeds and the full test split are missing; training data is unavailable. Only an independent fixed-protocol result is defensible.
- **`a1`:** The current paper did not rerun SOTA1; it copied the original paper's number. Audit the SOTA1 paper separately.
- **`a2`:** SOTA1 used a different dataset split from Ours although both appear in the same comparison column.

For other-model claims, also record whether the value was `cited_from_original_paper`, `rerun_by_current_authors`, or `unclear`. Only an actual rerun under the same protocol belongs directly to the current table's test chain; copying a cited number is not a reproduction by the current authors.

## Install

Copy or symlink `baseline-reproducer/` into the skill directory used by Codex, Claude Code, Cursor, or another Agent Skills-compatible client.

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/baseline-reproducer" ~/.codex/skills/baseline-reproducer
```

Then ask: “Use `$baseline-reproducer` to audit this paper's official artifacts and reproduce the strongest claim the public release supports.”

## Origin

The workflow was distilled from a long-running reproduction effort across released video-generation checkpoints, evaluators, public datasets and multi-GPU paths. It generalizes identity freezing, protocol lanes, output-integrity audits, evaluator replay, non-overwriting evidence, explicit invalidation, and refusal of scientifically material substitutions.

No private artifacts, credentials, machine paths, or experiment data are included.

[^evaluator-replay]: <strong>Evaluator replay</strong> means recalculating a paper's score from the authors' released outputs and evaluation code. For example, the authors release 1,000 generated videos and the VBench code; rerunning it gives `81.0`, matching the paper's `81.0`. This shows only that the scoring process is reproducible—not that the model generation or training process is reproducible.

[^api-call]: <strong>Changing an API call</strong> means adapting obsolete function names, argument names, or call syntax to a newer dependency without changing the supplied values or computation. For example, replace the old `torch_device="cuda"` argument with the new `device="cuda"` argument.

[^independent-seed]: <strong>Reproducer-chosen seeds</strong> are seeds selected by the reproducer when the authors do not release the original ones—for example, `42, 43, 44, 45, 46`. They should be fixed and recorded before running to prevent selecting only favorable results afterward. Because they are not the authors' original seeds, the run is not an exact recovery of the original experiment.

[^protocol]: A <strong>protocol</strong> is the fixed set of choices used to produce and score a metric, such as the test split, input preprocessing, inference steps, seeds, sample count, and scoring method. Renaming a legacy API argument does not change the protocol; using a different test set or number of inference steps does.

## License

MIT
