from __future__ import annotations

"""
Parser-based verifier for Branch Arithmetic Equation Solver Draft v1.

What it does:
- parses an equation string like "x/(x-1) = 2"
- safely detects only *direct* top-level quotient structure
- applies branch-first solver rules
- prints guarded branch solutions with detector labels

What it does NOT do:
- it does not do unrestricted simplification before branch split
- it does not combine arbitrary fractions or expand/factor globally
- it is not a full CAS
"""

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple, Union
import argparse
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr as sympy_parse_expr


@dataclass
class SideForm:
    expr: sp.Expr
    numerator: sp.Expr
    denominator: sp.Expr
    is_direct_quotient: bool


@dataclass
class BranchResult:
    name: str
    guard_text: str
    detector_text: str
    transformed_equation: str
    status: str
    solutions: Union[List[sp.Expr], str]


ALL_REALS_GUARD = sp.Symbol("ALL_REALS_GUARD")


def D(expr: sp.Expr) -> str:
    return f"D_({sp.sstr(expr)}) = 1"


def N(expr: sp.Expr) -> str:
    return f"N_({sp.sstr(expr)}) = 1"


def parse_expr(text: str, var_name: str = "x") -> sp.Expr:
    var = sp.Symbol(var_name, real=True)
    locals_map = {var_name: var}
    return sympy_parse_expr(text, local_dict=locals_map, evaluate=False)


def parse_equation(text: str, var_name: str = "x") -> Tuple[sp.Expr, sp.Expr, sp.Symbol]:
    if text.count("=") != 1:
        raise ValueError("Equation must contain exactly one '=' sign.")
    left_text, right_text = [part.strip() for part in text.split("=", 1)]
    var = sp.Symbol(var_name, real=True)
    return parse_expr(left_text, var_name), parse_expr(right_text, var_name), var


def mul_of(exprs: Sequence[sp.Expr]) -> sp.Expr:
    if not exprs:
        return sp.Integer(1)
    out = sp.Integer(1)
    for e in exprs:
        out *= e
    return sp.simplify(out)


def direct_quotient_form(expr: sp.Expr) -> SideForm:
    """
    Detect only direct top-level quotient structure.

    Accepted examples:
      x/(x-1)
      (x+1)/(x-1)
      3/(x-1)
      x/x

    Rejected as direct quotients:
      1 + x/(x-1)
      (x/(x-1)) + (1/x)
      (x/(x-1))*(1/(x+1))   # multiple top-level denominator factors
    """
    if expr.is_Atom:
        return SideForm(expr, expr, sp.Integer(1), False)

    if isinstance(expr, sp.Pow) and expr.exp == -1:
        # 1/B
        return SideForm(expr, sp.Integer(1), expr.base, True)

    if isinstance(expr, sp.Mul):
        denom_factors: List[sp.Expr] = []
        numer_factors: List[sp.Expr] = []
        for factor in expr.args:
            if isinstance(factor, sp.Pow) and factor.exp == -1:
                denom_factors.append(factor.base)
            else:
                numer_factors.append(factor)
        if len(denom_factors) == 0:
            return SideForm(expr, expr, sp.Integer(1), False)
        if len(denom_factors) == 1:
            return SideForm(expr, mul_of(numer_factors), sp.simplify(denom_factors[0]), True)
        return SideForm(expr, expr, sp.Integer(1), False)

    # sums and everything else count as plain expressions for this verifier
    return SideForm(expr, expr, sp.Integer(1), False)


def unique_sorted(values: List[sp.Expr]) -> List[sp.Expr]:
    out: List[sp.Expr] = []
    for v in values:
        v = sp.simplify(v)
        if all(sp.simplify(v - w) != 0 for w in out):
            out.append(v)
    return sorted(out, key=sp.default_sort_key)


