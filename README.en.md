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

### Delivery completeness grade definitions

Delivery grades apply to `TD` and `RD`. They assess only what chain the authors' released materials can support; the reproducer's execution does not count toward these grades. The example below still uses Table 1 of `Paper X`, which reports `b1=82.7`. The examples primarily illustrate `TD`; apply the same scale to the released raw-data-to-checkpoint materials for `RD`.

| Grade | Chain completeness | Delivery meaning | `Paper X / b1=82.7` example |
|---|---|---|---|
| <strong>AAA</strong> | Fully closed | All required artifacts, identities, protocols, splits, and aggregation details are explicitly released, allowing the original chain to be closed. | The authors release the exact Table 1 checkpoint, full test split, evaluation code, seeds, and aggregation procedure. |
| <strong>AA</strong> | Substantially closed | The main-chain materials are complete, requiring only traceable compatibility handling or deterministic reconstruction that does not alter scientific meaning. | All official artifacts exist, but the test manifest must be deterministically rebuilt by a released script, or the code needs only a legacy API-call update[^api-call]. |
| <strong>A</strong> | Executable with material limitations | Core materials support claim-level validation, but seeds, exact versions, checkpoint selection, or statistical details remain unresolved. | The checkpoint, code, and data exist, but author seeds are missing, so the original test setup cannot be recovered strictly. |
| <strong>BBB</strong> | Partial chain | The release supports only evaluator replay, a frozen subset, or an independent protocol; the paper's original metric chain cannot be closed. | No checkpoint is released—only ready-made predictions and scoring code. These can recalculate `82.7` but cannot show that the model produces those predictions. |
| <strong>BB</strong> | Smoke only | The release supports at most import, checkpoint loading, one-sample inference, or evaluator-interface checks. | A checkpoint and example script are released, but the full test split or executable full-evaluation entry point is absent. |
| <strong>B</strong> | Artifacts traced | Some code, weight, or data entry points are known, but they do not yet form an executable metric chain. | A repository and weight URL are found, but the weight cannot be tied to Table 1 and no evaluation command is provided. |
| <strong>CCC</strong> | Critically incomplete | A key checkpoint, code path, dataset, split, pairing key, or evaluator is absent, so the public release cannot test the claim. | The paper reports `82.7`, but releases no matching weight, test split, or metric implementation. |
| <strong>D</strong> | Invalid chain | A released artifact's identity or protocol conflicts with the target claim and cannot be attributed to it. | The download points to another model variant, or the released script uses a different `Dataset 1` split. |
| <strong>NR</strong> | Not rated/not applicable | Delivery artifacts have not yet been audited, or this delivery dimension does not apply to the claim. | `b1=82.7` is registered, but the authors' code, weights, data, and evaluation materials have not been inspected. |

### Reproduction completeness grade definitions

Reproduction grades apply to `TR` and `RR`. They assess how far the reproducer actually executed and audited the chain. Merely available materials do not earn a high reproduction grade if they have not been run. The examples primarily illustrate `TR`; apply the same scale to actual raw-data-to-new-checkpoint-to-metric execution for `RR`.

| Grade | Chain completeness | Reproduction meaning | `Paper X / b1=82.7` example |
|---|---|---|---|
| <strong>AAA</strong> | Fully closed | The target chain was fully executed, fully audited, and subjected to required repetitions/uncertainty analysis, with inspectable evidence retained. | With checkpoint, full split, seeds, and aggregation pinned, a complete rerun gives `82.6` within the preregistered tolerance; per-item and repeated-run evidence is retained. |
| <strong>AA</strong> | Substantially closed | The complete main chain was executed and audited with only traceable compatibility handling or deterministic reconstruction that does not alter scientific meaning. | A recorded patch changes only an API call—not the model or protocol[^protocol]—and the complete rerun gives `82.6`. |
| <strong>A</strong> | Executable with material limitations | A claim-level run is complete, but seeds, exact versions, checkpoint selection, or statistical details cannot be strictly aligned with the paper. | Author seeds are missing. The reproducer preregisters reproducer-chosen seeds[^independent-seed], completes the full test, and gets `82.5`; only an independent fixed-protocol result is defensible. |
| <strong>BBB</strong> | Partial chain | Evaluator replay, a frozen subset, or an independent-protocol validation was executed, but the paper's original metric chain remains open. | Without loading the model, the reproducer feeds released predictions into the scorer and recovers `82.7` (evaluator replay[^evaluator-replay]). |
| <strong>BB</strong> | Smoke only | Only import, checkpoint loading, one-sample inference, or evaluator-interface execution was completed. | The checkpoint loads and predicts one `Dataset 1` sample; the full test set has not run. |
| <strong>B</strong> | Artifacts traced | Some artifacts or entry points were located, but no metric-producing chain has run successfully. | The repository and weight were downloaded, but weight identity is unconfirmed and the evaluation command has not run. |
| <strong>CCC</strong> | Critically incomplete | Missing critical artifacts or protocol details prevent execution from starting or reaching a claim-testable state. | The matching weight and test split are absent, so the `b1` test chain cannot run. |
| <strong>D</strong> | Invalid chain | The run used the wrong identity or a substituted protocol; its result is invalidated and cannot be attributed to the target claim. | After execution, the weight is found to be another model variant or the split to differ; the resulting number cannot belong to `b1`. |
| <strong>NR</strong> | Not rated/not applicable | This reproduction dimension has not yet been executed or audited, or it does not apply to the claim. | `b1=82.7` is registered, but execution of its test chain has not begun. |

The grade measures <strong>chain completeness, not performance or paper credibility</strong>. A complete pinned reproduction that stably disagrees with the paper may still be `TR-AAA` (Test Reproduction Completeness AAA), with the numeric outcome separately recorded as `not_matched` or `contradicted_under_pinned_protocol`. A nearby number alone never earns a high grade.

### Rating example

| Claim | Type | TD | RD | TR | RR | Outcome |
|---|---|:---:|:---:|:---:|:---:|---|
| `b1` | self-model | AAA | AA | AAA | BBB | matched |
| `b2` | self-model | A | CCC | A | NR | not_strictly_comparable |
| `a1` | other-model | BBB | NR | BBB | NR | author_table_only |
| `a2` | other-model | D | NR | D | NR | invalidated |

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
