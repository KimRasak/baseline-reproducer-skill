# Evidence model

## Atomic claim key

Track evidence at this granularity:

```text
(paper revision, table/figure row, model/config, checkpoint,
 training data, evaluation data/split, inference protocol,
 evaluator code/weights, metric, aggregation, reported value)
```

Two numbers belong to one lane only when all scientifically material fields match. Otherwise create a new independent or compatibility lane.

## Claim-evidence ladder

| State | Evidence reached | Permitted wording |
|---|---|---|
| C0 | Value/order appears in the paper | “The paper reports…” |
| C1 | Code, data references, checkpoint and evaluator identities traced | “Artifacts were traced…” |
| C2 | Official evaluator replays author outputs/scores, or an interface/deployment smoke succeeds | Name the exact subtype only |
| C3 | Matching released checkpoint generates fresh outputs and recovers the metric under the frozen protocol | “Released-checkpoint metric reproduced…” |
| C4 | Public raw data through preprocessing, training, checkpoint, inference, evaluation and aggregation is reproduced | “The paper claim/process was reproduced…” |
| C5 | Independent implementation or independently reconstructed data also recovers the claim | “Independently replicated…” |
| X | Exact available protocol repeatedly yields a stable incompatible result after plausible implementation causes are excluded | “Contradicted under the pinned protocol…” |
| U | Required artifacts cannot legally or practically be reconstructed | “Untestable from the public release…” |

Do not use C2 without a subtype such as evaluator replay, media-interface smoke, or deployment. Only C4/C5 permits the unqualified phrase “the paper claim was reproduced.”

## Artifact readiness

Readiness ranks execution candidates; it is not claim evidence:

| Level | Public artifacts |
|---|---|
| A | Matching weights, evaluation protocol, reconstructable training data/config, and affordable full process |
| B | Exact checkpoint evaluation possible; training data/preprocessing incomplete |
| C | Official code and evaluation exist; matching checkpoint absent |
| D | Weights run, but checkpoint identity or paper protocol is incomplete |
| E | Material code, weights, data, evaluator, or license missing |

## Multidimensional fidelity

Record data, training, inference, evaluation, statistical, and numerical fidelity separately. A total can agree while important components diverge; compare the full profile when available.

## Verdict vocabulary

Prefer narrow values: `artifact_audit_complete`, `blocked_missing_artifact`, `deployment_smoke_passed`, `evaluator_interface_passed`, `evaluator_replay_matched`, `checkpoint_metric_matched`, `checkpoint_metric_not_matched`, `independent_protocol_result`, `training_process_smoke_passed`, `training_claim_reproduced`, or `untestable_from_public_release`.
