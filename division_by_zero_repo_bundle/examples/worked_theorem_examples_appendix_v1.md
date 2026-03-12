# Worked Theorem / Examples Appendix v1

This appendix maps the compact rule sheet in `formal_axioms_inference_rules_v1.md` to concrete worked examples.

It has two purposes:

1. make the formal rules easier to inspect,
2. show which rules already have practical support from the current Python tools.

This appendix does **not** prove completeness. It documents representative cases that are consistent with the current branch arithmetic drafts, unified solver spec, soundness notes, and experimental tools.

---

## Conventions

- `->` means rewrite.
- `[guard] -> result` means a guarded branch clause.
- `D_f := 1 - f/f` is the zero detector.
- `N_f := f/f` is the nonzero detector.
- “Verified by tool” means that the current Python toolchain already exhibits the stated behavior on representative inputs.

---

## Group A — Primitive quotient semantics

### Axiom A1. Zero-denominator erasure

**Statement.** If a denominator normalizes to `0`, then

`A / B -> A`.

### Example A1.1

Expression:

`x / 0`

Rewrite:

`x / 0 -> x`

Guard form:

`[true] -> x`

**Observed in tools:** expression branch engine.

### Example A1.2

Expression:

`(u+v) / (y-y)`

Denominator normalization:

`y-y -> 0`

So:

`(u+v)/(y-y) -> u+v`

Guard form:

`[y-y = 0] -> u+v`

Since `y-y` is identically zero, this collapses to:

`[true] -> u+v`

**Observed in tools:** branch-normal-form engine families where denominator classifies as `ZERO`.

---

### Axiom A2. NZ-branch ordinary division

**Statement.** If a denominator is classified as nonzero, ordinary division is allowed on that branch.

### Example A2.1

Expression:

`6 / 2`

Since `2` is provably nonzero:

`6/2 -> 3`

Branch form:

`[true] -> 3`

### Example A2.2

Equation:

`x / 2 = 5`

Since `2 != 0`, solve by ordinary division laws:

`x = 10`

Guard form:

`[true] -> x = 10`

**Observed in tools:** parser/equation verifier families.

---

## Group B — Detector-backed guards

### Rule B1. Zero detector

**Statement.** `D_f := 1 - f/f` behaves as a guard for `f = 0`.

### Example B1.1

Take `f := x-1`.

Then the zero branch of `x/(x-1)` may be written as:

`[x-1 = 0] -> x`

or equivalently as detector-backed notation:

`[D_(x-1) = 1] -> x`

### Example B1.2

For the denominator `(a+b)-(b+a)`, the zero branch of

`(x+1)/((a+b)-(b+a))`

may be expressed as:

`[D_((a+b)-(b+a)) = 1] -> x+1`

which simplifies further because the denominator normalizes to `0`.

---

### Rule B2. Nonzero detector

**Statement.** `N_f := f/f` behaves as a guard for `f != 0`.

### Example B2.1

For `x/(x-1)`, the NZ branch is:

`[x-1 != 0] -> x/(x-1)`

or detector-backed:

`[N_(x-1) = 1] -> x/(x-1)`

### Example B2.2

For `A/B = C`, the NZ local solver clause is:

`[B != 0] -> solve(A = BC)`

or detector-backed:

`[N_B = 1] -> solve(A = BC)`

---

## Group C — Branch firewall

### Rule C1. No NZ-only move before branch split

**Statement.** Cancellation, cross-multiplication, and inverse-style laws are NZ-only and cannot be used before branch split.

### Example C1.1

Expression:

`(x^2 - x) / x`

**Forbidden global move:**

`(x^2 - x)/x -> x-1`

This is invalid before branch split because it destroys the zero branch.

**Correct branch-first form:**

- `[x = 0] -> 0`
- `[x != 0] -> x - 1`

### Example C1.2

Equation:

`A/B = C/D`

**Forbidden global move:**

`AD = BC`

before determining the status of `B` and `D`.

