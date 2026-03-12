# Solver Soundness Test Suite v1

## 1. Purpose

This document defines an adversarial soundness-oriented test suite for the current branch-aware solver prototype.

It is designed to answer one question:

> Can the solver preserve branch semantics and avoid illegal algebraic collapse on hard cases?

This suite is **not** a completeness benchmark.
It is a **soundness benchmark**.

Domain: **Real numbers ℝ**.

Related files:

- `core_semantics_v1.md`
- `rewrite_rules_v1.md`
- `normal_form_engine_v1.md`
- `solver_semantics_v1.md`
- `solver_acceptance_tests_v1.md`
- `soundness_claims_v1.md`

---

## 2. Evaluation Policy

Each test is scored as:

- **PASS** — semantically correct branch behavior / solution extraction
- **PARTIAL** — safe but incomplete
- **FAIL** — unsound rewrite, wrong branch logic, or wrong extracted solution

The main red flag is:

```text
unsound simplification
```

Incomplete solving is acceptable. Unsound solving is not.

---

## 3. Core Adversarial Categories

The suite is organized into six categories:

1. Self-cancellation traps
2. Hidden-factor denominator traps
3. Product / quotient interaction traps
4. Zero-branch tautology / contradiction traps
5. Residual-solving traps
6. Multi-denominator branch interaction traps

---

## 4. Category A — Self-Cancellation Traps

### A1
Input:

```text
x/x = 1
```

Expected:

```text
Ne(x, 0)
```

### A2
Input:

```text
x/x = 0
```

Expected:

```text
Eq(x, 0)
```

### A3
Input:

```text
x/x = 2
```

Expected:

```text
no solutions
```

Reason:
- nonzero branch gives `1 = 2`
- zero branch gives `0 = 2`

### A4
Input:

```text
y*(x/x) = y
```

Expected broad behavior:

- branch `x != 0` -> tautology
- branch `x = 0` -> `0 = y`

Expected extracted behavior:
not yet necessarily canonical, but must **not** globally reduce `y*(x/x)` to `y`.

---

## 5. Category B — Hidden-Factor Denominator Traps

### B1
Input:

```text
(x^2 - 1)/(x - 1) = 3
```

Expected:

```text
Eq(x, 2)
```

### B2
Input:

```text
((x - 1)(x + 1))/(x - 1) = 0
```

Expected:

```text
Eq(x, -1) or Eq(x, 1)
```

### B3
Input:

```text
(x(x + 1))/x = 3
```

Expected:

```text
Eq(x, 2)
```

### B4
Input:

```text
(x(x + 1))/x = x + 1
```

Expected broad behavior:

- branch `x != 0` -> tautology
- branch `x = 0` -> `0 = x + 1` -> contradiction

Expected extracted result:

```text
Ne(x, 0)
```

---

## 6. Category C — Product / Quotient Interaction Traps

### C1
Input:

```text
(x/(x - 1))*(x - 1) = x
```

Expected:
- nonzero branch -> tautology
- zero branch -> `0 = x`

At `x = 1`, zero branch becomes `0 = 1`, contradiction.

Expected final result:

```text
Ne(x - 1, 0)
```

or equivalent guarded condition.

### C2
Input:

```text
(x/(x - 1))*(x - 1) = 0
```

Expected:
- nonzero branch -> `x = 0`
- zero branch -> `0 = 0` at `x = 1`

Expected final result:

```text
Eq(x, 0) or Eq(x, 1)
```

### C3
Input:

```text
(x/x)*(y/y) = 1
```

Expected branch behavior:

- both nonzero -> tautology
- one zero, one nonzero -> contradiction
- both zero -> contradiction

Expected broad solution condition:

```text
Ne(x, 0) and Ne(y, 0)
```

Current prototype may remain PARTIAL here because multivariable extraction is limited.

---

## 7. Category D — Zero-Branch Tautology / Contradiction Traps

### D1
Input:

```text
x/(x - 1) = x
```

Expected:

```text
Eq(x, 0) or Eq(x, 1) or Eq(x, 2)
```

### D2
Input:

```text
x/(x - 1) = 1
```

Expected:
- nonzero branch -> `x = x - 1` -> contradiction
- zero branch -> `1 = 1` -> tautology at `x = 1`

Expected final result:

```text
Eq(x, 1)
```

### D3
Input:

```text
x/(x - x) = x
```

Expected:
- denominator identically zero
- equation becomes `x = x`

Expected final result:
all real `x`

Current prototype may report this only partially because universal-solution extraction is still limited.

### D4
Input:

```text
x/(x - x) = x + 1
```

Expected:
- equation becomes `x = x + 1`
- contradiction

Expected final result:

```text
no solutions
```

---

## 8. Category E — Residual-Solving Traps

### E1
Input:

```text
(x^2 - 1)/(x - 1) = x + 1
```

Expected:
- nonzero branch -> tautology
- zero branch -> `0 = x + 1`, which at `x = 1` is contradiction

Expected extracted result:

```text
Ne(x - 1, 0)
```

or equivalent.

### E2
Input:

```text
x/0 = 3
```

Expected:

```text
Eq(x, 3)
```

### E3
Input:

```text
(x + 2)/0 = 5
```

Expected:

```text
Eq(x, 3)
```

### E4
Input:

```text
(x + 2)/0 = x + 2
```

Expected:
all real `x`

Current prototype may not yet emit a universal solution object. If so, this is PARTIAL, not FAIL, provided branch semantics are correct.

---

## 9. Category F — Multi-Denominator Interaction Traps

### F1
Input:

```text
x/(x - 1) + 1/x = 2
```

Expected minimum requirements:

- impossible overlap branch removed
- zero/nonzero branch logic preserved
- no global denominator clearing

Current solver may remain PARTIAL.

### F2
Input:

```text
x/y = 1
```

Expected broad behavior:

- `y != 0` -> residual `x/y = 1`
- `y = 0` -> residual `x = 1`

This should not collapse globally.

### F3
Input:

```text
x/x + y/y = 2
```

Expected:
- both nonzero -> tautology
- one zero -> contradiction
- both zero -> contradiction

Again, extraction may remain PARTIAL until multivariable support improves.

---

## 10. Regression Rules

A regression occurs if:

- any PASS case becomes FAIL
- a firewall-protected case begins simplifying globally
- an impossible branch is retained
- a contradiction branch yields a fake solution
- a tautology branch is lost when it should contribute a solution

---

## 11. Honest Current Status

The current prototype is expected to do well on:

- single-variable quotient traps
- zero/nonzero branch extraction
- hidden denominator preservation
- simple residual solving

It is not yet expected to fully solve:

- multivariable guarded systems
- universal-solution extraction in all cases
- advanced branch-merge canonicalization

That is acceptable for this stage.

---

## 12. Design Intent

This suite exists to harden the framework against exactly the kinds of mistakes that ordinary symbolic manipulation often makes:

- illegal cancellation
- silent domain loss
- zero-case erasure
- incorrect equation solving after premature simplification

If the engine survives this suite, the branch firewall idea gains serious credibility.