def solve_zero_guard(guard_expr: sp.Expr, var: sp.Symbol) -> List[sp.Expr]:
    sols = sp.solveset(sp.Eq(guard_expr, 0), var, domain=sp.S.Reals)
    if sols is sp.S.EmptySet:
        return []
    if sols is sp.S.Reals:
        return [ALL_REALS_GUARD]
    if isinstance(sols, sp.FiniteSet):
        return unique_sorted(list(sols))
    return [ALL_REALS_GUARD]


def equation_text(eq) -> str:
    if eq is sp.S.true or eq == True:
        return "True"
    if eq is sp.S.false or eq == False:
        return "False"
    return f"{sp.sstr(eq.lhs)} = {sp.sstr(eq.rhs)}"


def solve_eq(eq, var: sp.Symbol) -> Union[str, List[sp.Expr]]:
    if eq is sp.S.true or eq == True:
        return "all reals"
    if eq is sp.S.false or eq == False:
        return []
    sols = sp.solveset(eq, var, domain=sp.S.Reals)
    if sols is sp.S.EmptySet:
        return []
    if sols is sp.S.Reals:
        return "all reals"
    if isinstance(sols, sp.FiniteSet):
        return unique_sorted(list(sols))
    return str(sols)


def satisfies_eq(eq, var: sp.Symbol, value: sp.Expr) -> bool:
    if eq is sp.S.true or eq == True:
        return True
    if eq is sp.S.false or eq == False:
        return False
    lhs = sp.simplify(eq.lhs.subs(var, value))
    rhs = sp.simplify(eq.rhs.subs(var, value))
    return sp.simplify(lhs - rhs) == 0


def satisfies_zero(expr: sp.Expr, var: sp.Symbol, value: sp.Expr) -> bool:
    return sp.simplify(expr.subs(var, value)) == 0


def satisfies_nonzero(expr: sp.Expr, var: sp.Symbol, value: sp.Expr) -> bool:
    return sp.simplify(expr.subs(var, value)) != 0


def branch_z(name: str, guard_expr: sp.Expr, eq, var: sp.Symbol) -> BranchResult:
    guard_text = f"{sp.sstr(guard_expr)} = 0"
    det_text = D(guard_expr)
    transformed = equation_text(eq)
    guard_solutions = solve_zero_guard(guard_expr, var)
    if not guard_solutions:
        return BranchResult(name, guard_text, det_text, transformed, "impossible", [])
    if guard_solutions == [ALL_REALS_GUARD]:
        # guard is broad; solve equation globally then keep points satisfying the guard.
        sols = solve_eq(eq, var)
        if sols == "all reals":
            return BranchResult(name, guard_text, det_text, transformed, "tautology", f"all real {var} satisfying {guard_text}")
        if isinstance(sols, str):
            return BranchResult(name, guard_text, det_text, transformed, "unsupported", sols)
        valid = [v for v in sols if satisfies_zero(guard_expr, var, v)]
        return BranchResult(name, guard_text, det_text, transformed, "ok" if valid else "contradiction", unique_sorted(valid))

    valid = [v for v in guard_solutions if satisfies_eq(eq, var, v)]
    return BranchResult(name, guard_text, det_text, transformed, "ok" if valid else "contradiction", unique_sorted(valid))


def branch_nz(name: str, guard_exprs: Sequence[sp.Expr], eq, var: sp.Symbol) -> BranchResult:
    guard_text = " and ".join(f"{sp.sstr(g)} != 0" for g in guard_exprs)
    det_text = " and ".join(N(g) for g in guard_exprs)
    transformed = equation_text(eq)
    sols = solve_eq(eq, var)
    if sols == "all reals":
        return BranchResult(name, guard_text, det_text, transformed, "tautology", f"all real {var} satisfying {guard_text}")
    if isinstance(sols, str):
        return BranchResult(name, guard_text, det_text, transformed, "unsupported", sols)
    valid = [v for v in sols if all(satisfies_nonzero(g, var, v) for g in guard_exprs)]
    return BranchResult(name, guard_text, det_text, transformed, "ok" if valid else "contradiction", unique_sorted(valid))