**Correct branch split:**

- `[B=0, D=0] -> solve(A=C)`
- `[B=0, D!=0] -> solve(AD=C)`
- `[B!=0, D=0] -> solve(A=BC)`
- `[B!=0, D!=0] -> solve(AD=BC)`

This is the branch-safe version of two-quotient solving.

---

## Group D — Hidden-zero detection

### Rule D1. Additive symmetry zero

**Statement.** Opposite additive structures inside the denominator may normalize to `0`.

### Example D1.1

Denominator:

`(u-v) + (v-u)`

Normalize:

`u + (-v) + v + (-u) -> 0`

So:

`A / ((u-v)+(v-u)) -> A`

### Example D1.2

Denominator:

`(a+b) - (b+a)`

Normalize:

`(a+b) + (-(b+a)) -> a+b-b-a -> 0`

So:

`(x+1)/((a+b)-(b+a)) -> x+1`

**Observed in tools:** branch-normal-form engine examples.

---

### Rule D2. Product symmetry zero

**Statement.** Commutative product matching can expose zero denominators.

### Example D2.1

Denominator:

`x*y - y*x`

After canonical factor sorting:

`xy - xy -> 0`

So:

`N / (xy - yx) -> N`

### Example D2.2

Denominator:

`(a+b)*t - t*(b+a)`

Canonicalization gives identical factors, so the denominator reduces to `0`.

Thus:

`N / ((a+b)t - t(b+a)) -> N`

---

### Rule D3. Structured factor cancellation inside denominators

**Statement.** Shared factors may be extracted inside denominators solely to expose zero.

### Example D3.1

Denominator:

`A*(u-v) + A*(v-u)`

Factor `A`:

`A*((u-v)+(v-u)) -> A*0 -> 0`

So:

`N / (A(u-v)+A(v-u)) -> N`

### Example D3.2

Denominator:

`p*q - p*r - p*(q-r)`

Group first two terms:

`p(q-r) - p(q-r) -> 0`

So:

`N / (pq-pr-p(q-r)) -> N`

---

### Rule D4. Internal `/0` erasure can create hidden zero

**Statement.** Erasing `/0` inside a denominator can collapse the denominator to zero.

### Example D4.1

Denominator:

`(x/0) - x`

Inner rewrite:

`x/0 -> x`

So denominator:

`x-x -> 0`

Hence:

`A / ((x/0)-x) -> A`

### Example D4.2

Denominator:

`((p/0)-p) + ((q-r)+(r-q))`

Both parts normalize to `0`, so the total denominator is `0`.

Hence:

`A / (((p/0)-p)+((q-r)+(r-q))) -> A`

**Observed in tools:** branch-normal-form engine families.

---

## Group E — Expression branch normal form

### Rule E1. Unknown denominator produces two branches

**Statement.** If denominator status is unresolved, retain both branches.

### Example E1.1

Expression:

`x / (x-1)`

The denominator is not identically zero and not provably nonzero in the core kernel, so:

- `[x-1 = 0] -> x`
- `[x-1 != 0] -> x/(x-1)`

Detector-backed form:

- `[D_(x-1) = 1] -> x`
- `[N_(x-1) = 1] -> x/(x-1)`

**Observed in tools:** expression branch-normal-form engine.

### Example E1.2

Expression:

`(x/(x-1)) + (y/(y-y))`

The second quotient collapses immediately because `y-y -> 0`, while the first retains two branches.

So the final result is a mixed branch object with at least:

- `[x-1 = 0] -> x + y`
- `[x-1 != 0] -> x/(x-1) + y`

This demonstrates branch propagation through a larger expression.

**Observed in tools:** expression branch-normal-form engine families.

---

### Rule E2. Branch collapse by simplification

**Statement.** Different branches may collapse to the same expression and can then be merged.

### Example E2.1

Expression:

`(x/(y-y)) - x`

The quotient collapses:

`x/(y-y) -> x`

So whole expression becomes:

