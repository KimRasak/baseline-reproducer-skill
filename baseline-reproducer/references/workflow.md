# Reproduction execution workflow

The repository README is the canonical source for `TD`, `RD`, `TR`, and `RR` grade definitions. This document supplies execution detail only and must not introduce a competing rating system.

## 1. Register one claim

Identify one table/figure cell and freeze the paper revision, model/configuration, checkpoint, reported value, metric, aggregation, dataset and split, evaluator, test protocol, training initialization, and training protocol. Different scientifically material settings are different claims or independently labelled protocol lanes.

## 2. Audit delivery independently of execution

For `TD`, inspect author-released test environment information, claim-matching weights, exact test set/split, test parameters, and test rules. For `RD`, inspect the training environment, exact training data/split, initialization or base weights, training code, all parameters, stopping conditions, checkpoint-selection rule, and training rules.

Use official primary sources and record URLs, revisions, hashes, licenses, identities, and omissions. Delivery grades depend only on what the authors made available and specified. A local run, successful checkpoint, or matching number never changes `TD` or `RD`.

## 3. Bound reproduction by delivery

You may independently download a publicly available dataset and exact split explicitly identified by the authors. You may run preprocessing that the paper or official repository fully specifies. These are retrieval or deterministic reconstruction and do not reduce `TR` or `RR`.

Do not write missing author training code or guess omitted training parameters, stopping conditions, or checkpoint-selection rules. Record them as missing. Any result from a reproducer-written implementation, guessed setting, substituted dataset, reduced model, or materially altered protocol belongs to a clearly labelled independent protocol and is not strict reproduction.

## 4. Freeze protocol and agreement rule

Before execution, save effective environment versions, code and artifact hashes, input IDs, parameters, seeds, retries, preprocessing, metric implementation, aggregation, expected output count, and an absolute or relative tolerance. Base tolerance on reporting precision, metric variability, and domain convention; never loosen it after seeing the result.

A compatible CUDA, driver, or hardware version does not reduce `TR` or `RR` when documented and verified not to alter computation/training semantics, precision mode, or result interpretation.

## 5. Execute cheapest-first

1. Verify files, versions, identities, and hashes.
2. Import code and strictly load the checkpoint.
3. Produce one readable, correctly paired output.
4. Verify the evaluator accepts a tiny valid input and emits per-item output.
5. Run a frozen subset and validate complete mappings and denominators.
6. Run the full checkpoint test.
7. For eligible training, read a real batch, compute losses, backpropagate, step, save, reload, and resume.
8. Run full training only after the target test endpoint is closed.

An interface smoke, tiny subset, or evaluator replay is not a full checkpoint reproduction.

## 6. Check output integrity before scoring

Validate planned versus observed IDs, sample count, input-output and input-label pairing, seeds, hashes and duplicates, readability, schema/shape, failed items, retries, denominator coverage, and raw-input-to-score mapping. Exit code zero is insufficient.

Freeze the output set before scoring. Save evaluator command/environment, code and weight hashes, per-item scores, coverage, aggregation, and result hash. Evaluator replay uses author-released outputs and scoring code; it verifies scoring, not model generation or training.

## 7. Apply the training compute gate

Compare local compute with the training resources stated by the paper or official repository. If local resources are lower, skip training reproduction and record `RR-NR`. Do not reduce model size, data, epochs/steps, world size, or precision and then grade the run as reproduction of the original claim.

## 8. Close and grade

Retain commands, logs, outputs, hashes, failed attempts, superseded results, compatibility changes, resource interference, and deviations.

Assign all four dimensions using the README:

- `TD` and `RD`: author delivery only.
- `TR`: actual checkpoint-to-metric execution, protocol alignment, evidence, and numeric agreement.
- `RR`: actual initialization-to-trained-checkpoint-to-metric execution, subject to compute eligibility.

`TR-O` and `RR-O` require values within the preregistered tiny tolerance. A strictly aligned result outside tolerance may receive the applicable lower reproduction grade, with the numeric verdict separately recorded as `not_matched` or `contradicted_under_pinned_protocol`.
