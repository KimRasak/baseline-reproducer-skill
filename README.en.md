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
- Distinguish [evaluator replay](#evaluator-replay), released-checkpoint metric reproduction, and full training reproduction.
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

Grade each of the four dimensions independently; one generic table cannot be used to infer the others. The base grades, in ascending order, are `F`, `I`, `M`, `E`, and `O`. Use `M+` or `E+` when the evidence clearly exceeds the base requirements for `M` or `E` but does not reach the next base grade. The labels follow the “Failed / Improving / Medium / Excellent / Outstanding” naming scheme[[1](https://www.zhihu.com/question/495085246), [2](https://www.dingteam.com/article/285)], but here they measure <strong>how much auditable evidence the released materials and actual reproduction provide for the claimed value</strong>. The grade therefore affects confidence in that value, but it does not judge whether the value is high or low, nor does it extend to an overall credibility rating for the entire paper. `NR` means Not Rated / Not Applicable and is not a grade on this scale.

Every definition applies to one frozen claim. For example, “the model scores `b1=82.7` on `Dataset 1` in Table 1 of `Paper X`” is one claim; other cells in the same paper are graded separately.

#### TD: Test Delivery Completeness

Assign the <strong>highest grade supported by the released materials</strong>, using a weakest-critical-link rule: completeness elsewhere cannot compensate for a critical gap in checkpoint identity, test split, or evaluation rules.

| Grade | Definition | Example (`Paper X / b1=82.7`) |
|---|---|---|
| **O** | The complete runtime environment and its version numbers are specified; model weights that exactly match the target claim are available, as are the paper's test set and exact split; all test-time parameters are disclosed; and the test rules (including data preprocessing, inference, evaluation, aggregation, and randomness handling) are clear and complete, with no result-affecting setting left to guess or substitute. | The authors provide `environment.yml` specifying Python 3.10.13, PyTorch 2.1.2, and CUDA 12.1. Table 1 is explicitly tied to `paper-x-step-50000.ckpt`, whose SHA-256 is supplied, and `test_ids.txt` lists all 10,000 evaluated sample IDs. The test command sets `seed=42` and `batch_size=64`; images are resized to 256 pixels and center-cropped to 224×224; the released `accuracy.py` then computes top-1 accuracy over all samples, yielding the reported `82.7`. |
| **E** | The main materials and rules from the matching checkpoint to the paper metric are delivered; only minor traceable deterministic reconstruction or compatibility handling is required, and it changes neither the model, data, parameters, nor evaluation meaning.<br><strong>Award E+ when:</strong> the checkpoint, test set and split, test-time parameters, and test rules are complete and exactly tied to the claim; no result-affecting choice is left to the reproducer, and only operational details such as the hardware model, an example launch command, or a noncritical dependency version are absent. | **E:** The authors provide `paper-x-step-50000.ckpt`, `Dataset 1 v2.1`, and `make_test_ids.py`; running the script deterministically produces the same 10,000-sample list from public metadata. The evaluation code's deprecated `torch_device="cuda"` argument must be equivalently changed to `device="cuda"`.<br>**E+:** The authors directly provide that checkpoint, all 10,000 sample IDs, `seed=42`, the 224×224 center-crop rule, and `accuracy.py`, but do not state whether an A100 or H100 was used and provide no complete launch command. |
| **M** | Part of an executable test chain is delivered, but material gaps remain. The release may support only one-sample testing or [evaluator replay](#evaluator-replay); alternatively, it may support a full test while the checkpoint version, test split, key inference parameter, evaluator, or aggregation rule cannot be strictly aligned with the paper. The result cannot be treated as the paper's original metric.<br><strong>Award M+ when:</strong> a complete checkpoint-to-metric chain can be formed, the weights, test set, and evaluation method broadly match the claim, and only one noncore setting—such as the original seed, an exact dependency version, a secondary test parameter, or a statistical detail—is missing. | **M:** The authors release only `table1_predictions.json` and `accuracy.py`; passing its 10,000 predictions to the script recalculates `82.7`, but the checkpoint that generated them is absent. In another case, `paper-x.ckpt` supports a full test, but the repository contains both `test-v1.txt` and `test-v2.txt` and the paper does not identify which was used.<br>**M+:** The authors release `paper-x-step-50000.ckpt`, `test_ids.txt`, and `accuracy.py`, and specify a 224×224 center crop and `batch_size=64`, but omit the original seed; the reproducer must fix a seed before running. |
| **I** | Only the paper value, repository, weight URL, data entry point, or scattered code can be found. Critical artifacts are severely incomplete or cannot be tied together, so no executable claim-level test chain can yet be formed. | The repository links only a weight named `model_final.ckpt`, with no configuration or table mapping that ties it to Table 1. The `Dataset 1` website offers multiple test splits, but the repository selects none of them and provides no evaluation command. |
| **F** | Released artifacts are confirmed to conflict with the target claim—for example, the weight belongs to another model variant, a different test split is used, or the evaluation protocol was substituted. Even if these materials run, their result cannot be attributed to the target claim. | The download page labels `paper-x-large.ckpt` as the Table 1 weight, but its configuration has `hidden_size=768`, whereas the Table 1 Large model requires `hidden_size=1024`; its test result therefore cannot be attributed to `b1=82.7`. |

#### RD: Training Delivery Completeness

| Grade | Definition |
|---|---|
| **O** | The complete runtime environment and versions, training code, and configuration are specified; the paper's training data and exact split, dependent weights, and initialization materials are available; all training parameters, stopping conditions, and checkpoint-selection rules are disclosed; and the training rules (including data preprocessing, sampling, optimization, distributed training, and randomness handling) are clear and complete, with no result-affecting setting left to guess or substitute. |
| **E** | The main materials and rules from training data to the target checkpoint are delivered; only minor traceable deterministic data reconstruction or compatibility handling is required, and it changes neither the model, data, parameters, nor training meaning.<br><strong>Award E+ when:</strong> the training data and split, code, full configuration, dependent weights, training parameters, and checkpoint-selection rules are complete and exactly tied to the claim; no result-affecting choice is left to the reproducer, and only operational details such as the hardware model, example launch command, or a noncritical dependency version are absent. |
| **M** | Part of an executable training chain is delivered, but critical materials or settings are missing. The release may support only data loading, short-step training, or a subset smoke test; alternatively, full training may be possible while the data version/split, initialization weights, key hyperparameters, stopping condition, or checkpoint-selection rule cannot be strictly aligned with the paper.<br><strong>Award M+ when:</strong> a complete data-to-checkpoint chain can be formed, the model, primary data, and training method broadly match the claim, and only limited information that does not prevent chain closure—such as the original seed, exact dependency version, secondary hyperparameter, or statistical detail—is missing. |
| **I** | Only a paper description, scattered training code, or a data entry point is available. Training data, split, key dependent weights, configuration, or the training entry point is critically incomplete, so no executable target-training chain can yet be formed. |
| **F** | Training artifacts are confirmed to conflict with the target claim—for example, the code or configuration belongs to another model, a different training-data version is used, or the training protocol was substituted. The resulting checkpoint cannot be attributed to the claim. |

#### TR: Test Reproduction Completeness

| Grade | Definition |
|---|---|
| **O** | In a clean, version-specified environment, a full end-to-end test is completed with the exact checkpoint and test split tied to the claim and with complete test parameters and rules; integrity checks and required repetitions or uncertainty analysis are complete, while per-item results, commands, logs, hashes, and all deviations are retained for direct third-party audit. |
| **E** | The checkpoint, test split, test parameters, and aggregation rules are frozen; the full run and integrity checks are complete, and per-item results are retained, with at most minor traceable compatibility handling that does not change test meaning.<br><strong>Award E+ when:</strong> preregistered repetitions or uncertainty analysis are also complete and aggregation plus key artifact identities are independently checked; only clean-environment end-to-end reconstruction or the evidence needed for direct third-party audit remains absent. |
| **M** | Part of a valid test chain was executed, or a full test was completed while key conditions could not be strictly aligned with the paper—for example, only one-sample inference or evaluator replay was completed, or reproducer-chosen seeds, substitute versions, or incomplete statistics were used.<br><strong>Award M+ when:</strong> the matching checkpoint was fully tested under a substantially aligned protocol and results were retained, with only limited information affecting strict alignment missing or required repetitions/uncertainty analysis still incomplete. |
| **I** | Materials were audited or execution attempted, but critical artifacts, configuration, or execution errors still block the test chain, and no valid result for judging the target claim exists. |
| **F** | The executed run is confirmed to have used the wrong checkpoint, test split, or evaluation protocol. Its result is invalidated and cannot be attributed to the target claim. |

#### RR: Training Reproduction Completeness

| Grade | Definition |
|---|---|
| **O** | In a clean, version-specified environment, end-to-end training and full testing are completed with the exact data, model configuration, and training rules tied to the claim; required independent training repetitions or uncertainty analysis are complete, while data lineage, commands, logs, intermediate checkpoints, resource use, hashes, and all deviations are retained for direct third-party audit. |
| **E** | Training data and split, model configuration, training parameters, dependent weights, stopping conditions, and checkpoint-selection rules are frozen; end-to-end training, full testing, and training-trajectory audit are complete, with at most minor traceable compatibility handling that does not change training meaning.<br><strong>Award E+ when:</strong> preregistered independent training repetitions or uncertainty analysis are also complete and data, checkpoint, and aggregation identities are checked; only clean-environment reconstruction or the evidence needed for direct third-party audit remains absent. |
| **M** | Part of a valid training chain was executed, or one training run and evaluation were completed while key conditions could not be strictly aligned with the paper—for example, only short-step or subset smoke training was completed, or data, seeds, scale, hyperparameters, or stopping rules differed materially.<br><strong>Award M+ when:</strong> one end-to-end training and full test were completed under a substantially aligned protocol, with only limited information affecting strict alignment missing or repeated training/uncertainty analysis still incomplete. |
| **I** | Materials were audited or training attempted, but critical data, configuration, dependency, or resource problems still block progress, and no valid checkpoint suitable for full evaluation exists. |
| **F** | The executed training is confirmed to have used the wrong data, model configuration, or training protocol. The resulting checkpoint and result are invalidated and cannot be attributed to the target claim. |

High grades do not require a result close to the paper value. A complete pinned run that stably disagrees with the paper may still earn `TR-E+` or `TR-O`, while the numeric outcome is separately recorded as `not_matched` or `contradicted_under_pinned_protocol`. A nearby number alone never earns a high grade.

### Rating example

| Claim | Type | TD | RD | TR | RR | Outcome |
|---|---|:---:|:---:|:---:|:---:|---|
| `b1` | self-model | E | M+ | E+ | M | matched |
| `b2` | self-model | M | I | M | NR | not_strictly_comparable |
| `a1` | other-model | M | NR | M | NR | author_table_only |
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

<a id="evaluator-replay"></a>
<strong>Evaluator replay</strong> means recalculating a paper's score from the authors' released outputs and evaluation code. For example, the authors release 1,000 generated videos and the VBench code; rerunning it gives `81.0`, matching the paper's `81.0`. This shows only that the scoring process is reproducible—not that the model generation or training process is reproducible.

<a id="api-call"></a>
<strong>Changing an API call</strong> means adapting obsolete function names, argument names, or call syntax to a newer dependency without changing the supplied values or computation. For example, replace the old `torch_device="cuda"` argument with the new `device="cuda"` argument.

<a id="independent-seed"></a>
<strong>Reproducer-chosen seeds</strong> are seeds selected by the reproducer when the authors do not release the original ones—for example, `42, 43, 44, 45, 46`. They should be fixed and recorded before running to prevent selecting only favorable results afterward. Because they are not the authors' original seeds, the run is not an exact recovery of the original experiment.

<a id="protocol"></a>
A <strong>protocol</strong> is the fixed set of choices used to produce and score a metric, such as the test split, input preprocessing, inference steps, seeds, sample count, and scoring method. Renaming a legacy API argument does not change the protocol; using a different test set or number of inference steps does.

## License

MIT