`x - x -> 0`

Final branch object:

`[true] -> 0`

**Observed in tools:** expression branch-normal-form engine.

### Example E2.2

Expression:

`((u+v)/(z-z)) - (u+v)`

The first term collapses to `u+v`, so the whole expression becomes `0`.

Final branch object:

`[true] -> 0`

---

## Group F — Equation kernel v1

### Rule F1. One quotient against a plain expression

**Statement.**

For `A/B = C`:

- `[B=0] -> solve(A=C)`
- `[B!=0] -> solve(A=BC)`

### Example F1.1

Equation:

`x/(x-1) = 2`

Split on `x-1`.

Zero branch:

`x = 2` under `x-1=0`, so with `x=1` this fails.

NZ branch:

`x = 2(x-1)` gives `x = 2x - 2`, hence `x = 2`.

Check guard: `2-1 != 0`, valid.

Final solution normal form:

`[x-1 != 0] -> x = 2`

### Example F1.2

Equation:

`(x+1)/((a+b)-(b+a)) = 7`

Denominator normalizes to `0`, so only zero branch survives.

Solve:

`x+1 = 7`

Hence:

`[true] -> x = 6`

**Observed in tools:** branch-normal-form engine examples.

---

### Rule F2. Plain expression against one quotient

**Statement.**

For `C = A/B`:

- `[B=0] -> solve(C=A)`
- `[B!=0] -> solve(BC=A)`

### Example F2.1

Equation:

`3 = x/(x-2)`

Zero branch:

`3 = x` under `x=2` fails.

NZ branch:

`3(x-2)=x` gives `3x-6=x`, hence `2x=6`, so `x=3`.

Guard check: `3-2 != 0`, valid.

Final:

`[x-2 != 0] -> x = 3`

### Example F2.2

Equation:

`5 = (x+2)/(y-y)`

Denominator is identically zero, so solve:

`5 = x+2`

Hence:

`[true] -> x = 3`

---

### Rule F3. Two quotients

**Statement.**

For `A/B = C/D`, split on both denominators:

- `[B=0, D=0] -> solve(A=C)`
- `[B=0, D!=0] -> solve(AD=C)`
- `[B!=0, D=0] -> solve(A=BC)`
- `[B!=0, D!=0] -> solve(AD=BC)`

### Example F3.1

Equation:

`x/(x-1) = 2/3`

Right denominator is always nonzero. Split only on `x-1` in practice.

Zero branch:

`x = 2/3` under `x=1` fails.

NZ branch:

`3x = 2(x-1)` gives `3x = 2x - 2`, hence `x = -2`.

Guard check: `-2 - 1 != 0`, valid.

Final:

`[x-1 != 0] -> x = -2`

### Example F3.2

Equation:

`(x+1)/(x-x) = (y+1)/(y-y)`

Both denominators are identically zero, so only `[B=0, D=0]` survives.

Thus solve:

`x+1 = y+1`

Hence:

`[true] -> x = y`

---

### Rule F4. Fixed-point equation `A/B = A`

**Statement.**

Split on `B`.

- `[B=0] -> true` (because `A/B -> A`)
- `[B!=0] -> solve(A = AB)`

### Example F4.1

Equation:

`x/(x-1) = x`

Zero branch:

`x=x` under `x=1`, so `x=1` is valid.

NZ branch:

`x = x(x-1)` gives `x = x^2 - x`, so `x^2 - 2x = 0`, hence `x=0` or `x=2`.

Guard check: both satisfy `x-1 != 0`.

Final:

- `[x-1 = 0] -> x = 1`
- `[x-1 != 0] -> x = 0 or x = 2`

### Example F4.2

Equation:

`(u+v)/(y-y) = u+v`

Denominator is identically zero, so the equation is automatically true.

Final:

`[true] -> true`

---

### Rule F5. Zero target `A/B = 0`

**Statement.**

- `[B=0] -> solve(A=0)`
- `[B!=0] -> solve(A=0)`

