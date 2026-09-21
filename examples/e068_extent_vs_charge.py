"""E068: does an EXTENT-only, vacuum-controlled persistence criterion flag objects in the
regimes physics says should host them -- and agree with the charge-signature criterion?

Run: python examples/e068_extent_vs_charge.py
Writes reference/local_qwen/data/e068_extent_persistence.json.

E066 exposed that naive overlap-lineage survival is vacuous under unconstrained acceptance
(tracker follows the heat; clusters end at ~100% of global curvature). E067 built a Gauss-
solved charge sector with a measured confinement scale. This unit supplies the criterion
E066 promised (src/constraintnet/persistence_metrics.py: extent stability + locality vs a
MATCHED VACUUM) and asks one sharp question across two regimes, priors stated BEFORE running:

R1 relational-curvature (DriverA(relational), Z2 n=3): seed a localized curved-face lump.
   PRIOR: NOT independently persistent -- interior moves heat/diffuse the bulk (E065/E066),
   so locality -> ~1 and extent blows past its band; matched vacuum also grows structure,
   so the seed beats nothing. Expect verdict.independently_persistent = False.

R2 gauss-confined-pair (DriverG, Z2 n=3, high beta_E/beta_B): load a flux string between two
   far interior vertices (E067). PRIOR: INDEPENDENTLY PERSISTENT -- charge number is Gauss-
   protected (endpoints cannot vanish except by annihilation/exit) and confinement bounds the
   tube, so extent stays in band and locality stays low; matched vacuum noise is suppressed
   because spurious pairs cost energy. Expect verdict.independently_persistent = True.

If R2 comes out NOT persistent (e.g. the pair annihilates quickly), that is a real finding
about classical-Z2 confinement lifetime, reported as-is -- not tuned away. The point of an
INDEPENDENT criterion is precisely that it can disagree with expectation and be believed.

Agreement note: this extent-only criterion ignores charge signature entirely; where it agrees
with persistence.is_persistent (which uses the frozen conserved core), two independent notions
of "object" coincide -- evidence, not definition.
"""

import itertools
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from constraintnet.drivers import DriverA, DriverG
from constraintnet.gauss import GaussState
from constraintnet.holonomy import triangle_holonomy
from constraintnet.persistence_metrics import evaluate, signal_to_noise
from constraintnet.seeds import kuhn_ball

N = 3
STEPS = 500
SEEDS = (0, 1, 2)


# ---------------------------------------------------------------- curvature helpers
def curved(cx):
    ident = cx.group.identity()
    return {tuple(sorted(f)) for f in cx.faces() if triangle_holonomy(cx, f) != ident}


def face_components(curved_set, cx):
    face_tets = {}
    for t in (tuple(sorted(x)) for x in cx.tetrahedra()):
        for face in itertools.combinations(t, 3):
            face_tets.setdefault(face, []).append(t)
    unseen, out = set(curved_set), []
    while unseen:
        start = min(unseen)
        comp, queue = {start}, [start]
        unseen.discard(start)
        for f in queue:
            for t in face_tets.get(f, ()):
                for g in itertools.combinations(t, 3):
                    if g in unseen and g in curved_set:
                        unseen.discard(g); comp.add(g); queue.append(g)
        out.append(frozenset(comp))
    return out


