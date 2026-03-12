# Contributing

## Purpose

This repository develops an experimental symbolic formalism around branch-evaluated division and detector-backed guards. Contributions are welcome, but they must preserve the project’s core discipline.

---

## Core rules contributors must preserve

### 1. Branch firewall

No rewrite that requires a denominator to be nonzero may be used before the relevant branch split.

This includes, at minimum:

- cancellation across the main quotient
- cross-multiplication
- denominator clearing
- inverse-style division identities

### 2. Guard explicitness

When a zero/nonzero distinction matters, it must remain explicit in the output.

Preferred output form:

- `[guard] -> result`

### 3. Detector preference

Whenever a guard has the form `f = 0` or `f != 0`, detector-backed notation is preferred where practical.

### 4. No overclaiming

Do not describe a rule or engine as complete, confluent, or field-like unless that claim is stated with exact scope and proof conditions.

---

## Good contributions

Examples of useful contributions:

- clearer notation
- new worked examples
- branch-local proofs for restricted rule families
- better hidden-zero tests
- verifier improvements that preserve the firewall
- documentation of failure cases and open problems

---

## Risky contributions

These need extra care and review:

- adding expansion rules
- adding unrestricted factorization
- introducing global cancellation heuristics
- importing domain assumptions implicitly
- collapsing guarded outputs into single expressions too early

---

## Style guidelines

- state assumptions explicitly
- separate soundness claims from completeness claims
- prefer narrow, testable statements
- include examples when adding rules
- document failure boundaries honestly

---

## Suggested pull request structure

A good pull request should include:

1. what changed
2. why the change is needed
3. whether the change affects soundness, completeness, implementation, or presentation
4. at least one worked example
5. at least one note on limitations or boundary conditions

---

## Bottom line

This project gets stronger by becoming more explicit, more guarded, and more testable — not by becoming more aggressive.
