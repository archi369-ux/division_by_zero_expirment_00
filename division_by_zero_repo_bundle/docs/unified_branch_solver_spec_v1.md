# Unified Branch Solver Spec v1

## Purpose

This document unifies expression branch normal form and guarded equation solving into one formal pipeline.

## Core Principle

A quotient must be branch-split before any rewrite that requires a nonzero denominator.

## Semantic Base

- Primitive semantic rule: `a/0 := a`
- Zero detector: `D_f := 1 - f/f`
- Nonzero detector: `N_f := f/f`
- Detector laws:
  - `D_f = 1` iff `f = 0`
  - `N_f = 1` iff `f != 0`
  - `D_f + N_f = 1`
  - `D_f N_f = 0`

## Objects

### Guard
A condition built from zero/nonzero claims and optionally Boolean combinations.

### Branch
A pair `[G] -> E` where `G` is a guard and `E` is an expression.

### Branch Normal Form (BNF)
A finite set of branches.

### Solution Normal Form (SNF)
A finite set of guarded solution clauses:

`[G] -> S`

where `S` is a classical solution set or reduced equation on that branch.

## Pipeline

### Stage 1: Expression BNF
Convert each input expression into branch normal form.

For a quotient `A/B`:
1. Normalize `B` with the safe denominator engine.
2. Classify `B` as `ZERO`, `NONZERO`, or `UNKNOWN`.
3. Emit branches:
   - `ZERO`: `[D_B = 1] -> A`
   - `NONZERO`: `[N_B = 1] -> A/B`
   - `UNKNOWN`: both branches

Branching is recursive for nested quotients.

### Stage 2: Equation lifting
For an equation `L = R`:
1. Compute `BNF(L)` and `BNF(R)`.
2. Take the branch product.
3. For each pair `[G1] -> E1`, `[G2] -> E2`, produce:

`[G1 and G2] -> solve(E1 = E2)`

4. Simplify guards.
5. Prune inconsistent branches.
6. Merge equivalent surviving solutions.

## Guard Discipline

### Allowed guard atoms
- `f = 0`
- `f != 0`
- Detector forms `D_f = 1`, `N_f = 1`

### Detector preference
Whenever a guard is exactly a zero/nonzero claim on an expression `f`, it should be representable by detectors.

### Guard simplification
- `D_f and N_f -> false`
- `D_f or N_f -> true`
- duplicate atoms collapse
- impossible numeric guards collapse, e.g. `2 = 0 -> false`

## Branch Firewall

Before a quotient has been split on its denominator, the following are forbidden across that quotient:
- cancellation
- cross-multiplication
- denominator clearing
- inverse-style division laws
- fraction compression/expansion that presumes nonzero denominator

These become legal only inside a branch guarded by `N_B = 1`.

## Solver Kernel v2

### Case U1: `A/B = C`
- `[D_B = 1] -> solve(A = C)`
- `[N_B = 1] -> solve(A = B C)`

### Case U2: `C = A/B`
- `[D_B = 1] -> solve(C = A)`
- `[N_B = 1] -> solve(B C = A)`

### Case U3: `A/B = C/D`
- `[D_B = 1 and D_D = 1] -> solve(A = C)`
- `[D_B = 1 and N_D = 1] -> solve(A D = C)`
- `[N_B = 1 and D_D = 1] -> solve(A = B C)`
- `[N_B = 1 and N_D = 1] -> solve(A D = B C)`

### Case U4: `A/B = A`
- `[D_B = 1] -> true`
- `[N_B = 1] -> solve(A = A B)`

### Case U5: `A/B = B`
- `[D_B = 1] -> solve(A = 0)`
- `[N_B = 1] -> solve(A = B^2)`

### Case U6: `A/B = 0`
- `[D_B = 1] -> solve(A = 0)`
- `[N_B = 1] -> solve(A = 0)`

So this can be merged to:
- `[true] -> solve(A = 0)`

### Case U7: `A/B = 1`
- `[D_B = 1] -> solve(A = 1)`
- `[N_B = 1] -> solve(A = B)`

## Worked Examples

### Example 1: `x/(x-1) = 2`
Left BNF:
- `[D_{x-1}=1] -> x`
- `[N_{x-1}=1] -> x/(x-1)`

Lift to equation:
- `[x-1=0] -> solve(x = 2)` gives contradiction with `x=1`, so prune
- `[x-1!=0] -> solve(x = 2(x-1))` gives `x = 2`

Check guard: `2-1 != 0`, survives.

Final SNF:
- `[true] -> {x = 2}`

### Example 2: `x/((x-x)+(y-y)) = 3`
Denominator normalizes to `0`.

Left BNF:
- `[true] -> x`

Solve `x = 3`.

Final SNF:
- `[true] -> {x = 3}`

### Example 3: `x/(x-1) = x`
- `[x-1=0] -> true` gives branch `x=1`
- `[x-1!=0] -> solve(x = x(x-1))`

NZ branch simplifies to `x(x-2)=0`, so candidates `x=0` or `x=2`.
Both satisfy `x-1 != 0`.

Final SNF:
- `[true] -> {x = 0, 1, 2}`

### Example 4: `(x+1)/((a+b)-(b+a)) = 7`
Denominator normalizes to `0`.

Equation becomes `x+1 = 7`.

Final SNF:
- `[true] -> {x = 6}`

## Acceptance Criteria

The unified solver is acceptable if:
1. every top-level quotient is branch-split before NZ-only algebra
2. both sides are converted to BNF before solving
3. guards use detectors whenever possible
4. inconsistent branches are pruned explicitly
5. equivalent surviving branches are merged
6. hidden-zero denominator normalization stays one-way and bounded

## Verification Checklist

For any equation:
1. Did each side first convert to BNF?
2. Did any forbidden quotient rewrite happen before branch split?
3. Did each quotient guard become a zero/nonzero branch?
4. Were detectors used for zero/nonzero guards when available?
5. Were impossible guard combinations removed?
6. Were branch-local classical solutions checked against their guards?

## Scope Boundary

This spec does not claim:
- reciprocal semantics at zero
- full confluence of unrestricted algebra
- calculus or limit semantics
- order/sign logic
- general completeness for all symbolic hidden-zero forms

It is a guarded symbolic solver built on totalized zero-semantic division.
