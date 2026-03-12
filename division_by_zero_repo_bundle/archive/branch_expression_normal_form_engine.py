from __future__ import annotations

"""
Expression branch-normal-form engine for the current division-by-zero theory.

Purpose:
- parse a symbolic expression string
- preserve quotient structure before NZ-only algebra
- recursively split quotient-shaped subexpressions into guarded Z / NZ branches
- use the denominator zero detector from branch_normal_form_engine.py
- return a branch normal form object: a finite list of guarded expression branches

Deliberate limits:
- conservative; it may return UNKNOWN guards rather than prove more cases
- no unrestricted algebra before branch split
- denominator detection is local and safe, not complete
"""

from dataclasses import dataclass, field
from itertools import product
from typing import Iterable, List, Optional, Sequence, Tuple
import argparse
import sympy as sp

from branch_normal_form_engine import (
    D,
    N,
    parse_expr,
    normalize_denominator,
    classify_denominator,
)


# ----------------------------- models -----------------------------

@dataclass(frozen=True)
class Guard:
    expr: sp.Expr
    kind: str  # ZERO / NONZERO

    def text(self) -> str:
        op = "=" if self.kind == "ZERO" else "!="
        return f"{sp.sstr(self.expr)} {op} 0"

    def detector(self) -> str:
        return D(self.expr) if self.kind == "ZERO" else N(self.expr)


@dataclass
class ExprBranch:
    guards: List[Guard] = field(default_factory=list)
    expr: sp.Expr = sp.Integer(0)

    def guard_text(self) -> str:
        if not self.guards:
            return "true"
        return " and ".join(g.text() for g in self.guards)

    def detector_text(self) -> str:
        if not self.guards:
            return "true"
        return " and ".join(g.detector() for g in self.guards)


# ----------------------------- helpers -----------------------------


def _sort_key(expr: sp.Expr):
    return sp.default_sort_key(expr)


def _build_mul(args: Sequence[sp.Expr]) -> sp.Expr:
    if not args:
        return sp.Integer(1)
    out = args[0]
    for a in args[1:]:
        out = sp.Mul(out, a, evaluate=False)
    return out


def _build_add(args: Sequence[sp.Expr]) -> sp.Expr:
    if not args:
        return sp.Integer(0)
    out = args[0]
    for a in args[1:]:
        out = sp.Add(out, a, evaluate=False)
    return out


def _flatten_mul(expr: sp.Expr) -> List[sp.Expr]:
    if isinstance(expr, sp.Mul):
        out: List[sp.Expr] = []
        for a in expr.args:
            out.extend(_flatten_mul(a))
        return out
    return [expr]


def _flatten_add(expr: sp.Expr) -> List[sp.Expr]:
    if isinstance(expr, sp.Add):
        out: List[sp.Expr] = []
        for a in expr.args:
            out.extend(_flatten_add(a))
        return out
    return [expr]


def quotient_form_any(expr: sp.Expr) -> Tuple[bool, sp.Expr, sp.Expr]:
    """
    Accept any top-level product with at least one denominator factor as a quotient.

    Example:
      x/(a*b)        -> numerator x, denominator a*b
      (x+1)/(y-1)^2  -> only explicit Pow(-1) factors are treated as denominator factors
    """
    if isinstance(expr, sp.Pow) and expr.exp == -1:
        return True, sp.Integer(1), expr.base

    if isinstance(expr, sp.Mul):
        numer: List[sp.Expr] = []
        denom: List[sp.Expr] = []
        for factor in _flatten_mul(expr):
            if isinstance(factor, sp.Pow) and factor.exp == -1:
                denom.append(factor.base)
            else:
                numer.append(factor)
        if denom:
            numer_expr = _build_mul(sorted(numer, key=_sort_key)) if numer else sp.Integer(1)
            denom_expr = _build_mul(sorted(denom, key=_sort_key))
            return True, numer_expr, denom_expr
    return False, expr, sp.Integer(1)


def safe_rebuild_add(args: Sequence[sp.Expr]) -> sp.Expr:
    return normalize_denominator(_build_add(list(args)))


def safe_rebuild_mul(args: Sequence[sp.Expr]) -> sp.Expr:
    return normalize_denominator(_build_mul(list(args)))


def safe_make_frac(numer: sp.Expr, denom: sp.Expr) -> sp.Expr:
    return normalize_denominator(sp.Mul(numer, sp.Pow(denom, -1, evaluate=False), evaluate=False))


def guards_consistent(guards: Sequence[Guard]) -> bool:
    seen: dict[str, str] = {}
    for g in guards:
        key = sp.srepr(normalize_denominator(g.expr))
        if key in seen and seen[key] != g.kind:
            return False
        seen[key] = g.kind
    return True


def canonical_guard_list(guards: Sequence[Guard]) -> List[Guard]:
    best: dict[Tuple[str, str], Guard] = {}
    for g in guards:
        norm = normalize_denominator(g.expr)
        key = (sp.srepr(norm), g.kind)
        best[key] = Guard(norm, g.kind)
    out = list(best.values())
    out.sort(key=lambda g: (g.kind, _sort_key(g.expr)))
    return out


def merge_branches(branches: Sequence[ExprBranch]) -> List[ExprBranch]:
    merged: dict[Tuple[str, str], ExprBranch] = {}
    for br in branches:
        guards = canonical_guard_list(br.guards)
        if not guards_consistent(guards):
            continue
        expr = normalize_denominator(br.expr)
        gkey = "|".join(f"{g.kind}:{sp.srepr(g.expr)}" for g in guards)
        key = (gkey, sp.srepr(expr))
        merged[key] = ExprBranch(guards=guards, expr=expr)
    return sorted(merged.values(), key=lambda b: (b.guard_text(), _sort_key(b.expr)))


