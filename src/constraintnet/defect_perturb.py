"""P33 (local recreation): effective hopping and virtual-pair corrections for H(lam)=H0+lam*V.

Pre-registered in docs/P33_VIRTUAL_PAIRS.md (protocol commits b8e462f, a836e7d). This module was
written INDEPENDENTLY from the registered protocol by local Qwen on 2026-09-20 -- not copied from
the sibling checkout's uncommitted implementation -- so agreement with Astra's archived numbers is
a genuine cross-checkout reproduction.

POSTULATED perturbation (neither H0, continuous-time unitary evolution, nor this phase action
follows from the implication axiom as formalized; see the protocol's assumption ledger):

    H(lam) = H0 + lam V,   V = -sum_edges W_e,  W_e = nontrivial-character string on one edge.

W_e is diagonal in the label basis (Z2: phase (-1)^l_e), commutes with every B_f, anticommutes
with S_a and S_b at its endpoints, and changes defect number N by 0 or +/-2. In the flat sector
H0 = E_vac + N. Registered algebra checked here as identities before any spectral claim:

    sum_m P_m V P_m = -sum_ab W_ab (I - S_a S_b)/2          (first order = P32B's K / kappa)
    C = P_2 V P_0 V P_2 / 2 - P_2 V P_4 V P_2 / 2           (second order, both intermediates)

with pair-basis coefficients predicted as: C_vac = -|E|/2; diagonal C_ab,ab = (deg a + deg b
- |E|)/2 (no two-body diagonal potential after subtracting C_vac); shared-endpoint transfers
sum over common neighbours of (1[v=b] - 1/2); disjoint transfers vanish by vacuum/four-defect
cancellation. On K4 all coefficients vanish identically (pre-execution refinement, commit a836e7d).

Success removes EXACT number conservation as a required fundamental postulate for the LEADING
hopping approximation only; it derives nothing about binding, fermions, or reduction itself.
"""

from __future__ import annotations

import itertools
from collections import deque

import numpy as np
from scipy.linalg import expm

from .defect import GaugePatch
from .defect_ops import DefectDynamics
from .seeds import make_bipyramid, make_tetrahedron_boundary

Z2_CHARACTER = np.array([1.0 + 0j, -1.0 + 0j])


def bfs_path(adjacency, source, target):
    """Shortest graph path as a vertex list (deterministic: sorted neighbours)."""
    if source == target:
        raise ValueError("path endpoints must differ")
    seen = {source}
    queue = deque([(source, [source])])
    while queue:
        node, path = queue.popleft()
        for nxt in sorted(adjacency[node]):
            if nxt in seen:
                continue
            if nxt == target:
                return path + [nxt]
            seen.add(nxt)
            queue.append((nxt, path + [nxt]))
    raise ValueError(f"no path from {source} to {target}")


