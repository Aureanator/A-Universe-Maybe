"""Explicit D(G)-modules and the universal R-matrix: braiding eigenvalues from first principles.

Layer-2 open problem 2 (the fermion gate): theta = -1 on W2, W3 fixes the ribbon TWIST;
exchange statistics is the R-eigenvalue in the vacuum channel of a self-dual dyon with
itself. Following the E018 lesson -- no remembered F-symbol formulas, no convention
assumptions -- we build the category CONCRETELY:

* Simple D(G)-modules M([g], rho): basis {(x, v)} over the flux class cl(g) with v in V_rho.
  Group element k acts by k.(x,v) = (kxk^-1, rho(u) v) where u = t_{kgk^-1}^-1 k t_x is the
  canonical-transversal correction lying in C_G(g); dual-basis projectors p_h grade by x.
* Universal R-matrix of D(G): R = sum_h e_h (x) h, so on homogeneous m of degree x:
  Rhat(m (x) n) = m (x) (x.n), and the braiding is c = flip o Rhat.
* Vacuum channel of a self-dual simple W: Hom_D(1, W (x) W) = invariant line(s); found as
  joint nullspace of (k - I) over all k in G acting on W (x) W. On that line, c(v0) = R v0
  with R = +-1 EXACTLY -- the exchange sign, read off, not postulated.

Self-verification built in: module axioms checked at construction; monodromy c^2 on the
vacuum line must equal theta_c/(theta_a theta_b) (= +1 for our targets); fusion multiplicities
from intertwiner dimensions must match category.fusion_coefficients. If any check fails, we
raise -- wrong conventions surface immediately rather than silently mislabeling fermions.

Kernel module: no RNG, no scheduler, no coordinates.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

from .category import AnyonType, double_sectors, fusion_coefficients, s_matrix
from .groups import AlternatingGroup4, Group

__all__ = ["DModule", "module_for_sector", "vacuum_braiding_eigenvalues", "fermion_report",
         "pair_channel_report", "channel_intertwiners", "double_braid_matrix",
         "pair_state", "envariance_check"]

CPLX = complex


@dataclass(frozen=True)
class DModule:
    """Concrete simple D(G)-module M([g], rho)."""

    sector: AnyonType
    elements: Tuple                    # sorted G
    fluxes: Tuple                      # sorted cl(g): grade of each basis index (i, v_k)
    dim_rho: int
    k_actions: Dict[CPLX, np.ndarray]  # k -> unitary matrix on the module

    @property
    def dimension(self) -> int:
        return len(self.fluxes) * self.dim_rho


def _transversal(g: Group, rep, class_elems: List, scan_order=None):
    """Canonical t_x for each x in cl(rep): first group element (scan order) with x = t rep t^-1.

    ``scan_order`` lets tests build ALTERNATE transversals (e.g. reversed scan) to verify
    that physical eigenvalues are independent of the transversal choice (E028 caveat iii).
    """
    order = tuple(g.elements) if scan_order is None else tuple(scan_order)
    t_of = {}
    for x in class_elems:
        for t in order:
            if g.multiply(g.multiply(t, rep), g.inverse(t)) == x:
                t_of[x] = t
                break
        else:                                    # pragma: no cover - impossible by definition
            raise AssertionError(f"no transversal element found for {x}")
    return t_of


def module_for_sector(sector: AnyonType, group: Optional[Group] = None,
                      transversal_scan=None) -> DModule:
    """Build M([g], rho) with explicit actions; verifies representation axioms."""
    g = group or AlternatingGroup4()
    rep = sector.representative
    class_elems = sorted(sector.flux_class)
    t_of = _transversal(g, rep, class_elems, scan_order=transversal_scan)
    cent = sector.centralizer

    # rho on centralizer elements as matrices: reconstruct from character values is not enough;
    # for our 1-dim centralizer irreps (Z3 chars, V4 chars) the representation IS the character.
    # For pure charges of the 3-dim irrep we need actual matrices -- built from permutation
    # action on R^4/diagonal when dim_rho == 3.
    if sector.class_index == 0 and sector.dimension == 3:
        rho = _standard_a4_matrices(g)
    else:
        rho = {h: np.array([[sector.character[h]]], dtype=complex) for h in cent}

    basis = [(x, j) for x in class_elems for j in range(sector.dimension)]
    bidx = {b: i for i, b in enumerate(basis)}
    n = len(basis)

    k_actions: Dict[CPLX, np.ndarray] = {}
    for k in g.elements:
        M = np.zeros((n, n), dtype=complex)
        for (x, j) in basis:
            x2 = g.multiply(g.multiply(k, x), g.inverse(k))
            u = g.multiply(g.multiply(g.inverse(t_of[x2]), k), t_of[x])   # in C_G(g)
            assert u in cent, "transversal correction left the centralizer"
            col = bidx[(x, j)]
            for jj in range(sector.dimension):
                M[bidx[(x2, jj)], col] += rho[u][jj, j]
        k_actions[k] = M
        # unitarity check (permutation-like monomial structure)
        assert np.allclose(M.conj().T @ M, np.eye(n), atol=1e-9)

    mod = DModule(sector, tuple(g.elements), tuple(class_elems), sector.dimension, k_actions)

    # representation axiom: rho(k1)rho(k2) == rho(k1 k2); p_h projectors consistent with grades
    for k1 in g.elements:
        for k2 in g.elements:
            assert np.allclose(k_actions[k1] @ k_actions[k2],
                               k_actions[g.multiply(k1, k2)], atol=1e-9), "not a representation"
    return mod


def _standard_a4_matrices(g: Group) -> Dict[object, np.ndarray]:
    """3-dim irrep as permutation action on R^4 restricted to the 3-plane sum=0."""
    # orthonormal basis of {sum=0} plane in R^4
    B = np.array([[1, -1, 0, 0], [1, 1, -2, 0], [1, 1, 1, -3]], dtype=float)
    B = B / np.linalg.norm(B, axis=1, keepdims=True)
    mats = {}
    for k in g.elements:
        P = np.zeros((4, 4))
        for i in range(4):                       # groups.py convention: p[i] = image of i (0-based)
            P[k[i], i] = 1.0
        Q = B @ P @ B.T                          # action on plane coords (B orthonormal rows)
        mats[k] = Q.astype(complex)
    return mats


def _tensor_action(mod1: DModule, mod2: DModule):
    """D(G)-action on M1 (x) M2 via coproduct: k acts as k (x) k; p_h grades additively-by-product."""
    n1, n2 = mod1.dimension, mod2.dimension

    def basis_index(a, b):
        return a * n2 + b

    k_ops = {}
    for k in mod1.k_actions:
        K1, K2 = mod1.k_actions[k], mod2.k_actions[k]
        k_ops[k] = np.kron(K1, K2)
    # projector p_h acts as (grade1 == h) AND (grade2 == h')... p_h on tensor: sum over
    # decompositions? For D(G), Delta(p_h) = sum_{ab=h} p_a (x) p_b. Grades are group elements:
    grade1 = [x for x in mod1.fluxes for _ in range(mod1.dim_rho)]
    grade2 = [y for y in mod2.fluxes for _ in range(mod2.dim_rho)]
    g = AlternatingGroup4()
    p_ops = {}
    for h in g.elements:
        P = np.zeros((n1 * n2, n1 * n2), dtype=complex)
        for i, x in enumerate(grade1):
            for j, y in enumerate(grade2):
                if g.multiply(x, y) == h:
                    idx = basis_index(i, j)
                    P[idx, idx] = 1.0
        p_ops[h] = P
    return k_ops, p_ops, (n1, n2)


def _intertwiner_basis(k_ops_a, mod_c: DModule):
    """Solve T M_c(k) = k_A T for all k in G; returns a basis of Hom_D(M_c, A)."""
    nc = mod_c.dimension
    na = len(next(iter(k_ops_a.values())))
    rows = []
    for k in k_ops_a:
        lhs_k = k_ops_a[k]                       # action on A (target)
        rhs_k = mod_c.k_actions[k]               # action on M_c (source)
        # vec(T M_c(k)) = (I (x) M_c(k)^T) vec(T);  vec(k_A T) = (k_A (x) I) vec(T)
        eqn = np.kron(np.eye(nc), rhs_k.T) - np.kron(lhs_k, np.eye(nc))
        rows.append(eqn)
    A = np.vstack(rows)
    _, s, vh = np.linalg.svd(A)
    tol = 1e-8 * max(1.0, s[0] if len(s) else 1.0)
    rank = int(sum(1 for x in s if x > tol))
    return [vh[i].conj().reshape(nc, na)         # row-major: matches np.kron convention above
            for i in range(rank, len(vh))]


def vacuum_braiding_eigenvalues(sector_index: Optional[int] = None):
    """For each self-dual simple W with a vacuum line in W (x) W: compute R = eigenvalue of c.

    Returns list of dicts: sector label, theta, monodromy check (c^2), R sign, verdict.
    """
    g = AlternatingGroup4()
    sectors = double_sectors(g)
    report = []
    for i, W in enumerate(sectors):
        if sector_index is not None and i != sector_index:
            continue
        modW = module_for_sector(W, g)
        k_ops, p_ops, dims = _tensor_action(modW, modW)
        ntot = modW.dimension ** 2

        # Vacuum search happens in the GRADE-E subspace of W (x) W: pairs (a,b) whose
        # grade product is e. This subspace is k-invariant (the product conjugates), and
        # the trivial module lives exactly there. Solving invariance per-vector on the full
        # space and filtering afterwards is WRONG: SVD bases mix grades; project first.
        grade = [x for x in modW.fluxes for _ in range(modW.dim_rho)]
        e_idx = np.array([a * modW.dimension + b
                          for a in range(modW.dimension)
                          for b in range(modW.dimension)
                          if g.multiply(grade[a], grade[b]) == g.identity()], dtype=int)
        if len(e_idx) == 0:
            continue
        rows = []
        for k, K in k_ops.items():
            Ke = K[np.ix_(e_idx, e_idx)]          # restricted block (subspace invariant)
            rows.append(Ke - np.eye(len(e_idx)))
        A = np.vstack(rows)
        _, s, vh = np.linalg.svd(A)
        tol = 1e-8 * max(1.0, s[0] if len(s) else 1.0)
        rank = int(sum(1 for x in s if x > tol))
        inv_lines = []
        for i in range(rank, len(vh)):
            v_e = vh[i].conj()
            v = np.zeros(ntot, dtype=complex)
            v[e_idx] = v_e
            inv_lines.append(v / np.linalg.norm(v))
        if not inv_lines:
            continue

        n2 = modW.dimension
        # braiding c = flip o Rhat;  Rhat(m (x) n) = m (x) (deg(m).n)
        def apply_c(vec):
            V = vec.reshape(n2, n2)              # rows: first factor basis index
            out = np.zeros((n2, n2), dtype=complex)
            grade1 = [x for x in modW.fluxes for _ in range(modW.dim_rho)]
            for a in range(n2):
                if not np.any(V[a]):
                    continue
                x = grade1[a]
                Kx = modW.k_actions[x]           # acts on second factor
                out[a] += V[a] @ Kx.T            # (deg . n) components
            return out.T.reshape(ntot)           # flip factors

        results = []
        for v0 in inv_lines:
            cv = apply_c(v0)
            overlap = np.vdot(v0, cv)            # should be +-1 exactly
            c2 = apply_c(cv)
            mono = np.vdot(v0, c2)
            R = round(overlap.real)
            assert abs(overlap.imag) < 1e-8 and abs(abs(overlap) - 1) < 1e-8, \
                f"vacuum line not an eigenvector of c: {overlap}"
            assert abs(mono - 1) < 1e-8, "monodromy on vacuum channel must be +1"
            results.append(R)

        theta = W.character[W.representative] / W.dimension
        for R in results:
            verdict = ("TRUE FERMION (odd exchange)" if abs(theta + 1) < 1e-9 and R == -1 else
                       "twist-fermion but bosonic exchange" if abs(theta + 1) < 1e-9 else
                       "bosonic exchange" if R == 1 else "exotic")
            report.append({"sector": str(W), "theta": theta, "R_vacuum_channel": R,
                           "verdict": verdict})
    return report


def fermion_report():
    """Run the vacuum-channel braiding scan over all self-dual sectors."""
    rows = vacuum_braiding_eigenvalues()
    lines = [f"{r['sector']:>22}  theta={r['theta']:.3f}  R={r['R_vacuum_channel']:+d}  {r['verdict']}"
             for r in rows]
    return "\n".join(lines) if lines else "no vacuum channels found"


# --------------------------------------------------------- pair channels: monodromy vs category

def _braiding_matrix(mod1: DModule, mod2: DModule) -> np.ndarray:
    """Matrix of the braiding c_{1,2}: M1 (x) M2 -> M2 (x) M1 = flip o Rhat (row-major vec)."""
    n1, n2 = mod1.dimension, mod2.dimension
    grade1 = [x for x in mod1.fluxes for _ in range(mod1.dim_rho)]
    C = np.zeros((n2 * n1, n1 * n2), dtype=complex)
    for a in range(n1):
        Kx = mod2.k_actions[grade1[a]]           # degree of first factor acts on second
        for j in range(n2):
            for jp in range(n2):
                if Kx[jp, j] != 0:
                    C[jp * n1 + a, a * n2 + j] = Kx[jp, j]
    return C


def double_braid_matrix(modA: DModule, modB: DModule) -> np.ndarray:
    """Monodromy M = c_{B,A} o c_{A,B}: endomorphism of M_A (x) M_B.

    Physically this is the full loop-through-loop braid: what an interferometer measures
    when one flux string passes through the spanning surface of the other.
    """
    C_ab = _braiding_matrix(modA, modB)
    C_ba = _braiding_matrix(modB, modA)
    return C_ba @ C_ab


def channel_intertwiners(modA: DModule, modB: DModule, mod_c: DModule) -> List[np.ndarray]:
    """Basis of Hom_D(M_c, M_A (x) M_B) as matrices T (nAB x nc).

    Intertwining the FULL double means commuting with BOTH structures:
      * k-equivariance:   A_k T == T C_k            (group part), and
      * grade preservation: p_h^{A(x)B} T == T p_h^C for every h  (algebra part).
    Dropping the grade constraints inflates Hom (spurious grade-mixing maps; Schur fails)
    -- caught by the Verlinde cross-check below.

    Column count is the concrete fusion multiplicity; tests cross-check it against the
    Verlinde coefficients computed independently from the S-matrix.
    """
    g = AlternatingGroup4()
    n1, n2 = modA.dimension, modB.dimension
    na, nc = n1 * n2, mod_c.dimension
    grade_a = [x for x in modA.fluxes for _ in range(modA.dim_rho)]
    grade_b = [y for y in modB.fluxes for _ in range(modB.dim_rho)]
    grade_ab = [g.multiply(x, y) for x in grade_a for y in grade_b]     # row-major (i*n2+j)
    grade_c = [x for x in mod_c.fluxes for _ in range(mod_c.dim_rho)]
    rows = []
    # ROW-MAJOR vec of T (na x nc):  vec(A T) = (A kron I_nc) v ;  vec(T C) = (I_na kron C^T) v
    for k in modA.k_actions:
        A_k = np.kron(modA.k_actions[k], modB.k_actions[k])
        C_k = mod_c.k_actions[k]
        rows.append(np.kron(A_k, np.eye(nc)) - np.kron(np.eye(na), C_k.T))
    for h in g.elements:
        pa = np.diag([1.0 + 0j if x == h else 0j for x in grade_ab])
        pc = np.diag([1.0 + 0j if x == h else 0j for x in grade_c])
        rows.append(np.kron(pa, np.eye(nc)) - np.kron(np.eye(na), pc.T))
    M = np.vstack(rows)
    _, s, vh = np.linalg.svd(M)
    tol = 1e-8 * max(1.0, s[0] if len(s) else 1.0)
    rank = int(sum(1 for x in s if x > tol))
    return [vh[i].conj().reshape(na, nc) for i in range(rank, len(vh))]


# ------------------------------------------------- envariance prerequisite: glued pair states

def pair_state(sector_index: int, group: Optional[Group] = None):
    """Glued flux-antiflux pair state |Psi> in M_a (x) M_anti(a): the vacuum channel.

    The unique (multiplicity-one -- guaranteed for a x anti-a) invariant line of
    Hom_D(1, M_a (x) M_anti(a)) is the categorical Bell pair: created by a string that
    nucleates flux g next to flux g^-1 with conjugate charges, total charge vacuum.

    Returns dict with the normalized state vector psi (length dA*dB), reduced density
    matrix rho_A, effective Schmidt rank, and entanglement entropy log(rank) when flat.
    """
    g = group or AlternatingGroup4()
    sectors = double_sectors(g)
    a = sectors[sector_index]
    from .category import charge_conjugation
    ibar = charge_conjugation(sectors, g)[sector_index]
    modA = module_for_sector(a, g)
    modB = module_for_sector(sectors[ibar], g)
    vacuum_mod = module_for_sector(sectors[0], g)
    Ts = channel_intertwiners(modA, modB, vacuum_mod)
    assert len(Ts) == 1, f"vacuum channel of a x anti-a must be multiplicity one, got {len(Ts)}"
    T = Ts[0]                                        # (dA*dB) x 1
    psi = T.reshape(-1)
    psi = psi / np.linalg.norm(psi)
    dA, dB = modA.dimension, modB.dimension
    Psi = psi.reshape(dA, dB)
    rho_A = Psi @ Psi.conj().T
    # Schmidt structure
    sv = np.linalg.svd(Psi, compute_uv=False)
    sv2 = sv ** 2
    sv2 = sv2[sv2 > 1e-12]
    flat = np.allclose(sv2, sv2[0], atol=1e-9)       # maximally entangled on its support?
    rank = len(sv2)
    entropy = float(-np.sum(sv2 * np.log(sv2)))
    return {"sector": str(a), "antiparticle": str(sectors[ibar]), "psi": psi,
            "rho_A": rho_A, "schmidt_squared": sv2, "maximally_entangled_on_support": bool(flat),
            "effective_rank": int(rank), "entropy_log": entropy,
            "support_projector_proportional": bool(np.allclose(
                rho_A, (1.0 / rank) * np.eye(dA)[:rank, :rank], atol=1e-9)) or
            bool(np.allclose(rho_A @ rho_A, rho_A) and abs(np.trace(rho_A) - 1.0) < 1e-9)}


def envariance_check(sector_index: int, group: Optional[Group] = None):
    """Zurek envariance of the glued pair state: swaps of equal-amplitude Schmidt partners
    on side A are undone by an operator on side B ALONE.

    Concretely, for each transposition tau of computational basis vectors inside the support
    (equal Schmidt weights -- verified flat beforehand), solve (tau_A tensor I)|Psi> =
    (I tensor V_B)|Psi> for V_B and check V_B is unitary on the support. This is the swap
    symmetry the envariance route to the Born rule needs; the measure itself remains a
    declared postulate (Memo patch P5) -- this constructor supplies the structure, not the step.
    """
    info = pair_state(sector_index, group)
    if not info["maximally_entangled_on_support"]:
        return {"sector": info["sector"], "envariant": False,
                "reason": "Schmidt weights not flat -- equal-amplitude swaps undefined"}
    g = group or AlternatingGroup4()
    sectors = double_sectors(g)
    from .category import charge_conjugation
    ibar = charge_conjugation(sectors, group)[sector_index]
    modA = module_for_sector(sectors[sector_index], g)
    modB = module_for_sector(sectors[ibar], g)
    dA, dB = modA.dimension, modB.dimension
    psi = info["psi"]
    rank = info["effective_rank"]
    results = []
    for i in range(rank):
        for j in range(i + 1, rank):
            tau = np.eye(dA, dtype=complex)
            tau[i, i] = tau[j, j] = 0.0
            tau[i, j], tau[j, i] = 1.0, 1.0          # swap basis vectors i <-> j on A
            lhs = np.kron(tau, np.eye(dB)) @ psi     # (tau_A tensor I)|Psi>
            # solve for V_B: (I tensor V_B)|Psi> = lhs with row-major Psi (dA x dB):
            # (I tensor V) acts as Psi -> Psi V^T ; need Psi V^T = Lmat
            Lmat = lhs.reshape(dA, dB)
            Pm = psi.reshape(dA, dB)
            # least squares for V^T: Pm X = Lmat  (X = V^T), restricted to support rows/cols
            X, residuals, rcond, _ = np.linalg.lstsq(Pm[:rank], Lmat[:rank], rcond=None)
            Vt = X
            V = Vt.T
            residual = np.max(np.abs(Pm @ Vt - Lmat))
            unitary_support = np.allclose(V.conj().T @ V, np.eye(rank), atol=1e-8) \
                or np.allclose(V @ V.conj().T, np.eye(V.shape[0]), atol=1e-8)
            results.append({"swap": (i, j), "residual": float(residual),
                            "V_unitary_on_support": bool(unitary_support)})
    ok = all(r["residual"] < 1e-8 and r["V_unitary_on_support"] for r in results)
    return {"sector": info["sector"], "envariant": bool(ok), "swaps": results,
            "effective_rank": rank}


def pair_channel_report(group: Optional[Group] = None):
    """Measure monodromy per fusion channel concretely; verify against theta-ratio prediction.

    For every sector pair (a, b) and every simple c appearing in a (x) b:
      * concrete Hom dimension == Verlinde N^c_{ab}  (category layer cross-check),
      * the double braid acts on the channel as the scalar theta_c / (theta_a theta_b)
        (ribbon prediction from modular data, measured from the universal R-matrix).

    Returns list of row dicts; also asserts internally -- failures raise, never whisper.
    """
    g = group or AlternatingGroup4()
    sectors = double_sectors(g)
    S = s_matrix(sectors, g)
    N = fusion_coefficients(S)

    def theta(s):
        return s.character[s.representative] / s.dimension

    mods = [module_for_sector(s, g) for s in sectors]
    rows = []
    max_err = 0.0
    channels_checked = 0
    for ia, a in enumerate(sectors):
        for ib, b in enumerate(sectors):
            if not any(N[ic][ia][ib] for ic in range(len(sectors))):
                continue
            D = double_braid_matrix(mods[ia], mods[ib])
            for ic, c in enumerate(sectors):
                mult = N[ic][ia][ib]
                if mult == 0:
                    continue
                Ts = channel_intertwiners(mods[ia], mods[ib], mods[ic])
                assert len(Ts) == mult, (
                    f"Hom dimension {len(Ts)} != Verlinde N[{ic}][{ia}][{ib}] = {mult}")
                predicted = theta(c) / (theta(a) * theta(b))
                for T in Ts:
                    DT = D @ T                     # acts on each column (channel vector)
                    lam = np.vdot(T, DT) / np.vdot(T, T)
                    err_col = np.max(np.abs(DT - lam * T))
                    assert err_col < 1e-8, f"monodromy not scalar on channel {c}"
                    err = abs(lam - predicted)
                    max_err = max(max_err, err)
                    channels_checked += 1
                    rows.append({"a": str(a), "b": str(b), "c": str(c), "multiplicity": mult,
                                 "monodromy_measured": lam, "theta_ratio_predicted": predicted,
                                 "abs_error": float(err)})
    assert max_err < 1e-8, f"monodromy disagrees with theta-ratio prediction: {max_err}"
    return rows, channels_checked, max_err
