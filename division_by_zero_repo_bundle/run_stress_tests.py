from __future__ import annotations

import sympy as sp
from division_by_zero_repo_bundle.oldies.minimal_guarded_engine import Guard, normalize_with_branching, _normalize_under_guard, q


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

    print("\nPRIMITIVE / BRANCH TESTS\n")
    show(q(sp.Integer(7), sp.Integer(0)))
    show(q(sp.Integer(0), sp.Integer(0)))
    show(q(x + 2, x - x))
    show(q(x, x))
    show(q(x**2 - 1, x - 1))
    show(q(x, (x - x) + (y - y)))
    show(q(x + 1, y))
    show(q(x, y - y))

    print("\nGUARDED NORMALIZATION TESTS\n")
    show_under_guard(q(x, x), nonzero=[x])
    show_under_guard(q(x**2 - 1, x - 1), nonzero=[x - 1])
    show_under_guard(q(x**2 - 1, x - 1), zero=[x - 1])
    show_under_guard(q(x + 1, y), zero=[y])

    print("\nNOTES\n")
    print("- This runner is safety-oriented, not completeness-oriented.")
    print("- Partial results are acceptable if the firewall is preserved.")
    print("- A wrong simplification is worse than an incomplete simplification.")


if __name__ == "__main__":
    main()