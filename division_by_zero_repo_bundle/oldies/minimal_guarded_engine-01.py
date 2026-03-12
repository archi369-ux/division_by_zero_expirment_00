"""
Minimal guarded algebra engine prototype.

Reference implementation for the division-by-zero experimental framework.

Capabilities:
- classify denominators as ZERO / NONZERO / UNKNOWN
- protect quotients with unresolved denominators
- branch on unresolved denominators
- apply primitive rule a/0 := a
- apply guarded simplification (x/x -> 1 if x != 0)
- apply simple guard-aware reduction in zero branches

This is intentionally minimal and safety-oriented.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List
import sympy as sp

ZERO = "ZERO"
NONZERO = "NONZERO"
UNKNOWN = "UNKNOWN"


def q(num: sp.Expr, den: sp.Expr) -> sp.Expr:
    """Construct a protected quotient without eager evaluation."""
    return sp.Mul(num, sp.Pow(den, -1, evaluate=False), evaluate=False)


@dataclass(frozen=True)
class Guard:
    zero: frozenset[sp.Expr] = frozenset()
    nonzero: frozenset[sp.Expr] = frozenset()

    def add_zero(self, expr: sp.Expr) -> "Guard":
        return Guard(self.zero | {sp.simplify(expr)}, self.nonzero)

    def add_nonzero(self, expr: sp.Expr) -> "Guard":
        return Guard(self.zero, self.nonzero | {sp.simplify(expr)})

    def is_inconsistent(self) -> bool:
        if self.zero & self.nonzero:
            return True

        for z in self.zero:
            s = sp.simplify(z)
            if s.is_number and s != 0:
                return True

        for nz in self.nonzero:
            s = sp.simplify(nz)
            if s == 0:
                return True

        return False

    def format(self) -> str:
        atoms: List[str] = []
        atoms.extend([f"{sp.sstr(e)} = 0" for e in sorted(self.zero, key=sp.sstr)])
        atoms.extend([f"{sp.sstr(e)} != 0" for e in sorted(self.nonzero, key=sp.sstr)])
        return " and ".join(atoms) if atoms else "true"


@dataclass(frozen=True)
class Branch:
    guard: Guard
    expr: sp.Expr

    def format(self) -> str:
        return f"[{self.guard.format()}] -> {sp.sstr(self.expr)}"


def _is_zero(expr: sp.Expr) -> bool:
    return bool(sp.simplify(expr) == 0)


def _is_nonzero_constant(expr: sp.Expr) -> bool:
    s = sp.simplify(expr)
    return bool(s.is_number and s != 0)


def classify_denominator(expr: sp.Expr, guard: Guard) -> str:
    expr = sp.simplify(expr)

    if expr in guard.zero:
        return ZERO
    if expr in guard.nonzero:
        return NONZERO
    if _is_zero(expr):
        return ZERO
    if _is_nonzero_constant(expr):
        return NONZERO

    return UNKNOWN


def _simple_guard_substitutions(guard: Guard) -> dict[sp.Symbol, sp.Expr]:
    """
    Very small substitution extractor.

    Supports only patterns like:
    - x = 0
    - x - c = 0
    - x + c = 0
    where c is numeric
    """
    subs: dict[sp.Symbol, sp.Expr] = {}

    for g in guard.zero:
        s = sp.expand(sp.simplify(g))

        # x = 0
        if isinstance(s, sp.Symbol):
            subs[s] = sp.Integer(0)
            continue

        # Try solving simple one-variable linear equations
        symbols = list(s.free_symbols)
        if len(symbols) != 1:
            continue

        sym = symbols[0]
        try:
            sol = sp.solve(sp.Eq(s, 0), sym, dict=True)
        except Exception:
            sol = []

        if len(sol) == 1 and sym in sol[0]:
            val = sp.simplify(sol[0][sym])
            if val.is_number:
                subs[sym] = val

    return subs


def _apply_guard_reduction(expr: sp.Expr, guard: Guard) -> sp.Expr:
    """
    Reduce an expression using very simple equalities from the guard.
    This is intentionally conservative.
    """
    subs = _simple_guard_substitutions(guard)
    if subs:
        try:
            expr = expr.xreplace(subs)
        except Exception:
            expr = expr.subs(subs)

    return sp.simplify(expr)


def _normalize_quotient(num: sp.Expr, den: sp.Expr, guard: Guard) -> sp.Expr:
    # Only simplify after quotient structure has been isolated.
    num = _apply_guard_reduction(sp.simplify(num), guard)
    den = _apply_guard_reduction(sp.simplify(den), guard)
    status = classify_denominator(den, guard)

    if status == ZERO:
        return _apply_guard_reduction(num, guard)  # primitive rule a/0 := a

    if status == NONZERO:
        if sp.simplify(num - den) == 0:
            return sp.Integer(1)

        try:
            return _apply_guard_reduction(sp.simplify(sp.cancel(num / den)), guard)
        except Exception:
            return q(num, den)

    # UNKNOWN: keep quotient protected
    return q(num, den)


def _normalize_under_guard(expr: sp.Expr, guard: Guard) -> sp.Expr:
    # Do not simplify the whole expression up front.
    if expr.is_Atom:
        return _apply_guard_reduction(expr, guard)

    if isinstance(expr, sp.Pow) and expr.exp == -1:
        den = _normalize_under_guard(expr.base, guard)
        status = classify_denominator(den, guard)
        if status == ZERO:
            return sp.Integer(1)  # reciprocal case: 1/0 := 1
        return sp.Pow(den, -1, evaluate=False)

    if expr.is_Mul:
        num_factors: List[sp.Expr] = []
        den_factors: List[sp.Expr] = []

        for a in expr.args:
            if isinstance(a, sp.Pow) and a.exp == -1:
                den_factors.append(_normalize_under_guard(a.base, guard))
            else:
                num_factors.append(_normalize_under_guard(a, guard))

        if len(den_factors) == 1:
            num = sp.Mul(*num_factors, evaluate=False) if num_factors else sp.Integer(1)
            den = den_factors[0]
            return _normalize_quotient(num, den, guard)

        rebuilt = sp.Mul(
            *(num_factors + [sp.Pow(d, -1, evaluate=False) for d in den_factors]),
            evaluate=False,
        )
        return _apply_guard_reduction(rebuilt, guard)

    if expr.is_Add:
        args = [_normalize_under_guard(a, guard) for a in expr.args]
        return _apply_guard_reduction(sp.Add(*args, evaluate=False), guard)

    if expr.is_Pow:
        args = [_normalize_under_guard(a, guard) for a in expr.args]
        try:
            out = expr.func(*args, evaluate=False)
        except Exception:
            out = expr.func(*args)
        return _apply_guard_reduction(out, guard)

    if expr.is_Function:
        return _apply_guard_reduction(expr.func(*[_normalize_under_guard(a, guard) for a in expr.args]), guard)

    args = [_normalize_under_guard(a, guard) for a in expr.args]
    try:
        out = expr.func(*args, evaluate=False)
    except Exception:
        out = expr.func(*args)
    return _apply_guard_reduction(out, guard)


def find_unknown_denominators(expr: sp.Expr, guard: Guard) -> List[sp.Expr]:
    found: List[sp.Expr] = []

    def visit(e: sp.Expr) -> None:
        if isinstance(e, sp.Pow) and e.exp == -1:
            den = sp.simplify(e.base)
            if classify_denominator(den, guard) == UNKNOWN:
                found.append(den)
        for a in getattr(e, "args", ()):
            visit(a)

    visit(expr)

    unique: List[sp.Expr] = []
    seen = set()
    for d in found:
        key = sp.sstr(d)
        if key not in seen:
            seen.add(key)
            unique.append(d)
    return unique


def normalize_with_branching(expr: sp.Expr, guard: Guard | None = None, depth: int = 4) -> List[Branch]:
    guard = guard or Guard()

    if guard.is_inconsistent():
        return []

    if depth < 0:
        return [Branch(guard, _normalize_under_guard(expr, guard))]

    unknown = find_unknown_denominators(expr, guard)
    if not unknown:
        return [Branch(guard, _normalize_under_guard(expr, guard))]

    d = unknown[0]
    zero_branch = normalize_with_branching(expr, guard.add_zero(d), depth - 1)
    nonzero_branch = normalize_with_branching(expr, guard.add_nonzero(d), depth - 1)
    return sort_branches(zero_branch + nonzero_branch)


def sort_branches(branches: Iterable[Branch]) -> List[Branch]:
    return sorted(branches, key=lambda b: (b.guard.format(), sp.sstr(b.expr)))


def demo() -> None:
    x, y = sp.symbols("x y")
    examples = [
        q(x, x),
        q(x**2 - 1, x - 1),
        q(x + 2, x - x),
        q(x, y - y),
        q(x + 1, y),
        q(sp.Integer(7), sp.Integer(0)),
        q(sp.Integer(0), sp.Integer(0)),
    ]

    for expr in examples:
        print("=" * 60)
        print("INPUT:", sp.sstr(expr))
        for branch in normalize_with_branching(expr):
            print(" ", branch.format())


if __name__ == "__main__":
    demo()
