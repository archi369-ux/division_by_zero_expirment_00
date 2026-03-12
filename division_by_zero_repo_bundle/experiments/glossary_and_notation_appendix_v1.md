# Glossary and Notation Appendix v1

This appendix fixes the core terms and notation used across the branch arithmetic, detector algebra, normalization, and solver documents.

The goal is not to introduce new rules. The goal is to make the existing rules readable, consistent, and reviewable.

---

## 1. Purpose of this appendix

This project uses several terms in a nonstandard way:

- division by zero is not treated as inverse multiplication,
- branch conditions are first-class objects,
- detectors can stand in for zero/nonzero guards,
- solver output is guarded rather than forced into a single classical expression.

Because of that, vocabulary drift is dangerous.

This appendix fixes the intended meanings.

---

## 2. Core symbols

### 2.1 Equality and rewrite

Two notations are used for different purposes.

- `=` means equality inside a branch, or equality of mathematical statements.
- `->` means a legal rewrite step in the formal system.

Examples:

- `a / 0 -> a`
- if `B != 0`, then `A / B = C` implies `A = BC`

The rule `a / 0 := a` is therefore best read operationally as:

- `a / 0 -> a`

not as an inverse-division statement.

### 2.2 Definition marker

- `:=` means “is defined as.”

Examples:

- `D_f := 1 - f/f`
- `N_f := f/f`

### 2.3 Guard arrow

The project writes guarded outputs in the form:

- `[guard] -> expression`
- `[guard] -> solution`

This means:

- under the stated guard, the branch expression or branch solution is valid.

---

## 3. Core operational objects

### 3.1 Quotient

A **quotient** is any expression of the form:

- `A / B`

where `A` is the numerator and `B` is the denominator.

### 3.2 Main quotient

The **main quotient** is the quotient currently being evaluated or solved at the active step.

This matters because the branch firewall protects the main quotient from NZ-only algebra before branch split.

### 3.3 Nested quotient

A **nested quotient** is a quotient that appears strictly inside another expression, including inside a denominator.

Example:

- in `A / ((x/0) - x)`, the subexpression `x/0` is a nested quotient.

Nested quotients may be normalized inside denominators according to the denominator engine, but that does not license cancellation across the main quotient.

---

## 4. Branch vocabulary

### 4.1 Branch

A **branch** is one guarded case produced by the system after denominator classification or equation splitting.

A branch always has:

- a guard, and
- a branch-local expression or solution.

### 4.2 Zero branch

The **zero branch** is the branch in which the relevant denominator is taken to normalize to zero.

For a quotient `A / B`, the zero branch gives:

- if `B -> 0`, then `A / B -> A`

### 4.3 NZ-branch

The **NZ-branch** is the branch in which the relevant denominator is taken to be nonzero.

On this branch, ordinary division laws are allowed.

### 4.4 Branch split

A **branch split** is the operation that replaces a single quotient-bearing object by its guarded zero/nonzero cases.

For `A / B`, branch split yields:

- `[B = 0] -> A`
- `[B != 0] -> A / B`

unless one branch is ruled out by classification.

### 4.5 Branch product

The **branch product** is the combined case analysis obtained when the left-hand side and right-hand side of an equation are both already in branch normal form.

If the left side has branches `L_i` and the right side has branches `R_j`, then the equation is solved over all compatible pairs `(L_i, R_j)`.

### 4.6 Branch pruning

**Branch pruning** is removal of impossible or contradictory branches.

Examples:

- `[x - x != 0]` is impossible
- over the reals, `[x^2 + 1 = 0]` is impossible if a real-domain module is active

### 4.7 Branch merging

**Branch merging** is combining branches that have equivalent outputs and compatible guards.

Example shape:

- `[G1] -> E`
- `[G2] -> E`

may be merged into a broader guard if the logic permits it.

---

## 5. Normal forms

### 5.1 Branch Normal Form (BNF)

**Branch Normal Form** is the official output form for expressions in the current theory.

It is a finite set of guarded clauses:

