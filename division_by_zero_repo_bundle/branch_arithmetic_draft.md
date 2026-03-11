# Branch Arithmetic: A Draft Formalism for Zero-Denominator Erasure

**Status:** Draft v0.1  
**Author:** Archi (concept) + ChatGPT/Saba (formalization draft)  
**Intended use:** review draft, discussion draft, GitHub publication, future refinement

---

## 1. Abstract

This document proposes a branch-evaluated arithmetic formalism in which division by a denominator that normalizes to zero does not attempt to compute a quotient. Instead, the division layer is erased and evaluation continues with the numerator unchanged.

The core rule is not interpreted as inverse multiplication. It is interpreted as a structural rewrite:

- if a denominator normalizes to `0`, then `A / B` rewrites to `A`
- if a denominator is known to be nonzero, then ordinary division applies
- if zero/nonzero status cannot be decided safely, both branches are retained

The system is therefore not a field extension and not standard algebra with a patched point. It is a branch-sensitive rewrite system with guarded use of ordinary algebra.

Its purpose is to preserve a usable nonzero branch while also allowing a zero branch in which zero-denominator layers erase rather than fail.

---

## 2. Scope

This draft focuses on:

1. division and denominator behavior
2. branch splitting into zero and nonzero cases
3. safe denominator normalization before branch selection
4. hidden-zero detection inside denominators
5. legality conditions for when ordinary algebra is and is not allowed

This draft does **not** claim:

1. full algebraic completeness
2. full confluence in the unrestricted rewriting sense
3. compatibility with ordinary field axioms
4. completeness for all possible hidden-zero identities
5. a finished theory over all algebraic domains

---

## 3. Guiding Interpretation

The central semantic shift is this:

- ordinary division for nonzero denominators remains ordinary division
- division by a denominator that normalizes to zero is **not** treated as inverse multiplication
- it is treated as **zero-denominator erasure**

So the expression:

`A / B`

is evaluated by first asking:

> does `B` normalize to `0`, normalize to provably nonzero, or remain undecided?

That classification determines whether the expression enters:

- the **Z-branch**: denominator normalizes to zero
- the **NZ-branch**: denominator is nonzero
- or a guarded piecewise result when neither can be settled globally

---

## 4. Core Axioms and Definitions

### Axiom A1 — Ordinary Division on the NZ-Branch

If a denominator is established to be nonzero, division behaves ordinarily.

For `B != 0`:

`A / B` is ordinary division.

This includes all usual division-dependent algebraic moves that are already valid under the assumption `B != 0`.

### Axiom A2 — Zero-Denominator Erasure

If a denominator normalizes to `0`, then the quotient layer is erased:

`A / B -> A` whenever `B -> 0`

The arrow `->` is the intended reading. This is a rewrite rule, not an inverse-multiplication claim.

### Axiom A3 — Zero Numerator Rule

For every expression `B`:

`0 / B -> 0`

including the case `B -> 0`. Therefore:

`0 / 0 -> 0`

### Axiom A4 — Branch Split Before NZ-Only Algebra

A quotient must be branch-split before any simplification that relies on the denominator being nonzero.

This is the main safety axiom of the system.

### Definition D1 — Branch Normal Form

The value of a quotient is allowed to be a guarded branch object rather than a single expression.

We write guarded outputs in the form:

- `[condition] -> expression`

Example:

`(x^2 - x) / x`

becomes:

- `[x = 0] -> 0`
- `[x != 0] -> x - 1`

### Definition D2 — Zero-Test Normalization (ZTN)

`ZTN(B)` is the denominator normalization procedure used to classify a denominator `B` as:

- `ZERO`
- `NONZERO`
- `UNKNOWN`

The purpose of `ZTN` is not full simplification. Its purpose is to safely determine branch status.

---

## 5. Hard Constraint

The following is a locked rule of the system:

> **A quotient must be branch-split before any simplification that relies on the denominator being nonzero.**

This means that the following moves are **NZ-branch only** and are forbidden before branch split on the main quotient:

1. cancellation across the main `/`
2. factor removal across the main `/`
3. cross-multiplication
4. denominator clearing
5. quotient compression or expansion that assumes a live denominator
6. any manipulation that tacitly assumes denominator invertibility

If such a move is used, it is understood as an implicit choice of the NZ-branch.

---

## 6. Evaluation Pipeline

For a main quotient:

`A / B`

perform the following steps.