def cartesian_combine(branch_lists: Sequence[Sequence[ExprBranch]], rebuild) -> List[ExprBranch]:
    if not branch_lists:
        return [ExprBranch([], sp.Integer(0))]
    out: List[ExprBranch] = []
    for combo in product(*branch_lists):
        guards: List[Guard] = []
        exprs: List[sp.Expr] = []
        for br in combo:
            guards.extend(br.guards)
            exprs.append(br.expr)
        if not guards_consistent(guards):
            continue
        out.append(ExprBranch(canonical_guard_list(guards), rebuild(exprs)))
    return merge_branches(out)


# ----------------------------- expression evaluator -----------------------------


def expression_bnf(expr: sp.Expr, depth: int = 0, max_depth: int = 12) -> List[ExprBranch]:
    if depth > max_depth:
        return [ExprBranch([], normalize_denominator(expr))]

    # atoms
    if expr.is_Atom:
        return [ExprBranch([], expr)]

    # quotient-shaped expressions branch before generic handling
    is_q, numer, denom = quotient_form_any(expr)
    if is_q:
        numer_branches = expression_bnf(numer, depth + 1, max_depth)
        denom_branches = expression_bnf(denom, depth + 1, max_depth)
        out: List[ExprBranch] = []
        for nb in numer_branches:
            for db in denom_branches:
                base_guards = canonical_guard_list(nb.guards + db.guards)
                if not guards_consistent(base_guards):
                    continue
                info = classify_denominator(db.expr)
                if info.classification == "ZERO":
                    out.append(ExprBranch(base_guards + [Guard(info.normalized, "ZERO")], nb.expr))
                elif info.classification == "NONZERO":
                    out.append(ExprBranch(base_guards + [Guard(info.normalized, "NONZERO")], safe_make_frac(nb.expr, info.normalized)))
                else:
                    out.append(ExprBranch(base_guards + [Guard(info.normalized, "ZERO")], nb.expr))
                    out.append(ExprBranch(base_guards + [Guard(info.normalized, "NONZERO")], safe_make_frac(nb.expr, info.normalized)))
        return merge_branches(out)

    # generic addition
    if isinstance(expr, sp.Add):
        child_lists = [expression_bnf(a, depth + 1, max_depth) for a in _flatten_add(expr)]
        return cartesian_combine(child_lists, safe_rebuild_add)

    # generic multiplication
    if isinstance(expr, sp.Mul):
        child_lists = [expression_bnf(a, depth + 1, max_depth) for a in _flatten_mul(expr)]
        return cartesian_combine(child_lists, safe_rebuild_mul)

    # powers other than explicit quotient nodes
    if isinstance(expr, sp.Pow):
        base_branches = expression_bnf(expr.base, depth + 1, max_depth)
        exp_branches = expression_bnf(expr.exp, depth + 1, max_depth)
        out: List[ExprBranch] = []
        for bb in base_branches:
            for eb in exp_branches:
                guards = canonical_guard_list(bb.guards + eb.guards)
                if not guards_consistent(guards):
                    continue
                rebuilt = normalize_denominator(sp.Pow(bb.expr, eb.expr, evaluate=False))
                out.append(ExprBranch(guards, rebuilt))
        return merge_branches(out)

    # fallback
    child_lists = [expression_bnf(a, depth + 1, max_depth) for a in expr.args]
    def _rebuild(exprs: Sequence[sp.Expr]) -> sp.Expr:
        return normalize_denominator(expr.func(*exprs, evaluate=False))
    return cartesian_combine(child_lists, _rebuild)


# ----------------------------- reporting -----------------------------


def format_bnf_report(expr_text: str, branches: Sequence[ExprBranch]) -> str:
    lines: List[str] = []
    lines.append(f"expression: {expr_text}")
    lines.append(f"branch count: {len(branches)}")
    for i, br in enumerate(branches, start=1):
        lines.append(f"  branch {i}:")
        lines.append(f"    guard: {br.guard_text()}")
        lines.append(f"    detector: {br.detector_text()}")
        lines.append(f"    expression: {sp.sstr(br.expr)}")
    return "\n".join(lines)


DEFAULT_EXAMPLES = [
    "x/0",
    "x/(x-1)",
    "x/((x-x)+(y-y))",
    "(x+1)/((a+b)-(b+a)) + 3",
    "(x/(y-y)) - x",
    "(u/((v-v))) + (w/(z-1))",
    "(a/(b-b)) * (c/(d-1))",
    "((p/0)-p) + q",
    "(x/(x-1)) + (y/(y-y))",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Expression branch-normal-form engine")
    parser.add_argument("expression", nargs="?", help="Expression string like '(x+1)/((a+b)-(b+a)) + 3'")
    parser.add_argument("--var", default="x", help="Primary variable name for parsing (default: x)")
    parser.add_argument("--examples", action="store_true", help="Run built-in examples")
    args = parser.parse_args()

    if args.examples or not args.expression:
        reports: List[str] = []
        for ex in DEFAULT_EXAMPLES:
            try:
                expr = parse_expr(ex, args.var)
                branches = expression_bnf(expr)
                reports.append("=" * 80)
                reports.append(format_bnf_report(ex, branches))
            except Exception as exc:
                reports.append("=" * 80)
                reports.append(f"expression: {ex}")
                reports.append(f"error: {exc}")
        print("\n".join(reports))
        return

    expr = parse_expr(args.expression, args.var)
    branches = expression_bnf(expr)
    print(format_bnf_report(args.expression, branches))


if __name__ == "__main__":
    main()
