from __future__ import annotations
import sympy as sp
from division_by_zero_repo_bundle.engine.minimal_guarded_engine import (
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

    print("\nBATCH 10 — SOLVER SOUNDNESS TEST SUITE V1\n")

    x, y = sp.symbols("x y")

    # Category A
    show_solution_extraction(q(x, x), sp.Integer(1))
    show_solution_extraction(q(x, x), sp.Integer(0))
    show_solution_extraction(q(x, x), sp.Integer(2))
    show_equation_with_residual_solving(sp.Mul(q(x, x), y, evaluate=False), y)

    # Category B
    show_solution_extraction(q(x**2 - 1, x - 1), sp.Integer(3))
    show_solution_extraction(q((x - 1)*(x + 1), x - 1), sp.Integer(0))
    show_solution_extraction(q(x*(x + 1), x), sp.Integer(3))
    show_solution_extraction(q(x*(x + 1), x), x + 1)

    # Category C
    show_solution_extraction(sp.Mul(q(x, x - 1), x - 1, evaluate=False), x)
    show_solution_extraction(sp.Mul(q(x, x - 1), x - 1, evaluate=False), sp.Integer(0))
    show_equation_with_residual_solving(sp.Mul(q(x, x), q(y, y), evaluate=False), sp.Integer(1))

    # Category D
    show_solution_extraction(q(x, x - 1), x)
    show_solution_extraction(q(x, x - 1), sp.Integer(1))
    show_solution_extraction(q(x, x - x), x)
    show_solution_extraction(q(x, x - x), x + 1)

    # Category E
    show_solution_extraction(q(x**2 - 1, x - 1), x + 1)
    show_solution_extraction(q(x, x - x), sp.Integer(3))
    show_solution_extraction(q(x + 2, x - x), sp.Integer(5))
    show_solution_extraction(q(x + 2, x - x), x + 2)

    #Category F
    show_equation_with_residual_solving(q(x, x - 1) + q(1, x), sp.Integer(2))
    show_equation_with_residual_solving(q(x, y), sp.Integer(1))
    show_equation_with_residual_solving(q(x, x) + q(y, y), sp.Integer(2))

    print("\nBATCH 11 — GUARDED RESIDUAL EXTRACTION\n")
    show_solution_extraction(sp.Mul(q(x, x), y, evaluate=False), y)
    show_solution_extraction(sp.Mul(q(x, x), q(y, y), evaluate=False), sp.Integer(1))
    show_solution_extraction(q(x, y), sp.Integer(1))
    show_solution_extraction(q(x, x - 1) + q(1, x), sp.Integer(2))

if __name__ == "__main__":
    main()