class EffectiveDefects:
    """Full-space operators, flat-sector reduction, subset basis, and perturbative blocks."""

    def __init__(self, fixture: str = "tetrahedron"):
        cx = (make_tetrahedron_boundary("Z2") if fixture == "tetrahedron"
              else make_bipyramid("Z2", triangulation="two"))
        self.fixture = fixture
        self.patch = GaugePatch(cx)
        self.ops = DefectDynamics(self.patch)
        p = self.patch
        dim = p.dim
        identity = np.eye(dim, dtype=complex)

        # Projectors and H0 (dense; fixtures are 64 and 512 dimensional).
        self.A = {v: p.star_projector(v) for v in p.vertices}
        self.B = {f: p.plaquette_projector(f) for f in p.faces}
        self.S = {v: 2 * self.A[v] - identity for v in p.vertices}
        self.n = {v: identity - self.A[v] for v in p.vertices}
        self.Nop = sum(self.n.values())
        self.H0 = -sum(self.A.values()) - sum(self.B.values())

        # Edge string operators W_e (diagonal) and the perturbation V.
        adjacency = {v: set() for v in p.vertices}
        for a, b in p.edges:
            adjacency[a].add(b)
            adjacency[b].add(a)
        self.adjacency = adjacency
        self.W = {}
        for (a, b) in p.edges:
            diag = self.ops.string_factor([a, b], Z2_CHARACTER)
            self.W[(a, b)] = np.diag(diag.astype(complex))
        self.V = -sum(self.W.values())

        # Flat sector: configurations with every face holonomy trivial.
        flat_mask = np.ones(dim, bool)
        for f in p.faces:
            flat_mask &= (p.holonomy(f) == p.e_id)
        self.flat_indices = np.nonzero(flat_mask)[0]
        self.flat_dim = int(flat_mask.sum())
        F = np.zeros((dim, self.flat_dim), dtype=complex)
        F[self.flat_indices, np.arange(self.flat_dim)] = 1.0
        self.F = F  # flat-sector inclusion; restriction of a flat-preserving M is F^H M F

        # Defect-number spectral projectors P_m (N has integer spectrum: commuting A_v).
        evals, evecs = np.linalg.eigh(self.Nop)
        rounded = np.rint(evals).astype(int)
        self.number_values = sorted(set(rounded.tolist()))
        self.P = {m: (evecs[:, rounded == m] @ evecs[:, rounded == m].conj().T)
                  for m in self.number_values}

        # Subset basis over even vertex-occupation subsets (vacuum, pairs, quadruples...).
        vertices = list(p.vertices)
        self.subsets = [s for r in range(0, len(vertices) + 1, 2)
                        for s in itertools.combinations(vertices, r)]
        self.basis_states = {}
        vacuum = self.ops.flat_vacuum()
        for subset in self.subsets:
            state = vacuum.copy()
            for u, w in zip(subset[0::2], subset[1::2]):  # pair sorted endpoints
                path = bfs_path(adjacency, u, w)
                state = state * self.ops.string_factor(path, Z2_CHARACTER)
            self.basis_states[subset] = state

        # Vacuum energy in the flat sector.
        self.E_vac = float(np.vdot(vacuum, self.H0 @ vacuum).real)

    # ------------------------------------------------------------------ helpers
    def _pair_states(self):
        return np.column_stack([self.basis_states[s] for s in self.subsets if len(s) == 2])

    def pair_matrix(self, operator):
        states = self._pair_states()
        return states.conj().T @ operator @ states

    def flat_matrix(self, operator):
        return self.F.conj().T @ operator @ self.F

    # ------------------------------------------------------------------ audits
    def basis_audit(self):
        """Orthonormality and completeness of the subset basis against flat configurations."""
        states = np.column_stack([self.basis_states[s] for s in self.subsets])
        gram = states.conj().T @ states
        ortho = float(np.abs(gram - np.eye(len(self.subsets))).max())
        outside = max(float(np.linalg.norm(s - self.F @ (self.F.conj().T @ s)))
                      for s in states.T)
        return {"flat_basis_orthonormality": ortho, "flat_basis_completeness": ortho + outside}

    def first_order_block_identity(self):
        """|| sum_m P_m V P_m  +  sum_ab W_ab (I - S_a S_b)/2 ||_F on the full space."""
        block = sum(P @ self.V @ P for P in self.P.values())
        rhs = -sum(W @ (np.eye(self.patch.dim, dtype=complex) - self.S[a] @ self.S[b]) / 2
                   for (a, b), W in self.W.items())
        return float(np.linalg.norm(block - rhs))

    def duality_audit(self):
        """In the subset basis: H0 == E_vac + sum n_v and V == -(sum_ab X_a X_b)."""
        states = np.column_stack([self.basis_states[s] for s in self.subsets])
        index = {s: i for i, s in enumerate(self.subsets)}
        h0_dual = np.zeros((len(self.subsets),) * 2, dtype=complex)
        v_dual = np.zeros_like(h0_dual)
        edge_pairs = [tuple(sorted(e)) for e in self.patch.edges]
        for i, s in enumerate(self.subsets):
            h0_dual[i, i] = self.E_vac + len(s)
            for a, b in edge_pairs:  # hopping along COMPLEX edges only (K4 hides this distinction)
                flipped = tuple(sorted(set(s) ^ {a, b}))
                j = index.get(flipped)
                if j is not None:
                    v_dual[i, j] -= 1.0
        h0_pair = states.conj().T @ self.H0 @ states
        v_pair = states.conj().T @ self.V @ states
        return {"H0_duality": float(np.abs(h0_pair - h0_dual).max()),
                "V_duality": float(np.abs(v_pair - v_dual).max())}

    # ------------------------------------------------------------------ second order
    def second_order_full(self):
        """C = P2 V P0 V P2 / 2 - P2 V P4 V P2 / 2 (full space; both intermediates kept)."""
        p2, p0 = self.P[2], self.P[0]
        p4 = self.P.get(4, np.zeros_like(p0))
        via0 = p2 @ self.V @ p0 @ self.V @ p2 / 2.0
        via4 = p2 @ self.V @ p4 @ self.V @ p2 / 2.0
        return {"via_zero": via0, "via_four": via4, "C": via0 - via4}

    def coefficient_predictions(self):
        """Check the four registered coefficient formulas against computed C."""
        edges = self.patch.edges
        degrees = {v: len(self.adjacency[v]) for v in self.patch.vertices}
        pairs = [s for s in self.subsets if len(s) == 2]
        c_pair = self.pair_matrix(self.second_order_full()["C"])

        diag_err = max(abs(c_pair[i, i].real - (degrees[a] + degrees[b] - len(edges)) / 2)
                       for i, (a, b) in enumerate(pairs))
        off_err = 0.0
        disjoint_err = 0.0
        for i, (a, b) in enumerate(pairs):
            for j, (c, d) in enumerate(pairs):
                if i >= j:
                    continue
                shared = {a, b} & {c, d}
                value = c_pair[i, j].real
                if not shared:
                    disjoint_err = max(disjoint_err, abs(value))
                elif len(shared) == 1:
                    # |a,b> vs |c,d> sharing one vertex: differ at the two MOVING vertices;
                    # registered formula sums over common neighbours of those two, with 1[v=shared]-1/2.
                    moving_i = ({a, b} - shared).pop()
                    moving_j = ({c, d} - shared).pop()
                    fixed = next(iter(shared))
                    common = self.adjacency[moving_i] & self.adjacency[moving_j]
                    predicted = sum((1.0 if v == fixed else 0.0) - 0.5 for v in common)
                    off_err = max(off_err, abs(value - predicted))

        # Vacuum second-order shift: only the m=2 intermediate contributes, denominator -2.
        vacuum = self.basis_states[tuple()]
        v_psi = self.V @ vacuum
        c_vac = -0.5 * float(np.vdot(self.P[2] @ v_psi, self.P[2] @ v_psi).real)
        return {"diagonal_coefficient": diag_err,
                "shared_endpoint_transfer": off_err,
                "disjoint_transfer_vanishes": disjoint_err,
                "vacuum_shift_error": abs(c_vac + len(edges) / 2),
                "C_vac_value": c_vac}

    # ------------------------------------------------------------------ spectral sweep
    def sweep(self, couplings=(0.01, 0.02, 0.04, 0.08)):
        h0_flat = self.flat_matrix(self.H0)
        v_flat = self.flat_matrix(self.V)
        first = self.pair_matrix(sum(P @ self.V @ P for P in self.P.values()))
        second = self.pair_matrix(self.second_order_full()["C"])
        block = np.diag([self.E_vac + 2] * first.shape[0]).astype(complex)

        results, previous = [], None
        for lam in couplings:
            eigvals = np.sort(np.linalg.eigvalsh(h0_flat + lam * v_flat).real)
            band = eigvals[np.abs(eigvals - (self.E_vac + 2)) < 1.0]
            pred1 = np.sort(np.linalg.eigvalsh(block + lam * first).real)
            pred2 = np.sort(np.linalg.eigvalsh(block + lam * first + lam * lam * second).real)
            err1 = float(np.abs(band[:len(pred1)] - pred1).max())
            err2 = float(np.abs(band[:len(pred2)] - pred2).max())
            entry = {"coupling": lam, "band_eigenvalues": band.tolist(),
                     "first_order_error": err1, "second_order_error": err2}
            if previous is not None:
                ratio = lam / previous["coupling"]
                entry["observed_order_first"] = (np.log(max(err1, 1e-18) / max(previous["first_order_error"], 1e-18))
                                                 / np.log(ratio)) if previous["first_order_error"] > 0 else None
                entry["observed_order_second"] = (np.log(max(err2, 1e-18) / max(previous["second_order_error"], 1e-18))
                                                  / np.log(ratio)) if previous["second_order_error"] > 0 else None
            results.append(entry)
            previous = {"coupling": lam, "first_order_error": err1, "second_order_error": err2}
        return results

    # ------------------------------------------------------------------ exact evolution
    def evolve_bare_pairs(self, coupling, times=(0.0, 0.25, 1.0, 3.0, 7.0)):
        """Exact exp(-it(H0+lam V)) on the flat sector for every bare pair; conservation ledger."""
        h_flat = self.flat_matrix(self.H0 + coupling * self.V)
        v_flat = self.flat_matrix(self.V)
        n_flat = {v: self.F.conj().T @ self.n[v] @ self.F for v in self.patch.vertices}
        sector_flat = {m: self.F.conj().T @ Pm @ self.F for m, Pm in self.P.items()}

        rows = []
        for subset in [s for s in self.subsets if len(s) == 2]:
            psi0 = self.F.conj().T @ self.basis_states[subset]
            for t in times:
                psi = expm(-1j * h_flat * t) @ psi0
                sector_probs = {m: float(np.vdot(psi, pf @ psi).real)
                                for m, pf in sector_flat.items()}
                n_expect = sum(float(np.vdot(psi, nf @ psi).real) for nf in n_flat.values())
                var_n = sum((m - n_expect) ** 2 * p for m, p in sector_probs.items())
                rows.append({"pair": list(subset), "time": t,
                             "norm": float(np.vdot(psi, psi).real),
                             "energy_total": float(np.vdot(psi, h_flat @ psi).real),
                             "h0_expectation": float(np.vdot(psi, h_flat @ psi).real)
                             - coupling * float(np.vdot(psi, v_flat @ psi).real),
                             "N_expectation": n_expect, "N_variance": var_n,
                             "sector_probabilities": {str(m): p for m, p in sector_probs.items()}})
        return rows
