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
- Distinguish evaluator replay, released-checkpoint metric reproduction, and full training reproduction.
- Pin code revisions, artifact hashes, data splits, seeds, and evaluation protocols.
- Retain failed runs, compatibility changes, resource interference, and invalidated results.
- Stop explicitly when critical data, weights, or protocol details are missing; do not make an unlabelled substitution.
- Start expensive training only after checkpoint verification and the training gate are complete.

### Example: released weights and evaluation code, but incomplete training artifacts

Suppose a paper reports `82.7%` accuracy on a public test set and releases a checkpoint, evaluation script, and training script, but does not release the exact training-data manifest used for the paper.

The skill proceeds as follows:

1. Pin the paper revision, official code commit, checkpoint SHA-256, test-set version, and evaluation command.
2. Run the official evaluation script with the official checkpoint.
3. If the fresh result is `82.6%` and the preregistered tolerance is `±0.3` percentage points, record a released-checkpoint metric match.
4. Audit the training path and discover that its only data URL is dead, leaving the actual samples, filtering, and split unknown.
5. Set the training gate to `do_not_start` instead of silently substituting a similar dataset.
6. Report: “The released-checkpoint metric is supported; the full training process is not reproducible from the public release.”

This is not a full-paper reproduction, but the missing training artifacts also do not invalidate the checkpoint-level result. The two conclusions remain separate.

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

## License

MIT
