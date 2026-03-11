
# Equation Solver Draft v1

## Status

This draft locks three decisions:

1. **Branch firewall stays active.**  
   No rule that requires a denominator to be nonzero may be used before branch split.

2. **Branch guards use detectors whenever possible.**  
   For any guard on an expression `B`:
   - zero guard: `D_B := 1 - B/B`
   - nonzero guard: `N_B := B/B`

   On semantic evaluation, `D_B = 1` iff `B = 0`, `N_B = 1` iff `B != 0`, and
   `D_B + N_B = 1`, `D_B N_B = 0`.

3. **Equation solving is branch-first.**  
   A quotient is never "cleared" until its zero and nonzero branches are separated.

---

## Semantic base layer

This draft uses the semantic rule:

- if `b != 0`, then `a / b` is ordinary division
- if `b = 0`, then `a / 0 := a`

together with bottom-up evaluation and the explicit warning that reciprocal, cancellation,
and cross-multiplication do **not** extend across denominator zero.

---

## Official solution object

A solution is a finite set of guarded clauses:

- `[guard] -> solution set`
- or equivalently
- `detector * branch`

Examples of guard notation:

- `[B = 0]` or `[D_B = 1]`
- `[B != 0]` or `[N_B = 1]`

The branch object is the official output. A single flat solution is only a merged special case.

---

## Branch-local soundness principle

Every solver rule must be justified branch by branch:

- on a zero branch, replace `A/B` by `A`
- on a nonzero branch, ordinary field/integral-domain algebra may be used

No solver rule is globally valid unless each branch has been handled separately.

---

# Solver Kernel v1

The current kernel covers these equation forms:

1. `A/B = C`
2. `C = A/B`
3. `A/B = C/D`
4. `A/B = A`
5. `A/B = B`
6. `A/B = 0`
7. `A/B = 1`

Each rule is given first in guard form, then in detector form.

---

## Case 1. `A/B = C`

### Rule

Split on `B`.

- Z-branch: `[B = 0] -> solve(A = C)`
- NZ-branch: `[B != 0] -> solve(A = B*C)`

Detector form:

- `[D_B = 1] -> solve(A = C)`
- `[N_B = 1] -> solve(A = B*C)`

### Why sound

- If `B = 0`, then `A/B -> A`, so the equation becomes `A = C`.
- If `B != 0`, ordinary multiplication by `B` is allowed, so `A/B = C` becomes `A = BC`.

### Worked example 1

Solve:
`x/(x-1) = 2`

Split on `x-1`.

- Z-branch: `x-1 = 0`, solve `x = 2`
  - guard gives `x = 1`
  - branch equation gives `x = 2`
  - contradiction, so branch dies

- NZ-branch: `x-1 != 0`, solve `x = 2(x-1)`
  - `x = 2x - 2`
  - `x = 2`
  - guard holds since `2-1 != 0`

Result:
- `[x-1 != 0] -> {2}`

### Worked example 2

Solve:
`(x+1)/(x-1) = 3`

Split on `x-1`.

- Z-branch: `x-1 = 0`, solve `x+1 = 3`
  - guard gives `x = 1`
  - branch equation gives `x = 2`
  - contradiction

- NZ-branch: `x-1 != 0`, solve `x+1 = 3(x-1)`
  - `x+1 = 3x - 3`
  - `x = 2`
  - guard holds

Result:
- `[x-1 != 0] -> {2}`

---

## Case 2. `C = A/B`

### Rule

Split on `B`.

- Z-branch: `[B = 0] -> solve(C = A)`
- NZ-branch: `[B != 0] -> solve(B*C = A)`

Detector form:

- `[D_B = 1] -> solve(C = A)`
- `[N_B = 1] -> solve(B*C = A)`

### Why sound

Same reasoning as Case 1, with the quotient on the right.

### Worked example 1

Solve:
`2 = (x+2)/x`

Split on `x`.

- Z-branch: `x = 0`, solve `2 = x+2`
  - under `x = 0`, branch equation is true
  - so `x = 0` survives

- NZ-branch: `x != 0`, solve `2x = x+2`
  - `x = 2`
  - guard holds

Result:
- `[x = 0] -> {0}`
- `[x != 0] -> {2}`

Merged result:
- `{0, 2}`

### Worked example 2

Solve:
`3 = (x+1)/(x-1)`

Split on `x-1`.

- Z-branch: `x-1 = 0`, solve `3 = x+1`
  - guard gives `x = 1`
  - branch equation gives `x = 2`
  - contradiction

