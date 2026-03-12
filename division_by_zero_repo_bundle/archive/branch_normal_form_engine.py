from __future__ import annotations

"""
Small branch-normal-form engine for the current division-by-zero theory.

Scope:
- parses a single-variable equation string like "x/((x-x)+1) = 2"
- preserves top-level quotient structure before solving
- normalizes *denominators only* using safe hidden-zero rules
- classifies each denominator as ZERO / NONZERO / UNKNOWN
- emits guarded branches using detector notation D_f and N_f
- solves the branch-local transformed equations over the reals

Important limits:
- this is a practical verifier, not a full theorem prover or CAS
- it does not do unrestricted algebra before branch split
- hidden-zero detection is conservative and denominator-local
"""

from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple, Union
import argparse
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr as sympy_parse_expr


# ----------------------------- data models -----------------------------

@dataclass
class SideForm:
    expr: sp.Expr
    numerator: sp.Expr
    denominator: sp.Expr
    is_direct_quotient: bool


@dataclass
class DenominatorInfo:
    original: sp.Expr
    normalized: sp.Expr
    classification: str  # ZERO / NONZERO / UNKNOWN
    reason: str


@dataclass
class BranchResult:
    name: str
    guard_text: str
    detector_text: str
    transformed_equation: str
    status: str
    solutions: Union[str, List[sp.Expr]]


ALL_REALS_GUARD = sp.Symbol("ALL_REALS_GUARD")


# ----------------------------- parsing -----------------------------


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


# ----------------------------- top-level quotient detection -----------------------------


def mul_of(exprs: Sequence[sp.Expr]) -> sp.Expr:
    if not exprs:
        return sp.Integer(1)
    out = exprs[0]
    for e in exprs[1:]:
        out = sp.Mul(out, e, evaluate=False)
    return out


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
            return SideForm(expr, mul_of(numer_factors), denom_factors[0], True)
        return SideForm(expr, expr, sp.Integer(1), False)

    return SideForm(expr, expr, sp.Integer(1), False)


# ----------------------------- denominator normalization -----------------------------


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


def _coeff_and_core(term: sp.Expr) -> Tuple[sp.Expr, sp.Expr]:
    coeff, core = term.as_coeff_Mul(rational=True)
    return sp.simplify(coeff), core


def _flatten_add(expr: sp.Expr) -> List[sp.Expr]:
    if isinstance(expr, sp.Add):
        out: List[sp.Expr] = []
        for a in expr.args:
            out.extend(_flatten_add(a))
        return out
    return [expr]


def _flatten_mul(expr: sp.Expr) -> List[sp.Expr]:
    if isinstance(expr, sp.Mul):
        out: List[sp.Expr] = []
        for a in expr.args:
            out.extend(_flatten_mul(a))
        return out
    return [expr]


def _make_frac(numer: sp.Expr, denom: sp.Expr) -> sp.Expr:
    return sp.Mul(numer, sp.Pow(denom, -1, evaluate=False), evaluate=False)


def normalize_denominator(expr: sp.Expr) -> sp.Expr:
    """
    Safe denominator-local normalizer.

    Design choices:
    - recursive, denominator-local only
    - /0 inside the denominator is treated as erasure: A/0 -> A
    - 0/x -> 0 follows from zero factor propagation
    - additive cancellation and coefficient merging are allowed
    - bounded visible regrouping is allowed by canonical additive merging
    - no unrestricted expansion and no main-quotient cancellation exist here
    """
    prev = None
    cur = expr
    for _ in range(20):
        new = _normalize_den_once(cur)
        if sp.srepr(new) == sp.srepr(cur):
            return new
        prev, cur = cur, new
    return cur


