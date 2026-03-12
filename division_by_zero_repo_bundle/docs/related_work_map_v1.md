# Related Work Map v1

## 1. Purpose

This document compares the current branch-aware primitive-0 framework with nearby mathematical traditions.

It is not a claim of priority.
Its purpose is to separate:

- what is already standard,
- what is parallel,
- what seems genuinely different in the current project.

The comparison focuses on:

1. affine geometry
2. inversive / projective reciprocal geometry
3. totalized-division systems
4. the current primitive-0 branch framework

---

## 2. Comparison Table

| Feature | Affine geometry | Inversive / projective reciprocal geometry | Totalized-division systems (meadows / wheels / transreal-like families) | Current primitive-0 branch framework |
|---|---|---|---|---|
| Preferred origin | No fixed preferred origin; origin is chosen by coordinates | Usually ordinary coordinate origin, plus reciprocal / projective structure | Usually algebra-first, not centered on movable origin | Symmetry center may be treated as chosen reference point |
| Sign symmetry | Standard | Standard | Standard | Standard, but interpreted together with branch structure |
| Reciprocal map `x -> 1/x` | Ordinary, domain excludes zero | Central object; often completed by adding infinity / projective closure | Totalized in different ways depending on system | Classical for nonzero branches, primitive / branch-sensitive at zero |
| Division by zero | Undefined in ordinary affine arithmetic | Undefined unless extended by projective / inversive completion | Explicitly formalized | Explicitly formalized by primitive rule `a/0 := a` |
| Value of `0/0` | Undefined | Undefined | Depends on system | `0/0 := 0` |
| Global cancellation | Standard where defined | Standard where defined | Depends on system axioms | Forbidden globally unless guard justifies nonzero condition |
| Branch-aware outputs | Not a core feature | Not a core feature | Usually no branch objects as first-class outputs | Yes; branch objects are first-class |
| Guarded identities | Not central | Not central | Usually algebraic equations, not branch guards | Central feature |
| Infinity as formal object | Not primary | Often yes, for closure | Often yes, depending on system | Classical infinity may remain classical, but not required for primitive-0 local semantics |
| “Void” as totality distinct from infinity | No standard analogue in this exact form | No standard analogue in this exact form | No standard analogue in this exact form | Provisional concept only; not yet formalized |
| Focus on reversibility safety | Usually implicit | Usually implicit | Sometimes implicit via axioms | Explicit and central |
| Main novelty candidate | Movable origin viewpoint | Reciprocal inside/outside structure | Division-by-zero formalization | Primitive `a/0 := a` + branch firewall + guarded local algebra + branch-first solving |

---

## 3. Affine Geometry

### What is standard here

Affine geometry already supports the idea that there is **no absolute preferred origin**.

A point can be chosen as origin, and coordinates are then measured relative to that choice.

This matches the project insight that:

> the symmetry center is the chosen reference point; `0` is only its coordinate label in a given representation.

### What affine geometry does not provide directly

Affine geometry does not, by itself, provide:

- a primitive zero-division rule,
- a branch-aware rewrite system,
- guarded denominator logic,
- or a solver that preserves zero branches explicitly.

So affine geometry supports the **movable-center intuition**, but not the primitive-0 branch algebra itself.

---

## 4. Inversive / Projective Reciprocal Geometry

### What is standard here

The reciprocal map:

```text
x -> 1/x
```

is a classical structural object.

It exchanges the inner and outer magnitude regimes:

```text
0 < |x| < 1
|x| > 1
```

and fixes the boundary:

```text
|x| = 1
```

In projective / inversive settings, zero is usually paired with infinity so that the reciprocal map closes neatly.

### What differs from the current project

The current project does not preserve the classical reciprocal picture unchanged.

Instead:

- reciprocal is classical on nonzero branches,
- zero is treated by primitive rule,
- branch semantics replace global reciprocal closure.

So the project is **related** to reciprocal geometry, but does not simply reproduce it.

---

## 5. Totalized-Division Systems

### What is standard here

There are already mathematical systems that attempt to totalize division.

Typical examples include families like:

- meadows,
- wheels,
- transreal-style extensions,
- and related division-by-zero algebras.

These show that the broad idea

> “division should be formalized rather than left undefined”

has already been explored.

### What differs in the current project

The current project uses a very specific primitive rule:

```text
a/0 := a
```

and combines it with:

- a branch firewall,
- guarded branch-local identities,
- denominator-sensitive solving,
- and explicit branch outputs.

This combination is not the same as the standard totalized-division families.

In particular, the project emphasizes:

> soundness through guarded local algebra rather than unrestricted global equations.

---

## 6. Current Primitive-0 Branch Framework

### Core distinguishing features

The current framework combines:

1. **Primitive zero-division clause**
   ```text
   a/0 := a
   ```
2. **Branch firewall**
   - no denominator- or reversibility-sensitive rewrite without justification
3. **Guarded local algebra**
   - ordinary identities survive only on justified branches
4. **Branch-first solver**
   - equations normalize, classify, and solve branchwise
5. **First-class branch outputs**
   - final outputs can be guarded conditions, not only globally simplified formulas

### Why this matters

This turns many classical global identities into:

```text
guarded identities
```

rather than universal equalities.

That is the most important structural difference from the nearby traditions listed above.

---

## 7. The “Void” Concept

### Current status

“Void” is currently a **provisional interpretive concept**, not a formal algebraic object.

The intended role seems to be:

- distinct from classical infinity,
- distinct from ordinary zero,
- related to the totality of the line relative to a chosen center,
- and useful for describing total structural decomposition rather than directional unboundedness.

### Comparison with related work

No standard analogue was identified in the nearby theories reviewed here for:

```text
void = totality of the line distinct from classical infinity
```

That does not prove novelty in the absolute historical sense.
It only means it does not line up neatly with the most obvious neighbouring frameworks.

### Caution

At the current stage, “void” should be treated as:

- conceptual,
- structural,
- and not yet part of the formal algebra.

---

## 8. What Looks Standard vs What Looks New

### Standard / already existing ingredients

- movable origin intuition
- sign symmetry around a chosen center
- reciprocal map and its inside/outside regime structure
- the general ambition to formalize division by zero

### Potentially new synthesis

The likely originality of the project lies not in any single ingredient, but in their combination:

- primitive `a/0 := a`,
- zero as branch-trigger rather than simple undefined point,
- branch firewall,
- reversibility-sensitive rewrites,
- guarded branch-local identities,
- branch-first equation solving,
- and possibly the later interpretation of void as distinct from classical infinity.

That package is the real thing to test and refine.

---

## 9. Recommended Public Positioning

A careful public-facing description would be:

> This project is a branch-aware symbolic framework with a primitive zero-division clause. It draws conceptually on origin-relative symmetry, reciprocal regime structure, and prior work on totalized division, but combines them into a guarded branch-local algebra rather than a direct extension of any one standard system.

This is strong without overclaiming.

---

## 10. Next Use of This Document

This comparison note should be used for two purposes:

1. **review discipline**
   - to avoid accidentally claiming classical ideas as new
2. **research direction**
   - to clarify which parts of the project are inherited, parallel, or genuinely novel

It is best treated as a map, not a final verdict.

Future versions can refine the comparison as the theory becomes more formal.
