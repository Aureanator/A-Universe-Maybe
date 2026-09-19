"""Audit class-only matching against one common apex-frame alignment.

Run with PYTHONPATH=src. This is a convention probe, not an absorption model.
"""

from constraintnet.groups import AlternatingGroup4
from constraintnet.interaction import compatible_on_shared_face, face_flux


def main():
    group = AlternatingGroup4()
    identity = group.identity()
    x = (identity, (0, 2, 3, 1), (1, 2, 0, 3))
    y = (identity, (0, 2, 3, 1), (0, 3, 1, 2))
    shared = [((0, 1), identity), ((1, 2), identity), ((0, 2), identity)]
    index = {0: 0, 1: 1, 2: 2}

    def fluxes(state):
        return tuple(face_flux(group, state[v], label, state[w])
                     for (v, w), label in shared)

    flux_x, flux_y = fluxes(x), fluxes(y)
    class_match = all(group.class_of(a) == group.class_of(b)
                      for a, b in zip(flux_x, flux_y))
    alignments = [mu for mu in group.elements
                  if all(group.conjugate(mu, a) == b
                         for a, b in zip(flux_x, flux_y))]
    assert class_match and not alignments
    print(f"Per-edge conjugacy classes match: {class_match}")
    print(f"Common frame alignments: {len(alignments)}")
    print("Current library compatibility:",
          compatible_on_shared_face(group, x, y, shared, index, index))


if __name__ == "__main__":
    main()
