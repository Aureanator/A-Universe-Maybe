"""Sheaf-defect tests: locally free, globally obstructed -- Bianchi as counting."""

from constraintnet.sheaf import gluing_defect


def test_locally_free_globally_obstructed():
    r = gluing_defect("Z3")
    assert r["pairwise_locally_free"] is True          # no local law whatsoever
    assert r["globally_realizable"] == 27              # of 81 local worlds
    assert r["defect_forbidden_by_globality"] == 54    # forbidden by globality alone


def test_gauss_kernel_is_exactly_the_global_image():
    """Set equality (asserted inside gluing_defect) -- Bianchi is the ONLY obstruction."""
    r = gluing_defect("Z3")
    assert r["gauss_kernel_equals_global"] is True
    assert r["gauss_kernel_size"] == r["globally_realizable"]