So the same algebraic equation appears on both branches, but guards may prune differently.

### Example F5.1

Equation:

`x/(x-1) = 0`

Zero branch:

`x=0` under `x=1` fails.

NZ branch:

`x=0` under `x-1 != 0` succeeds.

Final:

`[x-1 != 0] -> x = 0`

### Example F5.2

Equation:

`(x+1)/(y-y) = 0`

Denominator is identically zero, so solve:

`x+1 = 0`

Hence:

`[true] -> x = -1`

---

### Rule F6. Unit target `A/B = 1`

**Statement.**

- `[B=0] -> solve(A=1)`
- `[B!=0] -> solve(A=B)`

### Example F6.1

Equation:

`x/(x-1) = 1`

Zero branch:

`x = 1` under `x=1`, valid.

NZ branch:

`x = x-1`, impossible.

Final:

`[x-1 = 0] -> x = 1`

### Example F6.2

Equation:

`(u+1)/(v-v) = 1`

Denominator is identically zero, so solve:

`u+1 = 1`

Hence:

`[true] -> u = 0`

---

### Rule F7. Self-denominator target `A/B = B`

**Statement.**

- `[B=0] -> solve(A=B)` which becomes `solve(A=0)` on that branch
- `[B!=0] -> solve(A=B^2)`

### Example F7.1

Equation:

`x/(x-1) = x-1`

Zero branch:

`x = 0` under `x=1` fails.

NZ branch:

`x = (x-1)^2 = x^2 - 2x + 1`

So:

`x^2 - 3x + 1 = 0`

Hence:

`x = (3 ± sqrt(5))/2`

Both satisfy `x-1 != 0`.

Final:

`[x-1 != 0] -> x = (3 ± sqrt(5))/2`

### Example F7.2

Equation:

`(u+2)/(y-y) = y-y`

Since `y-y = 0`, the target is `0` and the denominator is also zero.

So solve:

`u+2 = 0`

Hence:

`[true] -> u = -2`

---

## Group G — Pruning and merging

### Rule G1. Impossible-branch pruning

**Statement.** A branch is discarded if its guard contradicts the branch-local solution.

### Example G1.1

Equation:

`x/(x-1) = 2`

Zero branch requires simultaneously:

- `x-1 = 0`, hence `x=1`
- `x = 2`

Contradiction, so the zero branch is pruned.

### Example G1.2

Equation:

`x/(x-1) = 0`

Zero branch requires:

- `x=1`
- `x=0`

Contradiction, so the zero branch is pruned.

---

### Rule G2. Branch merging

**Statement.** If two surviving branches have equivalent guards and the same result, they may be merged.

### Example G2.1

Expression:

`(x/(y-y)) - x`

Any apparent branch structure collapses to the same expression `0`, so the result becomes:

`[true] -> 0`

### Example G2.2

Equation:

`(u+v)/(z-z) = u+v`

The denominator is identically zero, so only one clause survives and no branch distinction remains:

`[true] -> true`

This is the simplest merged solution normal form.

---

## Group H — Current practical verification map

The current Python tools do not yet prove the theory, but they already cover representative behavior.

### Covered experimentally

- direct zero-denominator erasure,
- expression branch normal form for direct quotient structures,
- hidden-zero denominator classification for several additive / structured examples,
- guarded equation solving for kernel schemas,
- branch pruning on contradictory branches.

### Tool references

- `branch_equation_verifier.py`
- `branch_equation_parser_verifier.py`
- `branch_normal_form_engine.py`
- `branch_expression_normal_form_engine.py`

and their corresponding `*_output.txt` files.

---

## Group I — What this appendix does not claim

This appendix does **not** claim:

- full hidden-zero completeness,
- full expression confluence,
- unrestricted polynomial identity detection,
- analytic meaning for `/0`,
- replacement of ordinary arithmetic.

It is a worked bridge between the current formal rule sheet and the examples already driving the project.