def _normalize_den_once(expr: sp.Expr) -> sp.Expr:
    # atoms
    if expr.is_Atom:
        return expr

    # powers
    if isinstance(expr, sp.Pow):
        base = normalize_denominator(expr.base)
        exp = normalize_denominator(expr.exp)
        if exp == -1:
            if base == 0:
                # 1/0 -> 1 by erasing /0 from numerator 1
                return sp.Integer(1)
            if base == 1:
                return sp.Integer(1)
            return sp.Pow(base, -1, evaluate=False)
        return sp.Pow(base, exp, evaluate=False)

    # multiplication / quotient-shape handling
    if isinstance(expr, sp.Mul):
        args = [normalize_denominator(a) for a in _flatten_mul(expr)]

        # partition numerator-like and denominator-like factors
        numer: List[sp.Expr] = []
        denom: List[sp.Expr] = []
        for a in args:
            if isinstance(a, sp.Pow) and a.exp == -1:
                denom.append(normalize_denominator(a.base))
            else:
                numer.append(a)

        # zero propagation from numerator-like factors => 0/x -> 0 and 0*X -> 0
        if any(a == 0 for a in numer):
            return sp.Integer(0)

        # erase denominator factors that normalize to zero: A/0 -> A
        denom = [d for d in denom if d != 0]

        # strip 1s
        numer = [a for a in numer if a != 1]
        denom = [d for d in denom if d != 1]

        # if denominator now empty, rebuild numerator product only
        if not denom:
            if not numer:
                return sp.Integer(1)
            numer = sorted(numer, key=_sort_key)
            return _build_mul(numer)

        numer = sorted(numer, key=_sort_key)
        denom = sorted(denom, key=_sort_key)
        n_expr = _build_mul(numer) if numer else sp.Integer(1)
        d_expr = _build_mul(denom)

        # tiny literal rational evaluation only
        if n_expr.is_number and d_expr.is_number and d_expr != 0:
            return sp.simplify(n_expr / d_expr)

        return _make_frac(n_expr, d_expr)

    # addition with hidden-zero detection
    if isinstance(expr, sp.Add):
        terms = [normalize_denominator(a) for a in _flatten_add(expr)]

        # remove zeros first
        terms = [t for t in terms if t != 0]
        if not terms:
            return sp.Integer(0)

        # coefficient merge for identical canonical cores
        buckets: dict[str, Tuple[sp.Expr, sp.Expr]] = {}
        for t in terms:
            coeff, core = _coeff_and_core(t)
            key = sp.srepr(core)
            if key not in buckets:
                buckets[key] = (coeff, core)
            else:
                old_coeff, old_core = buckets[key]
                buckets[key] = (sp.simplify(old_coeff + coeff), old_core)

        merged: List[sp.Expr] = []
        for coeff, core in buckets.values():
            coeff = sp.simplify(coeff)
            if coeff == 0:
                continue
            if core == 1:
                merged.append(coeff)
            elif coeff == 1:
                merged.append(core)
            else:
                merged.append(sp.Mul(coeff, core, evaluate=False))

        if not merged:
            return sp.Integer(0)

        # bounded visible regrouping: F*U + F*V + ... -> F*(U+V+...) and right-factor analog
        regrouped = _group_visible_common_factors(merged)
        if regrouped is not None:
            return normalize_denominator(regrouped)

        merged = sorted(merged, key=_sort_key)
        return _build_add(merged)

    # generic fallback: recursively normalize args and rebuild
    new_args = [normalize_denominator(a) for a in expr.args]
    return expr.func(*new_args, evaluate=False)


def _group_visible_common_factors(terms: Sequence[sp.Expr]) -> Optional[sp.Expr]:
    """
    Bounded regrouping over direct additive siblings only.

    Strategy:
    - look for a visible common *left or right factor* shared by >= 2 terms
    - if regrouping decreases top-level term count, keep it
    - one regrouping at a time, then re-normalize
    """
    if len(terms) < 2:
        return None

    # Build candidate maps for left and right visible factors on explicit products only.
    left_groups: dict[str, Tuple[sp.Expr, List[Tuple[int, sp.Expr]]]] = {}
    right_groups: dict[str, Tuple[sp.Expr, List[Tuple[int, sp.Expr]]]] = {}

    for idx, t in enumerate(terms):
        coeff, core = _coeff_and_core(t)
        if isinstance(core, sp.Mul):
            factors = list(_flatten_mul(core))
            if len(factors) >= 2:
                left = factors[0]
                right = factors[-1]
                left_rest = _build_mul(factors[1:])
                right_rest = _build_mul(factors[:-1])
                signed_left_rest = left_rest if coeff == 1 else sp.Mul(coeff, left_rest, evaluate=False)
                signed_right_rest = right_rest if coeff == 1 else sp.Mul(coeff, right_rest, evaluate=False)
                lk = sp.srepr(left)
                rk = sp.srepr(right)
                left_groups.setdefault(lk, (left, []) )[1].append((idx, signed_left_rest))
                right_groups.setdefault(rk, (right, []))[1].append((idx, signed_right_rest))

    best_expr: Optional[sp.Expr] = None
    best_reduction = 0

    def try_group(groups, side: str):
        nonlocal best_expr, best_reduction
        for _, (factor, items) in groups.items():
            if len(items) < 2:
                continue
            idxs = [i for i, _ in items]
            inner_terms = [r for _, r in items]
            grouped_inner = normalize_denominator(_build_add(inner_terms))
            grouped_term = (
                sp.Mul(factor, grouped_inner, evaluate=False)
                if side == 'left'
                else sp.Mul(grouped_inner, factor, evaluate=False)
            )
            remaining = [t for j, t in enumerate(terms) if j not in idxs]
            candidate_terms = remaining + [grouped_term]
            reduction = len(terms) - len(candidate_terms)
            if reduction > 0:
                candidate = normalize_denominator(_build_add(candidate_terms))
                if reduction > best_reduction:
                    best_reduction = reduction
                    best_expr = candidate

    try_group(left_groups, 'left')
    try_group(right_groups, 'right')
    return best_expr


