"""Stage 4 -- the frozen production run matrix.

The 15 runs the project actually ran (REPORT.md 11, 15). This is the authoritative list:
the aggregator (Stage 5) is driven by it rather than by globbing the Results directory, so
the obsolete comparison runs (_wal_/_tix_) in that directory are never picked up by accident.

LOCKED by the experimental design and Walther's 2026-07-19 guidance -- see the constants.
"""

from __future__ import annotations

from mcxray_wrapper.spec import RunSpec

# Set A -- thickness arm, x fixed. LO4 geometric doubling series.
SET_A_X_BI = 0.2
SET_A_THICKNESSES_NM = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]

# Set B -- composition arm, thickness fixed. LO4 range 0.01-0.2.
SET_B_THICKNESS_NM = 100
SET_B_X_BI = [0.01, 0.02, 0.05, 0.1, 0.2]

# Set C -- the low-x thickness arm (added 2026-08-13, Ethan's sign-off; the 15 above stay
# frozen). Sets A and B form a CROSS: A sweeps thickness at x=0.2, B sweeps x at 100 nm, and
# nothing sits at low x AND high t -- exactly where the Bi signal is weakest and the absorption
# path longest, i.e. where "at what x does Bi stop being measurable" is actually answered.
#
# Interpolating into that corner was tested and rejected. Predicting Set B's Ga K/L from Set A
# alone, treating absorption as a function of rho.t, is exact at x=0.2 (-0.05%) but drifts
# monotonically to -3.80% at x=0.01 -- ~100x the 0.037% Monte-Carlo noise floor, and that is at
# 100 nm, with the absorption path ten times shorter than the thick end. Bi is a heavy absorber,
# so the alloy's mass attenuation coefficient moves with COMPOSITION, not only with density:
# rho.t alone does not determine absorption, and the cross cannot predict its own interior.
#
# Mirrors Set A's thick half only. The thin end is deliberately omitted: foils <=16 nm need 10^7
# electrons and measured ~21.6 min each against ~2-10 min for the thick runs, and thin foils are
# the regime where absorption -- the thing this arm probes -- is negligible anyway.
SET_C_X_BI = 0.01
SET_C_THICKNESSES_NM = [32, 64, 128, 256, 512, 1024]

# Walther (2026-07-19): 10^7 electrons for thin foils, 10^6 otherwise. Measured cutoff: foils
# <=16 nm fall below 10,000 MC counts at 10^6 (REPORT.md 15.4).
THIN_CUTOFF_NM = 16
N_ELECTRONS_THIN = 10_000_000
N_ELECTRONS_THICK = 1_000_000

# Si:Li detector crystal, per Walther (was 0.3 in the golden set).
PRODUCTION_DETECTOR_THICKNESS_CM = 0.5


def _electrons_for(thickness_nm: float) -> int:
    return N_ELECTRONS_THIN if thickness_nm <= THIN_CUTOFF_NM else N_ELECTRONS_THICK


def _production_run_id(x_bi: float, thickness_nm: float) -> str:
    """`GaAsBi_<t>nm_x<xxx>_rho<dddd>` -- the exact stem the runs were written under.

    Density encoded as rho*1000 so the value is readable off a flat directory and these do
    not collide with the obsolete `_wal_`/`_tix_` runs. Must match the on-disk filenames.
    """
    probe = RunSpec(
        run_id="probe",
        x_bi=x_bi,
        thickness_nm=thickness_nm,
        n_electrons=_electrons_for(thickness_nm),
        detector_crystal_thickness_cm=PRODUCTION_DETECTOR_THICKNESS_CM,
    )
    t = int(thickness_nm)
    return f"GaAsBi_{t}nm_x{round(x_bi * 100):03d}_rho{round(probe.mass_density_g_cm3() * 1000)}"


def _make_spec(x_bi: float, thickness_nm: float) -> RunSpec:
    return RunSpec(
        run_id=_production_run_id(x_bi, thickness_nm),
        x_bi=x_bi,
        thickness_nm=thickness_nm,
        n_electrons=_electrons_for(thickness_nm),
        detector_crystal_thickness_cm=PRODUCTION_DETECTOR_THICKNESS_CM,
        # density_model defaults to WALTHER_REVISED (production).
    )


def production_matrix() -> list[RunSpec]:
    """The 15 production runs: Set A (10 thicknesses) + Set B (5 compositions).

    Deliberately UNCHANGED by the Set C extension. Every result derived before 2026-08-13 was
    computed from exactly this list, so leaving it fixed keeps those reproducible and keeps the
    Set A / Set B filters in kfactors.py and roundtrip.py meaning what they meant. Use
    full_matrix() to include Set C.
    """
    specs = [_make_spec(SET_A_X_BI, t) for t in SET_A_THICKNESSES_NM]
    specs += [_make_spec(x, SET_B_THICKNESS_NM) for x in SET_B_X_BI]
    return specs


def extension_matrix() -> list[RunSpec]:
    """Set C only: the 6 low-x thickness runs (x=0.01, 32-1024 nm)."""
    return [_make_spec(SET_C_X_BI, t) for t in SET_C_THICKNESSES_NM]


def full_matrix() -> list[RunSpec]:
    """All 21 runs: the frozen 15 plus Set C. This is what the aggregator should be driven by.

    Still a fixed list rather than a directory glob, so the obsolete `_wal_`/`_tix_` comparison
    runs sharing the flat Results directory are never picked up by accident.
    """
    return production_matrix() + extension_matrix()
