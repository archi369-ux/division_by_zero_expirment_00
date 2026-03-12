# Branch-Sensitive Identity Examples v1

## 1. Purpose

This document tests the current theory **on paper first**.

It does not depend on the current engine implementation.
Its purpose is to stress the semantics manually before further code patching.

Focus:

- branch-sensitive identities
- firewall-safe rewrites
- review-driven soundness checks
- examples that show where classical algebra must become guarded algebra

Domain: **Real numbers ℝ**.

Related documents:

- `core_semantics_v1.md`
- `rewrite_rules_v1.md`
- `normal_form_engine_v1.md`
- `solver_semantics_v1.md`
- `soundness_claims_v1.md`
- `prototype_status_v1.md`

---

## 2. Paper-First Review Method

For each identity candidate:

1. identify all denominator-sensitive subexpressions
2. split into zero / nonzero branches
3. simplify only inside justified branches
4. record the final guarded expression
5. compare against the naive classical identity
6. mark whether the classical identity survives globally or only branch-locally

This gives a manual soundness pass independent of the program.

---

## 3. Example A — Self quotient

Input:

```text
a/a
```

Relevant branch split:

- `a = 0`
- `a != 0`

Evaluation:

- `[a = 0] -> a/a -> a -> 0`
- `[a != 0] -> a/a -> 1`

Final guarded result:

```text
[a = 0] -> 0
[a != 0] -> 1
```

Classical identity:

```text
a/a = 1
```

Status:

- valid only branch-locally under `a != 0`
- invalid as a global identity

Review consequence:

This is the canonical example showing why `f/f -> 1` must be guarded.

---

## 4. Example B — Product cancellation

Input:

```text
(a/b) * b
```

Relevant branch split:

- `b = 0`
- `b != 0`

Evaluation:

### Branch `[b = 0]`

```text
(a/b) * b -> (a/0) * 0 -> a * 0 -> 0
```

### Branch `[b != 0]`

```text
(a/b) * b -> a
```

Final guarded result:

```text
[b = 0] -> 0
[b != 0] -> a
```

Classical identity:

```text
(a/b) * b = a
```

Status:

- valid only branch-locally under `b != 0`
- false globally

Review consequence:

This is one of the central reasons the division firewall is necessary.

---

## 5. Example C — Quotient sum symmetry

Input:

```text
a/b + b/a
```

Relevant branches:

- `a = 0`, `a != 0`
- `b = 0`, `b != 0`

### Branch `[a != 0 and b != 0]`

Classical combination allowed:

```text
a/b + b/a -> (a^2 + b^2)/(ab)
```

### Branch `[a = 0 and b != 0]`

```text
a/b + b/a -> 0/b + b/0 -> 0 + b -> b
```

### Branch `[a != 0 and b = 0]`

```text
a/b + b/a -> a/0 + 0/a -> a + 0 -> a
```

### Branch `[a = 0 and b = 0]`

```text
a/b + b/a -> 0/0 + 0/0 -> 0 + 0 -> 0
```

Final guarded result:

```text
[a != 0 and b != 0] -> (a^2 + b^2)/(ab)
[a = 0 and b != 0] -> b
[a != 0 and b = 0] -> a
[a = 0 and b = 0] -> 0
```

Classical identity:

```text
a/b + b/a = (a^2 + b^2)/(ab)
```

Status:

- valid only on the nonzero branch
- not global

Review consequence:

Rational identities in this theory are typically piecewise identities.

---

## 6. Example D — Quotient difference symmetry

Input:

```text
a/b - b/a
```

Branches:

### `[a != 0 and b != 0]`

```text
a/b - b/a -> (a^2 - b^2)/(ab)
```

### `[a = 0 and b != 0]`

```text
0/b - b/0 -> 0 - b -> -b
```

### `[a != 0 and b = 0]`

```text
a/0 - 0/a -> a - 0 -> a
```

### `[a = 0 and b = 0]`

```text
0/0 - 0/0 -> 0 - 0 -> 0
```

Final guarded result:

```text
[a != 0 and b != 0] -> (a^2 - b^2)/(ab)
[a = 0 and b != 0] -> -b
[a != 0 and b = 0] -> a
[a = 0 and b = 0] -> 0
```

Status:

Again only branch-locally classical.

---

## 7. Example E — Affine quotient

Input:

```text
(a + b)/b
```

Branches:

### `[b != 0]`

```text
(a + b)/b -> a/b + b/b -> a/b + 1
```

### `[b = 0]`