# ----------------------------- classification -----------------------------


def classify_denominator(expr: sp.Expr) -> DenominatorInfo:
    normalized = normalize_denominator(expr)
    simplified = sp.simplify(normalized)
    if normalized == 0:
        return DenominatorInfo(expr, normalized, "ZERO", "normalized exactly to 0")
    if simplified == 0:
        return DenominatorInfo(expr, simplified, "ZERO", "simplified normalized denominator to 0")
    if normalized.is_number and normalized != 0:
        return DenominatorInfo(expr, normalized, "NONZERO", "normalized to explicit nonzero numeric literal")
    if simplified.is_number and simplified != 0:
        return DenominatorInfo(expr, simplified, "NONZERO", "simplified normalized denominator to explicit nonzero numeric literal")
    # conservative symbolic nonzero tests
    if normalized.is_Symbol:
        return DenominatorInfo(expr, normalized, "UNKNOWN", "symbolic denominator")
    if normalized.is_number:
        return DenominatorInfo(expr, normalized, "UNKNOWN", "number status unclear")
    return DenominatorInfo(expr, normalized, "UNKNOWN", "no safe proof of zero or nonzero")


# ----------------------------- equation helpers -----------------------------


def equation_text(eq) -> str:
    if eq is sp.S.true or eq == True:
        return "True"
    if eq is sp.S.false or eq == False:
        return "False"
    return f"{sp.sstr(eq.lhs)} = {sp.sstr(eq.rhs)}"


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


# ----------------------------- guarded branch builders -----------------------------


def branch_z(name: str, guard_info: DenominatorInfo, eq, var: sp.Symbol) -> BranchResult:
    guard_expr = guard_info.normalized
    guard_text = f"{sp.sstr(guard_expr)} = 0"
    det_text = D(guard_expr)
    transformed = equation_text(eq)

    if guard_info.classification == "ZERO":
        sols = solve_eq(eq, var)
        if sols == "all reals":
            return BranchResult(name, guard_text, det_text, transformed, "tautology", f"all real {var} satisfying {guard_text}")
        if isinstance(sols, str):
            return BranchResult(name, guard_text, det_text, transformed, "unsupported", sols)
        valid = [v for v in sols if satisfies_zero(guard_expr, var, v)]
        if sols == []:
            return BranchResult(name, guard_text, det_text, transformed, "contradiction", [])
        return BranchResult(name, guard_text, det_text, transformed, "ok" if valid else "contradiction", unique_sorted(valid))

    guard_solutions = solve_zero_guard(guard_expr, var)
    if not guard_solutions:
        return BranchResult(name, guard_text, det_text, transformed, "impossible", [])
    if guard_solutions == [ALL_REALS_GUARD]:
        sols = solve_eq(eq, var)
        if sols == "all reals":
            return BranchResult(name, guard_text, det_text, transformed, "tautology", f"all real {var} satisfying {guard_text}")
        if isinstance(sols, str):
            return BranchResult(name, guard_text, det_text, transformed, "unsupported", sols)
        valid = [v for v in sols if satisfies_zero(guard_expr, var, v)]
        return BranchResult(name, guard_text, det_text, transformed, "ok" if valid else "contradiction", unique_sorted(valid))

    valid = [v for v in guard_solutions if satisfies_eq(eq, var, v)]
    return BranchResult(name, guard_text, det_text, transformed, "ok" if valid else "contradiction", unique_sorted(valid))


