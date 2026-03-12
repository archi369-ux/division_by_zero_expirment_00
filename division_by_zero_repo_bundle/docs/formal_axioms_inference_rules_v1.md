# Formal Axioms and Inference Rules v1

## Purpose

This document gives a compact reference specification for the current branch-arithmetic core.
It is not a completeness or confluence proof. It is a theorem-style summary of the rules the
rest of the repository uses.

---

## 1. Language

Expressions are built from:

- variables: `x, y, z, ...`
- constants: `0, 1, -1, 2, ...`
- operations: `+ , - , * , /`
- parentheses

An equation is an ordered pair of expressions written `L = R`.

---

## 2. Primitive interpretation

### Axiom A1 — Zero-denominator erasure
For any expression `A`:

`A / 0 -> A`

This is a rewrite rule, not an inverse-division law.

### Axiom A2 — Zero numerator
For any expression `B`:

`0 / B -> 0`

In particular:

`0 / 0 -> 0`

### Axiom A3 — Ordinary division on NZ-branches
If a denominator has already been established to be nonzero, ordinary division laws are available on that branch.

### Axiom A4 — Branch firewall
No rule that relies on a denominator being nonzero may be applied before branch split.

This forbids pre-branch use of:

- cancellation across the main quotient
- cross-multiplication
- inverse-style division laws
- denominator clearing
- any proof step that silently assumes `B != 0`

---

## 3. Branch objects

### Definition D1 — Branch clause
A branch clause has the form:

`[guard] -> expression`

### Definition D2 — Branch Normal Form (BNF)
A Branch Normal Form is a finite set of branch clauses representing the guarded outcomes of an expression.

### Definition D3 — Solution Normal Form (SNF)
A Solution Normal Form is a finite set of guarded solution clauses:

`[guard] -> solution-set or reduced equation`

---

## 4. Detector-backed guards

These align with the semantic base developed in the Zero-Set Detector Algebra note.

### Definition D4 — Zero detector
For any expression `f`:

`D_f := 1 - f/f`

### Definition D5 — Nonzero detector
For any expression `f`:

`N_f := f/f`

### Axiom A5 — Detector partition

`D_f + N_f = 1`

### Axiom A6 — Detector exclusivity

`D_f * N_f = 0`

### Interpretation I1
- `D_f = 1` corresponds to the zero branch `f = 0`
- `N_f = 1` corresponds to the nonzero branch `f != 0`

Whenever possible, guards should be written in detector-backed form.

---

## 5. Denominator classification

### Definition D6 — Denominator classifier
A denominator classifier maps a denominator `B` to one of:

- `ZERO`
- `NONZERO`
- `UNKNOWN`

after safe denominator-only normalization.

### Rule C1 — ZERO classification
If the denominator normalization procedure reduces `B` to literal `0`, classify as `ZERO`.

### Rule C2 — NONZERO classification
If the denominator normalization procedure proves `B` is nonzero by admissible rules, classify as `NONZERO`.

### Rule C3 — UNKNOWN classification
If neither ZERO nor NONZERO can be established, classify as `UNKNOWN`.

---

## 6. Safe denominator normalization rules

These rules apply only inside denominators before branch split.

### Structural rules

#### R1 — Normalize subexpressions first
Normalization is recursive and bottom-up.

#### R2 — Flatten sums and products
Nested sums and products may be flattened.

#### R3 — Canonical ordering
Additive sibling terms and multiplicative factors may be sorted into a fixed canonical order.

### Additive rules

#### R4
`X + 0 -> X`

#### R5
`0 + X -> X`

#### R6
`X - 0 -> X`

#### R7
`X - X -> 0`

#### R8
`X + (-X) -> 0`

#### R9
`(-X) + X -> 0`

#### R10
`0 - X -> -X`

#### R11
`-0 -> 0`

#### R12
`-(-X) -> X`

#### R13 — Subtraction to signed sum
`X - Y -> X + (-Y)`

#### R14 — Negation pushdown over addition
`-(X + Y) -> (-X) + (-Y)`

### Multiplicative rules

#### R15
`X * 1 -> X`

#### R16
`1 * X -> X`

#### R17
`X * 0 -> 0`

#### R18
`0 * X -> 0`

#### R19
`(-1) * X -> -X`

#### R20
`X * (-1) -> -X`

#### R21 — Sign normalization in products
`(-X)*Y -> -(X*Y)`

#### R22
`X*(-Y) -> -(X*Y)`

#### R23
`(-X)*(-Y) -> X*Y`

### Division rules inside subexpressions

#### R24
`X / 0 -> X`

#### R25
`0 / X -> 0`

#### R26
`X / 1 -> X`

#### R27 — Literal division
If `m,n` are numeric literals and `n != 0`, then `m/n` may be evaluated numerically.

### Hidden-zero rules

#### R28 — Opposite-term cancellation
If two additive terms are canonical opposites, they may cancel to `0`.

#### R29 — Duplicate-term coefficient merge
Repeated identical additive terms may be merged by integer coefficient bookkeeping.

#### R30 — Pairwise common-left-factor grouping
`F*U - F*V -> F*(U - V)`

#### R31 — Pairwise common-right-factor grouping
`U*F - V*F -> (U - V)*F`