### Step 1 — Normalize the Denominator Internally

Apply `ZTN(B)` using only safe denominator-internal rewrite rules.

### Step 2 — Classify the Denominator

After normalization, classify `B` as one of:

- `ZERO`
- `NONZERO`
- `UNKNOWN`

### Step 3 — Evaluate by Case

#### Case Z: `B` is `ZERO`

Only the zero branch survives:

`A / B -> A`

Then simplify `A` under the branch assumption.

#### Case NZ: `B` is `NONZERO`

Only the nonzero branch survives:

`A / B`

remains ordinary division. Standard algebra may now be used.

#### Case U: `B` is `UNKNOWN`

Return both branches:

- `[B = 0] -> A`
- `[B != 0] -> ordinary A / B`

Then simplify each branch under its own condition.

### Step 4 — Prune Impossible Branches

Remove branches whose assumptions are contradictory in the chosen domain.

### Step 5 — Merge Equivalent Outputs

If multiple surviving branches produce the same final expression, merge them.

---

## 7. Kernel Rewrite Rules for Denominator Normalization

The kernel is intentionally conservative.

### 7.1 Structural Rules

1. normalize subexpressions before parents
2. flatten nested additions
3. flatten nested multiplications
4. sort additive terms canonically
5. sort multiplicative factors canonically
6. normalize signs into canonical form

These are mandatory because term matching depends on them.

### 7.2 Additive Rules

1. `X + 0 -> X`
2. `0 + X -> X`
3. `X - 0 -> X`
4. `X - X -> 0`
5. `X + (-X) -> 0`
6. `(-X) + X -> 0`
7. `0 - X -> -X`
8. `-0 -> 0`
9. `-(-X) -> X`
10. rewrite subtraction as signed addition when useful:
   - `X - Y -> X + (-Y)`
11. push negation into sums:
   - `-(X + Y) -> (-X) + (-Y)`

### 7.3 Multiplicative Rules

1. `X * 1 -> X`
2. `1 * X -> X`
3. `X * 0 -> 0`
4. `0 * X -> 0`
5. `(-1) * X -> -X`
6. `X * (-1) -> -X`
7. `(-X) * Y -> -(X * Y)`
8. `X * (-Y) -> -(X * Y)`
9. `(-X) * (-Y) -> X * Y`

### 7.4 Division Rules Inside Subexpressions

1. `X / 0 -> X`
2. `0 / X -> 0`
3. `X / 1 -> X`
4. literal division with nonzero literal denominator may be evaluated numerically

These rules may be used inside denominators and subexpressions before main branch split.

### 7.5 Literal Arithmetic

Literal-only subexpressions may be evaluated directly.

Examples:

- `2 + 3 -> 5`
- `7 - 7 -> 0`
- `4 * (-2) -> -8`
- `6 / 2 -> 3`

---

## 8. Forbidden Pre-Branch Moves on the Main Quotient

For a main quotient `A / B`, the following are illegal before branch split:

1. `(A*C) / C -> A`
2. `(X^2 - X) / X -> X - 1`
3. `(A/B)/C -> A/(B*C)` when this changes main-quotient structure before branch selection
4. multiplying both sides of an equation by the denominator
5. any cross-multiplication involving the main denominator
6. any inference that requires `B != 0`

These moves are legal only on the NZ-branch.

---

## 9. Hidden Zero Module HZ-1 — Additive Hidden Zeros

HZ-1 catches additive and sign-based hidden zeros inside denominators.

### HZ-1 Capabilities

1. detect symmetry zeros:
   - `(u-v) + (v-u) -> 0`
2. detect commutative cancellation:
   - `(a+b) - (b+a) -> 0`
3. detect signed pair cancellation:
   - `T + (-T) -> 0`
4. merge repeated linear terms:
   - `2*X - X - X -> 0`
5. recursively detect zeros generated inside subexpressions

### HZ-1 Examples

- `(u-v) + (v-u) -> 0`
- `(a+b) - (b+a) -> 0`
- `2*x - x - x -> 0`
- `((x/0)-x) -> 0`

---

## 10. Hidden Zero Module HZ-2 — Pairwise Structured Factor Zeros

HZ-2 introduces limited factor-aware zero detection.

### HZ2.1 Exact Duplicate Cancellation

- `T - T -> 0`
- `T + (-T) -> 0`

including structured terms such as:

- `A/B - A/B -> 0`
- `x*(u-v) - x*(u-v) -> 0`

