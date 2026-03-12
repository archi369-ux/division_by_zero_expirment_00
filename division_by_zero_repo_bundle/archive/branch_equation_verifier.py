
"""
Branch Arithmetic Equation Solver Draft v1 - simple verifier

Scope:
- one-variable verification helper for the seven kernel cases
- branch-first solving only
- guards kept explicit
- detector labels attached for each denominator where possible

This is not a full CAS and does not attempt unrestricted simplification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Union, Optional

import sympy as sp


@dataclass
class BranchResult:
    name: str
    guard_text: str
    detector_text: str
    equation_text: str
    solutions: Union[List[sp.Expr], str]
    status: str  # "ok", "contradiction", "tautology", "impossible"


def D(expr: sp.Expr) -> str:
    return f"D_({sp.sstr(expr)}) = 1"


def N(expr: sp.Expr) -> str:
    return f"N_({sp.sstr(expr)}) = 1"


def parse_expr(s: str, var_name: str = "x") -> sp.Expr:
    var = sp.Symbol(var_name, real=True)
    locals_map = {var_name: var}
    return sp.sympify(s, locals=locals_map)


def unique_sorted(values: List[sp.Expr]) -> List[sp.Expr]:
    out: List[sp.Expr] = []
    for v in values:
        if all(sp.simplify(v - w) != 0 for w in out):
            out.append(sp.simplify(v))
    return sorted(out, key=sp.default_sort_key)


def solve_guard_eq(guard_eq: sp.Expr, var: sp.Symbol) -> List[sp.Expr]:
    # solves guard_eq = 0
    sols = sp.solveset(sp.Eq(guard_eq, 0), var, domain=sp.S.Reals)
    if sols is sp.S.EmptySet:
        return []
    if isinstance(sols, sp.FiniteSet):
        return unique_sorted(list(sols))
    return [sp.Symbol("ALL_REALS_GUARD")]  # fallback marker




def equation_text_of(branch_eq) -> str:
    if branch_eq is sp.S.true or branch_eq == True:
        return "True"
    if branch_eq is sp.S.false or branch_eq == False:
        return "False"
    return f"{sp.sstr(branch_eq.lhs)} = {sp.sstr(branch_eq.rhs)}"


def solve_main_eq(eq, var: sp.Symbol) -> Union[List[sp.Expr], str]:
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


def satisfies_nonzero(expr: sp.Expr, var: sp.Symbol, value: sp.Expr) -> bool:
    return sp.simplify(expr.subs(var, value)) != 0


def make_branch_result(name: str, guard_text: str, detector_text: str, equation_text: str,
                       solutions: Union[List[sp.Expr], str], status: str) -> BranchResult:
    return BranchResult(name, guard_text, detector_text, equation_text, solutions, status)


def solve_branch_z(guard_expr: sp.Expr, branch_eq: sp.Eq, var: sp.Symbol) -> BranchResult:
    guard_solutions = solve_guard_eq(guard_expr, var)
    guard_text = f"{sp.sstr(guard_expr)} = 0"
    detector_text = D(guard_expr)
    equation_text = equation_text_of(branch_eq)
    if not guard_solutions:
        return make_branch_result("Z", guard_text, detector_text, equation_text, [], "impossible")

    if guard_solutions == [sp.Symbol("ALL_REALS_GUARD")]:
        return make_branch_result("Z", guard_text, detector_text, equation_text, "guard too broad", "unsupported")

    valid = [v for v in guard_solutions if satisfies_eq(branch_eq, var, v)]
    if not valid:
        return make_branch_result("Z", guard_text, detector_text, equation_text, [], "contradiction")
    return make_branch_result("Z", guard_text, detector_text, equation_text, unique_sorted(valid), "ok")


def solve_branch_nz(guard_exprs: List[sp.Expr], branch_eq: sp.Eq, var: sp.Symbol) -> BranchResult:
    guard_text = " and ".join(f"{sp.sstr(g)} != 0" for g in guard_exprs)
    detector_text = " and ".join(N(g) for g in guard_exprs)
    equation_text = equation_text_of(branch_eq)

    sols = solve_main_eq(branch_eq, var)
    if sols == "all reals":
        return make_branch_result("NZ", guard_text, detector_text, equation_text,
                                  f"all real {var} satisfying {guard_text}", "tautology")
    if isinstance(sols, str):
        return make_branch_result("NZ", guard_text, detector_text, equation_text, sols, "unsupported")

    valid = []
    for v in sols:
        if all(satisfies_nonzero(g, var, v) for g in guard_exprs):
            valid.append(v)

    if not valid:
        return make_branch_result("NZ", guard_text, detector_text, equation_text, [], "contradiction")
    return make_branch_result("NZ", guard_text, detector_text, equation_text, unique_sorted(valid), "ok")


def solve_case(case_type: str, A: str, B: str, C: str, D_expr: Optional[str] = None,
               var_name: str = "x") -> Dict[str, Union[str, List[BranchResult]]]:
    x = sp.Symbol(var_name, real=True)
    A_e = parse_expr(A, var_name)
    B_e = parse_expr(B, var_name)
    C_e = parse_expr(C, var_name)
    D_e = parse_expr(D_expr, var_name) if D_expr is not None else None

    branches: List[BranchResult] = []

    if case_type == "AB_eq_C":
        branches.append(solve_branch_z(B_e, sp.Eq(A_e, C_e), x))
        branches.append(solve_branch_nz([B_e], sp.Eq(A_e, B_e * C_e), x))

    elif case_type == "C_eq_AB":
        branches.append(solve_branch_z(B_e, sp.Eq(C_e, A_e), x))
        branches.append(solve_branch_nz([B_e], sp.Eq(B_e * C_e, A_e), x))

    elif case_type == "AB_eq_CD":
        assert D_e is not None
        # ZZ
        zz_guard_solutions = solve_guard_eq(B_e, x)
        dd_guard_solutions = solve_guard_eq(D_e, x)
        if zz_guard_solutions and dd_guard_solutions and zz_guard_solutions != [sp.Symbol("ALL_REALS_GUARD")] and dd_guard_solutions != [sp.Symbol("ALL_REALS_GUARD")]:
            inter = [v for v in zz_guard_solutions for w in dd_guard_solutions if sp.simplify(v - w) == 0]
            inter = unique_sorted(inter)
            if inter:
                eq = sp.Eq(A_e, C_e)
                valid = [v for v in inter if satisfies_eq(eq, x, v)]
                branches.append(make_branch_result(
                    "ZZ",
                    f"{sp.sstr(B_e)} = 0 and {sp.sstr(D_e)} = 0",
                    f"{D(B_e)} and {D(D_e)}",
                    f"{sp.sstr(A_e)} = {sp.sstr(C_e)}",
                    valid if valid else [],
                    "ok" if valid else "contradiction"
                ))
            else:
                branches.append(make_branch_result(
                    "ZZ",
                    f"{sp.sstr(B_e)} = 0 and {sp.sstr(D_e)} = 0",
                    f"{D(B_e)} and {D(D_e)}",
                    f"{sp.sstr(A_e)} = {sp.sstr(C_e)}",
                    [],
                    "impossible"
                ))
        else:
            branches.append(make_branch_result(
                "ZZ",
                f"{sp.sstr(B_e)} = 0 and {sp.sstr(D_e)} = 0",
                f"{D(B_e)} and {D(D_e)}",
                f"{sp.sstr(A_e)} = {sp.sstr(C_e)}",
                "unsupported",
                "unsupported"
            ))

        # ZN
        guard_solutions = solve_guard_eq(B_e, x)
        if guard_solutions and guard_solutions != [sp.Symbol("ALL_REALS_GUARD")]:
            eq = sp.Eq(A_e * D_e, C_e)
            valid = [v for v in guard_solutions if satisfies_eq(eq, x, v) and satisfies_nonzero(D_e, x, v)]
            branches.append(make_branch_result(
                "ZN",
                f"{sp.sstr(B_e)} = 0 and {sp.sstr(D_e)} != 0",
                f"{D(B_e)} and {N(D_e)}",
                f"{sp.sstr(A_e * D_e)} = {sp.sstr(C_e)}",
                valid if valid else [],
                "ok" if valid else "contradiction"
            ))
        else:
            branches.append(make_branch_result(
                "ZN",
                f"{sp.sstr(B_e)} = 0 and {sp.sstr(D_e)} != 0",
                f"{D(B_e)} and {N(D_e)}",
                f"{sp.sstr(A_e * D_e)} = {sp.sstr(C_e)}",
                [],
                "impossible"
            ))

        # NZ
        guard_solutions = solve_guard_eq(D_e, x)
        if guard_solutions and guard_solutions != [sp.Symbol("ALL_REALS_GUARD")]:
            eq = sp.Eq(A_e, B_e * C_e)
            valid = [v for v in guard_solutions if satisfies_eq(eq, x, v) and satisfies_nonzero(B_e, x, v)]
            branches.append(make_branch_result(
                "NZ",
                f"{sp.sstr(B_e)} != 0 and {sp.sstr(D_e)} = 0",
                f"{N(B_e)} and {D(D_e)}",
                f"{sp.sstr(A_e)} = {sp.sstr(B_e * C_e)}",
                valid if valid else [],
                "ok" if valid else "contradiction"
            ))
        else:
            branches.append(make_branch_result(
                "NZ",
                f"{sp.sstr(B_e)} != 0 and {sp.sstr(D_e)} = 0",
                f"{N(B_e)} and {D(D_e)}",
                f"{sp.sstr(A_e)} = {sp.sstr(B_e * C_e)}",
                [],
                "impossible"
            ))

        # NN
        branches.append(solve_branch_nz([B_e, D_e], sp.Eq(A_e * D_e, B_e * C_e), x))

    elif case_type == "AB_eq_A":
        branches.append(solve_branch_z(B_e, sp.Eq(A_e, A_e), x))
        branches.append(solve_branch_nz([B_e], sp.Eq(A_e, A_e * B_e), x))

    elif case_type == "AB_eq_B":
        branches.append(solve_branch_z(B_e, sp.Eq(A_e, B_e), x))
        branches.append(solve_branch_nz([B_e], sp.Eq(A_e, B_e**2), x))

    elif case_type == "AB_eq_0":
        zero = sp.Integer(0)
        branches.append(solve_branch_z(B_e, sp.Eq(A_e, zero), x))
        branches.append(solve_branch_nz([B_e], sp.Eq(A_e, zero), x))

    elif case_type == "AB_eq_1":
        one = sp.Integer(1)
        branches.append(solve_branch_z(B_e, sp.Eq(A_e, one), x))
        branches.append(solve_branch_nz([B_e], sp.Eq(A_e, B_e), x))

    else:
        raise ValueError(f"Unsupported case type: {case_type}")

    return {
        "case_type": case_type,
        "A": sp.sstr(A_e),
        "B": sp.sstr(B_e),
        "C": sp.sstr(C_e),
        "D": sp.sstr(D_e) if D_e is not None else None,
        "branches": branches,
    }


def pretty_print(result: Dict[str, Union[str, List[BranchResult]]]) -> str:
    lines = []
    lines.append(f"case_type: {result['case_type']}")
    for br in result["branches"]:
        lines.append(f"  branch {br.name}:")
        lines.append(f"    guard: {br.guard_text}")
        lines.append(f"    detector: {br.detector_text}")
        lines.append(f"    transformed equation: {br.equation_text}")
        lines.append(f"    status: {br.status}")
        lines.append(f"    solutions: {br.solutions}")
    return "\n".join(lines)


EXAMPLES = [
    ("Case 1 / Example 1", dict(case_type="AB_eq_C", A="x", B="x-1", C="2")),
    ("Case 1 / Example 2", dict(case_type="AB_eq_C", A="x+1", B="x-1", C="3")),
    ("Case 2 / Example 1", dict(case_type="C_eq_AB", A="x+2", B="x", C="2")),
    ("Case 2 / Example 2", dict(case_type="C_eq_AB", A="x+1", B="x-1", C="3")),
    ("Case 3 / Example 1", dict(case_type="AB_eq_CD", A="x+1", B="x-1", C="3", D_expr="x-1")),
    ("Case 3 / Example 2", dict(case_type="AB_eq_CD", A="x", B="x", C="x+1", D_expr="x+1")),
    ("Case 4 / Example 1", dict(case_type="AB_eq_A", A="x", B="x-1", C="unused")),
    ("Case 4 / Example 2", dict(case_type="AB_eq_A", A="x+1", B="x-1", C="unused")),
    ("Case 5 / Example 1", dict(case_type="AB_eq_B", A="x*(x-1)", B="x-1", C="unused")),
    ("Case 5 / Example 2", dict(case_type="AB_eq_B", A="x*(x+1)", B="x", C="unused")),
    ("Case 6 / Example 1", dict(case_type="AB_eq_0", A="x", B="x-1", C="unused")),
    ("Case 6 / Example 2", dict(case_type="AB_eq_0", A="x-1", B="x-1", C="unused")),
    ("Case 7 / Example 1", dict(case_type="AB_eq_1", A="x", B="x-1", C="unused")),
    ("Case 7 / Example 2", dict(case_type="AB_eq_1", A="x-1", B="x-1", C="unused")),
]


def run_examples() -> str:
    chunks = []
    for title, spec in EXAMPLES:
        chunks.append("=" * 72)
        chunks.append(title)
        res = solve_case(**spec)
        chunks.append(pretty_print(res))
    return "\n".join(chunks)


if __name__ == "__main__":
    print(run_examples())
