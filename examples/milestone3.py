"""Milestone 3 -- cone over ``d(Delta^3)`` and the count of hidden internal states.

Builds ``v * d(Delta^3)``, fixes an external boundary ``B``, enumerates all admissible
internal assignments, quotients by gauge transformations invisible at the boundary, and
reports ``|I(B)|``:

* ``|I| = 1`` -- direct / light-like: the exterior determines the interior uniquely;
* ``|I| > 1`` -- matter-like: the same external data admits several inequivalent interiors;
* ``|I| = 0`` -- forbidden: no internal resolution exists for that boundary and flux.

Run: ``PYTHONPATH=src python examples/milestone3.py``
"""

from __future__ import annotations

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from constraintnet.groups import AlternatingGroup4  # noqa: E402
from constraintnet.holonomy import triangle_holonomy  # noqa: E402
from constraintnet.resolutions import (  # noqa: E402
    materialise_resolution,
    resolution_space,
    resolution_table,
)
from constraintnet.seeds import make_cone_over_tetrahedron  # noqa: E402


def rule(title: str) -> None:
    print()
    print("=" * 74)
    print(title)
    print("=" * 74)


def main() -> int:
    a4 = AlternatingGroup4()

    rule("1. The cone  v * d(Delta^3)  = Delta^4")
    cx, apex, boundary = make_cone_over_tetrahedron("A4")
    print(f"   {cx.summary()}")
    print(f"   chi = {cx.euler_characteristic()} (a ball; the cone fills the tetrahedral boundary)")
    print(f"   interior vertex      : {apex}")
    print(f"   internal edges       : {[(apex, v) for v in boundary]}  <- genuine hidden variables")
    print("   equivalence          : x_i -> nu^-1 x_i (only the apex transforms: invisible outside)")

    rule("2. Flat boundary, no flux: |I| = 1 -- light-like")
    space = resolution_space(cx, apex, boundary)
    print(f"   raw assignments      : {space.count_raw} (= |G| = {a4.order()}, the free apex gauge)")
    print(f"   |I(B)|               : {space.count_physical}")
    print(f"   interpretation       : {space.kind()}")

    rule("3. Curved boundary, no flux: |I| = 0 -- curvature cannot be capped off")
    for seed in range(4):
        curved, apex_c, bnd_c = make_cone_over_tetrahedron("A4", seed_labels=seed)
        curved_faces = [f for f in curved.faces() if triangle_holonomy(curved, f) != a4.identity()]
        space_c = resolution_space(curved, apex_c, bnd_c)
        print(f"   seed {seed}: boundary curvature on {len([f for f in curved_faces if 4 not in f])} faces"
              f" -> raw={space_c.count_raw:3d} |I|={space_c.count_physical}  {space_c.kind()}")

    rule("4. Flux classes: matter appears when the interior may carry curvature")
    edges = [tuple(sorted(pair)) for pair in itertools.combinations(boundary, 2)]
    classes = list(a4.conjugacy_classes())
    names = [a4.class_name(sorted(cls, key=repr)[0]) for cls in classes]
    print("   interior-face order  :", [list(e) for e in edges])
    for index, (cls, name) in enumerate(zip(classes, names)):
        flux = {edge: cls for edge in edges}
        space_f = resolution_space(cx, apex, boundary, flux)
        verdict = "unrealisable" if space_f.count_physical == 0 else f"|I| = {space_f.count_physical}"
        print(f"   all six faces in class {index} ({name:34s}): raw={space_f.count_raw:5d}  {verdict}")

    rule("5. Full flux census (one pass over all |G|^4 interiors)")
    table = resolution_table(cx, apex, boundary)
    entries = table["entries"]
    histogram: dict = {}
    for info in entries.values():
        histogram[info["physical"]] = histogram.get(info["physical"], 0) + 1
    print(f"   realisable flux patterns : {len(entries)} of {len(classes) ** 6} possible")
    print("   |I| histogram            : " + ", ".join(
        f"|I|={k}: {v} patterns" for k, v in sorted(histogram.items())
    ))
    top = list(entries.items())[:5]
    print("   most hidden interiors    :")
    for signature, info in top:
        readable = " ".join(f"{edges[i]}:{names[s]}" for i, s in enumerate(signature))
        print(f"     |I|={info['physical']:2d} (raw {info['raw']:4d})  {readable}")

    rule("6. Abelian control: Z3 has no hidden interior at all")
    cx3, apex3, bnd3 = make_cone_over_tetrahedron("Z3")
    table3 = resolution_table(cx3, apex3, bnd3)
    values = {info["physical"] for info in table3["entries"].values()}
    print(f"   realisable patterns  : {len(table3['entries'])}")
    print(f"   |I| values observed  : {sorted(values)}")

    rule("Checks")
    assert space.count_physical == 1, "flat boundary with no flux must be light-like"
    assert space.count_raw == a4.order(), "raw count should be exactly the free apex gauge"
    for seed in range(4):
        curved, apex_c, bnd_c = make_cone_over_tetrahedron("A4", seed_labels=seed)
        if any(triangle_holonomy(curved, f) != a4.identity() for f in curved.faces() if 4 not in f):
            assert resolution_space(curved, apex_c, bnd_c).count_physical == 0
    order_two_class = next(cls for cls in classes if a4.order_of(sorted(cls, key=repr)[0]) == 2)
    matter = resolution_space(cx, apex, boundary, {edge: order_two_class for edge in edges})
    assert matter.count_physical > 1, "expected a matter-like flux pattern"
    assert matter.count_raw == matter.count_physical * a4.order(), "orbits should be free"
    light_like = [sig for sig, info in entries.items() if info["physical"] == 1]
    assert len(light_like) == 1 and light_like[0] == tuple([0] * 6), "vacuum must be the unique light-like interior"
    assert values == {1}, "abelian groups should admit no hidden internal states"

    # a resolution really is a labelling: materialise one and re-check its curvature classes
    representative = matter.representatives[0]
    materialise_resolution(cx, apex, boundary, representative)
    print(f"   materialised |I|={matter.count_physical} representative x = "
          f"{[a4.format(v) for v in representative]}")
    print("   interior face curvatures now:", [
        a4.class_name(triangle_holonomy(cx, (apex, i, j))) for (i, j) in edges
    ])

    print()
    print("MILESTONE 3 COMPLETE: |I(B)| computed; light-like, matter-like and forbidden")
    print("boundaries all occur, and hidden internal ambiguity requires a non-abelian group.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
