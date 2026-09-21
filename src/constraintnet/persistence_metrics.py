"""Extent-based persistence metrics -- INDEPENDENT of the charge-signature criterion.

The Milestone-4 module :mod:`constraintnet.persistence` decides matter by a CONSERVED
EXTERNAL CHARGE SIGNATURE (frozen core + identity + connectivity, ``is_persistent``).
That is load-bearing and untouched here.

This module supplies a SECOND, INDEPENDENT criterion that consults NO charge signature at
all -- only the SIZE trajectory of a tracked component versus the global structure and a
matched-vacuum control. It exists because E066 exposed that naive overlap-lineage survival
is vacuous under unconstrained acceptance: when the vacuum heats, an extent tracker happily
follows the heat (tracked clusters ended at 96-100% of ALL global curvature while reporting
survival = 1.0). A defensible extent criterion must therefore (a) require the object to stay
LOCALIZED (not dilute into / absorb background that grew elsewhere) and (b) be judged against
a MATCHED VACUUM (same driver, same steps, NO seed) so "an object persisted" is not just
"the churn made something somewhere."

Pure measurement over trajectories: NO randomness, NO scheduler (kernel purity). Thresholds
are declared per-call and reported with every verdict so results can be re-cut. If this
extent-only criterion flags persistence in the SAME regimes where the charge-signature
criterion does, that agreement is evidence; if they disagree, which notion is load-bearing
becomes the finding. See examples/e068_extent_vs_charge.py.

Definitions:
* extent_stability(t) = |S(t)| / |S(0)| ; >>1 grew into the blob (E066 dissolution), <1/k
  shrank away, ~1 kept its size.
* lifetime_until(stability, band): first index leaving [1/band, band]; None if never.
* locality(tracked, global) = median |S(t)| / max(1,|G(t)|); ->1 means "became the vacuum"
  (E066 failure), small-with-nonzero-numerator means a compact object in a quiet background.
* vacuum_noise(components_over_time): mean spurious components in matched vacuum -- the floor
  any claimed persistence must beat, not zero.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence


def extent_stability(support_series: Sequence[float]) -> List[float]:
    """|S(t)| / |S(0)| elementwise; empty or zero-initial input yields []."""
    s0 = support_series[0] if support_series else 0
    if not s0:
        return []
    return [s / s0 for s in support_series]


def lifetime_until(stability: Sequence[float], band: float = 3.0) -> Optional[int]:
    """First index where extent_stability leaves [1/band, band]; None if it never does."""
    lo = 1.0 / band
    for i, s in enumerate(stability):
        if s > band or s < lo:
            return i
    return None


def locality(tracked_series: Sequence[float], global_series: Sequence[float]) -> float:
    """Median of tracked/global over the run; 0.0 if no samples."""
    ratios = sorted(t / max(1, g) for t, g in zip(tracked_series, global_series))
    n = len(ratios)
    if n == 0:
        return 0.0
    mid = n // 2
    if n % 2:
        return ratios[mid]
    return 0.5 * (ratios[mid - 1] + ratios[mid])


def vacuum_noise(components_over_time: Sequence[int]) -> float:
    """Mean number of connected components present in a matched-vacuum run."""
    if not components_over_time:
        return 0.0
    return sum(components_over_time) / len(components_over_time)


@dataclass(frozen=True)
class PersistenceVerdict:
    """One object's extent-normalized persistence, with its thresholds and control attached."""

    lifetime_step: Optional[int]      # None = stayed within the size band for the whole run
    median_locality: float            # fraction of global structure that is "the object"
    vacuum_noise_mean: float          # spurious components in matched vacuum (noise floor)
    band: float                       # extent band used (identity = within factor `band`)
    horizon: int                      # steps observed

    @property
    def localized(self) -> bool:
        """Did NOT become the background (E066 failure mode is locality -> ~1)."""
        return self.median_locality < 0.5

    @property
    def survived_horizon(self) -> bool:
        return self.lifetime_step is None

    @property
    def independently_persistent(self) -> bool:
        """Long-lived AND localized; the vacuum-noise comparison is applied by the caller
        against a per-run seed-survival baseline (see examples/e068_extent_vs_charge.py)."""
        return self.survived_horizon and self.localized


def evaluate(support_series, global_series, *, band=3.0, vacuum_components=None) -> PersistenceVerdict:
    """Assemble a verdict from raw trajectories (support = object size over time)."""
    stab = extent_stability(support_series)
    life = lifetime_until(stab, band=band)
    loc = locality(support_series, global_series)
    vn = vacuum_noise(vacuum_components or [])
    return PersistenceVerdict(
        lifetime_step=life, median_locality=round(loc, 4),
        vacuum_noise_mean=round(vn, 3), band=float(band), horizon=len(support_series),
    )
