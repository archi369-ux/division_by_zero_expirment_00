# Solver Completeness Boundaries v1

## Purpose

This note states **what the current branch-aware solver is intended to solve**, **what it can detect heuristically**, and **what remains outside its current scope**.

The goal is not to overclaim. The current system is designed to be **branch-sound first**, and only then gradually widened.

---

## Core principle

The solver operates under the branch rule:

- if a denominator normalizes to `0`, then `A / B -> A`
- if a denominator normalizes to provably nonzero, ordinary division applies
- if neither status is provable, both branches are retained

The solver therefore returns **guarded solution objects**, not necessarily a single classical solution set.

---

## Official output form

The current solver is complete only relative to its own output form:

- `[guard] -> solution`

A solver run is considered successful if it returns a finite branch object whose branches are individually sound.

---

## What Solver Kernel v1 covers

The current kernel is intended to cover equations whose top-level structure matches one of the following forms:

1. `A / B = C`
2. `C = A / B`
3. `A / B = C / D`
4. `A / B = A`
5. `A / B = B`
6. `A / B = 0`
7. `A / B = 1`

Where `A, B, C, D` are symbolic expressions in the current language.

For these forms, the solver is intended to be:

- **branch-sound**
- **guard-explicit**
- **NZ-law disciplined**

It is **not yet claimed** to be branch-complete for all possible simplification strategies.

---

## Completeness claims we can make now

### C1. Schema completeness for kernel branch splitting

For the seven top-level equation schemas above, the solver performs the required zero/nonzero branch split for each top-level denominator.

This means the solver does not silently discard the `B = 0` case when a quotient is present at top level.

### C2. Local completeness for branch generation

If a top-level denominator is classified as:

- `ZERO`, the solver keeps the zero branch
- `NONZERO`, the solver keeps the nonzero branch
- `UNKNOWN`, the solver keeps both attempted branches

This is complete **with respect to the current denominator classifier**.

### C3. Local completeness for guarded classical solving

Within each NZ-branch, the solver is allowed to use ordinary algebra appropriate to the current schema.

Within each Z-branch, the quotient erasure rule is applied and the reduced equation is solved instead.

This is complete **for the chosen kernel rules**, not for all imaginable derived transformations.

---

## Where the current solver is heuristic

### H1. Hidden-zero detection

The denominator normalizer can detect many hidden zeros, including:

- direct cancellation forms like `x - x`
- additive symmetry forms like `(u-v) + (v-u)`
- commutative product symmetry like `xy - yx`
- bounded factor regrouping like `ab + ac - a(b+c)`

However, this detector is **not complete for all algebraic identities**.

Examples of things it may miss:

- deeper polynomial identities
- identities requiring unrestricted expansion and refactoring
- domain-sensitive facts not explicitly supplied to the engine

So hidden-zero detection is currently **strong but heuristic**, not complete.

### H2. Symbolic condition reduction

Guards such as `B = 0` and `B != 0` are preserved explicitly, and detector notation may be attached.

But the system is not yet a full condition solver for arbitrary Boolean combinations of symbolic constraints.

### H3. Branch merging

Equivalent branch results may be merged when the equivalence is obvious under the current rule set.

This is not yet a complete branch minimization algorithm.

---

## What is currently outside scope

The following are intentionally outside the present completeness claim.

### O1. Full confluence

The project does not yet claim that all valid rewrite orders produce the same final symbolic expression.

The stronger current target is:

- stable branch classification
- stable guarded output shape

### O2. Full hidden-zero completeness

The system does not claim to detect every denominator that is mathematically equal to zero.

### O3. Arbitrary equation completeness

The system does not yet claim completeness for arbitrary equations containing nested quotients, multiple interacting branch conditions, or unrestricted algebraic transformations.

### O4. Domain-general completeness

The current solver does not claim complete behavior simultaneously over:

- reals
- complexes
- rings with zero divisors
- arbitrary algebraic structures

Any completeness claim must always be domain-qualified.

### O5. Analytic completeness

No completeness claim is made for:

- limits
- continuity
- differentiability
- integration
- asymptotic reasoning

---

## Safe statement of current scope

A good current statement is:

> The current solver is branch-sound for the kernel quotient schemas and operationally complete with respect to its own guarded branch-generation rules. Its hidden-zero detection and symbolic guard reduction remain intentionally incomplete.

This is the right level of honesty.

---

## Near-term completeness targets

The next realistic milestones are:

### T1. Expression-side branch completeness for one top-level quotient

Given a single top-level quotient expression, prove that the engine returns all branch cases required by the current zero/nonzero classifier.

### T2. Equation-side kernel completeness

For the seven kernel equation schemas, prove that every branch required by the current classifier is generated exactly once and solved by the corresponding local rule.

### T3. Finite hidden-zero family completeness

Choose a finite family of denominator patterns and prove completeness on that family only.

Example target families:

- duplicate cancellation
- additive symmetry
- common-factor distributive regrouping

This is a much better target than pretending to solve all hidden-zero identities.

---

## Review checklist

When evaluating a new solver claim, ask:

1. Is the claim about **soundness** or **completeness**?
2. Is it about **all expressions**, or only a **restricted schema**?
3. Is the domain fixed?
4. Does the claim rely on hidden-zero detection being complete?
5. Is the output a single expression, or a guarded branch object?

If these are not specified, the claim is too vague.

---

## Bottom line

The solver is currently strongest when described as:

- **branch-sound**
- **guard-explicit**
- **schema-complete on the kernel forms relative to the current classifier**
- **heuristic, not complete, on hidden-zero discovery**

That is the correct boundary for v1.
