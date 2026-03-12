# Branch-Local Soundness Notes v1

## Status

This note records the first soundness claims for the current branch arithmetic framework.
It is not a completeness proof and it is not a full confluence proof.
Its purpose is narrower:

1. define the official solution object,
2. justify the first solver rules branch by branch,
3. connect branch guards to detector guards,
4. justify pruning of impossible branches.

The semantic base is the published **Zero-Set Detector Algebra** note:

- primitive rule: `a/0 := a`,
- ordinary division when denominator is nonzero,
- bottom-up evaluation,
- detector definitions `D_f := 1 - f/f` and `N_f := f/f`,
- safe rewriting only after zero/nonzero status is resolved.

## 1. Ambient assumptions

Let `K` be a fixed field or integral domain, typically `Q` or `R`.
All ordinary arithmetic is classical except for the primitive rule

- if `b != 0`, then `a/b` is ordinary division,
- if `b = 0`, then `a/0 := a`.

Evaluation is bottom-up: subexpressions are evaluated first; division is applied only after denominator evaluation.

## 2. Official solution object

A **solution clause** is an item of the form

`[G] -> S`

where:

- `G` is a guard condition,
- `S` is a classical solution statement valid under `G`.

A **solution normal form** is a finite set of such clauses.

Examples:

- `[B = 0] -> solve(A = C)`
- `[B != 0] -> solve(A = B*C)`
- `[x = 0] -> {}` and `[x != 0] -> {x = 2}`

This object is official. Solver output is not required to collapse to one classical equation.

## 3. Branch firewall

The main quotient firewall is now a standing rule:

> No algebraic step that requires a denominator to be nonzero may be used before branch split on that denominator.

Consequences:

- cancellation across the main `/` is NZ-only,
- cross-multiplication is NZ-only,
- multiplying both sides by a denominator is NZ-only,
- factor removal across the main quotient is NZ-only.

This firewall is part of the soundness conditions, not a convenience.

## 4. Detector-backed guards

For any expression `f`, define:

- `D_f := 1 - f/f`
- `N_f := f/f`

By the semantic base:

- if `f = 0`, then `f/f = 0`, so `D_f = 1` and `N_f = 0`,
- if `f != 0`, then `f/f = 1`, so `D_f = 0` and `N_f = 1`.

Therefore:

- `D_f = 1` iff `f = 0`,
- `N_f = 1` iff `f != 0`,
- `D_f + N_f = 1`,
- `D_f N_f = 0`.

So branch guards of the form `[f = 0]` and `[f != 0]` may be written detector-first as

- `[D_f = 1]`
- `[N_f = 1]`

without changing branch meaning.

## 5. Guard agreement lemma

### Lemma 5.1
For every evaluated expression `f`, the branch guard `[f = 0]` is equivalent to the detector guard `[D_f = 1]`.

**Proof.**
If `f = 0`, then by the primitive rule `f/f = 0`, hence `D_f = 1 - 0 = 1`.
If `f != 0`, then `f/f = 1`, hence `D_f = 0`.
So `[f = 0]` and `[D_f = 1]` hold on exactly the same points. ∎

### Lemma 5.2
For every evaluated expression `f`, the branch guard `[f != 0]` is equivalent to the detector guard `[N_f = 1]`.

**Proof.**
Immediate from the same case split. ∎

These lemmas justify the policy:

> keep the branch firewall, but express branch guards with detectors whenever possible.

## 6. Branch-local soundness schema

Let an equation contain one or more top-level quotients.
The sound solver works in this order:

1. reduce each relevant denominator to a branch status,
2. split into branches,
3. solve each branch using only rules valid under its guard,
4. prune contradictory guards,
5. collect surviving clauses.

A solver rule is **branch-locally sound** if, on each branch, the transformed equation is equivalent to the original equation under that branch guard.

## 7. Soundness of the basic one-quotient rule

Consider

`A/B = C`.

### Rule S1
Return the two branch clauses:

- `[B = 0] -> solve(A = C)`
- `[B != 0] -> solve(A = B*C)`

### Proposition 7.1
Rule S1 is branch-locally sound.

**Proof.**
On the branch `B = 0`, the primitive rule gives `A/B = A`, so the equation becomes exactly `A = C`.
On the branch `B != 0`, division is ordinary, so `A/B = C` is classically equivalent to `A = B*C`.
No step crosses the firewall, because the NZ-only move is used only on the NZ branch. ∎

### Symmetric version
For `C = A/B`, return:

- `[B = 0] -> solve(C = A)`
- `[B != 0] -> solve(B*C = A)`

The proof is identical.

## 8. Soundness of the two-quotient rule

Consider

`A/B = C/D`.

### Rule S2
Return four branch clauses:

- `[B = 0 and D = 0] -> solve(A = C)`
- `[B = 0 and D != 0] -> solve(A*D = C)`
- `[B != 0 and D = 0] -> solve(A = B*C)`
- `[B != 0 and D != 0] -> solve(A*D = B*C)`

### Proposition 8.1
Rule S2 is branch-locally sound.

**Proof.**
Case split on the pair `(B,D)`:

