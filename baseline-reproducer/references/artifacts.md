# Evidence package

## Structure

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

Use `scripts/repro_case.py init`. Store large artifacts by official URI/revision/hash when redistribution is inappropriate.

## Core semantics

- `claim.json`: atomic claim, paper location/value, metric, aggregation, direction, decision rule, evidence state.
- `source_manifest.jsonl`: one official artifact per line with role, channel, URI, revision, path, bytes, SHA-256, license and status. “Already local” is not a source channel.
- `protocol.json`: actual effective configuration and exact/independent/compatibility/smoke lane.
- `run_manifest.jsonl`: append-only runs, including invalid attempts, command hash, environment, accelerator mapping, observed output counts, interference and exclusion reason.
- `reported_vs_reproduced.json`: keep paper report, author-artifact replay, fresh checkpoint result, and training result in separate fields.
- `training_gate.json`: `do_not_start`, `smoke_only`, or `approved`, with blockers, compute, start and stop conditions.
- `REPRODUCTION_CARD.md`: skeptical-reader summary of target, artifacts, conflicts, evidence, failures, non-claims and next permitted action.

Never replace raw media/data with derived features as provenance. Never put a paper value in a fresh-result field.

Run `python scripts/repro_case.py validate path/to/case`. This checks structure and basic consistency, not scientific truth.
