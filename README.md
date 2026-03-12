# Division by 0 — Branch-Aware Guarded Algebra

A research-style symbolic algebra prototype built around the primitive rule:

```text
a / 0 := a
```

This rule is **not** interpreted as inverse division. Instead, the project treats division by zero as a **branch-sensitive rewrite rule** inside a guarded symbolic framework.

## What this repo is trying to achieve

The project is not trying to replace ordinary arithmetic or claim a new field structure.

It is trying to build a **branch-aware symbolic system** that:

- preserves zero and nonzero denominator cases explicitly
- blocks illegal nonzero-only rewrites before branching
- supports guarded normalization of expressions
- supports branch-first equation solving
- returns guarded or extracted solutions instead of forcing one global simplification

In plain terms:

> turn “division by zero breaks everything” into a controlled symbolic case split.

## Core idea

For a quotient `A / B`:

- if `B` is proven zero, rewrite `A / B -> A`
- if `B` is proven nonzero, ordinary algebra is allowed locally
- if `B` is unresolved, keep both branches

Typical output:

```text
[B = 0]  -> A
[B != 0] -> A / B
```

instead of collapsing too early.

## Hard constraint: the branch firewall

The central rule of the repo is:

> No simplification that requires a denominator to be nonzero may be applied before branch split.

So these are **not allowed globally**:

- `x / x -> 1`
- factor cancellation across a denominator
- denominator clearing
- cross multiplication

They become legal only inside a branch whose guard proves the denominator is nonzero.

## Current repository state

The repo currently contains the root files `README.md` and `README-1.md`, and a main folder called `division_by_zero_repo_bundle`. The repo page currently presents the project as “Division by 0 — Branch Arithmetic and Zero-Set Detector Experiments.” citeturn374222view0

The current README already frames the project as a guarded symbolic system built around `a / 0 := a`, with branch splitting, NZ-only ordinary algebra, hidden-zero detection, and guarded equation solving. citeturn374222view0

## Recommended reading order

For a new reader, this is the cleanest order:

1. `README.md`
2. `division_by_zero_repo_bundle/core_semantics_v1.md`
3. `division_by_zero_repo_bundle/rewrite_rules_v1.md`
4. `division_by_zero_repo_bundle/denominator_classifier_v1.md`
5. `division_by_zero_repo_bundle/normal_form_engine_v1.md`
6. `division_by_zero_repo_bundle/branch_merge_and_equivalence_v1.md`
7. `division_by_zero_repo_bundle/solver_semantics_v1.md`
8. `division_by_zero_repo_bundle/solver_acceptance_tests_v1.md`
9. prototype Python engine and stress-test runner

## Suggested folder intent

The repo is strongest when read as three layers:

### 1. Specs
These define the formal behavior:

- `core_semantics_v1.md`
- `rewrite_rules_v1.md`
- `denominator_classifier_v1.md`
- `normal_form_engine_v1.md`
- `branch_merge_and_equivalence_v1.md`
- `solver_semantics_v1.md`
- `solver_acceptance_tests_v1.md`

### 2. Prototype engine
These implement the current behavior experimentally:

- `minimal_guarded_engine.py`
- `run_stress_tests.py`

### 3. Legacy / exploratory drafts
These preserve the evolution of the idea:

- earlier branch arithmetic drafts
- detector-algebra notes
- older verifier scripts
- historical outputs

## What is already working

The current prototype direction is strong on:

- primitive zero-denominator evaluation
- branch-first normalization
- guarded simplification on nonzero branches
- simple guard-aware reductions
- basic branch-aware equation classification
- simple residual solving
- first-pass solution extraction

## What is not yet claimed

This repo does **not** currently claim:

- classical field semantics
- full confluence
- full completeness
- calculus or analytic semantics
- unrestricted symbolic simplification
- full multivariable solving

## Best interpretation

This repo should be read as:

> a branch-sensitive symbolic rewrite and solving framework for zero/nonzero denominator reasoning

and **not** as:

> a drop-in replacement for ordinary arithmetic.

## Tidy-up recommendations

The repo would be cleaner with these changes:

1. Keep a single root `README.md` and remove or archive `README-1.md`.
2. Keep current production files inside `division_by_zero_repo_bundle/`.
3. Add a small `LICENSE` file if you want reuse by others.
4. Consider renaming the repo later from `division_by_zero_expirment_00` to `division_by_zero_experiment_00` for polish.
5. Separate files into:
   - `specs/`
   - `engine/`
   - `legacy/`
   in a later cleanup pass.

## Immediate next milestone

The next meaningful milestone is:

> stabilize the current solver prototype against the acceptance-test suite before expanding the theory further.

That keeps the project grounded and makes future changes easier to evaluate.
