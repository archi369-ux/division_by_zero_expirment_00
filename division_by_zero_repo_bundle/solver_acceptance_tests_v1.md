# Solver Acceptance Tests v1

## 1. Purpose

This document defines the first locked acceptance-test suite for the branch-aware solver prototype.

The purpose of this suite is to freeze the current intended behavior of the system so that future engine changes can be checked against a stable reference.

These tests focus on:

- primitive zero-division semantics
- branch-first normalization
- firewall preservation
- guarded simplification
- branch-aware equation solving
- solution extraction

Domain: **Real numbers ℝ**.

Related files:

- `core_semantics_v1.md`
- `rewrite_rules_v1.md`
- `solver_semantics_v1.md`
- `denominator_classifier_v1.md`
- `normal_form_engine_v1.md`
- `minimal_guarded_engine.py`

---

## 2. Pass Criteria

A solver acceptance test is considered:

- **PASS** if the extracted final solution matches the expected solution
- **PARTIAL** if normalization/classification is correct but extraction is not yet canonical
- **FAIL** if the solver violates branch semantics, firewall rules, or returns the wrong solution set

The primary red flag is:

```text
unsound solution extraction
```

Incompleteness is acceptable at this stage. Unsoundness is not.

---

## 3. Canonical Output Convention

Expected final outputs should be interpreted extensionally over ℝ.

For now the preferred printed forms are:

- `Eq(x, a)` for point solutions
- `Ne(x, 0)` for nonzero-domain solutions
- disjunctions such as:
  - `Eq(x, 0) or Eq(x, 1) or Eq(x, 2)`

Equivalent logically identical forms count as acceptable if they preserve the same solution set.

---

## 4. Acceptance Tests

### A1 — Primitive self-quotient equation

Input:

```text
x/x = 1
```

Expected branch behavior:

```text
[x != 0] -> 1 = 1
[x = 0] -> 0 = 1
```

Expected final solution:

```text
Ne(x, 0)
```

Status target: **PASS**

---

### A2 — Hidden-zero polynomial quotient

Input:

```text
(x^2 - 1)/(x - 1) = 3
```

Expected branch behavior:

```text
[x - 1 != 0] -> x + 1 = 3
[x - 1 = 0] -> 0 = 3
```

Expected final solution:

```text
Eq(x, 2)
```

Status target: **PASS**

---

### A3 — Identically zero denominator equation

Input:

```text
x/(x - x) = 3
```

Expected normalization:

```text
[true] -> x = 3
```

Expected final solution:

```text
Eq(x, 3)
```

Status target: **PASS**

---

### A4 — Mixed classical / primitive branch equation

Input:

```text
x/(x - 1) = x
```

Expected branch behavior:

```text
[x - 1 != 0] -> x/(x - 1) = x
[x - 1 = 0] -> 1 = 1
```

Expected final solution:

```text
Eq(x, 0) or Eq(x, 1) or Eq(x, 2)
```

Explanation:

- nonzero branch solves classically to `x = 0` or `x = 2`
- zero branch gives tautology at `x = 1`

Status target: **PASS**

---

### A5 — Explicit zero denominator constant equation

Input:

```text
7/0 = 7
```

Expected normalization:

```text
[true] -> 7 = 7
```

Expected final solution:

```text
true
```

Current prototype note:
The current extractor may not yet emit a standalone `true` solution object. If so, this test may temporarily remain **PARTIAL** rather than FAIL, provided branch semantics are correct.

Status target: **PARTIAL -> PASS later**

---

### A6 — Explicit zero denominator contradiction

Input:

```text
7/0 = 5
```

Expected normalization:

```text
[true] -> 7 = 5
```

Expected final solution:

```text
no solutions
```

Status target: **PASS**

---

### A7 — Parameter-preserving zero denominator equation

Input:

```text
(x + 2)/0 = 5
```

Expected normalization:

```text
[true] -> x + 2 = 5
```

Expected final solution:

```text
Eq(x, 3)
```

Status target: **PASS**

---

### A8 — Nonzero branch exclusion

Input:

```text
x/x = 0
```

Expected branch behavior:

```text
[x != 0] -> 1 = 0
[x = 0] -> 0 = 0
```

Expected final solution:

```text
Eq(x, 0)
```

Status target: **PASS**

---

### A9 — Product cancellation only under guard

Input:

```text
(x*(x + 1))/x = 3
```

Expected branch behavior:

```text
[x != 0] -> x + 1 = 3
[x = 0] -> 0 = 3
```

Expected final solution:

```text
Eq(x, 2)
```

Status target: **PASS**

---

### A10 — Factor cancellation with zero-branch retention

Input:

```text
((x - 1)*(x + 1))/(x - 1) = 0
```

Expected branch behavior:

```text
[x - 1 != 0] -> x + 1 = 0
[x - 1 = 0] -> 0 = 0
```

Expected final solution:

```text
Eq(x, -1) or Eq(x, 1)
```

Status target: **PASS**

---

## 5. Extended / Future Acceptance Cases

These are valuable but may remain outside the current prototype's capabilities for now.

### E1 — Multi-denominator sum

Input:

```text
x/(x - 1) + 1/x = 2
```

Expected broad branch structure:

- generic nonzero branch
- `x = 1` branch
- `x = 0` branch
- impossible overlap removed

This case should be promoted to full acceptance status after branch-aware solving of multi-term residual equations is stronger.

---

### E2 — Two self-quotients

Input:

```text
x/x + y/y = 2
```

Expected broad behavior:

- both nonzero -> `2 = 2`
- one zero, one nonzero -> `1 = 2`
- both zero -> `0 = 2`

This should eventually produce a guarded multi-variable solution condition. Current prototype is not yet designed for that.

---

## 6. Regression Policy

Any future engine change should be checked against this acceptance suite.

A regression occurs if:

- a PASS case becomes FAIL
- a PASS case becomes semantically wrong even if output is shorter/prettier
- branch structure is lost in a way that changes the solution set
- a firewall-protected case starts simplifying globally without guard justification

Improvements are welcome only if they preserve the accepted semantics.

---

## 7. Design Intent

This document freezes the first meaningful solver milestone of the project.

At this point the system is expected to behave as:

- a branch-aware symbolic normalizer
- a minimal branch-aware equation classifier
- a simple residual solver
- a basic solution extractor

It is **not yet** expected to be:

- a complete theorem prover
- a full multi-variable symbolic solver
- a final canonicalizer for all guarded outputs

That is acceptable.

The purpose of this suite is to protect what already works while the system evolves further.
