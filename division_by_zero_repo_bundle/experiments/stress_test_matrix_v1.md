# Stress Test Matrix v1

## 1. Purpose

This document defines the first structured stress-test suite for the guarded division-by-zero framework.

The goal is to test whether the current prototype preserves:

- the primitive rule `a / 0 := a`
- the branch firewall
- denominator classification safety
- branch-first normalization
- guarded simplification
- ambiguity handling

This is a **v0 stress matrix**. It is intended to expose weak spots quickly, not to certify full completeness.

Domain: **Real numbers ℝ**.

Related files:

- `core_semantics_v1.md`
- `rewrite_rules_v1.md`
- `solver_semantics_v1.md`
- `denominator_classifier_v1.md`
- `normal_form_engine_v1.md`
- `minimal_guarded_engine.py`

---

## 2. Test Buckets

The matrix is divided into five buckets:

1. **Primitive Rule Tests**
2. **Firewall Tests**
3. **Must-Branch Tests**
4. **Guarded Simplification Tests**
5. **Merge / Ambiguity Tests**

---

## 3. Primitive Rule Tests

### P1
Input:

```text
7 / 0
```

Expected:

```text
7
```

### P2
Input:

```text
0 / 0
```

Expected:

```text
0
```

### P3
Input:

```text
(x + 2) / 0
```

Expected:

```text
x + 2
```

### P4
Input:

```text
x / (x - x)
```

Expected branch behavior:

```text
[true] -> x
```

Reason:
`x - x` is provably zero, so no branch is needed.

---

## 4. Firewall Tests

### F1
Input:

```text
x / x
```

Global expectation:

```text
must NOT normalize directly to 1
```

Expected branch behavior:

```text
[x = 0] -> x
[x != 0] -> 1
```

### F2
Input:

```text
(x^2 - 1) / (x - 1)
```

Global expectation:

```text
must NOT normalize directly to x + 1
```

Expected branch behavior:

```text
[x = 1] -> 0
[x != 1] -> x + 1
```

### F3
Input equation:

```text
a / b = c
```

Global expectation:

```text
must NOT clear denominator before guard b != 0
```

### F4
Input equation:

```text
a / b = c / d
```

Global expectation:

```text
must NOT cross multiply before guards b != 0 and d != 0
```

---

## 5. Must-Branch Tests

### B1
Input:

```text
x / x
```

Expected:

```text
branch on x
```

### B2
Input:

```text
x / (x - 1)
```

Expected:

```text
branch on x - 1
```

### B3
Input:

```text
x / ((x - x) + (y - y))
```

Expected:

```text
[true] -> x
```

Reason:
denominator simplifies to zero before branching.

### B4
Input:

```text
(x + 1) / y
```

Expected:

```text
branch on y
```

### B5
Input:

```text
x / (y - y)
```

Expected:

```text
[true] -> x
```

---

## 6. Guarded Simplification Tests

### G1
Input under guard:

```text
x != 0
```

Expression:

```text
x / x
```

Expected:

```text
1
```

### G2
Input under guard:

```text
x != 1
```

Expression:

```text
(x^2 - 1) / (x - 1)
```

Expected:

```text
x + 1
```

### G3
Input under guard:

```text
x = 1
```

Expression:

```text
(x^2 - 1) / (x - 1)
```

Expected:

```text
0
```

### G4
Input under guard:

```text
y = 0
```

Expression:

```text
(x + 1) / y
```

Expected:

```text
x + 1
```

---

## 7. Solver Tests

### S1
Solve:

```text
x / x = 1
```

Expected:

```text
x != 0
```

### S2
Solve:

```text
(x^2 - 1) / (x - 1) = 3
```

Expected:

```text
x = 2
```

### S3
Solve:

```text
x / (x - 1) = x
```

Expected branch-first behavior:
- branch on `x - 1`
- solve only inside legal branches

### S4
Solve:

```text
x / (x - x) = 3
```

Expected:

```text
x = 3
```

Reason:
denominator is identically zero, so equation becomes `x = 3`.

---

## 8. Merge / Ambiguity Tests

### M1
Branches:

```text
[x = 0] -> 5
[x != 0] -> 5
```

Expected merge:

```text
[true] -> 5
```

### M2
Branches:

```text
[x = 0] -> 1
[x != 0] -> x/x
```

Expected:
- normalize second branch to `1`
- then merge to

```text
[true] -> 1
```

### M3
Branches:

```text
[x >= 0] -> 1
[x <= 0] -> 1
```

Expected merge:

```text
[true] -> 1
```

### M4
Branches:

```text
[x >= 0] -> 1
[x <= 0] -> 2
```

Expected:

```text
reject as ambiguous
```

### M5
Branches:

```text
[true] -> 5
[x = 0] -> 5
```

Expected:

```text
[true] -> 5
```

by absorption.

---

## 9. Current Prototype Expectations

The current minimal engine is expected to pass:

- most Primitive Rule tests
- most Must-Branch tests
- some Guarded Simplification tests
- some early Merge tests

It is **not yet expected** to fully pass:

- all solver cases
- all ambiguity checks
- all higher-order merge logic
- all equation-level firewall tests

That is acceptable at this stage.

---

## 10. Pass / Fail Policy

A test result should be marked:

- **PASS** if output matches expected behavior
- **PARTIAL** if the engine preserves safety but output is not yet fully canonical
- **FAIL** if the engine violates the firewall or produces wrong branch semantics

The main red flag is not incomplete simplification.

The main red flag is:

```text
unsound simplification
```

---

## 11. Design Intent

This matrix is intended to answer one practical question:

> Is the current system safe enough to keep evolving?

If the answer is:

- **safe but incomplete** -> continue hardening
- **unsound on core cases** -> fix semantics/engine before extending scope
