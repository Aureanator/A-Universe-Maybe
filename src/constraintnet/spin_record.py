"""Quantum record over the binary tetrahedral group 2T, with a spin-1/2 walker.

Same construction as ``qrecord.QuantumRecordWalk`` (DYNAMICS_DESIGN section 10), but the labels
live in 2T (the double cover of A4) and the walker's internal space is the 2-dim spinor
representation, which P29b showed is what stationary circulation requires.

State Psi[arc, record_config, 2]; one fixed unitary per tick, U = U_rec . U_walk, with
U_rec = exp(-i lB W/2) (x)_e exp(-i lE L/8) exp(-i lB W/2),
W = sum over faces touching a quantum edge of (1 - chi(hol)/2), chi the spinor character.
Note chi(-1) = -2, so a face whose holonomy is the double cover's central element (a 2 pi
rotation) costs the maximum 2, while a flat face costs 0.
"""

import numpy as np
from scipy.linalg import expm, schur

from .walk import ArcWalk


def binary_tetrahedral():
    """The 24 unit quaternions of 2T as SU(2) matrices, identity first."""
    qs = [np.array([1.0, 0, 0, 0])]
    for i in range(4):
        for s in (1, -1):
            if i == 0 and s == 1:
                continue
            q = np.zeros(4); q[i] = s
            qs.append(q)
    for signs in np.ndindex(2, 2, 2, 2):
        qs.append(np.array([(-1.0) ** s for s in signs]) / 2)
    out = []
    for w_, x, y, z in qs:
        out.append(np.array([[w_ + 1j * z, y + 1j * x], [-y + 1j * x, w_ - 1j * z]], complex))
    return out