def branch_nz(name: str, guard_infos: Sequence[DenominatorInfo], eq, var: sp.Symbol) -> BranchResult:
    guard_exprs = [g.normalized for g in guard_infos]
    guard_text = " and ".join(f"{sp.sstr(g)} != 0" for g in guard_exprs)
    det_text = " and ".join(N(g) for g in guard_exprs)
    transformed = equation_text(eq)

    if all(g.classification == "NONZERO" for g in guard_infos):
        sols = solve_eq(eq, var)
        if sols == "all reals":
            return BranchResult(name, guard_text, det_text, transformed, "tautology", f"all real {var} satisfying {guard_text}")
        return BranchResult(name, guard_text, det_text, transformed, "ok" if sols else "contradiction", sols)

    sols = solve_eq(eq, var)
    if sols == "all reals":
        return BranchResult(name, guard_text, det_text, transformed, "tautology", f"all real {var} satisfying {guard_text}")
    if isinstance(sols, str):
        return BranchResult(name, guard_text, det_text, transformed, "unsupported", sols)
    valid = [v for v in sols if all(satisfies_nonzero(g, var, v) for g in guard_exprs)]
    return BranchResult(name, guard_text, det_text, transformed, "ok" if valid else "contradiction", unique_sorted(valid))


# ----------------------------- solver kernel -----------------------------


def solve_from_forms(lhs: SideForm, rhs: SideForm, var: sp.Symbol) -> Tuple[str, List[BranchResult], List[DenominatorInfo]]:
    infos: List[DenominatorInfo] = []

    # Case 1: A/B = C
    if lhs.is_direct_quotient and not rhs.is_direct_quotient:
        A, B, C = lhs.numerator, lhs.denominator, rhs.expr
        Binfo = classify_denominator(B)
        infos = [Binfo]
        branches = [
            branch_z("Z", Binfo, sp.Eq(A, C), var),
            branch_nz("NZ", [Binfo], sp.Eq(A, Binfo.normalized * C), var),
        ]
        return "A/B = C", branches, infos

    # Case 2: C = A/B
    if (not lhs.is_direct_quotient) and rhs.is_direct_quotient:
        C, A, B = lhs.expr, rhs.numerator, rhs.denominator
        Binfo = classify_denominator(B)
        infos = [Binfo]
        branches = [
            branch_z("Z", Binfo, sp.Eq(C, A), var),
            branch_nz("NZ", [Binfo], sp.Eq(Binfo.normalized * C, A), var),
        ]
        return "C = A/B", branches, infos

    # Case 3: A/B = C/D
    if lhs.is_direct_quotient and rhs.is_direct_quotient:
        A, B, C, Dd = lhs.numerator, lhs.denominator, rhs.numerator, rhs.denominator
        Binfo = classify_denominator(B)
        Dinfo = classify_denominator(Dd)
        infos = [Binfo, Dinfo]
        zz_eq = sp.Eq(A, C)
        zn_eq = sp.Eq(A * Dinfo.normalized, C)
        nz_eq = sp.Eq(A, Binfo.normalized * C)
        nn_eq = sp.Eq(A * Dinfo.normalized, Binfo.normalized * C)
        # Explicit mixed guards because they depend on different denominators.
        zz = _two_zero_branch("ZZ", Binfo, Dinfo, zz_eq, var)
        zn = _one_zero_one_nonzero_branch("ZN", Binfo, Dinfo, zn_eq, var)
        nz = _one_nonzero_one_zero_branch("NZ", Binfo, Dinfo, nz_eq, var)
        nn = branch_nz("NN", [Binfo, Dinfo], nn_eq, var)
        return "A/B = C/D", [zz, zn, nz, nn], infos

    raise ValueError("Unsupported equation shape for kernel v1. Use one plain side and/or one direct quotient side, or two direct quotient sides.")


