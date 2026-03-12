# Soundness Claims v1

## 1. Purpose

This document records the first focused soundness claims for the branch-aware guarded algebra framework.

It does **not** attempt to prove full completeness, full confluence, or global uniqueness of normal forms.

Its purpose is narrower:

- state the main soundness targets of the framework
- explain what each target means
- give proof sketches for why the current design supports them
- define what still remains unproved

Domain: **Real numbers ℝ**.

This document works together with:

- `core_semantics_v1.md`
- `rewrite_rules_v1.md`
- `denominator_classifier_v1.md`
- `normal_form_engine_v1.md`
- `branch_merge_and_equivalence_v1.md`
- `solver_semantics_v1.md`
- `solver_acceptance_tests_v1.md`

---

## 2. Scope Boundary

This document does **not** claim that the framework is:

- a field extension
- a ring extension with unrestricted inverse laws
- complete for all symbolic equations
- confluent in the strongest rewrite-theoretic sense
- final in its guard language or solver power

Instead, it claims a smaller and more realistic result:

> the framework is sound as a **branch-aware guarded symbolic system** under its own stated semantics.

---

## 3. Main Soundness Targets

The current framework is built around four main soundness targets:

1. **Firewall Soundness**
2. **Branch-Local Algebra Soundness**
3. **Primitive Zero-Rule Soundness**
4. **Residual Solver / Solution Extraction Soundness**

These are the claims that matter most at the current stage.

---

## 4. Firewall Soundness

### Claim

No rewrite that depends on a denominator being nonzero is applied before the system has either:

- proved the denominator nonzero, or
- branched on the denominator status.

### Informal meaning

The framework must never silently use classical cancellation where a zero denominator case is still live.

### Typical forbidden examples

These must not happen globally:

```text
x / x -> 1
(x^2 - 1)/(x - 1) -> x + 1
A / B = C -> A = B*C
A / B = C / D -> A*D = B*C
```

unless the relevant denominator nonzero facts are already established.

### Why the framework supports this

The framework enforces a denominator trichotomy:

- `ZERO`
- `NONZERO`
- `UNKNOWN`

If a denominator is `UNKNOWN`, the quotient remains protected and branch splitting is triggered instead of denominator-dependent simplification.

So any rewrite requiring `B != 0` is blocked until the current guard or branch justifies it.

### Proof sketch

1. Every denominator is classified before quotient-sensitive rewrite.
2. If classification is `UNKNOWN`, the quotient is protected.
3. Protected quotients forbid denominator-dependent rewrites.
4. Therefore any rewrite needing nonzeroness can only occur:
   - after `NONZERO` classification, or
   - inside a branch whose guard implies nonzeroness.

Hence the firewall prevents unsound early cancellation.

---

## 5. Branch-Local Algebra Soundness

### Claim

Inside a branch, every allowed guarded rewrite preserves equality over ℝ under that branch’s guard.

### Informal meaning

Once the branch guard proves the needed condition, ordinary algebra is valid locally.

### Example

Under guard:

```text
x != 0
```

the rewrite

```text
x / x -> 1
```

is sound.

Under guard:

```text
x - 1 != 0
```

the rewrite

```text
(x^2 - 1)/(x - 1) -> x + 1
```

is sound.

### Why the framework supports this

The allowed guarded rewrites are ordinary algebraic identities valid over the reals under the stated nonzero assumptions.

The branch guard acts as the hypothesis that licenses the rewrite.

### Proof sketch

1. Each guarded rewrite is paired with an explicit side condition.
2. The side condition is checked via the branch guard or denominator classifier.
3. Over ℝ, the classical identity holds when the side condition holds.
4. Therefore the rewrite preserves equality on all values satisfying the guard.

So branch-local ordinary algebra is sound.

---

## 6. Primitive Zero-Rule Soundness

### Claim

When the framework classifies a denominator as zero, the rewrite

```text
A / 0 -> A
```

is sound **with respect to the framework’s chosen semantics**.

### Informal meaning

This is not a theorem of classical division.  
It is a semantic clause of the framework itself.

### Why this is not a contradiction

The framework does **not** claim:

```text
(A / 0) * 0 = A
```

nor does it claim inverse-division semantics survive globally.

Instead it defines zero-denominator evaluation primitively.

So the soundness question here is not:

> “Is this classical field division?”

It is:

> “Does the engine consistently apply the framework’s own chosen zero rule?”

### Proof sketch

1. The semantics document explicitly defines `A / 0 := A`.
2. The denominator classifier marks only proven-zero denominators as `ZERO`.
3. When a denominator is `ZERO`, the engine applies the primitive rule and no nonzero-dependent algebra is used.
4. Therefore the rewrite is exactly the intended semantics of the framework in zero branches.

So the rule is sound relative to the framework’s semantics.

---

## 7. Guard-Aware Zero-Branch Reduction Soundness

### Claim

After applying the primitive zero rule in a zero branch, further guard-aware reduction is sound when it uses only facts implied by that branch’s guard.

### Example

```text
[x = 0] -> x / x -> x -> 0
```

and

```text
[x - 1 = 0] -> (x^2 - 1)/(x - 1) -> x^2 - 1 -> 0
```

