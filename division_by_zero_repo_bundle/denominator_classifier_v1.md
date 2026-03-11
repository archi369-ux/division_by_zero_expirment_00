# Denominator Classifier v1

## 1. Purpose

This document defines how the system determines whether a denominator
is:

-   ZERO
-   NONZERO
-   UNKNOWN

The classifier is a **conservative decision procedure** used by the
guarded algebra framework to support:

-   branch generation
-   rewrite safety
-   solver correctness
-   firewall preservation

Domain: **Real numbers ℝ**.

This document works together with:

-   `core_semantics_v1.md`
-   `rewrite_rules_v1.md`
-   `solver_semantics_v1.md`
-   `branch_merge_and_equivalence_v1.md`

------------------------------------------------------------------------

# 2. Classifier Philosophy

The denominator classifier must **never guess**.

It must only declare:

    ZERO

or

    NONZERO

when this can be **proven**.

Otherwise the result must be:

    UNKNOWN

This guarantees that the branch firewall is never violated.

------------------------------------------------------------------------

# 3. Classification States

Every denominator `d` belongs to exactly one of three states:

  State     Meaning
  --------- --------------------------
  ZERO      Proven equal to 0
  NONZERO   Proven not equal to 0
  UNKNOWN   Cannot yet be determined

------------------------------------------------------------------------

# 4. ZERO Detection Rules

A denominator is classified as **ZERO** if the system can prove it
simplifies to `0`.

### 4.1 Direct zero

    0 → ZERO

### 4.2 Self subtraction

    x - x → 0

Example:

    (x - x) → ZERO

### 4.3 Sum of zeros

If all terms simplify to zero:

    (x - x) + (y - y) → 0

Then:

    ZERO

### 4.4 Constant arithmetic

    2 - 2 → 0
    5 + (-5) → 0

Result:

    ZERO

------------------------------------------------------------------------

# 5. NONZERO Detection Rules

A denominator is classified as **NONZERO** only when the guard proves
it.

### 5.1 Direct inequality

Under guard:

    x ≠ 0

classifier returns:

    NONZERO(x)

### 5.2 Nonzero constants

    1
    2
    -3
    π

All classify as:

    NONZERO

### 5.3 Guard-proven expressions

Example:

Guard:

    x ≠ 1

Expression:

    x - 1

Result:

    NONZERO

------------------------------------------------------------------------

# 6. UNKNOWN Classification

If neither ZERO nor NONZERO can be proven, the denominator is:

    UNKNOWN

Examples:

    x
    x - 1
    x² - 1
    sin(x)

without guard information.

UNKNOWN denominators trigger **branch splitting**.

------------------------------------------------------------------------

# 7. Guard Interaction

Classification always occurs **relative to a guard**.

Example:

Expression:

    x

Without guard:

    UNKNOWN

Under guard:

    x ≠ 0

Classifier result:

    NONZERO

------------------------------------------------------------------------

# 8. Detector Representation (Internal)

Internally the system may represent classification using detectors:

    D_f = 1  ⇔  f = 0
    N_f = 1  ⇔  f ≠ 0

These are internal helper objects.

User-facing output should prefer equation form.

------------------------------------------------------------------------

# 9. Branch Trigger Rule

If a denominator `d` is classified as:

    UNKNOWN

the solver generates branches:

    [d = 0]
    [d ≠ 0]

Example:

    x/x

Denominator:

    x → UNKNOWN

Branches:

    [x = 0]
    [x ≠ 0]

------------------------------------------------------------------------

# 10. Protected Quotients

If the denominator is:

    UNKNOWN

the quotient becomes a **protected quotient**.

Example:

    (x² - 1)/(x - 1)

Until classification resolves `x - 1`, cancellation is forbidden.

------------------------------------------------------------------------

# 11. Classifier Algorithm

Given denominator `d` and guard `G`:

1.  Simplify `d`
2.  If `d = 0` → return ZERO
3.  If guard proves `d ≠ 0` → return NONZERO
4.  If constant nonzero → return NONZERO
5.  Otherwise → return UNKNOWN

------------------------------------------------------------------------

# 12. Example Classifications

### Example 1

Expression:

    x - x

Result:

    ZERO

------------------------------------------------------------------------

### Example 2

Expression:

    x

Result:

    UNKNOWN

------------------------------------------------------------------------

### Example 3

Expression:

    x

Guard:

    x ≠ 0

Result:

    NONZERO

------------------------------------------------------------------------

### Example 4

Expression:

    (x - x) + (y - y)

Result:

    ZERO

------------------------------------------------------------------------

# 13. Classifier Soundness

The classifier must satisfy:

### 13.1 Safety

It never falsely labels UNKNOWN expressions as ZERO or NONZERO.

### 13.2 Guard consistency

Results must respect the current guard.

### 13.3 Firewall preservation

No rewrite depending on nonzero assumptions occurs before
classification.

------------------------------------------------------------------------

# 14. Design Intent

The denominator classifier is intentionally conservative.

It prioritizes:

-   soundness
-   firewall safety
-   predictable branching

over aggressive algebraic deduction.

Future versions may expand ZERO detection using:

-   polynomial factorization
-   symbolic identity detection
-   detector algebra integration.