- `[guard_1] -> expression_1`
- `[guard_2] -> expression_2`
- ...

BNF does not force one final expression when the theory naturally produces guarded alternatives.

### 5.2 Solution Normal Form (SNF)

**Solution Normal Form** is the official output form for equation solving.

It is a finite set of guarded solution clauses:

- `[guard_1] -> solution_1`
- `[guard_2] -> solution_2`
- ...

### 5.3 Canonical form

A **canonical form** is a fixed internal representation used for reliable matching.

Typical canonicalization steps include:

- sorting additive terms,
- sorting multiplicative factors,
- normalizing signs,
- rewriting subtraction as addition of negatives,
- flattening nested sums and products.

Canonical form is used for matching and classification, not as a claim of full symbolic simplification.

---

## 6. Denominator classification vocabulary

### 6.1 Denominator normalization

**Denominator normalization** is the restricted rewrite process applied inside denominators before branch split.

Its purpose is not full algebraic simplification.

Its purpose is to classify a denominator as:

- `ZERO`
- `NONZERO`
- `UNKNOWN`

### 6.2 Classifier

The **classifier** is the procedure that assigns one of the three statuses above to a normalized denominator.

### 6.3 ZERO

A denominator is in status **ZERO** when it reduces to literal `0` under the allowed denominator rules.

### 6.4 NONZERO

A denominator is in status **NONZERO** when it is provably nonzero by the currently active nonzero rules.

### 6.5 UNKNOWN

A denominator is in status **UNKNOWN** when the current engine proves neither zero nor nonzero.

This is a conservative output, not a failure.

---

## 7. Hidden-zero vocabulary

### 7.1 Hidden zero

A **hidden zero** is a denominator that is not written literally as `0` but reduces to `0` under allowed normalization.

Examples:

- `(u-v) + (v-u)`
- `x*y - y*x`
- `a*b + a*c - a*(b+c)`
- `(x/0) - x`

### 7.2 Hidden-zero module

A **hidden-zero module** is an optional structured extension of denominator normalization.

Currently discussed modules include:

- **HZ-1** — additive hidden zeros
- **HZ-2** — pairwise factor-aware hidden zeros
- **HZ-3** — bounded multi-term distributive regrouping

### 7.3 Bounded regrouping

**Bounded regrouping** means factor grouping is allowed only when it decreases complexity or exposes immediate cancellation.

This prevents oscillation between grouped and expanded forms.

---

## 8. Detector vocabulary

### 8.1 Detector

A **detector** is an algebraic object that encodes a zero/nonzero test.

The main detectors are:

- `D_f := 1 - f/f`
- `N_f := f/f`

under the project’s primitive rule `a/0 := a`.

### 8.2 Zero detector

`D_f` is the **zero detector** for `f`.

Intended meaning:

- `D_f = 1` iff `f = 0`
- `D_f = 0` iff `f != 0`

### 8.3 Nonzero detector

`N_f` is the **nonzero detector** for `f`.

Intended meaning:

- `N_f = 1` iff `f != 0`
- `N_f = 0` iff `f = 0`

### 8.4 Detector-backed guard

A **detector-backed guard** is a branch condition written using detectors when possible.

Examples:

- guard `B = 0` may be written as `D_B = 1`
- guard `B != 0` may be written as `N_B = 1`

These are preferred when the condition is directly of zero/nonzero type.

### 8.5 Detector agreement

**Detector agreement** means the informal branch guard and the detector form describe the same branch condition.

Examples:

- `[B = 0]` agrees with `[D_B = 1]`
- `[B != 0]` agrees with `[N_B = 1]`

---

## 9. Solver vocabulary

### 9.1 Branch-local solving

**Branch-local solving** means solving an equation only after the relevant denominator status has already been fixed by the branch guard.

### 9.2 Solver kernel

The **solver kernel** is the restricted family of equation schemas currently treated by the draft rules, including:

- `A/B = C`
- `C = A/B`
- `A/B = C/D`
- `A/B = A`
- `A/B = B`
- `A/B = 0`
- `A/B = 1`