1. If `B = 0` and `D = 0`, then `A/B = A` and `C/D = C`, so the equation becomes `A = C`.
2. If `B = 0` and `D != 0`, then `A/B = A` while `C/D` is ordinary. Thus `A = C/D`, which is classically equivalent to `A*D = C` because `D != 0` holds on this branch.
3. If `B != 0` and `D = 0`, then `A/B` is ordinary and `C/D = C`. Thus `A/B = C`, which is classically equivalent to `A = B*C` because `B != 0` holds on this branch.
4. If `B != 0` and `D != 0`, both sides are ordinary quotients, so classical cross-multiplication is valid and gives `A*D = B*C`.

Every classical step is guarded by the appropriate nonzero hypotheses. ∎

## 9. Soundness of selected kernel equations

### 9.1 Equation `A/B = A`

Return:

- `[B = 0] -> true`
- `[B != 0] -> solve(A = A*B)`

Under `B = 0`, `A/B` rewrites to `A`, so the equation becomes `A = A`, which is always true.
Under `B != 0`, the equation is ordinary and equivalent to `A = A*B`.
Therefore the rule is branch-locally sound.

If the ambient domain is an integral domain, the NZ branch can be refined:

`A = A*B` iff `A*(B-1) = 0`, hence `A = 0` or `B = 1`.

So a sharper output is:

- `[B = 0] -> true`
- `[B != 0] -> solve(A = 0 or B = 1)`

### 9.2 Equation `A/B = 0`

Return:

- `[B = 0] -> solve(A = 0)`
- `[B != 0] -> solve(A = 0)`

This can be merged to `[true] -> solve(A = 0)`.

**Reason.**
On `B = 0`, `A/B` becomes `A`, so the equation is `A = 0`.
On `B != 0`, ordinary division implies `A/B = 0` iff `A = 0`.
Thus both branches agree.

### 9.3 Equation `A/B = 1`

Return:

- `[B = 0] -> solve(A = 1)`
- `[B != 0] -> solve(A = B)`

This is branch-locally sound by the same split.

### 9.4 Equation `A/B = B`

Return:

- `[B = 0] -> solve(A = 0)`
- `[B != 0] -> solve(A = B^2)`

Again, the first branch uses erasure and the second uses ordinary division.

## 10. Impossible-branch pruning

A branch clause may be discarded only when its guard is contradictory in the chosen ambient domain.

Examples over `R`:

- `[x - x != 0]` is impossible,
- `[2 = 0]` is impossible,
- `[D_f = 1 and N_f = 1]` is impossible because `D_f N_f = 0`.

### Lemma 10.1
Pruning a contradictory branch preserves the full solution set.

**Proof.**
A contradictory guard is true at no assignment. Therefore the clause contributes no actual solutions. Removing it changes nothing. ∎

This justifies branch pruning after branch construction.

## 11. Merge lemma

If two surviving branches have equivalent solution content, they may be merged by guard union.

Example:

- `[B = 0] -> solve(A = 0)`
- `[B != 0] -> solve(A = 0)`

merge to:

- `[true] -> solve(A = 0)`

### Lemma 11.1
Merge by guard union is sound when the branch conclusions are identical.

**Proof.**
The set of assignments satisfying either original clause is exactly the set satisfying the union guard with the shared conclusion. ∎

## 12. Worked soundness checks

### Example 12.1
Equation: `x/(x-1) = 2`

- Z branch: `x - 1 = 0`, so `x = 1`. The equation becomes `x = 2`, hence `1 = 2`, impossible.
- NZ branch: `x - 1 != 0`. Solve `x = 2(x-1)`, so `x = 2`.

Final solution normal form:

- `[x - 1 != 0] -> {x = 2}`

This is sound because the Z branch was contradictory after substitution.

### Example 12.2
Equation: `x/(x-x) = 3`

- Denominator evaluates to `0` on every assignment.
- Only the Z branch survives.
- Solve `x = 3`.

Final output:

- `[true] -> {x = 3}`

### Example 12.3
Equation: `x/(x-1) = x`

- Z branch: `x = 1`, equation becomes `x = x`, so branch survives.
- NZ branch: solve `x = x(x-1)`, i.e. `x = x^2 - x`, hence `x(x-2)=0`.
  Together with `x != 1`, this yields `x = 0` or `x = 2`.

Final output:

- `[x = 1] -> {x = 1}`
- `[x != 1] -> {x = 0 or x = 2}`

## 13. What is proved and what is not

### Proved here

- detector guards match zero/nonzero branch guards,
- one-quotient and two-quotient kernel rules are branch-locally sound,
- contradictory branches may be pruned,
- identical branch conclusions may be merged.

### Not proved here

- completeness of the solver,
- global confluence of all rewrites,
- termination of every future normalization extension,
- analytic or order-theoretic meaning.

## 14. Review-ready summary

The current theory is sound in the following restricted but important sense:

1. branch split happens before NZ-only algebra,
2. each solver rule is justified separately on each branch,
3. detector guards are semantically equivalent to branch guards,
4. impossible branches contribute no solutions and may be removed,
5. identical conclusions may be merged without loss.

This is enough to support **Equation Solver Draft v1** and **Unified Branch Solver Spec v1** as a consistent branch-local solving framework.