class SpinRecordWalk:
    def __init__(self, cx, qedges, lam_E, lam_B, ring_weights=(1.0, 0.5), mode="closed",
                 frozen=None):
        self.cx = cx
        self.R = np.array(binary_tetrahedral())                      # (24,2,2), R[0] = I
        self.ng = len(self.R)
        self.e_id = 0
        self.mul = np.array([[self._index(self.R[i] @ self.R[j]) for j in range(self.ng)]
                             for i in range(self.ng)])
        self.inv = np.array([self._index(self.R[i].conj().T) for i in range(self.ng)])
        self.mode = mode
        self.walk = w = ArcWalk(cx, rep=None, dim=2, mode=mode, ring_weights=ring_weights)
        self.frozen = {} if frozen is None else {(min(a, b), max(a, b)): g for (a, b), g in frozen.items()}
        self.qedges = [tuple(sorted(e)) for e in qedges]
        self.k = k = len(self.qedges)
        self.nc = self.ng ** k
        self.qarcs = []
        for ax, (a, b) in enumerate(self.qedges):
            iab, iba = w.index.get((a, b)), w.index.get((b, a))
            if iab is None or iba is None:
                raise ValueError("quantum edges must join interior vertices")
            self.qarcs.append((ax, iab, iba))
        # frozen labels on the remaining arcs
        mats = np.zeros((len(w.arcs), 2, 2), complex)
        for i, (a, b) in enumerate(w.arcs):
            key = (min(a, b), max(a, b))
            g = self.frozen.get(key, 0)
            M = self.R[g]
            mats[i] = M.conj().T if a < b else M          # arc a->b transports by rho(A_ba)
        w.mats = mats
        n = len(w.arcs)
        self.src = np.full(n, n)
        self.src[w.target[w.kept]] = np.nonzero(w.kept)[0]
        self.lost = np.nonzero(~w.kept)[0]
        qset = {i for _, i, j in self.qarcs} | {j for _, i, j in self.qarcs}
        self.plain = np.array([a for a in range(n) if a not in qset])
        self.chi = np.trace(self.R, axis1=1, axis2=2).real
        gens = [i for i in range(self.ng) if abs(np.trace(self.R[i]).real - 1.0) < 1e-9]   # order-6 class
        L = np.zeros((self.ng, self.ng))
        for s in gens:
            for g in range(self.ng):
                L[g, g] += 1
                L[self.mul[s, g], g] -= 1
        self.L8 = L / max(len(gens), 1)
        self.W = self._wilson()
        self.lam_E, self.lam_B = lam_E, lam_B
        self.E1 = expm(-1j * lam_E * self.L8)
        self.half = np.exp(-0.5j * lam_B * self.W)
        self._bufs = {}
        self.vac = self._vacuum()

    def _index(self, M):
        d = np.abs(self.R - M[None]).reshape(self.ng, -1).max(axis=1)
        j = int(np.argmin(d))
        if d[j] > 1e-8:
            raise ValueError("matrix is not in 2T")
        return j

    def _wilson(self):
        qpos = {e: ax for ax, e in enumerate(self.qedges)}
        idx = np.indices((self.ng,) * self.k).reshape(self.k, -1)
        faces = [f for f in self.cx.faces()
                 if any(tuple(sorted(p)) in qpos for p in ((f[0], f[1]), (f[1], f[2]), (f[0], f[2])))]
        self.faces = faces
        W = np.zeros(self.nc)
        for f in faces:
            h = np.zeros(self.nc, int)
            for u, v in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
                key = (min(u, v), max(u, v))
                lab = (idx[qpos[key]] if key in qpos
                       else np.full(self.nc, self.frozen.get(key, 0)))
                if (u, v) != key:
                    lab = self.inv[lab]
                h = self.mul[h, lab]
            W += 1 - self.chi[h] / 2
        return W

    def _along(self, M, X, ax):
        return np.moveaxis(np.tensordot(M, X, axes=([1], [ax + 1])), 0, ax + 1)

    def apply_rec(self, Psi, inverse=False):
        half = self.half.conj() if inverse else self.half
        E = self.E1.conj().T if inverse else self.E1
        A, _, B = Psi.shape
        X = (half[None, :, None] * Psi).reshape((A,) + (self.ng,) * self.k + (B,))
        for ax in range(self.k):
            X = self._along(E, X, ax)
        return half[None, :, None] * X.reshape(A, self.nc, B)

    def apply_H(self, Psi):
        A, _, B = Psi.shape
        X = Psi.reshape((A,) + (self.ng,) * self.k + (B,))
        out = sum(self._along(self.L8, X, ax) for ax in range(self.k))
        return self.lam_E * out.reshape(Psi.shape) + self.lam_B * self.W[None, :, None] * Psi

    def rec_matrix(self):
        return self.apply_rec(np.eye(self.nc, dtype=complex)[None])[0]

    def _vacuum(self):
        e0 = np.zeros(self.nc, complex)
        e0[np.ravel_multi_index((self.e_id,) * self.k, (self.ng,) * self.k)] = 1
        if self.lam_E == 0:
            return e0
        T, Z = schur(self.rec_matrix(), output="complex")
        ev = np.diag(T)
        amp = Z.conj().T @ e0
        j = int(np.argmax(np.abs(amp)))
        cl = np.abs(ev - ev[j]) < 1e-9
        v = Z[:, cl] @ amp[cl]
        return v / np.linalg.norm(v)

    def _transport(self, X, ax, adjoint):
        R = np.conj(np.transpose(self.R, (0, 2, 1))) if adjoint else self.R
        Xk = np.moveaxis(X.reshape((self.ng,) * self.k + (2,)), ax, 0)
        Y = np.einsum("gij,g...j->g...i", R, Xk)
        return np.moveaxis(Y, 0, ax).reshape(X.shape)

    def walk_step(self, Psi):
        w = self.walk
        n = len(w.arcs)
        shape = (n + 1,) + Psi.shape[1:]
        B = self._bufs.get("B")
        if B is None or B.shape != shape or B.dtype != Psi.dtype:
            B = self._bufs["B"] = np.zeros(shape, Psi.dtype)
        Bn = B[:n]
        np.multiply(w.phi[:, None, None], Psi, out=Bn)
        ov = np.add.reduceat(Bn, w.starts, axis=0)
        np.take(ov, w.vertex_of_arc, axis=0, out=Bn)
        Bn *= 2 * w.phi[:, None, None]
        Bn -= Psi
        self.escaped = Bn[self.lost].copy() if len(self.lost) else None
        out = np.take(B, self.src, axis=0)
        for ax, iab, iba in self.qarcs:
            out[w.target[iab]] = self._transport(Bn[iab], ax, True)
            out[w.target[iba]] = self._transport(Bn[iba], ax, False)
        return out

    def step(self, Psi, record=True):
        Psi = self.walk_step(Psi)
        return self.apply_rec(Psi) if record else Psi

    def product_state(self, psi_walker):
        return psi_walker[:, None, :] * self.vac[None, :, None]