- NZ-branch: `x-1 != 0`, solve `3(x-1) = x+1`
  - `3x - 3 = x + 1`
  - `x = 2`
  - guard holds

Result:
- `[x-1 != 0] -> {2}`

---

## Case 3. `A/B = C/D`

### Rule

Split on both `B` and `D`.

- `[B = 0, D = 0] -> solve(A = C)`
- `[B = 0, D != 0] -> solve(A*D = C)`
- `[B != 0, D = 0] -> solve(A = B*C)`
- `[B != 0, D != 0] -> solve(A*D = B*C)`

Detector form:

- `[D_B = 1, D_D = 1] -> solve(A = C)`
- `[D_B = 1, N_D = 1] -> solve(A*D = C)`
- `[N_B = 1, D_D = 1] -> solve(A = B*C)`
- `[N_B = 1, N_D = 1] -> solve(A*D = B*C)`

### Why sound

Each branch resolves every quotient before any cross-multiplication is used.  
Cross-multiplication appears **only** on the branch where both denominators are already nonzero.

### Worked example 1

Solve:
`(x+1)/(x-1) = 3/(x-1)`

Here both denominators are `x-1`.

- `[x-1 = 0, x-1 = 0] -> solve(x+1 = 3)`
  - guard gives `x = 1`
  - branch equation gives `x = 2`
  - contradiction

- mixed branches are impossible because the same expression cannot be both zero and nonzero

- `[x-1 != 0, x-1 != 0] -> solve((x+1)(x-1) = 3(x-1))`
  - `x^2 - 1 = 3x - 3`
  - `x^2 - 3x + 2 = 0`
  - `x = 1 or x = 2`
  - guard removes `x = 1`

Result:
- `[x-1 != 0] -> {2}`

### Worked example 2

Solve:
`x/x = (x+1)/(x+1)`

Split on `x` and `x+1`.

- `[x = 0, x+1 = 0]` is impossible
- `[x = 0, x+1 != 0] -> solve(x(x+1) = x+1)`
  - guard gives `x = 0`
  - equation becomes `0 = 1`
  - contradiction

- `[x != 0, x+1 = 0] -> solve(x = x(x+1))`
  - guard gives `x = -1`
  - equation becomes `-1 = 0`
  - contradiction

- `[x != 0, x+1 != 0] -> solve(x(x+1) = x(x+1))`
  - tautology under guards

Result:
- `[x != 0 and x+1 != 0] -> all such x`

Equivalent solution set:
- all `x` except `0` and `-1`

---

## Case 4. `A/B = A`

### Rule

Split on `B`.

- Z-branch: `[B = 0] -> solve(A = A)`  
  This branch is automatically true if the guard is consistent.
- NZ-branch: `[B != 0] -> solve(A = A*B)`

Detector form:

- `[D_B = 1] -> true`
- `[N_B = 1] -> solve(A = A*B)`

### Why sound

- If `B = 0`, then `A/B -> A`, so the equation collapses to an identity.
- If `B != 0`, ordinary multiplication by `B` is permitted.

### Worked example 1

Solve:
`x/(x-1) = x`

Split on `x-1`.

- Z-branch: `x-1 = 0`
  - equation becomes `x = x`
  - so `x = 1` survives

- NZ-branch: `x-1 != 0`, solve `x = x(x-1)`
  - `x = x^2 - x`
  - `x^2 - 2x = 0`
  - `x = 0 or x = 2`
  - both satisfy guard

Result:
- `[x-1 = 0] -> {1}`
- `[x-1 != 0] -> {0, 2}`

Merged result:
- `{0, 1, 2}`

### Worked example 2

Solve:
`(x+1)/(x-1) = x+1`

Split on `x-1`.

- Z-branch: `x-1 = 0`
  - equation becomes `x+1 = x+1`
  - so `x = 1` survives

- NZ-branch: `x-1 != 0`, solve `x+1 = (x+1)(x-1)`
  - `(x+1)(x-1) - (x+1) = 0`
  - `(x+1)(x-2) = 0`
  - `x = -1 or x = 2`
  - both satisfy guard

Result:
- `{ -1, 1, 2 }`

---

## Case 5. `A/B = B`

### Rule

Split on `B`.

- Z-branch: `[B = 0] -> solve(A = B)`
- NZ-branch: `[B != 0] -> solve(A = B^2)`

Detector form:

- `[D_B = 1] -> solve(A = B)`
- `[N_B = 1] -> solve(A = B^2)`

### Why sound