### Why this is sound

The extra simplification does not assume more than the branch guard already states.

So once the primitive rule has reduced the quotient to the numerator, the remaining reduction is just ordinary simplification under the guard.

### Proof sketch

1. Primitive zero reduction replaces the quotient with its numerator.
2. Guard-aware reduction substitutes consequences of branch equalities.
3. Those substitutions hold on all points satisfying the guard.
4. Therefore the reduced expression is equal to the pre-reduction expression on that branch.

---

## 8. Branch Normalization Soundness

### Claim

The branch normalizer preserves extensional branch behavior over ℝ.

### Informal meaning

Normalization may change expression form, but it must not change what each surviving branch computes on real inputs satisfying its guard.

### Why the framework supports this

The normalizer only uses:
- globally safe rewrites,
- guarded rewrites under justified guards,
- primitive zero-rule evaluation on `ZERO` denominators,
- bounded guard-aware reduction using branch facts.

It also discards only branches detected as inconsistent.

### Proof sketch

1. Every normalization step belongs to one of the sound classes above.
2. Inconsistent branches represent no real valuation and may be safely removed.
3. Surviving branches preserve branch-local meaning.
4. Therefore the normalized branch set denotes the same extensional branch behavior.

---

## 9. Residual Branch Classification Soundness

### Claim

For a normalized equation branch, classification into:

- `TAUTOLOGY`
- `CONTRADICTION`
- `RESIDUAL`

is sound.

### Informal meaning

The classifier must not mark a false branch as tautological or a true branch as contradictory.

### Why the framework supports this

Classification is based on the guard-reduced difference:

```text
lhs - rhs
```

If it simplifies to:

- `0` -> tautology
- a nonzero number -> contradiction
- anything else -> residual

This is intentionally conservative.

### Proof sketch

1. If `lhs - rhs = 0` under the guard, then the equation holds on that branch.
2. If `lhs - rhs` is a fixed nonzero constant under the guard, then the equation fails on that branch.
3. Otherwise the framework refuses to overclaim and labels the branch residual.

Thus the classification is sound, though incomplete.

---

## 10. Residual Solver Soundness

### Claim

Whenever the residual solver returns a concrete solution for a residual branch, that solution satisfies the normalized branch equation.

### Informal meaning

The solver may miss solutions, but the ones it returns should not be fake.

### Current scope

The current residual solver is intentionally small. It only attempts simple SymPy-solvable residual equations, mainly in one variable.

### Proof sketch

1. The branch equation is first normalized under the branch guard.
2. The solver then solves the normalized residual equation.
3. Returned solutions are solutions of that residual equation.
4. Therefore they satisfy the normalized branch equation on that branch.

This is a soundness claim, not a completeness claim.

---

## 11. Solution Extraction Soundness

### Claim

Every extracted final solution object corresponds to a genuine solution of the original branch-aware equation under the framework semantics.

### Current extraction modes

The current extractor handles:

- contradiction branches -> discard
- tautology branches with simple fixed-value guards -> extract `Eq(x, a)`
- tautology branches with simple nonzero guards -> extract `Ne(expr, 0)`
- solved residual branches -> extract `Eq(x, a)` values returned by the residual solver

### Example

For:

```text
x/x = 1
```

the solver extracts:

```text
Ne(x, 0)
```

For:

```text
x/(x - 1) = x
```

the solver extracts:

```text
Eq(x, 0) or Eq(x, 1) or Eq(x, 2)
```

### Proof sketch

1. Contradiction branches are removed and contribute nothing.
2. Tautology branches contribute only conditions already guaranteed by the guard.
3. Residual branches contribute only solutions returned by the residual solver.
4. By residual solver soundness, those solutions satisfy the branch equation.
5. Therefore every extracted solution is a genuine solution of the original problem under branch semantics.

Again, this does **not** claim completeness.

---

## 12. What Is Not Yet Proved

The framework does **not** yet prove:

- full completeness of the solver
- full canonical uniqueness of normalized branch sets
- confluence of all rewrite sequences
- completeness of guard inconsistency detection
- full multivariable solving correctness
- full equivalence reduction for all logically identical guard formulas

These remain future work.

---

## 13. Honest Current Status

At the current milestone, the framework supports the following soundness claim:

> the current prototype is sound as a branch-aware guarded symbolic normalizer and early solver for the class of cases it explicitly handles.

This is already enough to justify continued development.

What it does **not** justify yet is making large claims about:

- complete algebraic foundations
- all symbolic equations
- replacing standard arithmetic
- advanced analytic mathematics

---

## 14. Why Further Development Is Allowed

The framework does not need a complete proof of everything before moving forward.

What matters is:

- the core soundness targets are clear,
- no internal contradiction has been exposed,
- the implementation matches the intended semantics on locked acceptance tests,
- and future expansion proceeds under regression control.

So further development is justified **provided** the acceptance suite and soundness targets remain the standard of review.

---

## 15. Design Intent

This document marks the current stage of the project:

- beyond free exploration,
- beyond raw theory drafts,
- and into a phase where semantics, engine behavior, and acceptance tests can be compared systematically.

It should be read as a declaration of the framework’s **current soundness ambitions**, not as a claim that the full theory is finished.
