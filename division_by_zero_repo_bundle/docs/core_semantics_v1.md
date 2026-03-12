# Core Semantics v1

## 1. Purpose

This document defines the core semantics of the division-by-zero experimental framework.

The framework is **not** a field extension and does **not** attempt to preserve all classical inverse-division laws globally. Instead, it defines a **guarded symbolic system** in which division by zero is given a primitive evaluation rule, while ordinary nonzero algebra is preserved **only inside justified branches**.

The intent is to support:

- explicit handling of zero-denominator cases
- branch-sensitive symbolic evaluation
- safe guarded simplification
- deterministic canonical branch objects over the real numbers

All semantics in this document are stated over the domain of **real numbers ℝ**.

---

## 2. Primitive Evaluation Rule

The primitive rule of the system is:

```text
a / 0 := a
```

for any real expression `a`.

This rule is **primitive**, not derived from inverse multiplication.

It must **not** be read as claiming:

```text
(a / 0) * 0 = a
0 * (a / 0) = a
```

nor as asserting that division by zero behaves like ordinary division in a field.

Instead, the rule is a **special evaluation clause** for quotients whose denominator is zero.

---

## 3. Meaning of Division in This Framework

Division is interpreted in two distinct modes:

### 3.1 Ordinary nonzero mode

When a denominator is known to be nonzero, ordinary field-style algebra is allowed locally.

Example:

```text
x ≠ 0  ⇒  x / x = 1
```

### 3.2 Zero-denominator primitive mode

When a denominator is zero, the quotient evaluates by the primitive rule:

```text
a / 0 := a
```

Example:

```text
5 / 0 = 5
0 / 0 = 0
(x + 1) / 0 = x + 1
```

### 3.3 Unknown-denominator mode

When denominator status is not yet known, the quotient must be treated as **guard-sensitive** and must not be simplified using rules that require nonzero denominator assumptions.

---

## 4. Denominator Status

Every denominator is treated as having one of three statuses:

- `ZERO`
- `NONZERO`
- `UNKNOWN`

These statuses are determined conservatively.

### 4.1 ZERO

A denominator is `ZERO` when the system can prove it equals zero.

Examples:

```text
x - x
(x - x) + (y - y)
0
```

### 4.2 NONZERO

A denominator is `NONZERO` when the system can prove it is not zero under the current guard.

Examples:

```text
x    under guard x ≠ 0
x - 1 under guard x ≠ 1
```

### 4.3 UNKNOWN

A denominator is `UNKNOWN` when neither zero nor nonzero can be safely established.

Example:

```text
x
x - 1
x^2 - 1
```

without additional guard information.

---

## 5. Guarded Evaluation

Expressions are evaluated relative to guards.

A branch has the form:

```text
[G] -> E
```

where:

- `G` is a guard over ℝ
- `E` is an expression valid under that guard

Guards may be written in equation / inequality form for user-facing output, while detector forms may be used internally.

Examples:

```text
[x = 0] -> x / x
[x ≠ 0] -> x / x
```

These branches are evaluated differently:

```text
[x = 0] -> x
[x ≠ 0] -> 1
```

Thus the system is **branch-sensitive by design**.

---

## 6. Branch Firewall

The most important structural rule of the system is the **Branch Firewall**.

### Firewall Principle

No algebraic rewrite that requires a denominator to be nonzero may be applied **before** denominator status has been split or justified by a guard.

In other words:

- nonzero-dependent simplification is **forbidden globally**
- nonzero-dependent simplification is **allowed locally inside justified branches**

This is the main rule preventing unsound collapse.

---

## 7. Forbidden Global Rewrites

The following rewrites are forbidden unless the relevant denominator is known to be nonzero under the current guard.

### 7.1 Quotient cancellation

Forbidden globally:

```text
x / x -> 1
```

Allowed only under guard:

```text
x ≠ 0
```

### 7.2 Factor cancellation across a denominator

Forbidden globally:

```text
(x^2 - 1) / (x - 1) -> x + 1
```

Allowed only under guard:

```text
x ≠ 1
```

### 7.3 Clearing denominators

Forbidden globally:

```text
a / b = c   ->   a = bc
```

unless `b ≠ 0` is justified in the branch.

### 7.4 Cross multiplication

Forbidden globally:

```text
a / b = c / d   ->   ad = bc
```

unless both `b ≠ 0` and `d ≠ 0` are justified in the branch.

### 7.5 Main-quotient regrouping that hides denominator status

Any rewrite that obscures, erases, or bypasses the denominator classification of the main quotient is forbidden before branch split.

---

## 8. Allowed Global Rewrites

The system still allows guard-independent rewrites that do not rely on denominator nonzeroness.

Examples include ordinary simplifications that do not touch the main quotient's denominator status, such as:

```text
x + 0 -> x
x * 1 -> x
x - x -> 0
```

provided these rewrites do not illegally restructure a protected quotient.

The key test is:

> Would this rewrite require assuming a denominator is nonzero, or would it bypass denominator classification?

