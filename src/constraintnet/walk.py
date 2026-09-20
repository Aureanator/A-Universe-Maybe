"""v4.0 implication walk (docs/DYNAMICS_DESIGN.md): gauge-covariant weighted reflection.

State: amplitude psi[arc, :] in C^dim on every directed edge v->w with v interior.
Tick:  U = S_rho . C
  C  at each vertex v: 2|phi_v><phi_v| - I on its outgoing arcs (same on every
     internal component), phi_v(v->w) = sqrt(w_vw / sum_w w_vw).
  S  arc v->w hops to arc w->v, transported by rho(A_wv) = rho(A_vw)^-1.
Boundary: ``mode="open"`` lets arcs into boundary vertices leave (sub-unitary:
the region is an open system); ``mode="closed"`` drops them (induced subgraph).
Weights by link-ring size: ring-4 edges get ring_weights[1], all others ring_weights[0].

Kernel-pure: no RNG, no scheduler, no coordinates. Time is the tick count.
"""

import numpy as np

from .curvature import CurvatureState


class ArcWalk:
    def __init__(self, cx, rep=None, dim=1, mode="open", ring_weights=(1.0, 0.5)):
        if mode not in ("open", "closed"):
            raise ValueError("mode must be 'open' or 'closed'")
        self.cx, self.rep, self.dim, self.mode = cx, rep, dim, mode
        st = CurvatureState(cx)
        ring = {st.edges[i]: len(st.edge_faces[i]) for i in range(len(st.edges))}
        boundary = {v for f in cx.boundary_faces() for v in f}
        verts = sorted(cx.vertices())
        self.interior = [v for v in verts if v not in boundary]
        inside = set(self.interior)
        nbrs = {v: [] for v in verts}
        for a, b in cx.edges():
            nbrs[a].append(b); nbrs[b].append(a)
        arcs, wts = [], []
        for v in self.interior:
            for w in sorted(nbrs[v]):
                if mode == "closed" and w not in inside:
                    continue
                arcs.append((v, w))
                r = ring[(min(v, w), max(v, w))]
                wts.append(ring_weights[1] if r == 4 else ring_weights[0])
        self.arcs = arcs
        self.index = {a: i for i, a in enumerate(arcs)}
        wts = np.array(wts, float)
        self.weights = wts
        self.src = np.array([a[0] for a in arcs])
        starts = [0] + [i for i in range(1, len(arcs)) if arcs[i][0] != arcs[i - 1][0]]
        self.starts = np.array(starts)
        self.vertex_of_arc = np.repeat(np.arange(len(starts)),
                                       np.diff(np.append(self.starts, len(arcs))))
        W = np.add.reduceat(wts, self.starts)
        self.vertex_weight = W
        self.phi = np.sqrt(wts / W[self.vertex_of_arc])
        target, mats = [], []
        for (v, w) in arcs:
            j = self.index.get((w, v))
            target.append(-1 if j is None else j)
            if rep is None:
                mats.append(np.eye(dim))
            else:
                mats.append(rep(cx.label(w, v)))          # rho(A_wv) = rho(A_vw)^-1
        self.target = np.array(target)
        self.mats = np.array(mats)
        self.kept = self.target >= 0

    @property
    def size(self):
        return len(self.arcs) * self.dim

    def coin_state(self, v):
        """phi_v as an arc vector (scalar profile); multiply by an internal vector."""
        out = np.zeros(len(self.arcs))
        sel = self.src == v
        out[sel] = self.phi[sel]
        return out

    def step(self, psi):
        """One tick. psi: (n_arcs, dim) complex."""
        ov = np.add.reduceat(self.phi[:, None] * psi, self.starts, axis=0)
        cpsi = 2 * self.phi[:, None] * ov[self.vertex_of_arc] - psi
        moved = np.einsum("aij,aj->ai", self.mats[self.kept], cpsi[self.kept])
        out = np.zeros_like(psi)
        out[self.target[self.kept]] = moved
        return out

    def matrix(self):
        """Dense U (size x size); for small complexes only."""
        n, d = len(self.arcs), self.dim
        U = np.zeros((n * d, n * d), complex)
        for k in range(n * d):
            e = np.zeros((n, d), complex)
            e[k // d, k % d] = 1
            U[:, k] = self.step(e).reshape(-1)
        return U

    def discriminant(self):
        """Classical-walk discriminant D_vw = w_vw / sqrt(W_v W_w) on interior vertices."""
        pos = {v: i for i, v in enumerate(self.interior)}
        D = np.zeros((len(self.interior), len(self.interior)))
        Wv = dict(zip(self.interior, self.vertex_weight))
        for (v, w), wt in zip(self.arcs, self.weights):
            if w in pos:
                D[pos[v], pos[w]] = wt / np.sqrt(Wv[v] * Wv[w])
        return D


def a4_irrep3(group):
    """3-dim irrep of A4 on sum-zero vectors: the tetrahedron's rotations."""
    Q = np.linalg.qr(np.vstack([np.ones(4), np.eye(4)[:3]]).T)[0][:, 1:]

    def rep(p):
        P = np.zeros((4, 4))
        for i, j in enumerate(p):
            P[j, i] = 1
        return Q.T @ P @ Q
    return rep


def _perm_parity(seq, ref):
    """Parity (+1/-1) of the permutation taking ref to seq."""
    pos = [ref.index(x) for x in seq]
    parity = 1
    for i in range(len(pos)):
        for j in range(i + 1, len(pos)):
            if pos[i] > pos[j]:
                parity = -parity
    return parity


class RecordWalk:
    """v4.1-sc (DYNAMICS_DESIGN section 8): v4.0 walk plus a responsive record.

    Labels are held as group-element indices. The tick is ``walk`` then
    ``write``; ``unstep`` inverts one tick exactly. Deterministic; no RNG.
    """

    def __init__(self, cx, kappa, ring_weights=(1.0, 0.5), mode="open"):
        self.cx = cx
        g = cx.group
        self.g = g
        self.els = list(g.elements)
        self.eidx = {x: i for i, x in enumerate(self.els)}
        self.rep = a4_irrep3(g)
        self.R = np.array([self.rep(x) for x in self.els])            # (12,3,3)
        self.mul = np.array([[self.eidx[g.multiply(x, y)] for y in self.els] for x in self.els])
        self.inv = np.array([self.eidx[g.inverse(x)] for x in self.els])
        # order-3 elements, their +120 degree axes (for Q)
        self.q_ids, axes = [], []
        for i, x in enumerate(self.els):
            if g.order_of(x) == 3:
                M = self.R[i]
                w, V = np.linalg.eig(M)
                n = np.real(V[:, np.argmin(abs(w - 1))]); n /= np.linalg.norm(n)
                # orient n so that M is a +120 degree rotation about n
                t = np.cross(n, [1.0, 0.3, 0.1]); t /= np.linalg.norm(t)
                if np.dot(np.cross(t, M @ t), n) < 0:
                    n = -n
                self.q_ids.append(i); axes.append(n)
        self.q_axes = np.array(axes)
        self.walk = ArcWalk(cx, rep=self.rep, dim=3, mode=mode, ring_weights=ring_weights)
        w = self.walk
        self.edges = sorted(cx.edges())
        self.edge_pos = {e: i for i, e in enumerate(self.edges)}
        self.lab = np.array([self.eidx[cx.label(a, b)] for a, b in self.edges])
        # arc -> (edge index, reversed?) for rebuilding transport matrices: arc v->w uses A_wv
        self.arc_edge = np.array([self.edge_pos[(min(v, u), max(v, u))] for v, u in w.arcs])
        self.arc_rev = np.array([u < v for v, u in w.arcs])   # A_wv = stored(w<v ? (w,v) : inverse)
        self.kappa = kappa
        # rings of interior edges whose ring vertices are interior
        inside = set(w.interior)
        self.ring_edges, self.rings = [], []
        for ei, (a, b) in enumerate(self.edges):
            if a not in inside or b not in inside:
                continue
            steps = {}
            for tet in cx.tets_around_edge(a, b):
                c, d = [x for x in tet if x not in (a, b)]
                if _perm_parity((a, b, c, d), tuple(cx.tet_order(tet))) > 0:
                    steps[c] = d
                else:
                    steps[d] = c
            start = min(steps)
            ring = [start]
            while steps[ring[-1]] != start:
                ring.append(steps[ring[-1]])
            if len(ring) != len(steps) or not all(c in inside for c in ring):
                continue
            fwd = [w.index[(ring[i], ring[(i + 1) % len(ring)])] for i in range(len(ring))]
            bwd = [w.index[(ring[(i + 1) % len(ring)], ring[i])] for i in range(len(ring))]
            self.ring_edges.append(ei); self.rings.append((a, b, np.array(fwd), np.array(bwd)))
        self.vpos = {v: i for i, v in enumerate(w.interior)}
        L = max((len(r[2]) for r in self.rings), default=0)
        n = len(self.rings)
        self.r_fwd = np.full((n, L), -1); self.r_bwd = np.full((n, L), -1)
        for i, (a, b, f, bk) in enumerate(self.rings):
            self.r_fwd[i, :len(f)] = f; self.r_bwd[i, :len(bk)] = bk
        self.r_a = np.array([self.vpos[r[0]] for r in self.rings], dtype=int)
        self.r_b = np.array([self.vpos[r[1]] for r in self.rings], dtype=int)
        self.ring_edges = np.array(self.ring_edges, dtype=int)
        self._rebuild()

    def _rebuild(self):
        lab = self.lab[self.arc_edge]
        lab = np.where(self.arc_rev, lab, self.inv[lab])     # arc v->w transports by A_wv
        self.walk.mats = self.R[lab]

    def spins(self, psi):
        cr = np.imag(np.cross(np.conj(psi), psi))              # per arc, real 3-vector
        return np.add.reduceat(cr, self.walk.starts, axis=0)   # per interior vertex (walk order)

    def Q(self, Y):
        """Vectorised: rows of Y -> index of the order-3 element whose axis best aligns."""
        return np.array(self.q_ids)[np.argmax(Y @ self.q_axes.T, axis=1)]

    def chops(self, psi):
        """(edge indices, s_a, s_b) of chops written this tick (vectorised)."""
        if not len(self.rings):
            return np.zeros(0, int), np.zeros(0, int), np.zeros(0, int)
        p2 = np.append((np.abs(psi) ** 2).sum(1), 0.0)         # index -1 -> 0
        K = p2[self.r_fwd].sum(1) - p2[self.r_bwd].sum(1)
        S = self.spins(psi)
        sa, sb = S[self.r_a], S[self.r_b]
        sel = (np.abs(K) >= self.kappa) & np.any(sa != 0, 1) & np.any(sb != 0, 1)
        sg = np.sign(K[sel])[:, None]
        return self.ring_edges[sel], self.Q(sg * sa[sel]), self.Q(sg * sb[sel])

    def step(self, psi):
        psi = self.walk.step(psi)
        ei, sa, sb = self.chops(psi)
        if len(ei):
            self.lab[ei] = self.mul[self.mul[sa, self.lab[ei]], sb]
            self._rebuild()
        return psi, len(ei)

    def unstep(self, psi):
        ei, sa, sb = self.chops(psi)
        if len(ei):
            self.lab[ei] = self.mul[self.mul[self.inv[sa], self.lab[ei]], self.inv[sb]]
            self._rebuild()
        U = self.walk
        back = np.zeros_like(psi)
        kept = U.kept
        back[kept] = np.einsum("aji,aj->ai", U.mats[kept], psi[U.target[kept]])
        ov = np.add.reduceat(U.phi[:, None] * back, U.starts, axis=0)
        return 2 * U.phi[:, None] * ov[U.vertex_of_arc] - back

    def curvature_count(self):
        for (a, b), li in zip(self.edges, self.lab):
            self.cx.set_label(a, b, self.els[li])
        from .landscape import curvature_action
        return curvature_action(self.cx)
