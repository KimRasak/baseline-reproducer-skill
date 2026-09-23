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

### Rating scale

The following running example uses one fictional claim: Table 1 of `Paper X` reports `b1=82.7` for its model on `Dataset 1`. Each row shows how the same claim is graded under a different artifact and execution state.

| Grade | Chain completeness | Meaning | `Paper X / b1=82.7` example |
|---|---|---|---|
| <strong>AAA</strong> | Fully closed | Artifacts, identities, protocols, splits, and aggregation are explicit. For reproduction, the complete run, full audit, and required repetitions/uncertainty analysis are also complete. | The matching checkpoint, full test split, evaluation code, seeds, and aggregation are pinned. A complete rerun gives `82.6`, within the preregistered tolerance, with per-item results retained. |
| <strong>AA</strong> | Substantially closed | The main chain is complete with only traceable compatibility handling or deterministic reconstruction that does not alter scientific meaning. | All official artifacts exist, but a legacy API no longer runs. A recorded compatibility patch changes only the API call—not the model or protocol[^protocol]—and the rerun gives `82.6`. |
| <strong>A</strong> | Executable with material limitations | Claim-level validation is possible, but seeds, exact versions, checkpoint selection, or statistical details remain unresolved; not a strict reproduction. | The checkpoint, code, and data exist, but author seeds are missing. A preregistered independent seed gives `82.5`, so only an independent fixed-protocol result is defensible. |
| <strong>BBB</strong> | Partial chain | Evaluator replay, a frozen subset, or an independent protocol can run, but the paper's exact metric chain is not closed. | The authors release predictions and scoring code only. Rescoring recovers `82.7`, but no matching checkpoint exists to show that the model can produce those predictions. |
| <strong>BB</strong> | Smoke only | Establishes import, checkpoint load, one-sample inference, or evaluator-interface execution only. | The checkpoint loads and predicts one `Dataset 1` sample. The full test set has not run, so no comparison with `82.7` is possible. |
| <strong>B</strong> | Artifacts traced | Some code, weight, or data entry points are known, but no executable metric chain exists yet. | A repository and weight URL are found, but the weight cannot yet be tied to Table 1 and no working evaluation command is identified. |
| <strong>CCC</strong> | Critically incomplete | A key checkpoint, code path, dataset, split, pairing key, or evaluator is absent, so the public release cannot test the claim. | The paper reports `82.7`, but releases no matching weight, test split, or metric implementation; the claim cannot be tested. |
| <strong>D</strong> | Invalid chain | Artifact identity is wrong, the protocol was silently substituted, the result was invalidated, or the evidence cannot belong to the target claim. | The downloaded weight is later found to be another model variant, or a different `Dataset 1` split was used. The number cannot be attributed to `b1` and is invalidated. |
| <strong>NR</strong> | Not rated/not applicable | Not yet audited, or the dimension does not apply to this claim. | `b1=82.7` has been registered, but its code, weight, data, and evaluation artifacts have not yet been audited. |

The grade measures <strong>chain completeness, not performance or paper credibility</strong>. A complete pinned reproduction that stably disagrees with the paper may still be `TR-AAA` (Test Reproduction Completeness AAA), with the numeric outcome separately recorded as `not_matched` or `contradicted_under_pinned_protocol`. A nearby number alone never earns a high grade.

### AAA requirements by dimension

<strong>TD-AAA (Test Delivery Completeness AAA)</strong> requires a claim-matching downloadable checkpoint; available evaluation code and dependent weights, or an unambiguous metric definition; obtainable test data with the complete original split/pairing; specified inference, preprocessing, seeds/sample count, failure handling and aggregation; and freezable versions, licenses and sources.

<strong>RD-AAA (Training Delivery Completeness AAA)</strong> additionally requires executable training code/configuration; raw training data with sample manifest, filtering, preprocessing and original split, or deterministic public reconstruction; all initialization/teacher/reward artifacts; and optimizer, schedule, batch, steps, randomness, compute, checkpoint selection and resume settings.

<strong>TR-AAA (Test Reproduction Completeness AAA)</strong> requires the reproducer to execute the frozen TD-AAA (Test Delivery Completeness AAA) path, audit all outputs, run the evaluator independently, retain per-item results, reproduce aggregation, and predeclare repetitions and uncertainty for stochastic evaluation.

<strong>RR-AAA (Training Reproduction Completeness AAA)</strong> requires executing preprocessing, complete training, checkpoint selection, inference, evaluation and aggregation from public raw data while preserving provenance. Numeric agreement is recorded separately as `matched`, `not_matched`, or an uncertainty-aware conclusion.

### Rating example

| Claim | Type | TD (Test Delivery) | RD (Training Delivery) | TR (Test Reproduction) | RR (Training Reproduction) | Numeric outcome | Explanation |
|---|---|---:|---:|---:|---:|---|---|
| `b1` | self-model | AAA | AA | AAA | BBB | matched | Exact weights, test set and evaluator were released and replayed; training data requires a public reconstruction script, and only a training subset has run. |
| `b2` | self-model | A | CCC | A | NR | not_strictly_comparable | Weights are public, but seeds and the full test split are missing; training data is unavailable. Only an independent fixed-protocol result is defensible. |
| `a1` | other-model | BBB | NR | BBB | NR | author_table_only | The current paper did not rerun SOTA1; it copied the original paper's number. Audit the SOTA1 paper separately. |
| `a2` | other-model | D | NR | D | NR | invalidated | SOTA1 used a different dataset split from Ours although both appear in the same comparison column. |

For other-model claims, also record whether the value was `cited_from_original_paper`, `rerun_by_current_authors`, or `unclear`. Only an actual rerun under the same protocol belongs directly to the current table's test chain; copying a cited number is not a reproduction by the current authors.

## Install

Copy or symlink `baseline-reproducer/` into the skill directory used by Codex, Claude Code, Cursor, or another Agent Skills-compatible client.

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/baseline-reproducer" ~/.codex/skills/baseline-reproducer
```

Then ask: “Use `$baseline-reproducer` to audit this paper's official artifacts and reproduce the strongest claim the public release supports.”

## Helper

```bash
python baseline-reproducer/scripts/repro_case.py init work/my-paper \
  --paper-id my-paper --title "My Paper baseline reproduction"
python baseline-reproducer/scripts/repro_case.py validate work/my-paper
```

The helper validates evidence-package structure, not scientific truth.

## Origin

The workflow was distilled from a long-running reproduction effort across released video-generation checkpoints, evaluators, public datasets and multi-GPU paths. It generalizes identity freezing, protocol lanes, output-integrity audits, evaluator replay, non-overwriting evidence, explicit invalidation, and refusal of scientifically material substitutions.

No private artifacts, credentials, machine paths, or experiment data are included.

[^evaluator-replay]: <strong>Evaluator replay</strong> means recalculating a paper's score from the authors' released outputs and evaluation code. For example, the authors release 1,000 generated videos and the VBench code; rerunning it gives `81.0`, matching the paper's `81.0`. This shows only that the scoring process is reproducible—not that the model generation or training process is reproducible.

[^protocol]: A <strong>protocol</strong> is the fixed set of choices used to produce and score a metric, such as the test split, input preprocessing, inference steps, seeds, sample count, and scoring method. Renaming a legacy API argument does not change the protocol; using a different test set or number of inference steps does.

## License

MIT
