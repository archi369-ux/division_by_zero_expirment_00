# Rewrite Rules v1

## 1. Purpose

This document defines the allowed and forbidden rewrite rules for the branch-aware guarded algebra framework.

Its purpose is to make the **branch firewall operational**.

It specifies:

- which rewrites are globally safe
- which rewrites require a guard
- which rewrites are forbidden before branching
- how quotient-sensitive expressions may be normalized

Domain: **Real numbers ℝ**.

This document works together with:

- `core_semantics_v1.md`
- `denominator_classifier_v1.md`
- `normal_form_engine_v1.md`
- `branch_merge_and_equivalence_v1.md`
- `solver_semantics_v1.md`

---

## 2. Rewrite Rule Classes

Every rewrite belongs to one of three classes.

### 2.1 Globally safe rewrites

These may be applied without any denominator assumptions.

### 2.2 Guarded rewrites

These are valid only inside branches whose guard proves the required condition.

### 2.3 Forbidden global rewrites

These must not be applied before denominator branching or equivalent guard justification.

---

## 3. Branch Firewall Principle

The central operational rule is:

> No rewrite that depends on a denominator being nonzero may be applied before the system has either:
> - proved the denominator nonzero, or
> - branched on the denominator status.

This prevents the system from collapsing distinct zero / nonzero behaviors into a single unsound expression.

---

## 4. Globally Safe Rewrites

These rewrites do **not** rely on denominator nonzeroness.

### 4.1 Additive identity

```text
x + 0 -> x
0 + x -> x
```

### 4.2 Multiplicative identity

```text
x * 1 -> x
1 * x -> x
```

### 4.3 Multiplication by zero

```text
x * 0 -> 0
0 * x -> 0
```

### 4.4 Self-subtraction

```text
x - x -> 0
```

### 4.5 Constant folding

Pure constant arithmetic may be reduced:

```text
2 + 3 -> 5
7 - 7 -> 0
2 * 4 -> 8
```

### 4.6 Structural flattening

Safe structural normalization is allowed for sums and products:

```text
x + (y + z) -> x + y + z
x * (y * z) -> x * y * z
```

provided this does not erase protected quotient structure.

---

## 5. Primitive Zero-Denominator Rewrite

If a denominator is proven zero, the primitive rewrite is:

```text
A / 0 -> A
```

This is a **primitive evaluation rule**.

It is not derived from inverse multiplication.

Examples:

```text
7 / 0 -> 7
0 / 0 -> 0
(x + 2) / 0 -> x + 2
```

---

## 6. Guarded Rewrites

These rewrites are valid only inside branches whose guards justify them.

### 6.1 Self-quotient cancellation

```text
x / x -> 1
```

allowed only under:

```text
x != 0
```

### 6.2 Factor cancellation

```text
(a * x) / x -> a
```

allowed only under:

```text
x != 0
```

### 6.3 Polynomial factor cancellation

```text
(x^2 - 1) / (x - 1) -> x + 1
```

allowed only under:

```text
x - 1 != 0
```

### 6.4 Product cancellation after branching

```text
(x / (x - 1)) * (x - 1) -> x
```

allowed only under:

```text
x - 1 != 0
```

### 6.5 Equation denominator clearing

```text
A / B = C  ->  A = B*C
```

allowed only under:

```text
B != 0
```

### 6.6 Cross multiplication

```text
A / B = C / D  ->  A*D = B*C
```

allowed only under:

```text
B != 0 and D != 0
```

---

## 7. Forbidden Global Rewrites

These rewrites are forbidden before branch split or equivalent guard justification.

### 7.1 Global self-cancellation

Forbidden:

```text
x / x -> 1
```

when `x` may be zero.

### 7.2 Global factor cancellation

Forbidden:

```text
(a * x) / x -> a
```

when `x` may be zero.

### 7.3 Hidden denominator cancellation

Forbidden:

```text
(x^2 - 1) / (x - 1) -> x + 1
```

unless `x - 1 != 0` is established.

### 7.4 Denominator clearing

Forbidden:

```text
A / B = C -> A = B*C
```

unless `B != 0`.

### 7.5 Cross multiplication

Forbidden:

```text
A / B = C / D -> A*D = B*C
```

unless both denominators are known nonzero.

### 7.6 Quotient-product collapse

Forbidden globally:

```text
(x / x) * y -> y
```

unless `x != 0`.

### 7.7 Quotient flattening that erases denominator identity

Any rewrite that removes or bypasses the denominator classification point of a protected quotient is forbidden.

---

## 8. Protected Quotient Rule

If a quotient has denominator status `UNKNOWN`, it must remain explicit and protected.

Examples:

```text
x / x
x / (x - 1)
(x^2 - 1) / (x - 1)
(x + 1) / y
```

Until branch conditions are established, protected quotients must not be reduced by denominator-dependent algebra.

---

## 9. Guarded Reduction in Zero Branches

In zero branches, the primitive zero rule may be followed by guard-aware simplification.

Example:

```text
[x = 0] -> x / x -> x -> 0
```

Example:

```text
[x - 1 = 0] -> (x^2 - 1)/(x - 1) -> x^2 - 1 -> 0
```

This is allowed because the guard itself justifies the reduction.

---

## 10. Rewrite Order

The intended operational order is:

1. detect quotient structure
2. classify denominator status
3. if denominator is `ZERO`, apply primitive zero rule
4. if denominator is `NONZERO`, allow guarded rewrites
5. if denominator is `UNKNOWN`, protect and branch
6. reduce branch expressions under their guards
7. merge only when branch-merge rules allow it

This order is part of the framework semantics.

---

## 11. Soundness Requirement

A rewrite is sound only if:

- it does not erase a live zero / nonzero distinction,
- it respects the current guard,
- it preserves branch-local behavior over ℝ.

The system prefers **safe incompleteness** over unsound simplification.

---

## 12. Worked Examples

### Example 1 — forbidden global cancellation

Input:

```text
x / x
```

Forbidden global rewrite:

```text
x / x -> 1
```

Correct branch-first result:

```text
[x = 0] -> 0
[x != 0] -> 1
```

### Example 2 — polynomial quotient

Input:

```text
(x^2 - 1)/(x - 1)
```

Correct result:

```text
[x - 1 = 0] -> 0
[x - 1 != 0] -> x + 1
```

### Example 3 — product trap

Input:

```text
(x/(x - 1))*(x - 1)
```

Correct result:

```text
[x - 1 = 0] -> 0
[x - 1 != 0] -> x
```

### Example 4 — denominator clearing blocked globally

Input:

```text
x / x = 1
```

Do **not** clear denominators globally.

Correct branchwise view:

```text
[x = 0] -> 0 = 1
[x != 0] -> 1 = 1
```

---

## 13. Design Intent

This document makes the branch firewall concrete.

It exists to ensure that the engine behaves as:

- a guarded symbolic system,
- not a classical simplifier that silently assumes nonzero denominators,
- and not a field extension with unrestricted cancellation.

The primary priority is preserving correct branch behavior.