def _two_zero_branch(name: str, Binfo: DenominatorInfo, Dinfo: DenominatorInfo, eq, var: sp.Symbol) -> BranchResult:
    guard_text = f"{sp.sstr(Binfo.normalized)} = 0 and {sp.sstr(Dinfo.normalized)} = 0"
    det_text = f"{D(Binfo.normalized)} and {D(Dinfo.normalized)}"
    transformed = equation_text(eq)
    sb = solve_zero_guard(Binfo.normalized, var) if Binfo.classification != 'ZERO' else [ALL_REALS_GUARD]
    sd = solve_zero_guard(Dinfo.normalized, var) if Dinfo.classification != 'ZERO' else [ALL_REALS_GUARD]

    if sb == [ALL_REALS_GUARD] and sd == [ALL_REALS_GUARD]:
        sols = solve_eq(eq, var)
        if sols == 'all reals':
            return BranchResult(name, guard_text, det_text, transformed, 'tautology', f"all real {var} satisfying {guard_text}")
        return BranchResult(name, guard_text, det_text, transformed, 'ok' if sols else 'contradiction', sols)

    if sb == [ALL_REALS_GUARD] or sd == [ALL_REALS_GUARD]:
        sols = solve_eq(eq, var)
        if isinstance(sols, list):
            valid = [v for v in sols if satisfies_zero(Binfo.normalized, var, v) and satisfies_zero(Dinfo.normalized, var, v)]
            return BranchResult(name, guard_text, det_text, transformed, 'ok' if valid else 'contradiction', unique_sorted(valid))
        return BranchResult(name, guard_text, det_text, transformed, 'unsupported', sols)

    inter = []
    for vb in sb:
        for vd in sd:
            if sp.simplify(vb - vd) == 0:
                inter.append(vb)
    inter = unique_sorted(inter)
    if not inter:
        return BranchResult(name, guard_text, det_text, transformed, 'impossible', [])
    valid = [v for v in inter if satisfies_eq(eq, var, v)]
    return BranchResult(name, guard_text, det_text, transformed, 'ok' if valid else 'contradiction', unique_sorted(valid))


def _one_zero_one_nonzero_branch(name: str, Zinfo: DenominatorInfo, NZinfo: DenominatorInfo, eq, var: sp.Symbol) -> BranchResult:
    guard_text = f"{sp.sstr(Zinfo.normalized)} = 0 and {sp.sstr(NZinfo.normalized)} != 0"
    det_text = f"{D(Zinfo.normalized)} and {N(NZinfo.normalized)}"
    transformed = equation_text(eq)
    zsols = solve_zero_guard(Zinfo.normalized, var) if Zinfo.classification != 'ZERO' else [ALL_REALS_GUARD]
    if zsols == [ALL_REALS_GUARD]:
        sols = solve_eq(eq, var)
        if isinstance(sols, list):
            valid = [v for v in sols if satisfies_zero(Zinfo.normalized, var, v) and satisfies_nonzero(NZinfo.normalized, var, v)]
            return BranchResult(name, guard_text, det_text, transformed, 'ok' if valid else 'contradiction', unique_sorted(valid))
        return BranchResult(name, guard_text, det_text, transformed, 'unsupported', sols)
    if not zsols:
        return BranchResult(name, guard_text, det_text, transformed, 'impossible', [])
    valid = [v for v in zsols if satisfies_eq(eq, var, v) and satisfies_nonzero(NZinfo.normalized, var, v)]
    return BranchResult(name, guard_text, det_text, transformed, 'ok' if valid else 'contradiction', unique_sorted(valid))


def _one_nonzero_one_zero_branch(name: str, NZinfo: DenominatorInfo, Zinfo: DenominatorInfo, eq, var: sp.Symbol) -> BranchResult:
    guard_text = f"{sp.sstr(NZinfo.normalized)} != 0 and {sp.sstr(Zinfo.normalized)} = 0"
    det_text = f"{N(NZinfo.normalized)} and {D(Zinfo.normalized)}"
    transformed = equation_text(eq)
    zsols = solve_zero_guard(Zinfo.normalized, var) if Zinfo.classification != 'ZERO' else [ALL_REALS_GUARD]
    if zsols == [ALL_REALS_GUARD]:
        sols = solve_eq(eq, var)
        if isinstance(sols, list):
            valid = [v for v in sols if satisfies_nonzero(NZinfo.normalized, var, v) and satisfies_zero(Zinfo.normalized, var, v)]
            return BranchResult(name, guard_text, det_text, transformed, 'ok' if valid else 'contradiction', unique_sorted(valid))
        return BranchResult(name, guard_text, det_text, transformed, 'unsupported', sols)
    if not zsols:
        return BranchResult(name, guard_text, det_text, transformed, 'impossible', [])
    valid = [v for v in zsols if satisfies_eq(eq, var, v) and satisfies_nonzero(NZinfo.normalized, var, v)]
    return BranchResult(name, guard_text, det_text, transformed, 'ok' if valid else 'contradiction', unique_sorted(valid))