def solve_from_forms(lhs: SideForm, rhs: SideForm, var: sp.Symbol) -> Tuple[str, List[BranchResult]]:
    # Case 1: A/B = C
    if lhs.is_direct_quotient and not rhs.is_direct_quotient:
        A, B, C = lhs.numerator, lhs.denominator, rhs.expr
        branches = [
            branch_z("Z", B, sp.Eq(A, C), var),
            branch_nz("NZ", [B], sp.Eq(A, B * C), var),
        ]
        return "A/B = C", branches

    # Case 2: C = A/B
    if (not lhs.is_direct_quotient) and rhs.is_direct_quotient:
        C, A, B = lhs.expr, rhs.numerator, rhs.denominator
        branches = [
            branch_z("Z", B, sp.Eq(C, A), var),
            branch_nz("NZ", [B], sp.Eq(B * C, A), var),
        ]
        return "C = A/B", branches

    # Case 3: A/B = C/D
    if lhs.is_direct_quotient and rhs.is_direct_quotient:
        A, B, C, Dd = lhs.numerator, lhs.denominator, rhs.numerator, rhs.denominator
        branches = [
            branch_z("ZZ", sp.simplify(B + 0*Dd), sp.Eq(A, C) if sp.simplify(B - Dd) == 0 else sp.Eq(A, C), var),
            branch_z("ZN", B, sp.Eq(A * Dd, C), var),
            branch_z("NZ", Dd, sp.Eq(A, B * C), var),
            branch_nz("NN", [B, Dd], sp.Eq(A * Dd, B * C), var),
        ]
        # Fix mixed-branch labels/guards/results explicitly.
        zz = branches[0]
        # override ZZ because it needs both zero guards, not one synthetic guard
        guard_B = solve_zero_guard(B, var)
        guard_D = solve_zero_guard(Dd, var)
        if guard_B == [ALL_REALS_GUARD] or guard_D == [ALL_REALS_GUARD]:
            zz = BranchResult("ZZ", f"{sp.sstr(B)} = 0 and {sp.sstr(Dd)} = 0", f"{D(B)} and {D(Dd)}", equation_text(sp.Eq(A, C)), "unsupported", "guard too broad")
        else:
            inter = []
            for vb in guard_B:
                for vd in guard_D:
                    if sp.simplify(vb - vd) == 0:
                        inter.append(vb)
            inter = unique_sorted(inter)
            valid = [v for v in inter if satisfies_eq(sp.Eq(A, C), var, v)]
            zz = BranchResult("ZZ", f"{sp.sstr(B)} = 0 and {sp.sstr(Dd)} = 0", f"{D(B)} and {D(Dd)}", equation_text(sp.Eq(A, C)), "ok" if valid else ("impossible" if not inter else "contradiction"), valid if valid else [])
        zn_eq = sp.Eq(A * Dd, C)
        nz_eq = sp.Eq(A, B * C)
        zn_sols = solve_zero_guard(B, var)
        if zn_sols == [ALL_REALS_GUARD]:
            zn = BranchResult("ZN", f"{sp.sstr(B)} = 0 and {sp.sstr(Dd)} != 0", f"{D(B)} and {N(Dd)}", equation_text(zn_eq), "unsupported", "guard too broad")
        else:
            valid = [v for v in zn_sols if satisfies_eq(zn_eq, var, v) and satisfies_nonzero(Dd, var, v)]
            zn = BranchResult("ZN", f"{sp.sstr(B)} = 0 and {sp.sstr(Dd)} != 0", f"{D(B)} and {N(Dd)}", equation_text(zn_eq), "ok" if valid else ("impossible" if not zn_sols else "contradiction"), unique_sorted(valid))
        nz_sols = solve_zero_guard(Dd, var)
        if nz_sols == [ALL_REALS_GUARD]:
            nz = BranchResult("NZ", f"{sp.sstr(B)} != 0 and {sp.sstr(Dd)} = 0", f"{N(B)} and {D(Dd)}", equation_text(nz_eq), "unsupported", "guard too broad")
        else:
            valid = [v for v in nz_sols if satisfies_eq(nz_eq, var, v) and satisfies_nonzero(B, var, v)]
            nz = BranchResult("NZ", f"{sp.sstr(B)} != 0 and {sp.sstr(Dd)} = 0", f"{N(B)} and {D(Dd)}", equation_text(nz_eq), "ok" if valid else ("impossible" if not nz_sols else "contradiction"), unique_sorted(valid))
        nn = branch_nz("NN", [B, Dd], sp.Eq(A * Dd, B * C), var)
        return "A/B = C/D", [zz, zn, nz, nn]

    raise ValueError("Unsupported equation shape for kernel v1. Use one plain side and/or one direct quotient side, or two direct quotient sides.")