### HZ2.2 Common-Left-Factor Detection

- `F*U - F*V -> F*(U-V)`
- `F*U + F*V -> F*(U+V)`

when used only to expose zero internally.

### HZ2.3 Common-Right-Factor Detection

- `U*F - V*F -> (U-V)*F`
- `U*F + V*F -> (U+V)*F`

again only for internal zero testing.

### HZ-2 Examples

- `x*y - y*x -> 0`
- `A*(u-v) + A*(v-u) -> 0`
- `(a+b)*t - t*(b+a) -> 0`
- `m*n - m*k -> m*(n-k)` and then usually remains `UNKNOWN`

### Restriction

HZ-2 is not unrestricted factoring. It is targeted factoring used only when it reduces denominator zero detection to a smaller problem.

---

## 11. Hidden Zero Module HZ-3 — Bounded Multi-Term Regrouping

HZ-3 extends factor-aware zero detection to additive clusters.

### HZ3.1 Multi-Left-Factor Grouping

- `F*U1 + F*U2 + ... + F*Un -> F*(U1 + U2 + ... + Un)`

### HZ3.2 Multi-Right-Factor Grouping

- `U1*F + U2*F + ... + Un*F -> (U1 + U2 + ... + Un)*F`

### HZ3.3 Signed Cluster Grouping

- `F*U1 + F*U2 - F*U3 -> F*(U1 + U2 - U3)`

when this reduces the top-level additive structure or exposes immediate cancellation.

### HZ-3 Examples

- `a*b + a*c - a*(b+c) -> 0`
- `x*(u-v) + y*(u-v) - (x+y)*(u-v) -> 0`
- `(m+n)*t - m*t - n*t -> 0`
- `p*q - p*r - p*(q-r) -> 0`

### Restriction

HZ-3 is one-way bounded regrouping. It is not free distributive expansion/factoring.

---

## 12. Mandatory One-Way Policy

To preserve termination and classification stability, denominator normalization uses the following one-way policy:

1. grouping may be used
2. free expansion may not be used
3. regrouping is legal only if it decreases structural complexity or exposes immediate cancellation

In particular:

- `a*b + a*c -> a*(b+c)` may be allowed
- `a*(b+c) -> a*b + a*c` is forbidden inside denominator normalization

This asymmetry is intentional.

---

## 13. Classification Rules

After denominator normalization, classify as follows.

### ZERO

If the normalized denominator is literally `0`.

### NONZERO

A denominator is provably nonzero only under explicit safe rules, such as:

1. nonzero numeric literal
2. product of provably nonzero expressions
3. quotient of provably nonzero expressions with nonzero denominator
4. negation of a provably nonzero expression

### UNKNOWN

If neither `ZERO` nor `NONZERO` can be safely concluded.

The system is deliberately conservative. It prefers `UNKNOWN` over unsound inference.

---

## 14. Domain Policy

Domain-sensitive rules are modular, not kernel rules.

Example:

- over the reals, `x^2 + 1` is always nonzero
- over the complex numbers, `x^2 + 1` may be zero

Therefore such rules must not be silently baked into the kernel. Domain assumptions must be declared explicitly.

---

## 15. Complexity / Termination Discipline

A denominator rewrite is legal only if it improves canonical form or reduces complexity.

A practical priority order is:

1. number of top-level additive sibling terms
2. number of unmatched opposite terms
3. number of explicit subtraction nodes
4. number of unsorted factors or terms
5. total syntax size

A rewrite is justified if it reduces an earlier measure or preserves them while improving canonicalization.

This is not yet a formal proof of termination, but it is the intended operational discipline.

---

## 16. Stability Claim

The strongest supported claim at this stage is the following:

> Under mandatory canonicalization, one-way bounded regrouping, and pre-branch protection of the main quotient, denominator normalization is classification-stable on the tested additive, factorized, and bounded distributive hidden-zero families.

This means that different **valid** rewrite orders gave the same denominator classification (`ZERO`, `NONZERO`, or `UNKNOWN`) on the tested families.

This document does **not** claim full unrestricted confluence.

---

## 17. Canonical Examples

### Example 1

`a / (x - x)`

Denominator normalizes to `0`, so:

`a / (x - x) -> a`

### Example 2

`a / ((x/0) - x)`

Inside denominator:

- `x/0 -> x`
- `x - x -> 0`

Therefore:

`a / ((x/0)-x) -> a`

### Example 3