def seed_lump(cx, rng_seed):
    import random
    rng = random.Random(rng_seed)
    edges = list(cx.edges())
    e0 = edges[len(edges) // 2]
    ident, other = list(cx.group.elements)
    cx.set_label(*e0, other)          # one flipped edge -> curved faces around it (a lump)
    seed_faces = frozenset(curved(cx))
    return seed_faces


def run_curvature(seed, with_seed=True):
    cx = kuhn_ball("Z2", n=N)
    if with_seed:
        seed_faces = seed_lump(cx, rng_seed=seed)
    else:
        seed_faces = frozenset()
    driver = DriverA(cx, rng_seed=seed, model="relational")
    support, glob, comps_over_time = [], [], []
    tracked = set(seed_faces)
    for _ in range(STEPS):
        driver.advance()
        cur = curved(cx)
        glob.append(len(cur))
        comps = face_components(cur, cx)
        comps_over_time.append(len(comps))
        if with_seed and tracked:
            cand = [c for c in comps if (tracked & c)]
            best = max(cand, key=lambda c: len(tracked & c)) if cand else frozenset()
            support.append(len(best))
            tracked = set(best) if best else tracked
        elif with_seed:
            support.append(0)
    return support, glob, comps_over_time


# ---------------------------------------------------------------- electric helpers
def flux_components(st):
    """Connected components of E=1 edges via shared vertices; returns list of edge-sets."""
    live = {i for i, b in enumerate(st.E) if b}
    adj = {}
    for i in live:
        u, w = st.edges[i]
        adj.setdefault(u, []).append(i); adj.setdefault(w, []).append(i)
    seen, out = set(), []
    for i in live:
        if i in seen:
            continue
        comp, queue = {i}, [i]; seen.add(i)
        while queue:
            e = queue.pop()
            for v in st.edges[e]:
                for j in adj.get(v, ()):
                    if j not in seen:
                        seen.add(j); comp.add(j); queue.append(j)
        out.append(comp)
    return out


def seed_string(st):
    interior = [v for v in st.vertices if v not in st.boundary_vertices]
    a, b = interior[0], interior[-1]
    path = st.shortest_path(a, b)
    st.load_string(path)
    return set(range(len(st.E))) & {i for i, bit in enumerate(st.E) if bit}, (a, b)


def run_electric(seed, beta_E, with_seed=True):
    cx = kuhn_ball("Z2", n=N)
    st = GaussState(cx)
    seed_edges, endpoints = (set(), None)
    if with_seed:
        seed_edges, endpoints = seed_string(st)
    driver = DriverG(st, rng_seed=seed, beta_B=8.0, beta_E=beta_E)
    support, glob, comps_over_time = [], [], []
    tracked = set(seed_edges)
    for _ in range(STEPS):
        driver.advance()
        live = {i for i, b in enumerate(st.E) if b}
        glob.append(len(live))
        comps = flux_components(st)
        comps_over_time.append(len(comps))
        if with_seed and tracked:
            cand = [c for c in comps if (tracked & c)]
            best = max(cand, key=lambda c: len(tracked & c)) if cand else set()
            support.append(len(best)); tracked = set(best) if best else tracked
        elif with_seed:
            support.append(0)
    return support, glob, comps_over_time


def summarize(supports, globs, vac_comps, vac_level):
    # verdict on the mean-support trajectory; vacuum noise + level from matched no-seed runs
    mean_support = [statistics.mean(s[i] for s in supports) for i in range(STEPS)]
    mean_glob = [statistics.mean(g[i] for g in globs) for i in range(STEPS)]
    v = evaluate(mean_support, mean_glob, band=3.0, vacuum_components=vac_comps)
    snr = signal_to_noise(mean_support, vac_level)
    support_defined = len(mean_support) > 0 and mean_support[0] > 0
    # lifetime None is only "survived" if extent was defined at t=0; zero averaged initial
    # support makes extent UNDEFINED (not survival) -- distinguish the two honestly.
    survived = v.survived_horizon and support_defined
    # TWO criteria reported side by side (E068 finding: locality alone misfires on a lone
    # object in a cold vacuum; the load-bearing gate is vacuum-relative SNR + bounded extent)
    persistent_locality_gate = survived and v.localized
    persistent_snr_gate = survived and snr > 1.0
    return {
        "lifetime_step": v.lifetime_step,
        "median_locality": v.median_locality,
        "vacuum_noise_mean": round(statistics.mean(vac_comps) if vac_comps else 0.0, 3),
        "vacuum_level": round(vac_level, 2),
        "signal_to_noise": round(snr, 2),
        "localized": v.localized,
        "extent_defined_at_t0": support_defined,
        "survived_horizon": survived,
        "persistent_LOCALITY_gate": survived and v.localized,
        "persistent_SNR_gate": survived and snr > 1.0,
    }


def main():
    results = {}

    # R1 relational curvature: seeded vs matched vacuum (no seed)
    r1_seed = [run_curvature(s, True) for s in SEEDS]
    r1_vac = [run_curvature(s, False) for s in SEEDS]
    vac_comps_r1 = [c for _, _, comps in r1_vac for c in comps]
    vac_level_r1 = statistics.mean(statistics.mean(g) for _, g, _ in r1_vac)
    results["R1_relational_curvature"] = summarize(
        [s for s, _, _ in r1_seed], [g for _, g, _ in r1_seed], vac_comps_r1, vac_level_r1)

    # R2 gauss-confined pair at high beta_E: seeded vs matched vacuum (no string)
    r2_seed = [run_electric(s, 8.0, True) for s in SEEDS]
    r2_vac = [run_electric(s, 8.0, False) for s in SEEDS]
    vac_comps_r2 = [c for _, _, comps in r2_vac for c in comps]
    vac_level_r2 = statistics.mean(statistics.mean(g) for _, g, _ in r2_vac)
    results["R2_gauss_confined_pair"] = summarize(
        [s for s, _, _ in r2_seed], [g for _, g, _ in r2_seed], vac_comps_r2, vac_level_r2)

    print(f"{'regime':>26} | lifetime locality vaclvl  SNR   persisted(locality-gate) persisted(SNR-gate)")
    for k, v in results.items():
        print(f"{k:>26} | {str(v['lifetime_step']):>8} {v['median_locality']:.3f} "
              f"{v['vacuum_level']:>5.1f} {v['signal_to_noise']:>5.2f}   "
              f"{str(v['persistent_LOCALITY_gate']):>7}                 {str(v['persistent_SNR_gate']):>7}")

    verdict = {
        "R1_not_persistent_both_gates": (results["R1_relational_curvature"]["persistent_LOCALITY_gate"] is False
                                         and results["R1_relational_curvature"]["persistent_SNR_gate"] is False),
        "R2_INCONCLUSIVE_extent_undefined_or_annihilated": (
            not results["R2_gauss_confined_pair"]["extent_defined_at_t0"]
            or results["R2_gauss_confined_pair"]["signal_to_noise"] <= 1.0),
        "metric_finding_locality_alone_misfires_on_cold_vacuum": (
            results["R2_gauss_confined_pair"]["median_locality"] >= 0.5
            and results["R2_gauss_confined_pair"]["vacuum_level"] < 1.0),
        # R2 PRIOR REFUTED IN-RUN (recorded, not tuned): a Gauss-confined pair is NOT an
        # independent persistent object -- at high beta_E retracting the string LOWERS energy,
        # so Metropolis drives the pair to annihilate into vacuum. Confinement bounds SEPARATION
        # but does not prevent ANNIHILATION; "confined" != "persistent". Matter needs a charge-
        # conjugation selection rule (see docs/ELECTRON_TARGET.md), which neither Gauss nor tension gives.
        "R2_prior_refuted_confinement_is_not_persistence": (
            results["R2_gauss_confined_pair"]["persistent_SNR_gate"] is False
            and results["R2_gauss_confined_pair"]["lifetime_step"] is not None),
    }
    print("\nVERDICTS:", json.dumps(verdict, indent=2))

    payload = {
        "provenance": {
            "script": "examples/e068_extent_vs_charge.py",
            "model": "local Qwen (LM Studio), E068 extent-based persistence criterion",
            "nature": ("extent-only criterion INDEPENDENT of charge-signature is_persistent; priors "
                       "R1/R2 stated in docstring before running; matched-vacuum controls included"),
        },
        "config": {"n": N, "steps": STEPS, "seeds": list(SEEDS), "band": 3.0},
        "results": results,
        "verdicts": verdict,
    }
    out = (Path(__file__).resolve().parents[1]
           / "reference" / "local_qwen" / "data" / "e068_extent_persistence.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
