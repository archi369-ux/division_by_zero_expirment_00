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
- reject some impossible combined guards via bounded linear consistency checks
- classify equation branches
- solve simple residual branches
- extract branch-aware solution objects
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Dict, Tuple
import sympy as sp

ZERO = "ZERO"
NONZERO = "NONZERO"
UNKNOWN = "UNKNOWN"

def q(num: sp.Expr, den: sp.Expr) -> sp.Expr:
    return sp.Mul(num, sp.Pow(den, -1, evaluate=False), evaluate=False)

def _single_symbol_linear_value(expr: sp.Expr) -> Tuple[sp.Symbol, sp.Expr] | None:
    s = sp.expand(sp.simplify(expr))
    if isinstance(s, sp.Symbol):
        return (s, sp.Integer(0))
    symbols = list(s.free_symbols)
    if len(symbols) != 1:
        return None
    sym = symbols[0]
    try:
        sol = sp.solve(sp.Eq(s, 0), sym, dict=True)
    except Exception:
        return None
    if len(sol) != 1 or sym not in sol[0]:
        return None
    val = sp.simplify(sol[0][sym])
    if val.is_number:
        return (sym, val)
    return None

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
        implied_values: Dict[sp.Symbol, sp.Expr] = {}
        for z in self.zero:
            parsed = _single_symbol_linear_value(z)
            if parsed is None:
                continue
            sym, val = parsed
            if sym in implied_values and sp.simplify(implied_values[sym] - val) != 0:
                return True
            implied_values[sym] = val
        for nz in self.nonzero:
            parsed = _single_symbol_linear_value(nz)
            if parsed is None:
                continue
            sym, forbidden_val = parsed
            if sym in implied_values and sp.simplify(implied_values[sym] - forbidden_val) == 0:
                return True
        if implied_values:
            for nz in self.nonzero:
                try:
                    reduced = sp.simplify(nz.xreplace(implied_values))
                except Exception:
                    reduced = sp.simplify(nz.subs(implied_values))
                if reduced == 0:
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

@dataclass(frozen=True)
class EquationBranch:
    guard: Guard
    lhs: sp.Expr
    rhs: sp.Expr
    def format(self) -> str:
        return f"[{self.guard.format()}] -> {sp.sstr(self.lhs)} = {sp.sstr(self.rhs)}"

@dataclass(frozen=True)
class SolutionBranch:
    guard: Guard
    solution: sp.Expr
    def format(self) -> str:
        return f"[{self.guard.format()}] -> {sp.sstr(self.solution)}"

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
    subs: dict[sp.Symbol, sp.Expr] = {}
    for g in guard.zero:
        parsed = _single_symbol_linear_value(g)
        if parsed is None:
            continue
        sym, val = parsed
        subs[sym] = val
    return subs

def _apply_guard_reduction(expr: sp.Expr, guard: Guard) -> sp.Expr:
    subs = _simple_guard_substitutions(guard)
    if subs:
        try:
            expr = expr.xreplace(subs)
        except Exception:
            expr = expr.subs(subs)
    return sp.simplify(expr)

def _normalize_quotient(num: sp.Expr, den: sp.Expr, guard: Guard) -> sp.Expr:
    num = _apply_guard_reduction(sp.simplify(num), guard)
    den = _apply_guard_reduction(sp.simplify(den), guard)
    status = classify_denominator(den, guard)
    if status == ZERO:
        return _apply_guard_reduction(num, guard)
    if status == NONZERO:
        if sp.simplify(num - den) == 0:
            return sp.Integer(1)
        try:
            return _apply_guard_reduction(sp.simplify(sp.cancel(num / den)), guard)
        except Exception:
            return q(num, den)
    return q(num, den)

def _normalize_under_guard(expr: sp.Expr, guard: Guard) -> sp.Expr:
    if expr.is_Atom:
        return _apply_guard_reduction(expr, guard)
    if isinstance(expr, sp.Pow) and expr.exp == -1:
        den = _normalize_under_guard(expr.base, guard)
        status = classify_denominator(den, guard)
        if status == ZERO:
            return sp.Integer(1)
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
        rebuilt = sp.Mul(*(num_factors + [sp.Pow(d, -1, evaluate=False) for d in den_factors]), evaluate=False)
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

def sort_branches(branches: Iterable[Branch]) -> List[Branch]:
    return sorted(branches, key=lambda b: (b.guard.format(), sp.sstr(b.expr)))