# ----------------------------- reporting -----------------------------


def solve_equation_string(text: str, var_name: str = "x") -> Tuple[str, SideForm, SideForm, List[DenominatorInfo], List[BranchResult]]:
    lhs_expr, rhs_expr, var = parse_equation(text, var_name)
    lhs_form = direct_quotient_form(lhs_expr)
    rhs_form = direct_quotient_form(rhs_expr)
    case_name, branches, infos = solve_from_forms(lhs_form, rhs_form, var)
    return case_name, lhs_form, rhs_form, infos, branches


def format_report(eq_text: str, case_name: str, lhs_form: SideForm, rhs_form: SideForm, infos: Sequence[DenominatorInfo], branches: Sequence[BranchResult]) -> str:
    lines: List[str] = []
    lines.append(f"equation: {eq_text}")
    lines.append(f"detected case: {case_name}")
    lines.append(f"lhs direct quotient: {lhs_form.is_direct_quotient} ; numerator={sp.sstr(lhs_form.numerator)} ; denominator={sp.sstr(lhs_form.denominator)}")
    lines.append(f"rhs direct quotient: {rhs_form.is_direct_quotient} ; numerator={sp.sstr(rhs_form.numerator)} ; denominator={sp.sstr(rhs_form.denominator)}")
    if infos:
        lines.append("denominator classification:")
        for idx, info in enumerate(infos, start=1):
            lines.append(f"  D{idx}: original={sp.sstr(info.original)}")
            lines.append(f"      normalized={sp.sstr(info.normalized)}")
            lines.append(f"      class={info.classification}")
            lines.append(f"      reason={info.reason}")
    for br in branches:
        lines.append(f"  branch {br.name}:")
        lines.append(f"    guard: {br.guard_text}")
        lines.append(f"    detector: {br.detector_text}")
        lines.append(f"    transformed equation: {br.transformed_equation}")
        lines.append(f"    status: {br.status}")
        lines.append(f"    solutions: {br.solutions}")
    return "\n".join(lines)


DEFAULT_EXAMPLES = [
    # simple kernel equations
    "x/(x-1) = 2",
    "2 = (x+2)/x",
    "(x+1)/(x-1) = 3/(x-1)",
    # hidden-zero denominators
    "x/((x-x)+(y-y)) = 3",
    "2 = ((x+2))/((x/0)-x)",
    "(x+1)/((a+b)-(b+a)) = 7",
    "3/((u-v)+(v-u)) = x",
    # guarded identity cases
    "x/(x-1) = x",
    "(x-1)/(x-1) = 1",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Branch-normal-form engine with denominator zero detection")
    parser.add_argument("equation", nargs="?", help="Equation string like 'x/((x-x)+1) = 2'")
    parser.add_argument("--var", default="x", help="Variable name to solve for (default: x)")
    parser.add_argument("--examples", action="store_true", help="Run built-in examples")
    args = parser.parse_args()

    if args.examples or not args.equation:
        reports = []
        for eq in DEFAULT_EXAMPLES:
            try:
                case_name, lhs_form, rhs_form, infos, branches = solve_equation_string(eq, args.var)
                reports.append("=" * 80)
                reports.append(format_report(eq, case_name, lhs_form, rhs_form, infos, branches))
            except Exception as exc:
                reports.append("=" * 80)
                reports.append(f"equation: {eq}")
                reports.append(f"error: {exc}")
        print("\n".join(reports))
        return

    case_name, lhs_form, rhs_form, infos, branches = solve_equation_string(args.equation, args.var)
    print(format_report(args.equation, case_name, lhs_form, rhs_form, infos, branches))


if __name__ == "__main__":
    main()
