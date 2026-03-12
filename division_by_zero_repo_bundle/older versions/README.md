# Division by 0 — Branch Arithmetic and Zero-Set Detector Experiments

This repository collects a developing formalism for **branch-evaluated arithmetic** built around the rule

- `a / 0 := a`

interpreted **not** as inverse division, but as a **rewrite / erasure rule**.

The project does **not** claim to extend ordinary field arithmetic in the classical sense. Instead, it develops a guarded symbolic system in which:

- division has a **zero branch** and a **nonzero branch**,
- zero denominators are handled by **branch splitting** rather than immediate failure,
- ordinary algebra is preserved only on **NZ-branches**,
- hidden zero denominators are detected by a dedicated normalization engine,
- equation solving returns **guarded solution objects** rather than forcing one global expression.

---

## Core idea

For a quotient `A / B`:

- if `B` normalizes to `0`, then `A / B -> A`
- if `B` normalizes to nonzero, then ordinary division applies
- if `B` is unresolved, both branches are retained

This leads to **Branch Normal Form** outputs such as:

- `[B = 0] -> A`
- `[B != 0] -> A / B`

rather than prematurely collapsing to a single expression.

---

## Hard constraint

A central rule of the system is the **branch firewall**:

> No simplification that requires a denominator to be nonzero may be used before branch split.

So moves like cancellation across the main quotient, cross-multiplication, and inverse-style division laws are treated as **NZ-branch-only**.

---

## Semantic base

This repo builds on the earlier **Zero-Set Detector Algebra** idea, especially:

- bottom-up denominator evaluation,
- the primitive rule `a/0 := a`,
- detector functions
  - `D_f := 1 - f/f`  (zero detector)
  - `N_f := f/f`      (nonzero detector)
- detector laws such as
  - `D_f + N_f = 1`
  - `D_f N_f = 0`

These detectors are used as formal guards whenever possible.

---

## Repository contents

### Main documents

- `repo_index_document_map_v1.md`
  - navigation map across the full repo
- `branch_arithmetic_draft.md`
  - high-level draft of the branch arithmetic framework
- `equation_solver_draft_v1.md`
  - first solver rules and worked examples
- `unified_branch_solver_spec_v1.md`
  - unified pipeline: expression branching first, equation solving second
- `branch_local_soundness_notes_v1.md`
  - branch-local soundness notes for the solver kernel
- `minimal_theorem_list_v1.md`
  - compact list of the current named theorem-level claims

### Reference text mirrors

- `branch_arithmetic_draft.txt`
- `branch_local_soundness_notes_v1.txt`

### Python tools

- `branch_equation_verifier.py`
  - first kernel verifier for equation schema cases
- `branch_equation_parser_verifier.py`
  - parser-based verifier for equation strings
- `branch_normal_form_engine.py`
  - branch-normal-form equation engine with denominator classification
- `branch_expression_normal_form_engine.py`
  - expression-level branch normal form engine

### Sample outputs

- `branch_equation_verifier_output.txt`
- `branch_equation_parser_verifier_output.txt`
- `branch_normal_form_engine_output.txt`
- `branch_expression_normal_form_engine_output.txt`

### Helper

- `github_publish_commands.txt`
  - example shell commands for publishing files to GitHub

---

## Current status

### Established

- branch firewall
- branch-normal-form output shape
- denominator normalization pipeline
- hidden-zero detection modules
- solver kernel v1
- branch-local soundness notes
- small experimental verifier tools

### Not yet claimed

- full confluence proof
- full completeness proof
- classical field semantics
- analytic / calculus semantics
- unrestricted symbolic simplification

---

## Intended interpretation

This project is best read as:

> a **branch-sensitive symbolic rewrite system** with detector-backed guards,
> not as a drop-in replacement for standard arithmetic.

It is primarily aimed at:

- guarded symbolic reasoning,
- explicit zero/nonzero case preservation,
- experimental formal systems around division by zero,
- equation solving with branch-aware semantics.

---

## Suggested reading order

1. `repo_index_document_map_v1.md`
2. `branch_arithmetic_draft.md`
3. `equation_solver_draft_v1.md`
4. `unified_branch_solver_spec_v1.md`
5. `branch_local_soundness_notes_v1.md`
6. `formal_axioms_inference_rules_v1.md`
7. `minimal_theorem_list_v1.md`
8. Python tools and sample outputs

---

## Scope boundary

This repository currently focuses on:

- expressions built from `+`, `-`, `*`, `/`
- guarded branch evaluation
- denominator-zero detection
- branch-aware equation solving

It intentionally avoids making stronger claims about:

- limits,
- continuity,
- derivatives,
- unrestricted polynomial identity solving,
- equivalence with ordinary algebra outside guarded NZ-branches.

---

## License / publication note

No license file is included in this bundle by default. If you want this repo to be reusable by others, add a license explicitly before publishing.
