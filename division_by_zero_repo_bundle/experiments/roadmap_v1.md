# Roadmap v1

## Goal

Turn the current branch-arithmetic project from a promising formal sketch into a reviewable symbolic theory with explicit scope, proofs, and executable verification.

---

## Phase 1 — Harden the formal core

### Completed
- branch firewall
- branch normal form
- denominator zero-detection kernel
- hidden-zero modules HZ-1 / HZ-2 / HZ-3
- solver kernel v1
- branch-local soundness notes

### Next targets
- solver completeness boundaries
- notation cleanup across all docs
- one canonical glossary of terms
- one canonical statement of scope and non-goals

---

## Phase 2 — Unify the spec

### Objectives
- make one consistent terminology set across all docs
- align examples so the same equations are reused across drafts
- remove duplicated or conflicting wording

### Deliverables
- unified notation appendix
- glossary
- assumptions and domain note
- versioned changelog

---

## Phase 3 — Strengthen the solver theory

### Objectives
- extend equation-solving rules carefully
- separate kernel-complete cases from heuristic cases
- formalize branch pruning and branch merging criteria

### Candidate deliverables
- Solver Kernel v2
- nested-quotient rule notes
- guard simplification notes
- branch-product solving notes

---

## Phase 4 — Strengthen the verifier tools

### Objectives
- keep implementation aligned with the theory
- avoid silent illegal rewrites
- add reproducible regression examples

### Candidate deliverables
- test suite for kernel equation schemas
- test suite for hidden-zero families
- branch normal form JSON output option
- rule-trace mode for debugging derivations

---

## Phase 5 — Restricted proof goals

### Objectives
- prove only what is realistically provable now
- avoid overclaiming global confluence or completeness

### Candidate proof targets
- branch-local soundness for all kernel solver rules
- classifier stability on selected denominator families
- termination of bounded denominator normalization on selected fragments
- kernel completeness relative to the current classifier

---

## Phase 6 — Optional extensions

These should come only after the core survives review.

### Possible extensions
- powers
- absolute value
- domain modules
- richer detector algebra integration
- nested branch normal form for composed expressions

### Deferred topics
- limits
- calculus
- full polynomial identity reasoning
- unrestricted global simplification
- analytic semantics

---

## Recommended immediate order

1. solver completeness boundaries
2. glossary and notation appendix
3. changelog / versioning
4. kernel test suite plan
5. solver kernel v2 notes

---

## Bottom line

The project is currently in the right stage to prioritize:

- sharper statements
- explicit limits
- small proofs
- executable tests

not broader claims.