```text
(a + b)/b -> (a + 0)/0 -> a
```

Final guarded result:

```text
[b != 0] -> a/b + 1
[b = 0] -> a
```

Classical identity:

```text
(a + b)/b = a/b + 1
```

Status:

- valid only under `b != 0`

Review consequence:

Even harmless-looking affine quotient identities become guarded.

---

## 8. Example F — Multiplicative quotient symmetry

Input:

```text
(a/b) * (b/a)
```

Relevant branches:

- `a = 0`, `a != 0`
- `b = 0`, `b != 0`

### `[a != 0 and b != 0]`

```text
(a/b) * (b/a) -> 1
```

### `[a = 0 and b != 0]`

```text
(0/b) * (b/0) -> 0 * b -> 0
```

### `[a != 0 and b = 0]`

```text
(a/0) * (0/a) -> a * 0 -> 0
```

### `[a = 0 and b = 0]`

```text
(0/0) * (0/0) -> 0 * 0 -> 0
```

Final guarded result:

```text
[a != 0 and b != 0] -> 1
[a = 0 and b != 0] -> 0
[a != 0 and b = 0] -> 0
[a = 0 and b = 0] -> 0
```

Classical identity:

```text
(a/b) * (b/a) = 1
```

Status:

- valid only when both denominators are nonzero

---

## 9. Example G — Mixed product / quotient trap

Input:

```text
(x/(x - 1)) * (x - 1)
```

Branches:

### `[x - 1 != 0]`

```text
(x/(x - 1)) * (x - 1) -> x
```

### `[x - 1 = 0]`

```text
(x/(x - 1)) * (x - 1) -> x/0 * 0 -> x * 0 -> 0
```

Since `[x - 1 = 0]` implies `x = 1`, that branch stays:

```text
0
```

Final guarded result:

```text
[x - 1 != 0] -> x
[x - 1 = 0] -> 0
```

Classical identity:

```text
(x/(x - 1)) * (x - 1) = x
```

Status:

- only branch-locally valid

This example is already central to the current solver tests.

---

## 10. Example H — Hidden-factor quotient

Input:

```text
(x^2 - 1)/(x - 1)
```

Branches:

### `[x - 1 != 0]`

```text
(x^2 - 1)/(x - 1) -> x + 1
```

### `[x - 1 = 0]`

Primitive zero rule first:

```text
(x^2 - 1)/(x - 1) -> x^2 - 1
```

Then guard reduction with `x = 1`:

```text
x^2 - 1 -> 0
```

Final guarded result:

```text
[x - 1 != 0] -> x + 1
[x - 1 = 0] -> 0
```

Status:

- classical simplification survives only on the nonzero branch

---

## 11. Review-Driven Non-Rules

The following are explicitly **not** global rules of the theory:

```text
f/f -> 1
(a/b)*b -> a
(a+b)/b -> a/b + 1
a/b + b/a -> (a^2 + b^2)/(ab)
a/b - b/a -> (a^2 - b^2)/(ab)
```

These are all branch-local only.

Also explicitly absent:

```text
A -> A/0
A -> A*0
```

These are non-rules and must remain so.

---

## 12. Paper Outcome for the Current Review Goals

These paper examples support the following conclusions.

### Safe-simplify patch motivation

Any simplifier that rewrites the above expressions directly into their classical forms is unsound for this theory.

Therefore a future `safe_simplify` must preserve protected quotients and must not invoke full rational cancellation globally.

### Review fixes motivation

The review suggestions about:
- explicit self-quotient branching
- explicit non-rules
- guard-reduced branch equations

are all justified by these examples.

### Freeze-doc update motivation

The freeze docs should state clearly that many classical rational identities survive only as guarded laws.

### Soundness-pass motivation

A future soundness pass should include all examples in this document as manual reference cases.

---

## 13. Current Practical Meaning

These examples show that the theory can already be used **on paper now**.

Specifically, it can already be used to:

- test candidate rewrite rules
- distinguish global vs branch-local identities
- derive guarded equation solutions by hand
- explain why the branch firewall is necessary

This is true even before further program fixes are made.

---

## 14. Main Theoretical Conclusion

The main theoretical lesson so far is:

> Under the current semantics, rational identities are generally **guarded identities**, not global identities.

This is not an accident.
It is the direct consequence of:

```text
a/0 := a
```

together with the branch firewall.

---

## 15. Freeze Note

This document should be treated as a paper-first reference set for the next stage of development.

The next implementation work should be judged against these examples rather than the other way around.
