from __future__ import annotations

import sympy as sp
from engine.minimal_guarded_engine import Guard, normalize_with_branching, _normalize_under_guard, q, solve_equation_branches, solve_equation_branches_with_residuals


def show(expr: sp.Expr) -> None:
    print("=" * 72)
    print("INPUT:", sp.sstr(expr))
    branches = normalize_with_branching(expr)
    for br in branches:
        print(" ", br.format())
    print()


def show_under_guard(expr: sp.Expr, *, zero=None, nonzero=None) -> None:
    zero = zero or []
    nonzero = nonzero or []
    g = Guard(
        zero=frozenset(sp.simplify(e) for e in zero),
        nonzero=frozenset(sp.simplify(e) for e in nonzero),
    )
    print("=" * 72)
    print("INPUT:", sp.sstr(expr))
    print("GUARD:", g.format())
    out = _normalize_under_guard(expr, g)
    print("OUTPUT:", sp.sstr(out))
    print()


def main() -> None:
    x, y = sp.symbols("x y")

    # print("\nPRIMITIVE / BRANCH TESTS\n")
    # show(q(sp.Integer(7), sp.Integer(0)))
    # show(q(sp.Integer(0), sp.Integer(0)))
    # show(q(x + 2, x - x))
    # show(q(x, x))
    # show(q(x**2 - 1, x - 1))
    # show(q(x, (x - x) + (y - y)))
    # show(q(x + 1, y))
    # show(q(x, y - y))

    # print("\nGUARDED NORMALIZATION TESTS\n")
    # show_under_guard(q(x, x), nonzero=[x])
    # show_under_guard(q(x**2 - 1, x - 1), nonzero=[x - 1])
    # show_under_guard(q(x**2 - 1, x - 1), zero=[x - 1])
    # show_under_guard(q(x + 1, y), zero=[y])

    # print("\nBATCH 1 — BRANCH PRESSURE\n")
    # show(q(x, (x - x) + (y - y)))
    # show(q(x, x - 1))
    # show(q(x + y, x - x))
    # show(q(x**2 + x, x))

    # print("\nBATCH 2 — FIREWALL PRESSURE\n")
    # show(q(x**2 - 1, x - 1))
    # show(q(x**2 + 2*x + 1, x + 1))
    # show(q(x*y, x))
    # show(sp.Mul(q(x, x), y, evaluate=False))

    # print("\nBATCH 3 — EQUATION PRESSURE (NORMALIZATION ONLY)\n")
    # # We are not solving yet; just inspect both sides branch-safely.
    # print("=" * 72)
    # print("EQ INPUT: x/x = 1")
    # for br in normalize_with_branching(q(x, x)):
    #     print(" ", br.format(), " ; RHS -> 1")
    # print()

    # print("=" * 72)
    # print("EQ INPUT: (x^2 - 1)/(x - 1) = 3")
    # for br in normalize_with_branching(q(x**2 - 1, x - 1)):
    #     print(" ", br.format(), " ; RHS -> 3")
    # print()

    # print("=" * 72)
    # print("EQ INPUT: x/(x - 1) = x")
    # for br in normalize_with_branching(q(x, x - 1)):
    #     print(" ", br.format(), " ; RHS -> x")
    # print()

    # print("=" * 72)
    # print("EQ INPUT: x/(x - x) = 3")
    # for br in normalize_with_branching(q(x, x - x)):
    #     print(" ", br.format(), " ; RHS -> 3")
    # print()

    # print("\nBATCH 4 — MULTI-DENOMINATOR PRESSURE\n")
    # show(q(x, y))
    # show(q(x, x - 1) + q(1, x))
    # show(q(x, x - 1) * q(1, x))
    # show(q(x, x) + q(y, y))

    # print("\nBATCH 5 — FIREWALL TRAPS\n")
    # show(q(x*(x + 1), x))
    # show(q((x - 1)*(x + 1), x - 1))
    # show(sp.Mul(q(x, x), q(y, y), evaluate=False))
    # show(sp.Mul(q(x, x - 1), x - 1, evaluate=False))

    # print("\nBATCH 6 — PRE-SOLVER EQUATION PRESSURE\n")
    # for br in normalize_with_branching(q(x*(x + 1), x)):
    #     print(" ", br.format(), " ; RHS -> x + 1")
    # print()

    # print("\nBATCH 7 — MINIMAL SOLVER CLASSIFICATION\n")
    # show_equation(q(x, x), sp.Integer(1))
    # show_equation(q(x**2 - 1, x - 1), sp.Integer(3))
    # show_equation(q(x, x - x), sp.Integer(3))
    # show_equation(q(x, x - 1), x)

    print("\nBATCH 8 — SIMPLE RESIDUAL SOLVING\n")
    show_equation_with_residual_solving(q(x, x), sp.Integer(1))
    show_equation_with_residual_solving(q(x**2 - 1, x - 1), sp.Integer(3))
    show_equation_with_residual_solving(q(x, x - x), sp.Integer(3))
    show_equation_with_residual_solving(q(x, x - 1), x)

    for br in normalize_with_branching(q((x - 1)*(x + 1), x - 1)):
        print(" ", br.format(), " ; RHS -> x + 1")
    print()

    for br in normalize_with_branching(q(x, y)):
        print(" ", br.format(), " ; RHS -> 1")
    print()

    print("\nNOTES\n")
    print("- This runner is safety-oriented, not completeness-oriented.")
    print("- Partial results are acceptable if the firewall is preserved.")
    print("- A wrong simplification is worse than an incomplete simplification.")

def show_equation(lhs: sp.Expr, rhs: sp.Expr) -> None:
    print("=" * 72)
    print("EQ INPUT:", f"{sp.sstr(lhs)} = {sp.sstr(rhs)}")
    for status, br in solve_equation_branches(lhs, rhs):
        print(" ", f"[{status}] {br.format()}")
    print()

def show_equation_with_residual_solving(lhs: sp.Expr, rhs: sp.Expr) -> None:
    print("=" * 72)
    print("EQ INPUT:", f"{sp.sstr(lhs)} = {sp.sstr(rhs)}")
    for status, br, solved in solve_equation_branches_with_residuals(lhs, rhs):
        if solved is None:
            print(" ", f"[{status}] {br.format()}")
        else:
            print(" ", f"[{status}] {br.format()}  ; solved -> {solved}")
    print()   

if __name__ == "__main__":
    main()