def merge_complementary_branches(branches: List[Branch]) -> List[Branch]:
    merged: List[Branch] = []
    used = set()
    for i, b1 in enumerate(branches):
        if i in used:
            continue
        merged_here = False
        for j, b2 in enumerate(branches):
            if i >= j or j in used:
                continue
            if sp.simplify(b1.expr - b2.expr) != 0:
                continue
            g1 = b1.guard
            g2 = b2.guard
            if (
                len(g1.zero) == 1 and len(g2.nonzero) == 1
                and list(g1.zero)[0] == list(g2.nonzero)[0]
                and not g1.nonzero and not g2.zero
            ):
                merged.append(Branch(Guard(), b1.expr))
                used.add(i); used.add(j); merged_here = True; break
            if (
                len(g2.zero) == 1 and len(g1.nonzero) == 1
                and list(g2.zero)[0] == list(g1.nonzero)[0]
                and not g2.nonzero and not g1.zero
            ):
                merged.append(Branch(Guard(), b1.expr))
                used.add(i); used.add(j); merged_here = True; break
        if not merged_here and i not in used:
            merged.append(b1)
    return sort_branches(merged)

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
    branches = sort_branches(zero_branch + nonzero_branch)
    return merge_complementary_branches(branches)

def normalize_equation(lhs: sp.Expr, rhs: sp.Expr, depth: int = 4) -> List[EquationBranch]:
    lhs_branches = normalize_with_branching(lhs, depth=depth)
    out: List[EquationBranch] = []
    for br in lhs_branches:
        rhs_norm = _normalize_under_guard(rhs, br.guard)
        out.append(EquationBranch(br.guard, sp.simplify(br.expr), sp.simplify(rhs_norm)))
    return out

def classify_equation_branch(branch: EquationBranch) -> str:
    diff = _apply_guard_reduction(sp.simplify(branch.lhs - branch.rhs), branch.guard)
    if diff == 0:
        return "TAUTOLOGY"
    if diff.is_number and diff != 0:
        return "CONTRADICTION"
    return "RESIDUAL"

def solve_equation_branches(lhs: sp.Expr, rhs: sp.Expr, depth: int = 4) -> List[tuple[str, EquationBranch]]:
    branches = normalize_equation(lhs, rhs, depth=depth)
    return [(classify_equation_branch(br), br) for br in branches]

def solve_simple_residual_branch(branch: EquationBranch):
    expr = _apply_guard_reduction(sp.simplify(branch.lhs - branch.rhs), branch.guard)
    symbols = sorted(expr.free_symbols, key=lambda s: s.name)
    if len(symbols) != 1:
        return None
    sym = symbols[0]
    try:
        sols = sp.solve(sp.Eq(expr, 0), sym, dict=True)
    except Exception:
        return None
    if not sols:
        return []
    return sols

def solve_equation_branches_with_residuals(lhs: sp.Expr, rhs: sp.Expr, depth: int = 4):
    out = []
    for status, br in solve_equation_branches(lhs, rhs, depth=depth):
        if status == "RESIDUAL":
            solved = solve_simple_residual_branch(br)
            out.append((status, br, solved))
        else:
            out.append((status, br, None))
    return out

def _solutions_from_guard_tautology(branch: EquationBranch):
    """
    Extract a simple solution from a tautology branch.

    Cases:
    - [x - 1 = 0] -> 1 = 1     gives   Eq(x, 1)
    - [x != 0]    -> 1 = 1     gives   Ne(x, 0)

    This stays intentionally conservative.
    """
    subs = _simple_guard_substitutions(branch.guard)
    if len(subs) == 1:
        sym = next(iter(subs))
        val = sp.simplify(subs[sym])
        return sp.Eq(sym, val)

    if len(branch.guard.nonzero) == 1 and not branch.guard.zero:
        expr = next(iter(branch.guard.nonzero))
        return sp.Ne(expr, 0)

    return None

def dedupe_solution_branches(branches: List[SolutionBranch]) -> List[SolutionBranch]:
    seen = set()
    out: List[SolutionBranch] = []
    for br in branches:
        key = (br.guard.format(), sp.sstr(br.solution))
        if key not in seen:
            seen.add(key)
            out.append(br)
    return sorted(out, key=lambda b: (b.guard.format(), sp.sstr(b.solution)))

def extract_solution_branches(lhs: sp.Expr, rhs: sp.Expr, depth: int = 4) -> List[SolutionBranch]:
    out: List[SolutionBranch] = []
    for status, br, solved in solve_equation_branches_with_residuals(lhs, rhs, depth=depth):
        if status == "CONTRADICTION":
            continue
        if status == "TAUTOLOGY":
            sol = _solutions_from_guard_tautology(br)
            if sol is not None:
                out.append(SolutionBranch(Guard(), sol))
            continue
        if status == "RESIDUAL" and solved is not None:
            for item in solved:
                if isinstance(item, dict) and len(item) == 1:
                    sym = next(iter(item))
                    val = sp.simplify(item[sym])
                    out.append(SolutionBranch(Guard(), sp.Eq(sym, val)))
    return dedupe_solution_branches(out)

def format_solution_set(branches: List[SolutionBranch]) -> str:
    if not branches:
        return "no solutions"
    parts = [sp.sstr(br.solution) if br.guard.format() == "true" else br.format() for br in branches]
    return " or ".join(parts)
