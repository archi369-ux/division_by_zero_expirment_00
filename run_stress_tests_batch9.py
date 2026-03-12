from __future__ import annotations
import sympy as sp
from minimal_guarded_engine import (
    Guard, normalize_with_branching, _normalize_under_guard, q,
    solve_equation_branches, solve_equation_branches_with_residuals,
    extract_solution_branches, format_solution_set,
)

def show_equation_with_residual_solving(lhs: sp.Expr, rhs: sp.Expr) -> None:
    print("=" * 72)
    print("EQ INPUT:", f"{sp.sstr(lhs)} = {sp.sstr(rhs)}")
    for status, br, solved in solve_equation_branches_with_residuals(lhs, rhs):
        if solved is None:
            print(" ", f"[{status}] {br.format()}")
        else:
            print(" ", f"[{status}] {br.format()}  ; solved -> {solved}")
    print()

def show_solution_extraction(lhs: sp.Expr, rhs: sp.Expr) -> None:
    print("=" * 72)
    print("EQ INPUT:", f"{sp.sstr(lhs)} = {sp.sstr(rhs)}")
    sols = extract_solution_branches(lhs, rhs)
    for br in sols:
        print(" ", br.format())
    print(" FINAL:", format_solution_set(sols))
    print()

def main() -> None:
    x = sp.Symbol("x")
    print("\\nBATCH 9 — SOLUTION EXTRACTION\\n")
    show_solution_extraction(q(x, x), sp.Integer(1))
    show_solution_extraction(q(x**2 - 1, x - 1), sp.Integer(3))
    show_solution_extraction(q(x, x - x), sp.Integer(3))
    show_solution_extraction(q(x, x - 1), x)

if __name__ == "__main__":
    main()
