#!/usr/bin/env python3
"""Initialize, validate, hash, and compare baseline-reproduction evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

STATES = {"C0", "C1", "C2", "C3", "C4", "C5", "X", "U"}
CORE = (
    "REPRODUCTION_CARD.md",
    "claim.json",
    "source_manifest.jsonl",
    "protocol.json",
    "run_manifest.jsonl",
    "reported_vs_reproduced.json",
    "training_gate.json",
    "commands.sh",
)


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def init_case(args: argparse.Namespace) -> int:
    root = Path(args.case_dir)
    if root.exists() and any(root.iterdir()):
        print(f"refusing to overwrite non-empty case: {root}", file=sys.stderr)
        return 2
    root.mkdir(parents=True, exist_ok=True)
    for name in ("patches", "logs", "outputs"):
        (root / name).mkdir(exist_ok=True)
    (root / "REPRODUCTION_CARD.md").write_text(
        f"# {args.title}\n\n"
        "## Target claim\n\nNot yet frozen.\n\n"
        "## Public artifacts\n\nNot yet audited.\n\n"
        "## Current evidence\n\nC0 — paper claim only.\n\n"
        "## Non-claims\n\nNo local reproduction claim has been established.\n\n"
        "## Next permitted action\n\nComplete the artifact and protocol audit.\n"
    )
    dump(root / "claim.json", {
        "paper_id": args.paper_id, "paper_revision": None, "claim_id": None,
        "paper_location": None, "model_config": None, "dataset_split": None,
        "metric": None, "aggregation": None, "reported_value": None,
        "direction": None,
        "decision_rule": {"absolute_tolerance": None, "relative_tolerance": None},
        "evidence_state": "C0",
    })
    dump(root / "protocol.json", {
        "protocol_id": None, "lane": None, "code_revision": None,
        "checkpoint_sha256": None, "inputs": {}, "inference": {},
        "evaluation": {}, "statistics": {}, "expected_outputs": None,
        "deviations": [],
    })
    dump(root / "reported_vs_reproduced.json", {
        "claim_id": None, "evidence_state": "C0", "paper_reported": None,
        "author_artifact_replay": None, "released_checkpoint_result": None,
        "training_reproduction_result": None, "coverage": None,
        "uncertainty": None, "protocol_deviations": [], "verdict": "not_run",
        "non_claims": [],
    })
    dump(root / "training_gate.json", {
        "decision": "do_not_start",
        "blockers": ["artifact and protocol audit incomplete"],
        "required_artifacts": [], "paper_protocol": {},
        "effective_code_protocol": {}, "compute_estimate": None,
        "start_conditions": [], "stop_conditions": [],
    })
    (root / "source_manifest.jsonl").touch()
    (root / "run_manifest.jsonl").touch()
    commands = root / "commands.sh"
    commands.write_text(
        "#!/usr/bin/env bash\nset -euo pipefail\n"
        "# Append reviewed commands; do not store secrets.\n"
    )
    commands.chmod(0o755)
    print(root)
    return 0


def read_json(path: Path, errors: list[str]) -> dict:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.name}: unreadable JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.name}: top level must be an object")
        return {}
    return value


def validate_jsonl(path: Path, errors: list[str]) -> int:
    count = 0
    try:
        lines = path.read_text().splitlines()
    except OSError as exc:
        errors.append(f"{path.name}: unreadable: {exc}")
        return 0
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{number}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path.name}:{number}: each line must be an object")
        count += 1
    return count


def validate_case(args: argparse.Namespace) -> int:
    root = Path(args.case_dir)
    errors: list[str] = []
    warnings: list[str] = []
    for name in CORE:
        if not (root / name).is_file():
            errors.append(f"missing {name}")
    if errors:
        for item in errors:
            print(f"ERROR {item}")
        return 1
    claim = read_json(root / "claim.json", errors)
    result = read_json(root / "reported_vs_reproduced.json", errors)
    protocol = read_json(root / "protocol.json", errors)
    gate = read_json(root / "training_gate.json", errors)
    source_count = validate_jsonl(root / "source_manifest.jsonl", errors)
    run_count = validate_jsonl(root / "run_manifest.jsonl", errors)
    for label, value in (
        ("claim", claim.get("evidence_state")),
        ("result", result.get("evidence_state")),
    ):
        if value not in STATES:
            errors.append(f"{label} evidence_state must be one of {sorted(STATES)}")
    if claim.get("claim_id") and result.get("claim_id") not in (None, claim.get("claim_id")):
        errors.append("claim_id differs between claim and result")
    high_state = result.get("evidence_state") in {"C3", "C4", "C5", "X"}
    if high_state and run_count == 0:
        errors.append("result state requires at least one run manifest")
    if high_state and not (
        result.get("released_checkpoint_result")
        or result.get("training_reproduction_result")
    ):
        errors.append("result state requires a fresh checkpoint or training result")
    if gate.get("decision") == "approved" and gate.get("blockers"):
        errors.append("training gate is approved but blockers are non-empty")
    if gate.get("decision") not in {"do_not_start", "smoke_only", "approved"}:
        errors.append("training_gate decision is invalid")
    if protocol.get("lane") not in {
        None, "exact", "independent_fixed", "compatibility", "smoke"
    }:
        errors.append("protocol lane is invalid")
    if source_count == 0:
        warnings.append("source manifest is empty; evidence cannot exceed C0")
    if claim.get("reported_value") is None:
        warnings.append("reported_value is not frozen")
    if not protocol.get("protocol_id"):
        warnings.append("protocol_id is not frozen")
    for item in errors:
        print(f"ERROR {item}")
    for item in warnings:
        print(f"WARN  {item}")
    print(
        f"SUMMARY sources={source_count} runs={run_count} "
        f"errors={len(errors)} warnings={len(warnings)}"
    )
    return 1 if errors else 0


def compare(args: argparse.Namespace) -> int:
    absolute = abs(args.actual - args.expected)
    relative = (
        absolute / abs(args.expected)
        if args.expected
        else (0.0 if absolute == 0 else None)
    )
    relative_match = (
        args.rel_tol is not None
        and relative is not None
        and relative <= args.rel_tol
    )
    matched = absolute <= args.abs_tol or relative_match
    print(json.dumps({
        "expected": args.expected, "actual": args.actual,
        "absolute_difference": absolute, "relative_difference": relative,
        "absolute_tolerance": args.abs_tol,
        "relative_tolerance": args.rel_tol, "matched": matched,
    }, indent=2))
    return 0 if matched else 1


def hash_file(args: argparse.Namespace) -> int:
    path = Path(args.path)
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    print(json.dumps({
        "path": str(path), "bytes": path.stat().st_size,
        "sha256": digest.hexdigest(),
    }))
    return 0


def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="create a non-overwriting evidence package")
    init.add_argument("case_dir")
    init.add_argument("--paper-id", required=True)
    init.add_argument("--title", required=True)
    init.set_defaults(func=init_case)
    validate = sub.add_parser("validate", help="check shape and basic consistency")
    validate.add_argument("case_dir")
    validate.set_defaults(func=validate_case)
    comp = sub.add_parser("compare", help="compare one reported and observed scalar")
    comp.add_argument("expected", type=float)
    comp.add_argument("actual", type=float)
    comp.add_argument("--abs-tol", type=float, required=True)
    comp.add_argument("--rel-tol", type=float)
    comp.set_defaults(func=compare)
    hashed = sub.add_parser("hash", help="print file size and SHA-256")
    hashed.add_argument("path")
    hashed.set_defaults(func=hash_file)
    return root


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
