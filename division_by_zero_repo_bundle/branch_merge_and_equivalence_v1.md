# Branch Merge and Equivalence v1

## 1. Scope

This document defines how **branch objects** are compared, merged, and
canonicalized in the division-by-zero experimental framework.

The goal is to ensure that branch objects:

-   represent **deterministic piecewise behavior**
-   preserve the **branch firewall**
-   remain **extensional over the real numbers**
-   admit a **canonical representation**

All definitions in this document assume the **domain of real numbers
ℝ**.

------------------------------------------------------------------------

# 2. Branch Object

A **branch** has the form:

    [G] -> E

where:

-   `G` is a **guard** (boolean condition over ℝ)
-   `E` is an **expression**

Example:

    [x = 0] -> 5
    [x ≠ 0] -> x/x

------------------------------------------------------------------------

# 3. Branch Object Semantics

A **branch object** is a **finite set of branches**.

Semantically:

-   it is an **unordered set**
-   order does **not affect meaning**
-   duplicate branches collapse

Operationally:

-   branches are **sorted into a canonical order** for deterministic
    output.

Thus:

    [x = 0] -> 5
    [x ≠ 0] -> 7

is equivalent to:

    [x ≠ 0] -> 7
    [x = 0] -> 5

------------------------------------------------------------------------

# 4. Guard Language

Guards may be written using:

### Equation / inequality form (user-facing)

    x = 0
    x ≠ 0
    x ≥ 0
    x < 1

### Detector form (internal)

    D_f = 1
    N_f = 1

where:

    D_f = 1  ⇔  f = 0
    N_f = 1  ⇔  f ≠ 0

Detectors and equation guards are **fully interchangeable**.

However, **canonical output form prefers equation / inequality guards**
whenever possible.

------------------------------------------------------------------------

# 5. Expression Equality

Expressions inside branches are compared **relative to their guard**.

Two branch expressions are equivalent if:

    G ⊢ (E1 = E2)

over the real numbers.

Example:

    [x ≠ 0] -> x/x
    [x ≠ 0] -> 1

These are considered equivalent because:

    x ≠ 0 ⇒ x/x = 1

------------------------------------------------------------------------

# 6. Impossible Branches

Branches are removed if their guards are **inconsistent over ℝ**.

Three kinds of contradiction are recognized:

### Literal contradiction

    x = 0 ∧ x ≠ 0

### Detector contradiction

    D_x = 1 ∧ N_x = 1

### Simple algebraic contradiction

Example:

    x = 1 ∧ x - 1 ≠ 0

Such branches are **discarded during canonicalization**.

------------------------------------------------------------------------

# 7. Overlap Consistency Rule

If two branches have **overlapping guards**, their outputs must agree on
the overlap.

Formally:

If

    [G1] -> E1
    [G2] -> E2

and

    G1 ∧ G2

is satisfiable over ℝ, then the system must verify:

    G1 ∧ G2 ⊢ E1 = E2

If this condition fails:

➡ the branch object is **rejected as ambiguous**.

Example (invalid):

    [x ≥ 0] -> 1
    [x ≤ 0] -> 2

because at `x = 0` both guards hold but outputs differ.

------------------------------------------------------------------------

# 8. Branch Merge Law

Branches may be merged **after branch-local normalization**.

Given:

    [G1] -> E1
    [G2] -> E2

First normalize expressions under their guards:

    E1' = normalize(E1 | G1)
    E2' = normalize(E2 | G2)

Then attempt to find a **safe representative expression** `E*`.

The merge is allowed only if:

    G1 ⊢ (E* = E1')
    G2 ⊢ (E* = E2')

and `E*` is valid under the merged guard:

    G* = G1 ∨ G2

Result:

    [G*] -> E*

------------------------------------------------------------------------

# 9. Safe Representative Requirement

The merged expression must remain **valid on the merged guard**.

Example:

Initial branches:

    [x = 0] -> 1
    [x ≠ 0] -> x/x

After normalization:

    [x = 0] -> 1
    [x ≠ 0] -> 1

Safe merge:

    [true] -> 1

Unsafe merge:

    [true] -> x/x

because `x/x` is not valid at `x = 0`.

------------------------------------------------------------------------

# 10. Conservative Fallback

If no safe representative expression exists, branches are **not
merged**.

This implements the policy:

    Option B: normalize and search for safe representative
    Fallback C: merge only if normalized outputs are identical

------------------------------------------------------------------------

# 11. Absorption Rule

If one guard logically implies another, the stronger branch absorbs the
weaker.

Example:

    [x ≠ 0] -> 1
    [x > 0] -> 1

Since

    x > 0 ⇒ x ≠ 0

the second branch is redundant.

Result:

    [x ≠ 0] -> 1

------------------------------------------------------------------------

# 12. Redundant Branch Removal

A branch is redundant if another branch already guarantees the same
output for all inputs satisfying its guard.

Example:

    [true] -> 5
    [x = 0] -> 5

The second branch is removed.

Result:

    [true] -> 5

------------------------------------------------------------------------

# 13. Canonicalization Pipeline

Every branch object is normalized using the following pipeline:

1.  **Normalize guards**
2.  **Remove impossible branches**
3.  **Normalize expressions under their guards**
4.  **Apply merge law**
5.  **Simplify merged guards**
6.  **Apply absorption**
7.  **Remove redundant branches**
8.  **Sort branches into canonical order**

------------------------------------------------------------------------

# 14. Equality of Branch Objects

Two branch objects are considered equal if they produce the **same
behavior for every real input**.

Operationally this is determined by comparing their **canonicalized
branch sets**.

------------------------------------------------------------------------

# 15. Example Canonical Forms

### Example 1

Input:

    [x = 0] -> 1
    [x ≠ 0] -> x/x

Canonical form:

    [true] -> 1

------------------------------------------------------------------------

### Example 2

Input:

    [x ≥ 0] -> 1
    [x ≤ 0] -> 1

Canonical form:

    [true] -> 1

------------------------------------------------------------------------

### Example 3

Input:

    [x ≥ 0] -> 1
    [x ≤ 0] -> 2

Result:

    Rejected: ambiguous branch overlap

------------------------------------------------------------------------

# 16. Design Intent

These rules enforce:

-   deterministic piecewise semantics
-   safe merging of branches
-   preservation of branch-local algebra
-   canonical representation of branch objects
