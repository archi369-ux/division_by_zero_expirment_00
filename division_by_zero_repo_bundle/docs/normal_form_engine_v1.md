# Normal Form Engine v1

## 1. Purpose

This document defines the guarded normal-form strategy for the branch-aware algebra framework.

Its job is to specify how expressions are normalized **without violating the branch firewall**.

It describes:

- protected quotient handling
- safe structural normalization
- guard-relative normalization
- the stopping condition for expression simplification
- how branch normal forms are produced

Domain: **Real numbers ℝ**.

This document works together with:

- `core_semantics_v1.md`
- `rewrite_rules_v1.md`
- `denominator_classifier_v1.md`
- `branch_merge_and_equivalence_v1.md`
- `solver_semantics_v1.md`

---

## 2. Design Principle

The normal-form engine is **not** a classical simplifier whose only goal is “smallest expression”.

Its goal is:

- preserve denominator distinctions
- expose zero / nonzero branch points
- normalize only when safe
- produce deterministic guarded outputs

So the system computes a **guarded normal form**, not a purely classical canonical simplification.

---

## 3. Expression Kinds

The engine conceptually treats expressions as built from:

```text
Const(c)
Var(x)
Add(e1, e2, ..., en)
Mul(e1, e2, ..., en)
Pow(base, exp)
Quot(num, den)
```

In the current prototype this is represented through SymPy-backed structures, but the intended logical form is as above.

---

## 4. Protected Quotients

A quotient is **protected** whenever its denominator status is `UNKNOWN`.

Examples:

```text
x / x
x / (x - 1)
(x^2 - 1) / (x - 1)
(x + 1) / y
```

Protected quotients must remain explicit until the engine has either:

- proved the denominator zero,
- proved the denominator nonzero,
- or branched on its status.

This is the core normal-form constraint.

---

## 5. Global Structural Normalization

The engine may apply safe structural normalization before branching.

### 5.1 Flatten sums and products

```text
x + (y + z) -> x + y + z
x * (y * z) -> x * y * z
```

### 5.2 Fold constants

```text
2 + 3 -> 5
7 - 7 -> 0
```

### 5.3 Remove identities

```text
x + 0 -> x
x * 1 -> x
```

### 5.4 Remove additive self-cancellation

```text
x - x -> 0
```

These are allowed only when they do not destroy protected quotient structure.

---

## 6. Quotient Normalization Cases

For a quotient `A / B`, there are three normal-form cases.

### 6.1 ZERO denominator

If `B` is classified as `ZERO`:

```text
A / B -> A
```

then continue guard-aware reduction on the result if possible.

### 6.2 NONZERO denominator

If `B` is classified as `NONZERO`, guarded rewrites become available.

Examples:

```text
x / x -> 1                 under x != 0
(x^2 - 1)/(x - 1) -> x + 1 under x - 1 != 0
```

### 6.3 UNKNOWN denominator

If `B` is `UNKNOWN`, keep the quotient protected.

No denominator-dependent simplification may occur yet.

---

## 7. Guard-Aware Reduction

Once inside a branch, the engine may use the guard to simplify expressions further.

Examples:

```text
[x = 0] -> x -> 0
[x - 1 = 0] -> x^2 - 1 -> 0
```

The current prototype supports a bounded version of this idea using simple single-variable linear substitutions.

This is intentionally conservative.

---

## 8. Guarded Expression Normal Form

An expression is in guarded normal form when:

1. safe structural rewrites have been applied,
2. all denominators have been classified relative to the current guard,
3. every `ZERO` denominator has been reduced by the primitive rule,
4. every `NONZERO` denominator has been simplified only by guard-legal rewrites,
5. every `UNKNOWN` denominator remains protected,
6. any further simplification would require a stronger guard or stronger solver power.

This is the stopping condition for expression normalization.

---

## 9. Branch Normal Form

A branch object is in branch normal form when:

1. each branch guard is internally consistent,
2. each branch expression is in guarded normal form,
3. impossible branches have been discarded,
4. branch outputs are sorted deterministically,
5. any safe complementary merge has been applied.

This connects single-expression normal form to branch-object normal form.

---

## 10. Operational Equality

Two expressions are operationally equal relative to a guard if they normalize to the same result under that guard.

Example:

```text
[x != 0] -> x/x
[x != 0] -> 1
```

are operationally equal in that branch.

But globally:

```text
x/x
1
```

are **not** interchangeable before branch splitting.

---

## 11. Normalization Pipeline

Given expression `E` under guard `G`, the intended pipeline is:

1. inspect structure without prematurely simplifying protected quotients
2. apply safe structural normalization
3. detect quotient nodes
4. classify each denominator relative to `G`
5. apply:
   - primitive zero rewrite if denominator is `ZERO`
   - guarded quotient rewrite if denominator is `NONZERO`
   - protection if denominator is `UNKNOWN`
6. apply bounded guard-aware reduction
7. recurse until fixpoint or until only guarded-residual structure remains

This is the intended operational semantics of normalization.

---

## 12. Minimal Examples

### Example 1 — self quotient

Input:

```text
x / x
```

Guarded normal form:

```text
[x = 0] -> 0
[x != 0] -> 1
```

### Example 2 — polynomial quotient

Input:

```text
(x^2 - 1)/(x - 1)
```

Guarded normal form:

```text
[x - 1 = 0] -> 0
[x - 1 != 0] -> x + 1
```

### Example 3 — pure zero denominator

Input:

```text
(x + 2)/0
```

Normal form:

```text
[true] -> x + 2
```

### Example 4 — partially unresolved denominator

Input:

```text
x / y
```

Guarded normal form:

```text
[y = 0] -> x
[y != 0] -> x/y
```

### Example 5 — product trap

Input:

```text
(x/(x - 1))*(x - 1)
```

Guarded normal form:

```text
[x - 1 = 0] -> 0
[x - 1 != 0] -> x
```

---

## 13. Current Prototype Boundaries

The current prototype is intentionally limited.

It does not yet provide:

- full canonical branch merging
- a custom AST independent of SymPy
- complete multivariable guard reduction
- full inequality reasoning
- full canonicalization of residual rational forms

That is acceptable for the current milestone.

---

## 14. Design Intent

This normal-form engine exists to guarantee that the system stays:

- branch-aware
- denominator-safe
- solver-friendly
- deterministic enough for regression testing

It should be understood as the operational layer between:

- semantics
- denominator classification
- guarded rewrites
- and equation solving

rather than as a generic CAS simplifier.