`7 / (x - 1)`

Denominator status is `UNKNOWN`, so output is:

- `[x = 1] -> 7`
- `[x != 1] -> 7 / (x - 1)`

### Example 4

`(x^2 - x) / x`

Main denominator is `x`, so branch split must happen before cancellation.

Correct output:

- `[x = 0] -> 0`
- `[x != 0] -> x - 1`

### Example 5

`N / (a*b + a*c - a*(b+c))`

Denominator reduces to `0`, so:

`N / (a*b + a*c - a*(b+c)) -> N`

### Example 6

`N / (x*y - y*x)`

Denominator reduces to `0`, so:

`N / (x*y - y*x) -> N`

---

## 18. What Unrestricted Algebra Means in This System

Unrestricted algebra is not globally wrong in this formalism. It is branch-local.

If a manipulation requires denominator nonzero, then it is understood as occurring on the NZ-branch.

So:

`(x^2 - x) / x -> x - 1`

is not globally valid, but it is valid as the NZ-branch result under the condition `x != 0`.

This is a feature of the system, not a bug.

---

## 19. Optional Magnitude-Subtraction Note

If one wishes to work with unsigned magnitudes rather than signed arithmetic, subtraction may be reinterpreted as magnitude difference:

`a - b := |a - b|`

on nonnegative magnitudes.

Under that interpretation:

- `a - 0 = a`
- `0 - a = a`

so `0` becomes a two-sided identity for magnitude subtraction.

This is separate from ordinary signed subtraction and should be treated as an explicitly different operation or explicitly different interpretation of `-`.

---

## 20. Non-Goals and Risks

### Non-Goals

This draft does not yet attempt:

1. a power/exponent module
2. full polynomial identity detection
3. semantic zero-detection for arbitrary equivalent forms
4. full equation theory
5. proof of confluence in the formal rewriting-theory sense

### Risks

The main risks are:

1. allowing too much expansion and reintroducing rewrite loops
2. silently using NZ-only algebra before branch split
3. mixing domain-sensitive nonzero facts into the kernel without declaration
4. overclaiming completeness

---

## 21. Review Questions

A reviewer should test the draft against the following questions.

1. Are the branch semantics clear?
2. Is zero-denominator erasure stated explicitly as a rewrite rather than inverse division?
3. Is the hard pre-branch constraint strong enough?
4. Are HZ-1 / HZ-2 / HZ-3 sufficiently bounded?
5. Is classification stability the right target instead of full syntactic confluence?
6. Which additional modules can be added without collapsing termination?
7. Is branch output the correct canonical answer format?

---

## 22. Minimal Pseudocode

```text
EvaluateQuotient(A, B):
    B* = ZTN(B)
    status = Classify(B*)

    if status == ZERO:
        return Simplify(A)

    if status == NONZERO:
        return SimplifyOrdinaryDivision(A / B*)

    if status == UNKNOWN:
        return {
            [B* = 0]  -> Simplify(A under B* = 0),
            [B* != 0] -> SimplifyOrdinaryDivision(A / B* under B* != 0)
        }
```

---

## 23. Current Claim Summary

This draft supports the following statement:

> Branch Arithmetic is a branch-evaluated arithmetic formalism in which denominators are normalized before quotient-level nonzero assumptions are allowed. If a denominator normalizes to zero, the quotient layer erases. If it is nonzero, ordinary division applies. If this cannot be decided safely, both branches are retained.

That is the current core of the theory.

---

## 24. Roadmap

Possible next steps:

1. formalize branch conditions more rigorously
2. add an explicit equation-solving layer
3. add a power module under domain assumptions
4. define a precise canonical form grammar
5. test the system against a broader rewrite-suite
6. implement a prototype evaluator
7. prove stronger termination/classification properties for the denominator kernel

---

## 25. License / Publication Note

This draft is suitable for publication to GitHub as a theory note, design document, or discussion draft. Before treating it as a formal paper, the rewrite system should be reviewed by people comfortable with:

1. term rewriting systems
2. algebraic structures
3. symbolic computation
4. operational semantics

---

## 26. Short Version for README / Repo Description

Branch Arithmetic is a branch-sensitive arithmetic formalism where denominators are normalized before quotient-level algebra is allowed. If a denominator reduces to zero, the quotient rewrites to its numerator instead of failing. If the denominator is nonzero, ordinary division applies. If branch status is unknown, both zero and nonzero branches are retained as guarded outputs.

