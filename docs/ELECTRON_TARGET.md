# Williamson–van der Mark structure: explicit reproduction target

Requested by the user on 2026-09-19. Status: **TARGET / NOT REPRODUCED**.
This guides experiments; it adds no electron object or microscopic rule.

## Reference and intended structure

J. G. Williamson and M. B. van der Mark, *Is the electron a photon with
toroidal topology?*, Annales de la Fondation Louis de Broglie 22(2), 133–160
(1997): [publisher's original paper](https://fondationlouisdebroglie.org/AFLB-222/MARK.TEX2.pdf).

The semiclassical proposal assumes a self-confined photon with one-wavelength
periodicity. Its field orientation accompanies a double circulation on toroidal
surfaces, with one full twist; the characteristic transport radius is lambda/(4 pi).
It discusses charge, half-integral spin and magnetic moment. Confinement is
postulated, a rigorous external electric-divergence derivation is not supplied,
and full quantum spin projection/statistics are explicitly left unresolved
(sections 1–4 and 7). This is a structural research target, not an established
identification of the electron.

## Operational gates for this repository

These are our proposed tests, not claims that the paper or present solver passes
them. The user has selected the target; a resemblance in a rendering is insufficient.

| Gate | Required evidence in constraintnet | Current status |
|---|---|---|
| W0: microscopic realization | Define the complete proposed state from simplices and labels, with any additional variables or rules declared. A prepared fixture must be labelled as prepared. | Not yet supplied for this target. P13 is a pair of linked loops, not one double-traversing oriented excitation. **2026-09-19:** the v4 state space (active implications with amplitude and orientation on directed edges, labels as record) is specified in `DYNAMICS_DESIGN.md`; this target's W0 must be expressed in it. |
| W1: localized circulation | Show moving, recurring gauge-invariant field/support observables under a stated driver, without pinning a core, reflecting wall, or prescribed trajectory. Report perturbation and vacuum controls. | Open. A static curved-face loop is not an energy-flow trajectory. A Driver B odometer period is not a physical clock. |
| W2: transported orientation | Specify a measurable internal orientation and its transport. Track position and orientation separately, and demonstrate the proposed return period without inserting it as a counter. | Open. The current labels have not been shown to provide the necessary phase/framing observable. |
| W3: persistence and mobility | Establish an independent barrier or lifetime relative to controls; test displacement and interactions with boundaries moved farther away. | Open. P12/P13 have decay/merger witnesses for other fixtures. |
| W4: external charge | Demonstrate a conserved, operationally measurable exterior residue; separately derive any identification with electromagnetic charge and its field law. | Holonomy observables exist. They are not yet Coulomb charge or a gapless electromagnetic sector. |
| W5: spin and exchange | Establish the appropriate rotation action on the candidate state space and independent exchange behavior of two identical localized candidates. | Open. A double traversal, a minus sign in a chosen representation, or the D(A4) loop-braiding result does not suffice. |
| W6: quantitative response | Define energy, momentum, angular momentum and magnetic response from the model; test dimensionless relations and scaling before assigning SI units. | Open. Curved-face action is a declared driver hypothesis, not measured electron mass. **2026-09-19:** mass is now defined as translation rewrite cost / maintenance cost of trapped circulation (M1/M2 in `DYNAMICS_DESIGN.md`). An electron candidate must show both definitions agree and satisfy E² = m² + p². |
| W7: emergence and reactions | After fixture validation, recover the structure from a declared ensemble and test pair creation/annihilation and selective binding with conservation accounting. | Open. Prepared structures and geometric mergers do not pass this gate. |

The basement axiom remains the project's framing. Group, mesh, boundary,
proposal law, action, quantum state space and measure must each keep their own
derived/postulated status. No confinement rule, special electron label, forced
minus sign, or fixed period will be introduced and then reported as an emergence.

## Next executable work

The P13 action-barrier question is closed. The linked fixture decays nonincreasingly
(P14), and so do non-commuting tethered links (P15). Under H, closed flux
loops alone do not persist, so W3 cannot be passed by a flux-loop fixture under the
present action. First question (historical wording kept): does the saved linked-flux
fixture admit a wholly nonincreasing decay? This measures how much the existing
reduction law supplies before proposing W0/W1 machinery. It tests the present
solver, not the referenced electron proposal. Afterward, specify a state-space
and gauge-invariant transport observable for W0/W2 before attempting an electron
fixture. Missing ingredients must be demonstrated as gaps rather than silently
replaced by a drawing, a scheduler period, or a supplied electromagnetic wave.

## Quantum-record follow-up (2026-09-20, Astra)

P19–P25 supply a reversible wave engine, a partial quantum record, cooling proxies
and compatible prepared dark-loop states. P26 tests phase-selected joint states
with full-step residuals, a boundary-size comparison and open release. These are
prerequisite diagnostics for W3, not a Williamson–van der Mark realization.

In particular, weight concentrated on a cycle does not demonstrate directed
circulating transport. P26 does not measure an operational current, a transported
orientation return period, or spin/exchange. W0–W2 remain open, as does mobility:
the quantum record still occupies three prescribed edges. Any further candidate
must separate these gates from mere persistence of a prepared dark mode.

**P27 current gate.** A probability-current observable now satisfies exact local
continuity in this walk, including record entanglement and open outflow. It is
not yet an electromagnetic energy or charge current. The conditional theorem in
DYNAMICS_DESIGN section 15 proves that an exact eigenray confined strictly to a
loop with available positive-weight exits has zero net current on every edge.
Unitary record/internal transport cannot evade that norm argument.

Thus making a compact dark loop perfectly stationary would not, by itself,
produce directed circulation. An exact stationary candidate carrying nonzero
probability current in this same architecture must relax that strict support
condition, for example through a surrounding field. Whether such a field binds
itself, remains mobile, and supplies the target's orientation structure is open.