def solve_equation_string(text: str, var_name: str = "x") -> Tuple[str, SideForm, SideForm, List[BranchResult]]:
    lhs_expr, rhs_expr, var = parse_equation(text, var_name)
    lhs_form = direct_quotient_form(lhs_expr)
    rhs_form = direct_quotient_form(rhs_expr)
    case_name, branches = solve_from_forms(lhs_form, rhs_form, var)
    return case_name, lhs_form, rhs_form, branches


def format_report(eq_text: str, case_name: str, lhs_form: SideForm, rhs_form: SideForm, branches: Sequence[BranchResult]) -> str:
    lines = []
    lines.append(f"equation: {eq_text}")
    lines.append(f"detected case: {case_name}")
    lines.append(f"lhs direct quotient: {lhs_form.is_direct_quotient} ; numerator={sp.sstr(lhs_form.numerator)} ; denominator={sp.sstr(lhs_form.denominator)}")
    lines.append(f"rhs direct quotient: {rhs_form.is_direct_quotient} ; numerator={sp.sstr(rhs_form.numerator)} ; denominator={sp.sstr(rhs_form.denominator)}")
    for br in branches:
        lines.append(f"  branch {br.name}:")
        lines.append(f"    guard: {br.guard_text}")
        lines.append(f"    detector: {br.detector_text}")
        lines.append(f"    transformed equation: {br.transformed_equation}")
        lines.append(f"    status: {br.status}")
        lines.append(f"    solutions: {br.solutions}")
    return "\n".join(lines)


DEFAULT_EXAMPLES = [
    "x/(x-1) = 2",
    "(x+1)/(x-1) = 3",
    "2 = (x+2)/x",
    "3 = (x+1)/(x-1)",
    "(x+1)/(x-1) = 3/(x-1)",
    "x/x = (x+1)/(x+1)",
    "x/(x-1) = x",
    "(x+1)/(x-1) = x+1",
    "(x*(x-1))/(x-1) = x-1",
    "(x*(x+1))/x = x",
    "x/(x-1) = 0",
    "(x-1)/(x-1) = 0",
    "x/(x-1) = 1",
    "(x-1)/(x-1) = 1",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Parser-based verifier for branch-equation kernel v1")
    parser.add_argument("equation", nargs="?", help="Equation string like 'x/(x-1) = 2'")
    parser.add_argument("--var", default="x", help="Variable name to solve for (default: x)")
    parser.add_argument("--examples", action="store_true", help="Run the built-in worked examples")
    args = parser.parse_args()

    if args.examples or not args.equation:
        reports = []
        for eq in DEFAULT_EXAMPLES:
            case_name, lhs_form, rhs_form, branches = solve_equation_string(eq, args.var)
            reports.append("=" * 80)
            reports.append(format_report(eq, case_name, lhs_form, rhs_form, branches))
        print("\n".join(reports))
        return

    case_name, lhs_form, rhs_form, branches = solve_equation_string(args.equation, args.var)
    print(format_report(args.equation, case_name, lhs_form, rhs_form, branches))


if __name__ == "__main__":
    main()
