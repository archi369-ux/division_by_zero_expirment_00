
# Operation Regime Matrix v1

This matrix summarizes how multiplication and division affect magnitude in different regimes.

## Magnitude Effect Matrix

| Operation | Operand Magnitude | Result Effect |
|-----------|------------------|--------------|
| x * a | |a| > 1 | magnitude increases |
| x * a | |a| = 1 | magnitude unchanged |
| x * a | 0 < |a| < 1 | magnitude decreases |
| x / a | |a| > 1 | magnitude decreases |
| x / a | |a| = 1 | magnitude unchanged |
| x / a | 0 < |a| < 1 | magnitude increases |

## Behavioral Symmetry

| Behavior | Equivalent Transformation |
|---------|---------------------------|
| multiply by small number | divide by large number |
| divide by small number | multiply by large number |

## Visual Interpretation

Small multipliers compress magnitude.

Small divisors expand magnitude.

Large multipliers expand magnitude.

Large divisors compress magnitude.

## Purpose

This matrix helps visualize magnitude‑dependent behavior and may guide future exploration of regime‑aware algebra.

It is **not part of the core algebra semantics** yet.
