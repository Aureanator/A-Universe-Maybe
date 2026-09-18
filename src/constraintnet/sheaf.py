"""Gluing axiom test: locally free curvature data, globally obstructed (sheaf defect).

Question (born in retirement conversation, executed while still warm): treat face
curvatures as LOCAL observable data on patches of the mesh. A family of local values is
admissible if every overlap can be realized by SOME edge labelling of that patch. The
presheaf of curvatures would be a sheaf iff every locally admissible family glued to a
globally realizable one. It is not — and the defect is exactly Gauss/Bianchi:

    Z3 on the single tetrahedron (6 edges, 4 faces):
      * pairwise: EVERY curvature pair is realizable on any two faces sharing an edge
        (the patches are locally free — no local law at all);
      * globally: only 27 of 81 curvature quadruples arise from labellings, and they are
        exactly the Gauss-kernel { sum sigma_f Phi_f = 0 };
      * defect: 54 locally-perfect worlds are forbidden by global consistency alone.

Reading: conservation laws are not local rules wearing a disguise — they are the failure
of free gluing, i.e. the mesh's non-locality made countable. This re-derives Bianchi
(from M4/PHYSICS_NOTES §2) as an obstruction count and quantifies "geometry is global
bookkeeping". A4 version needs 12^6 enumeration or smarter orbit methods: open, flagged.

Pure kernel: exhaustive over 3^6 = 729 labellings; no RNG anywhere.
"""

from __future__ import annotations

from itertools import product
from typing import Dict, List, Tuple

from .complex import SimplicialComplex
from .holonomy import triangle_holonomy
from .seeds import make_single_tetrahedron

__all__ = ["gluing_defect"]


def gluing_defect(group: str = "Z3") -> Dict:
    """Count locally admissible vs globally realizable curvature families on d(tet)."""
    cx = make_single_tetrahedron(group)
    g = cx.group
    tet = next(iter(cx.tetrahedra()))

    # boundary faces with induced signs from the tetrahedron's orientation
    from .complex import face_induced_signs

    signs = face_induced_signs(cx.tet_order(tuple(sorted(tet))))
    faces = sorted(signs)  # four triangles, canonical order
    edges = sorted(cx.edges())

    def curvature_tuple(labels) -> Tuple:
        store = {key: labels[i] for i, key in enumerate(edges)}

        def lab(u, v):
            return store[(u, v)] if (u, v) in store else g.inverse(store[(v, u)])

        out = []
        for (i, j, k) in faces:
            out.append(g.multiply(g.multiply(lab(i, j), lab(j, k)), lab(k, i)))
        return tuple(out)

    # global image: every labelling -> curvature quadruple
    global_set = set()
    for labels in product(g.elements, repeat=len(edges)):
        global_set.add(curvature_tuple(labels))

    n = g.order()
    all_families = n ** len(faces)  # 81 for Z3

    # Gauss kernel check: signed sum vanishes (abelian groups only; Z3 here)
    def gauss_ok(t) -> bool:
        total = g.identity()
        for value, face in zip(t, faces):
            term = value if signs[face] > 0 else g.inverse(value)
            total = g.multiply(total, term)
        return total == g.identity()

    assert all(gauss_ok(t) for t in global_set), "Bianchi violated?! engine integrity failure"
    kernel = {t for t in product(g.elements, repeat=len(faces)) if gauss_ok(t)}
    # equality of sets (not just counts): the Gauss kernel IS the global image
    assert kernel == global_set, "Gauss kernel != global image: theory needs a second constraint"

    # pairwise projections: is every pair realizable on each overlapping face-pair?
    pairwise_full = True
    for a in range(len(faces)):
        for b in range(a + 1, len(faces)):
            proj = {(t[a], t[b]) for t in global_set}
            if len(proj) != n * n:
                pairwise_full = False

    return {
        "group": g.name,
        "n_faces": len(faces),
        "all_local_families": all_families,
        "globally_realizable": len(global_set),
        "gauss_kernel_size": len(kernel),
        "gauss_kernel_equals_global": True,  # asserted by set equality above
        "pairwise_locally_free": pairwise_full,
        "defect_forbidden_by_globality": all_families - len(global_set),
    }