### 9.3 Branch-local soundness

A solver rule is **branch-locally sound** if it is valid under the guard assumed for that branch.

Example:

- on the NZ-branch, solving `A/B = C` by writing `A = BC` is sound
- on the zero branch, solving `A/B = C` by writing `A = C` is sound

### 9.4 Completeness boundary

A **completeness boundary** is an explicit statement describing what the current solver is not yet claiming to solve or classify completely.

---

## 10. Firewall vocabulary

### 10.1 Branch firewall

The **branch firewall** is the rule:

> no simplification requiring denominator nonzero may be used before branch split.

This is one of the core axioms of the current framework.

### 10.2 NZ-only rule

An **NZ-only rule** is any rule whose soundness depends on the denominator being nonzero.

Examples:

- cancellation across the main quotient
- cross-multiplication
- inverse-style division laws
- multiplying both sides by a denominator

These are forbidden before the relevant NZ-branch is active.

### 10.3 Main-quotient cancellation

**Main-quotient cancellation** means cancelling factors across the currently active quotient.

Example:

- `(x^2-x)/x -> x-1`

This is forbidden before branch split, because it destroys the zero branch `x=0`.

---

## 11. Expression and equation levels

### 11.1 Expression-level engine

The **expression-level engine** converts expressions into Branch Normal Form.

### 11.2 Equation-level engine

The **equation-level engine** solves equations by first converting both sides to Branch Normal Form, then solving over the branch product.

### 11.3 Unified solver

The **unified solver** is the architecture in which expression branching is primary and equation solving is secondary.

In short:

1. branch each side,
2. pair compatible branches,
3. solve locally,
4. prune contradictions,
5. merge when appropriate.

---

## 12. Complexity and legality vocabulary

### 12.1 Legal rewrite

A **legal rewrite** is any rewrite allowed by the current phase of the system.

A rewrite can be legal in denominator normalization but illegal before main branch split if it assumes NZ status.

### 12.2 Complexity decrease

A rewrite is said to **decrease complexity** if it reduces one of the monitored structural measures, such as:

- number of top-level additive siblings,
- number of unmatched opposite pairs,
- number of subtraction nodes,
- number of unsorted factors/terms,
- total syntax size.

### 12.3 One-way rule

A **one-way rule** is a rewrite that is oriented in one direction only to prevent loops.

Example:

- `a*b + a*c -> a*(b+c)` may be allowed in a bounded hidden-zero module
- the reverse expansion is forbidden in the kernel

---

## 13. Scope vocabulary

### 13.1 Kernel

The **kernel** is the smallest set of core rules the project is currently willing to defend as foundational.

### 13.2 Module

A **module** is an optional extension layered on top of the kernel.

Examples:

- hidden-zero modules
- domain-sensitive nonzero modules
- future power rules

### 13.3 Domain module

A **domain module** is a rule layer that depends on the chosen domain, such as reals or complexes.

Example:

- over the reals, `x^2 + 1` may be classified as NONZERO
- over the complexes, that same claim is false

So such rules are modular, not kernel-level.

---

## 14. Preferred notation summary

Use these by default.

### For rewrites

- `A / 0 -> A`
- `x - x -> 0`
- `ab + ac -> a(b+c)` only if allowed by the active hidden-zero module

### For branches

- `[B = 0] -> A`
- `[B != 0] -> A/B`

### For detector-backed branches

- `[D_B = 1] -> A`
- `[N_B = 1] -> A/B`

### For solutions

- `[guard] -> {solution set}`
- `[x-1 = 0] -> {x = 1}`
- `[x-1 != 0] -> {x = 2}`

---

## 15. Interpretation note

This glossary fixes usage inside the current project.

It does not claim that these terms match standard algebraic usage outside the project.

In particular:

- “division” at zero is operational, not inverse,
- “solution” is guarded rather than absolute,
- “normal form” means project-defined branch normal form, not universal canonicality.

That difference should be stated openly whenever the project is presented publicly.
