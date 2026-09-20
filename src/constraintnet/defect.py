"""Local conservation (Gauss law) and defects, in the quantum-double form.

The user's axiom, stated 2026-09-20: *causality travels to local effect, and it is always
travelling as a conserved quantity*. That is a constraint per vertex, not a soft cost:

    A_v = (1/|G|) sum_g A_v^g   projects onto states invariant under a gauge move at v
                                (nothing is created at a vertex: local conservation)
    B_f                          projects onto trivial holonomy around a face f (flatness)

Both are projectors, they commute, and the ground state satisfies every one of them. Excitations
are their violations:
  * a **charge** is a vertex where A_v fails - a point defect, the matter candidate;
  * a **flux** is a face where B_f fails. In three dimensions the faces that a single edge's label
    disturbs form the closed ring around that edge, so a flux is a **loop**, never a point.

This replaces the soft electric/Wilson costs of `qrecord`/`spin_record`, which have no gap and
impose no conservation. See `docs/UPGRADES_FROM_LITERATURE.md`.
"""

import itertools

import numpy as np

from .curvature import CurvatureState


class GaugePatch:
    """Exact configuration space |G|^E on a small patch, with the two projectors."""

    def __init__(self, cx, edges=None, faces=None):
        self.cx = cx
        st = CurvatureState(cx)
        self.edges = [tuple(sorted(e)) for e in (edges if edges is not None else cx.edges())]
        self.eindex = {e: i for i, e in enumerate(self.edges)}
        allowed = set(self.eindex)
        self.faces = [f for f in (faces if faces is not None else cx.faces())
                      if all(tuple(sorted(p)) in allowed
                             for p in ((f[0], f[1]), (f[1], f[2]), (f[0], f[2])))]
        self.vertices = sorted({v for e in self.edges for v in e})
        g = cx.group
        self.g = g
        self.els = list(g.elements)
        self.n = len(self.els)
        self.idx = {x: i for i, x in enumerate(self.els)}
        self.e_id = self.idx[g.identity()]
        self.mul = np.array([[self.idx[g.multiply(a, b)] for b in self.els] for a in self.els])
        self.inv = np.array([self.idx[g.inverse(a)] for a in self.els])
        self.dim = self.n ** len(self.edges)
        self.configs = np.array(list(itertools.product(range(self.n), repeat=len(self.edges))),
                                dtype=np.int64) if self.dim <= 4_000_000 else None

    # ---------------------------------------------------------------- gauge action
    def gauge_permutation(self, v, h):
        """Index permutation of the gauge move g_v -> h at vertex v.

        Convention: label(a, b) with a < b is the transport b -> a, so a move at v sends
        label(v, w) -> h . label(v, w) and label(w, v) -> label(w, v) . h^-1.
        """
        c = self.configs.copy()
        for i, (a, b) in enumerate(self.edges):
            if v == a:
                c[:, i] = self.mul[h, c[:, i]]          # label(a,b) stored with a < b
            elif v == b:
                c[:, i] = self.mul[c[:, i], self.inv[h]]
        return self._encode(c)

    def _encode(self, c):
        base = self.n ** np.arange(len(self.edges) - 1, -1, -1, dtype=np.int64)
        return c @ base

    def star_projector(self, v):
        """A_v as a dense matrix on the configuration basis (small patches only)."""
        P = np.zeros((self.dim, self.dim))
        for h in range(self.n):
            perm = self.gauge_permutation(v, h)
            P[perm, np.arange(self.dim)] += 1.0 / self.n
        return P

    def holonomy(self, face):
        """Holonomy index of every configuration around one face."""
        a, b, c = face
        h = np.full(self.dim, self.e_id, dtype=np.int64)
        for u, w in ((a, b), (b, c), (c, a)):
            key = (min(u, w), max(u, w))
            lab = self.configs[:, self.eindex[key]]
            if (u, w) != key:
                lab = self.inv[lab]
            h = self.mul[h, lab]
        return h

    def plaquette_projector(self, face):
        """B_f: diagonal projector onto trivial holonomy."""
        return np.diag((self.holonomy(face) == self.e_id).astype(float))

    def hamiltonian(self):
        """H = -sum_v A_v - sum_f B_f (Kitaev form); returns H and the two term lists."""
        A = [self.star_projector(v) for v in self.vertices]
        B = [self.plaquette_projector(f) for f in self.faces]
        H = -sum(A) - sum(B)
        return H, A, B

    # ---------------------------------------------------------------- defects
    def flux_faces(self, labels):
        """Faces with non-trivial holonomy for one classical label assignment."""
        g = self.g
        out = []
        for f in self.faces:
            h = g.identity()
            for u, w in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
                key = (min(u, w), max(u, w))
                lab = labels.get(key, g.identity())
                if (u, w) != key:
                    lab = g.inverse(lab)
                h = g.multiply(h, lab)
            if h != g.identity():
                out.append(f)
        return out


def flux_ring(cx, edge):
    """The faces a single edge's label disturbs: the closed ring around that edge (3D)."""
    a, b = edge
    return [tuple(sorted(f)) for f in cx.faces_around_edge(a, b)]


def ring_is_closed(cx, edge):
    """The flux ring closes iff every tetrahedron around the edge contributes two faces,
    each face shared by two tetrahedra: #faces == #tets. Boundary edges give open arcs."""
    a, b = edge
    faces = flux_ring(cx, edge)
    tets = cx.tets_around_edge(a, b)
    return len(faces) > 0 and len(faces) == len(tets)