- If `B = 0`, then `A/B -> A`, so the equation becomes `A = B`.
- If `B != 0`, multiplying by `B` is valid and yields `A = B^2`.

### Worked example 1

Solve:
`x(x-1)/(x-1) = x-1`

Split on `x-1`.

- Z-branch: `x-1 = 0`, solve `x(x-1) = x-1`
  - guard gives `x = 1`
  - branch equation becomes `0 = 0`
  - so `x = 1` survives

- NZ-branch: `x-1 != 0`, solve `x(x-1) = (x-1)^2`
  - `x^2 - x = x^2 - 2x + 1`
  - `x = 1`
  - guard rejects it

Result:
- `[x-1 = 0] -> {1}`

### Worked example 2

Solve:
`x(x+1)/x = x`

Split on `x`.

- Z-branch: `x = 0`, solve `x(x+1) = x`
  - under `x = 0`, branch equation is true
  - so `x = 0` survives

- NZ-branch: `x != 0`, solve `x(x+1) = x^2`
  - `x = 0`
  - guard rejects it

Result:
- `[x = 0] -> {0}`

---

## Case 6. `A/B = 0`

### Rule

Split on `B`.

- Z-branch: `[B = 0] -> solve(A = 0)`
- NZ-branch: `[B != 0] -> solve(A = 0)`

Detector form:

- `[D_B = 1] -> solve(A = 0)`
- `[N_B = 1] -> solve(A = 0)`

### Why sound

In either branch the equation reduces to `A = 0`, but the guards still matter for pruning.

### Worked example 1

Solve:
`x/(x-1) = 0`

Split on `x-1`.

- Z-branch: `x-1 = 0`, solve `x = 0`
  - guard gives `x = 1`
  - contradiction

- NZ-branch: `x-1 != 0`, solve `x = 0`
  - `x = 0`
  - guard holds

Result:
- `[x-1 != 0] -> {0}`

### Worked example 2

Solve:
`(x-1)/(x-1) = 0`

Split on `x-1`.

- Z-branch: `x-1 = 0`, solve `x-1 = 0`
  - gives `x = 1`
  - branch survives

- NZ-branch: `x-1 != 0`, solve `x-1 = 0`
  - gives `x = 1`
  - guard rejects it

Result:
- `[x-1 = 0] -> {1}`

---

## Case 7. `A/B = 1`

### Rule

Split on `B`.

- Z-branch: `[B = 0] -> solve(A = 1)`
- NZ-branch: `[B != 0] -> solve(A = B)`

Detector form:

- `[D_B = 1] -> solve(A = 1)`
- `[N_B = 1] -> solve(A = B)`

### Why sound

- If `B = 0`, then `A/B -> A`, so the equation becomes `A = 1`.
- If `B != 0`, ordinary multiplication by `B` yields `A = B`.

### Worked example 1

Solve:
`x/(x-1) = 1`

Split on `x-1`.

- Z-branch: `x-1 = 0`, solve `x = 1`
  - gives `x = 1`
  - branch survives

- NZ-branch: `x-1 != 0`, solve `x = x-1`
  - contradiction

Result:
- `[x-1 = 0] -> {1}`

### Worked example 2

Solve:
`(x-1)/(x-1) = 1`

Split on `x-1`.

- Z-branch: `x-1 = 0`, solve `x-1 = 1`
  - guard gives `x = 1`
  - branch equation gives `x = 2`
  - contradiction

- NZ-branch: `x-1 != 0`, solve `x-1 = x-1`
  - identity under guard

Result:
- `[x-1 != 0] -> all such x`

Equivalent solution set:
- all `x` except `1`

---

# Merge rules

After branch solving:

1. Drop impossible branches.
2. Merge branches that produce the same solution set.
3. Preserve guards when they genuinely distinguish solutions.
4. Keep detector form available as an equivalent encoding.

---

# Practical verifier scope

A simple verifier for this draft should do exactly this:

1. accept one of the seven kernel equation schemas
2. split into Z and NZ branches
3. solve each transformed branch equation
4. filter solutions by guards
5. return guarded branch clauses and the merged solution set

That verifier does **not** need to be a full CAS.
It only needs to test whether the branch-first rules behave as specified on the kernel cases.

---

# Locked limits

This draft still excludes:

- unrestricted cancellation before branch split
- global cross-multiplication
- limit/calc semantics
- order/sign logic
- claims of full confluence or completeness

The current target is narrower:

- branch-safe equation solving
- detector-backed guards
- testable operational soundness on the kernel cases
