# Solver Semantics v1

## 1. Purpose

This document defines the **equation solving semantics** for the guarded
division-by-zero framework.

The solver must respect the following principles:

-   branch-first evaluation
-   branch firewall preservation
-   denominator safety
-   extensional correctness over the real numbers

Domain: **Real numbers ℝ**.

This document works with:

-   `core_semantics_v1.md`
-   `rewrite_rules_v1.md`
-   `branch_merge_and_equivalence_v1.md`

------------------------------------------------------------------------

# 2. Solver Philosophy

Classical algebra often solves equations by **clearing denominators** or
**cross multiplication**.

Example:

    a/b = c
    → a = bc

However this step **assumes `b ≠ 0`**.

In the guarded framework such assumptions must **never be made
globally**.

Instead the solver operates by:

1.  detecting denominators
2.  branching on their status
3.  solving each branch under its guard

This guarantees sound handling of zero denominators.

------------------------------------------------------------------------

# 3. Solver Input

A solver input is an equation:

    E1 = E2

where `E1` and `E2` are symbolic expressions.

Example:

    x/x = 1

------------------------------------------------------------------------

# 4. Protected Quotients

Any quotient whose denominator status is unknown is treated as a
**protected quotient**.

Examples:

    x/x
    (x²-1)/(x-1)
    (x+1)/y

Protected quotients trigger **branch analysis**.

------------------------------------------------------------------------

# 5. Denominator Detection

Before solving, the solver must identify all denominators appearing in
the equation.

Example:

    (x²-1)/(x-1) = 3

Detected denominator:

    x - 1

------------------------------------------------------------------------

# 6. Branch Generation

For each detected denominator `d`, the solver generates branches:

    [d = 0]
    [d ≠ 0]

Example:

    x/x = 1

Branches:

    [x = 0]
    [x ≠ 0]

------------------------------------------------------------------------

# 7. Branch Evaluation

Each branch is solved independently under its guard.

Example:

    x/x = 1

Branches:

    [x = 0] -> x = 1
    [x ≠ 0] -> 1 = 1

Evaluation:

    [x = 0] -> contradiction
    [x ≠ 0] -> true

------------------------------------------------------------------------

# 8. Branch Simplification

Within each branch, guarded rewrites from `rewrite_rules_v1.md` may be
applied.

Example:

    [x ≠ 0] -> x/x → 1

The branch equation simplifies accordingly.

------------------------------------------------------------------------

# 9. Branch Solution Extraction

Each surviving branch yields a solution set constrained by its guard.

Example:

    [x ≠ 0] -> true

Solution:

    x ≠ 0

------------------------------------------------------------------------

# 10. Impossible Branch Removal

Branches producing contradictions are discarded.

Example:

    [x = 0] -> 0 = 1

This branch is impossible and removed.

------------------------------------------------------------------------

# 11. Solution Merge

Remaining branches are merged using rules from:

    branch_merge_and_equivalence_v1.md

Example:

    [x = 0] -> x = 0
    [x ≠ 0] -> x = 2

Final solution set:

    x = 0 ∨ x = 2

------------------------------------------------------------------------

# 12. Solver Output

The solver output is a **solution object** consisting of guarded
solutions.

General form:

    [G1] -> S1
    [G2] -> S2
    ...

Example:

    [x ≠ 0] -> solution

------------------------------------------------------------------------

# 13. Solver Algorithm

The solving procedure follows this sequence:

1.  Parse equation `E1 = E2`
2.  Detect denominators
3.  Classify denominator status
4.  Generate branches if status unknown
5.  Apply guarded rewrites inside each branch
6.  Solve resulting equations
7.  Remove impossible branches
8.  Merge equivalent branches
9.  Return guarded solution set

------------------------------------------------------------------------

# 14. Example 1 --- Self Quotient

Solve:

    x/x = 1

Branch split:

    [x = 0] -> x = 1
    [x ≠ 0] -> 1 = 1

Evaluation:

    [x = 0] -> impossible
    [x ≠ 0] -> true

Final solution:

    x ≠ 0

------------------------------------------------------------------------

# 15. Example 2 --- Hidden Zero Denominator

Solve:

    (x² - 1)/(x - 1) = 3

Denominator:

    x - 1

Branches:

    [x = 1]
    [x ≠ 1]

Branch evaluation:

    [x = 1] -> 0 = 3 (impossible)
    [x ≠ 1] -> x + 1 = 3

Solve second branch:

    x = 2

Final solution:

    x = 2

------------------------------------------------------------------------

# 16. Example 3 --- Multiple Denominators

Solve:

    x/(x-1) = 2/x

Detected denominators:

    x
    x - 1

Branches:

    [x = 0]
    [x ≠ 0]
    [x = 1]
    [x ≠ 1]

Branches combine into guarded cases.

Each case is solved independently.

------------------------------------------------------------------------

# 17. Solver Soundness Guarantees

The solver guarantees:

### 17.1 Firewall safety

No illegal denominator assumptions are made globally.

### 17.2 Guard correctness

All algebraic rewrites occur under guards that justify them.

### 17.3 Extensional correctness

Solutions satisfy the equation for all real inputs matching the guard.

------------------------------------------------------------------------

# 18. Design Intent

The solver is designed to:

-   prevent classical algebra errors caused by hidden zero denominators
-   maintain consistent behavior with the primitive rule `a / 0 := a`
-   produce deterministic guarded solution sets

It should be understood as a **branch-aware symbolic solver**, not a
classical algebra solver.