If yes, it is forbidden globally.

If no, it is admissible.

---

## 9. Branch-Local Rewrites

Inside a branch whose guard proves a denominator nonzero, ordinary algebra may be used locally.

Example:

Initial expression:

```text
x / x
```

Branch split:

```text
[x = 0] -> x / x
[x ≠ 0] -> x / x
```

Local simplification:

```text
[x = 0] -> x
[x ≠ 0] -> 1
```

This is valid because the second branch justifies cancellation, while the first branch uses the primitive zero rule.

---

## 10. Branch-First Evaluation Strategy

The system evaluates quotient-sensitive expressions using the following strategy:

1. identify the main protected quotient(s)
2. classify each denominator as `ZERO`, `NONZERO`, or `UNKNOWN`
3. if needed, split into branches
4. simplify expressions only within guards that justify the rewrite
5. merge branches only when merge rules from `branch_merge_and_equivalence_v1.md` are satisfied

This means the framework is **branch-first**, not simplification-first.

---

## 11. Protected Quotients

A quotient whose denominator status is unresolved is treated as a **protected quotient**.

Protected quotients must preserve enough structure for denominator analysis and safe branching.

Examples:

```text
x / (x - x)
(x^2 - 1) / (x - 1)
(x + 1) / y
```

If the denominator is unresolved, the quotient must not be flattened by unsafe cancellation.

---

## 12. Extensional Meaning of Branch Outputs

A branch object denotes piecewise behavior over ℝ.

Two branch objects are equal when they produce the same output for every real input.

Thus canonicalization is not merely syntactic. It is intended to preserve extensional behavior while respecting the firewall.

This links the core semantics to the branch merge and equivalence rules.

---

## 13. Equation Solving Principle

Equation solving must be **branch-first**.

Given an equation involving quotients:

1. do **not** clear denominators globally
2. first split on denominator status
3. solve each branch under its guard
4. discard impossible branches
5. merge equivalent solution branches when safe

Example:

```text
x / x = 1
```

Branch split:

```text
[x = 0] -> x = 1
[x ≠ 0] -> 1 = 1
```

Evaluation:

- branch `x = 0` gives `0 = 1`, impossible
- branch `x ≠ 0` gives tautology

Final solution:

```text
x ≠ 0
```

This is the correct branch-sensitive solution.

---

## 14. Primitive Rule Is Not Inverse Semantics

The framework explicitly rejects the inference:

```text
a / b = c  ⇒  a = bc
```

as a universal law.

That inference remains valid only inside branches where `b ≠ 0` is known.

Therefore the primitive rule:

```text
a / 0 := a
```

must be understood as an evaluation convention, not a restoration of inverse-division semantics.

This is a foundational non-classical feature of the system.

---

## 15. Soundness Target

The framework does not claim full completeness or global confluence in the strongest algebraic sense.

Its soundness target is narrower and operational:

### 15.1 Firewall soundness

No forbidden nonzero-dependent rewrite is applied before justification.

### 15.2 Branch-local soundness

Within a branch, every rewrite is valid under that branch's guard.

### 15.3 Conservative classification

A denominator is only marked `ZERO` or `NONZERO` when justified; otherwise it remains `UNKNOWN`.

### 15.4 Extensional branch preservation

Canonicalization and merging preserve branch object behavior over ℝ.

---

## 16. Minimal Worked Examples

### Example 1: Primitive zero evaluation

```text
7 / 0
```

evaluates to:

```text
7
```

---

### Example 2: Zero-sensitive self-quotient

```text
x / x
```

branch-splits to:

```text
[x = 0] -> x
[x ≠ 0] -> 1
```

---

### Example 3: Forbidden global cancellation

```text
(x^2 - 1) / (x - 1)
```

must not globally simplify to:

```text
x + 1
```

until the branch `x ≠ 1` is justified.

Correct branch-first form:

```text
[x = 1] -> (x^2 - 1) / (x - 1)
[x ≠ 1] -> x + 1
```

Then the zero branch evaluates by the primitive rule:

```text
[x = 1] -> 0
```

So the full branch behavior is:

```text
[x = 1] -> 0
[x ≠ 1] -> x + 1
```

---

### Example 4: Solver discipline

Solve:

```text
x / x = 1
```

Correct result:

```text
x ≠ 0
```

not by global denominator clearing, but by branch-first evaluation.

---

## 17. Design Intent

This framework should be read as:

- a guarded symbolic system
- with a primitive zero-denominator rule
- protected by a branch firewall
- operating over the real numbers
- using branch-first evaluation and branch-local algebra

It should **not** be read as an ordinary field extension or as a claim that all classical division laws survive globally.

---

## 18. Dependency on Other Documents

This document supplies the semantic backbone.

It works together with:

- `branch_merge_and_equivalence_v1.md`
- denominator classification / detector documents
- solver specifications
- protected quotient / normalization drafts

If later revisions refine the classifier or branch-object machinery, this document remains the top-level semantic contract.