#### R32 — Bounded multi-left-factor grouping
`F*U1 + ... + F*Un -> F*(U1 + ... + Un)`

#### R33 — Bounded multi-right-factor grouping
`U1*F + ... + Un*F -> (U1 + ... + Un)*F`

#### Admissibility condition on R30–R33
These grouping rules are legal only when they:

- operate on direct additive siblings,
- preserve the branch firewall,
- reduce structural complexity or expose immediate cancellation,
- are used only for denominator normalization.

### Forbidden pre-branch rules

#### F1
No cancellation across the main quotient.

#### F2
No cross-multiplication.

#### F3
No denominator clearing.

#### F4
No expansion/factoring cycles introduced only for convenience.

#### F5
No move whose validity requires silent use of `B != 0` before splitting on `B`.

---

## 7. Expression branch rules

Let `A / B` be a main quotient.

### Rule E1 — ZERO branch
If the denominator classifier returns `ZERO`, then:

`A / B -> A`

Output:

`[B = 0] -> A`

or detector-backed:

`[D_B = 1] -> A`

### Rule E2 — NONZERO branch
If the denominator classifier returns `NONZERO`, then ordinary division is retained:

`[B != 0] -> A / B`

or detector-backed:

`[N_B = 1] -> A / B`

with NZ-only rules admissible inside that branch.

### Rule E3 — UNKNOWN split
If the denominator classifier returns `UNKNOWN`, output both branches:

- `[B = 0] -> A`
- `[B != 0] -> A / B`

or detector-backed:

- `[D_B = 1] -> A`
- `[N_B = 1] -> A / B`

---

## 8. Equation solver kernel

Equations are solved by converting each side to branch normal form, taking the branch product, and solving branch-locally.

### Rule S1 — One quotient vs plain expression
For `A/B = C`:

- Z-branch: `[B = 0] -> solve(A = C)`
- NZ-branch: `[B != 0] -> solve(A = B*C)`

### Rule S2 — Plain expression vs one quotient
For `C = A/B`:

- Z-branch: `[B = 0] -> solve(C = A)`
- NZ-branch: `[B != 0] -> solve(B*C = A)`

### Rule S3 — Two quotients
For `A/B = C/D`:

- `[B = 0, D = 0] -> solve(A = C)`
- `[B = 0, D != 0] -> solve(A*D = C)`
- `[B != 0, D = 0] -> solve(A = B*C)`
- `[B != 0, D != 0] -> solve(A*D = B*C)`

### Rule S4 — Fixed right side `A/B = A`
For `A/B = A`:

- `[B = 0] -> true`
- `[B != 0] -> solve(A = A*B)`

Over an integral domain this reduces branch-locally to:

- `[B != 0] -> solve(A*(B - 1) = 0)`

### Rule S5 — Fixed right side `A/B = 0`

- `[B = 0] -> solve(A = 0)`
- `[B != 0] -> solve(A = 0)`

Hence branch merging may collapse the result to the unguarded equation `A = 0`.

### Rule S6 — Fixed right side `A/B = 1`

- `[B = 0] -> solve(A = 1)`
- `[B != 0] -> solve(A = B)`

### Rule S7 — Fixed right side `A/B = B`

- `[B = 0] -> solve(A = B)`
- `[B != 0] -> solve(A = B^2)`

In the current core language, the right-hand side may be kept as `B*B` if powers are not admitted.

---

## 9. Branch pruning and merging

### Rule P1 — Impossible-branch pruning
A branch whose guard is inconsistent is discarded.

Examples:

- `[X - X != 0]` is impossible
- `[2 = 0]` is impossible

### Rule P2 — Equivalent-branch merging
If two surviving branches yield the same expression or same reduced equation, they may be merged into a weaker combined guard.

### Rule P3 — Tautological-branch collapse
If a branch reduces to a tautology, it may be recorded as `true` under its guard.

---

## 10. Legality conditions

### L1 — Canonicalization before matching
Duplicate detection and opposite-term cancellation require canonicalized terms.

### L2 — Grouping is one-way in the detector
Grouping may be used to expose hidden zeros. Reverse expansion is not admitted in the normalization kernel.

### L3 — NZ-only rules are branch-local
Any inference that requires nonzero denominators is legal only inside a branch already guarded by nonzero conditions.

### L4 — Expression branching precedes equation solving
Equation rules do not bypass branch formation.

### L5 — Branch objects are official outputs
No result should be forced into a single unguarded expression when branch information is still live.

---

## 11. Acceptance criteria for v1

The current formal core is acceptable if the following hold.

### AC1
The branch firewall is never violated.

### AC2
Denominator classification is performed before NZ-only algebra.

### AC3
Expression outputs are given in Branch Normal Form when needed.

### AC4
Equation outputs are given in Solution Normal Form when needed.

### AC5
Impossible branches are pruned and equivalent branches may be merged.

### AC6
The system makes no claim beyond its guarded branch semantics.

---

## 12. Non-claims

This reference sheet does not claim:

- full confluence,
- full completeness,
- field semantics,
- analytic semantics,
- unrestricted symbolic simplification.

It is a compact formal reference for the current guarded branch calculus only.
