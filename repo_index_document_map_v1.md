# Repository Index / Document Map v1

This document maps the repository by purpose, reading order, and expected use.

---

## 1. Quick start by goal

### If you want the shortest path to the core idea
1. `README.md`
2. `branch_arithmetic_draft.md`
3. `minimal_theorem_list_v1.md`

### If you want the formal rule layer
1. `formal_axioms_inference_rules_v1.md`
2. `glossary_and_notation_appendix_v1.md`
3. `worked_theorem_examples_appendix_v1.md`

### If you want the solver story
1. `equation_solver_draft_v1.md`
2. `unified_branch_solver_spec_v1.md`
3. `branch_local_soundness_notes_v1.md`
4. `solver_completeness_boundaries_v1.md`

### If you want to understand limitations and future work
1. `solver_completeness_boundaries_v1.md`
2. `roadmap_v1.md`
3. `CONTRIBUTING.md`

### If you want to run code first
1. `branch_equation_verifier.py`
2. `branch_equation_parser_verifier.py`
3. `branch_normal_form_engine.py`
4. `branch_expression_normal_form_engine.py`
5. matching `*_output.txt` files

---

## 2. Repository layers

### Layer A — project overview
- `README.md`
  - front-page overview, scope, reading order, and repo summary
- `repo_index_document_map_v1.md`
  - navigation map across all documents and tools

### Layer B — high-level theory drafts
- `branch_arithmetic_draft.md`
  - the main prose draft of the branch arithmetic idea
- `equation_solver_draft_v1.md`
  - first solver-focused draft with worked cases
- `unified_branch_solver_spec_v1.md`
  - unifies expression branching and equation solving

### Layer C — proof / claim hardening
- `branch_local_soundness_notes_v1.md`
  - branch-local soundness arguments for the solver kernel
- `solver_completeness_boundaries_v1.md`
  - precise boundaries on what the current solver can and cannot claim
- `minimal_theorem_list_v1.md`
  - compact named propositions that summarize the current core claims

### Layer D — reference / formalization
- `glossary_and_notation_appendix_v1.md`
  - fixed terminology and notation
- `formal_axioms_inference_rules_v1.md`
  - compact theorem-style rule sheet
- `worked_theorem_examples_appendix_v1.md`
  - maps formal rules to concrete examples

### Layer E — planning / repo process
- `roadmap_v1.md`
  - staged development roadmap
- `CONTRIBUTING.md`
  - contribution rules and repo discipline
- `github_publish_commands.txt`
  - example shell commands for publishing to GitHub

### Layer F — plain-text mirrors
- `branch_arithmetic_draft.txt`
- `branch_local_soundness_notes_v1.txt`

### Layer G — experimental tools
- `branch_equation_verifier.py`
  - schema-based equation verifier
- `branch_equation_parser_verifier.py`
  - parser-based equation verifier
- `branch_normal_form_engine.py`
  - denominator classification + equation engine
- `branch_expression_normal_form_engine.py`
  - expression-level branch normal-form engine

### Layer H — sample outputs
- `branch_equation_verifier_output.txt`
- `branch_equation_parser_verifier_output.txt`
- `branch_normal_form_engine_output.txt`
- `branch_expression_normal_form_engine_output.txt`

---

## 3. Suggested reading paths

### Path 1 — reader new to the project
1. `README.md`
2. `branch_arithmetic_draft.md`
3. `glossary_and_notation_appendix_v1.md`
4. `minimal_theorem_list_v1.md`
5. `worked_theorem_examples_appendix_v1.md`

### Path 2 — reviewer checking mathematical structure
1. `formal_axioms_inference_rules_v1.md`
2. `branch_local_soundness_notes_v1.md`
3. `solver_completeness_boundaries_v1.md`
4. `minimal_theorem_list_v1.md`

### Path 3 — reviewer checking solver behavior
1. `equation_solver_draft_v1.md`
2. `unified_branch_solver_spec_v1.md`
3. `branch_normal_form_engine.py`
4. `branch_expression_normal_form_engine.py`
5. sample outputs

### Path 4 — contributor adding features
1. `CONTRIBUTING.md`
2. `glossary_and_notation_appendix_v1.md`
3. `formal_axioms_inference_rules_v1.md`
4. `solver_completeness_boundaries_v1.md`
5. `roadmap_v1.md`

---

## 4. Minimal core set

If someone wants only the smallest serious subset of the repo, use these files:
- `README.md`
- `branch_arithmetic_draft.md`
- `unified_branch_solver_spec_v1.md`
- `branch_local_soundness_notes_v1.md`
- `formal_axioms_inference_rules_v1.md`
- `minimal_theorem_list_v1.md`

That set is the smallest coherent publication package.

---

## 5. Experimental vs stable documents

### More stable
- `README.md`
- `glossary_and_notation_appendix_v1.md`
- `formal_axioms_inference_rules_v1.md`
- `minimal_theorem_list_v1.md`
- `branch_local_soundness_notes_v1.md`

### More exploratory
- `branch_arithmetic_draft.md`
- `equation_solver_draft_v1.md`
- `roadmap_v1.md`
- Python tools and sample outputs

---

## 6. What the code is for

The Python files are not presented as final proof artifacts. They are experimental verification tools used to:
- test branch-split behavior,
- test denominator classification,
- check example families,
- expose mismatches between the prose rules and actual execution.

The prose documents remain authoritative when there is a mismatch.

---

## 7. Current publication posture

The repository currently supports four reading layers:
1. overview and motivation,
2. formal rules,
3. theorem/proof notes,
4. experimental verification.

This is enough for a serious exploratory repo, but not yet a finished mathematical monograph.
