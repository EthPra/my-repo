"""Run specification for one MC X-Ray simulation, plus the quantities derived from it.

LOCKED by the experimental design. Do not make these configurable without an explicit
decision (CLAUDE.md, "Experimental design"):

    beam energy 200 keV, DetectorTOA=25, DetectorPitch=90, DetectorNoise=50,
    PhotonNbr=10000, EnergyChannelWidth=5, WindowNbr=64, and a free-standing foil
    (single BOX region, no substrate, vacuum both sides).

These locked values are not written by this module -- they already sit in the golden
templates, and inputgen asserts them there rather than re-emitting them. They are named
here so the locked design is readable in one place.

GENUINE PARAMETERS -- what a RunSpec carries, i.e. what may vary between runs:

    run_id, x_bi, thickness_nm, n_electrons, window.

Two conversions in here are the project's known silent killers. Both run without error
when wrong and produce plausible output:

    * thickness_angstrom() -- the .sam geometry is in ANGSTROMS, not the nanometres the
      v1.6 manual claims. A nm value in that field simulates a 10x thinner foil.
    * weight_fractions()   -- the .sam takes WEIGHT fraction, not atomic fraction. An
      atomic fraction in that field simulates the wrong alloy.
"""

from __future__ import annotations

from dataclasses import dataclass

# Atomic numbers of the three elements in GaAs(1-x)Bi(x).
GA = 31
AS = 33
BI = 83

ELEMENT_SYMBOLS = {GA: "Ga", AS: "As", BI: "Bi"}

# Standard atomic weights. VERIFIED 2026-07-19 against the primary source: IUPAC/CIAAW
# Standard Atomic Weights, 2024 edition (revision of the Atomic Weights 2021 report),
# https://www.ciaaw.org/atomic-weights.htm. Values as printed there, with uncertainties:
#
#     Ga  69.723(1)         As  74.921 595(6)        Bi  208.980 40(1)
#
# The project brief supplied As rounded to 74.9216; the full CIAAW value is used here
# instead. The change is inconsequential -- 0.07 ppm, leaving every weight fraction
# identical at the 6 dp written to the .sam and the molar mass unchanged to 5 dp -- but
# there is no reason to carry a rounded constant when the source value is known.
#
# Ga dominates the uncertainty budget at ~14 ppm relative (0.001/69.723); As and Bi are
# effectively exact by comparison, both being mononuclidic. Worth noting for context on the
# golden .sam's composition residue (REPORT.md 3, 6.5): its Ga offset is ~1.4 sigma of the
# CIAAW uncertainty and so could be an atomic-weight difference, but its Bi offset is
# ~1460 sigma and cannot be. That asymmetry is why the residue is classified as
# transcription rather than a different atomic-weight table.
# These are also the "A" of Walther's Eqs (2), (4) and (9) -- confirmed to be atomic WEIGHT,
# with rho (atomic density) a separate quantity that does not enter those equations. (Walther,
# personal communication, August 2026; the paper's "A for atomic densities" gloss conflated the
# two.) kfactors.py consumes them on that basis.
ATOMIC_WEIGHTS = {GA: 69.723, AS: 74.921595, BI: 208.98040}

# Uncertainties as printed by CIAAW, for anyone propagating an error budget later.
ATOMIC_WEIGHT_UNCERTAINTIES = {GA: 0.001, AS: 0.000006, BI: 0.00001}

# Density model rho(x) for GaAs(1-x)Bi(x), g/cm3. Two models, selected by
# RunSpec.density_model. Full history in REPORT.md 10 and 15.
#
#   WALTHER_REVISED (default, production) -- linear interpolation between the endpoint
#   densities Walther specified at the 2026-07-19 meeting: GaAs 5.32, hypothetical
#   zinc-blende GaBi 7.18. rho(x) = 5.32 + (7.18 - 5.32)*x = 5.32 + 1.86*x.
#
#     This SUPERSEDES the values in Walther's own paper (WALTHER_PAPER below). His reasoning:
#     both CASINO and MC X-Ray, left to auto-mix, interpolate the densities of the ELEMENTAL
#     metals Ga/As/Bi -- wrong for GaAsBi, whose bonds are covalent with slight ionicity, not
#     metallic. The 7.18 endpoint is his; it is consistent with Tixier's free-standing lattice
#     parameter (a(GaBi) = 6.33 A gives ~7.30; 7.18 <-> 6.36 A), so it agrees with the
#     lattice-based estimate of REPORT.md 10 to ~2%.
#
#     Walther's own caveat, same meeting: the choice of density model is NEGLIGIBLE for the
#     final result, because k*-factor calibration is self-correcting against a density offset
#     (it cancels in the calibrate-then-invert round trip). So this model is used for
#     correctness, not because the last percent matters.
#
#   WALTHER_PAPER (historical) -- the straight line through the two densities published in
#   Walther 2025, J. Microsc., DOI 10.1111/jmi.70058, Fig. 3 caption ("5.34 g cm-3 for
#   x = 0.1 and 5.36 g cm-3 for x = 0.2"): rho(x) = 5.32 + 0.20*x.
#
#     Retained for ONE reason: the golden set was generated with it (golden .sam carries
#     UserDefinedMassDensity=5.34 at x=0.1), so the golden regression test selects this model
#     to reproduce that byte-for-byte. NOT for new runs -- Walther revised it (above).
DENSITY_GAAS_G_CM3 = 5.32  # accepted GaAs density (Ioffe NSM; Blakemore 1982, 10.1063/1.331665)
DENSITY_GABI_G_CM3 = 7.18  # hypothetical zinc-blende GaBi, per Walther (2026-07-19 meeting)

WALTHER_PAPER_INTERCEPT_G_CM3 = 5.32  # coincides with the accepted GaAs density
WALTHER_PAPER_SLOPE_G_CM3 = 0.20  # (5.36 - 5.34) / (0.2 - 0.1)

# The two densities from Walther's paper, cited to the primary source. Regression-tested.
PUBLISHED_DENSITY_ANCHORS_G_CM3 = {0.1: 5.34, 0.2: 5.36}

WALTHER_REVISED = "walther_revised"
WALTHER_PAPER = "walther_paper"
DENSITY_MODELS = (WALTHER_REVISED, WALTHER_PAPER)

# Locked by the experimental design; asserted against the golden templates by inputgen.
LOCKED_BEAM_ENERGY_KEV = 200.0
LOCKED_DETECTOR_TOA_DEG = 25.0
LOCKED_DETECTOR_PITCH_DEG = 90.0
LOCKED_DETECTOR_NOISE_EV = 50.0
LOCKED_PHOTON_NBR = 10000
LOCKED_ENERGY_CHANNEL_WIDTH_EV = 5
# NOT the detector window. Options.txt echoes this as "Number of energy windows".
# The detector window is not settable through any input file: the .mic format documents
# no window field, and ATW (Al 0.02 um + Moxtek 0.3 um) is a compiled-in default.
LOCKED_WINDOW_NBR = 64

# "windowless" is not known to be settable at all -- that is an open spike. Until it is
# resolved there is no mechanism to invent, so anything but ATW is refused.
SUPPORTED_WINDOWS = ("ATW",)


@dataclass(frozen=True)
class RunSpec:
    """One simulation run. Everything not named here is locked by the design."""

    run_id: str
    x_bi: float
    thickness_nm: float
    n_electrons: int
    window: str = "ATW"
    # Production runs use Walther's revised model (2026-07-19); WALTHER_PAPER is retained
    # only so the golden regression test can reproduce the golden .sam's 5.34 (see the
    # density-model comment above). Selecting a model is a scientific choice.
    density_model: str = WALTHER_REVISED
    # Detector crystal thickness, cm. Golden default 0.3 (what generated the golden set).
    # Walther (2026-07-19): 0.5 for Si:Li, 0.04 for SDD. Production uses 0.5 (Si:Li, his
    # paper's detector). The golden gate keeps the default so it stays byte-identical.
    detector_crystal_thickness_cm: float = 0.3

    def __post_init__(self) -> None:
        if self.density_model not in DENSITY_MODELS:
            raise ValueError(
                f"density_model={self.density_model!r} is not one of {DENSITY_MODELS}. "
                "See REPORT.md 15: WALTHER_REVISED is production; WALTHER_PAPER exists only "
                "to reproduce the golden set. Silently falling back to either would be wrong."
            )
        if self.detector_crystal_thickness_cm <= 0:
            raise ValueError(
                f"detector_crystal_thickness_cm must be positive, got "
                f"{self.detector_crystal_thickness_cm}"
            )
        if self.window not in SUPPORTED_WINDOWS:
            raise NotImplementedError(
                f"window={self.window!r} is not implemented; only {SUPPORTED_WINDOWS} is "
                "supported. Whether a windowless detector is settable at all is an open "
                "question (pending a hands-on spike): the .mic format documents no window "
                "field. No mechanism is invented here."
            )
        if not self.run_id:
            raise ValueError("run_id must be a non-empty string")
        if not 0.0 <= self.x_bi <= 1.0:
            raise ValueError(f"x_bi must be in [0, 1], got {self.x_bi}")
        if self.thickness_nm <= 0:
            raise ValueError(f"thickness_nm must be positive, got {self.thickness_nm}")
        if self.n_electrons <= 0:
            raise ValueError(f"n_electrons must be positive, got {self.n_electrons}")

    def atomic_fractions(self) -> dict[int, float]:
        """Atomic fractions of the whole formula unit for GaAs(1-x)Bi(x).

        Ga occupies one sublattice; As and Bi share the other.
        """
        fractions = {
            GA: 0.5,
            AS: (1.0 - self.x_bi) / 2.0,
            BI: self.x_bi / 2.0,
        }
        total = sum(fractions.values())
        if abs(total - 1.0) > 1e-12:
            raise ValueError(f"atomic fractions sum to {total!r}, not 1")
        return fractions

    def weight_fractions(self) -> dict[int, float]:
        """w_i = a_i*M_i / sum_j(a_j*M_j).

        The .sam field is literally WeightFraction. Putting atomic fractions there runs
        fine and simulates the wrong alloy.
        """
        atomic = self.atomic_fractions()
        masses = {z: atomic[z] * ATOMIC_WEIGHTS[z] for z in atomic}
        total = sum(masses.values())
        return {z: masses[z] / total for z in masses}

    def mass_density_g_cm3(self) -> float:
        """Must reach the .sam as a non-zero UserDefinedMassDensity.

        The .sam format uses this value only when it is greater than 0.0; at 0 MC X-Ray
        auto-mixes from the ELEMENTAL densities of Ga/As/Bi, which is wrong for GaAsBi
        (covalent bonding, not metallic). Measured on this system, the auto-mix gave
        ~6.12-6.16 against ~5.5, with no error raised.

        Which model applies is set per-run by RunSpec.density_model (see the module-level
        density comment and REPORT.md 15):

          WALTHER_REVISED (default) -- linear between Walther's endpoint densities
            GaAs 5.32 and hypothetical GaBi 7.18: rho(x) = 5.32 + 1.86*x. Production model.

          WALTHER_PAPER -- rho(x) = 5.32 + 0.20*x, the line through his published anchors
            (5.34 at x=0.1, 5.36 at x=0.2). Retained only to reproduce the golden set.
        """
        if self.density_model == WALTHER_REVISED:
            slope = DENSITY_GABI_G_CM3 - DENSITY_GAAS_G_CM3  # 7.18 - 5.32 = 1.86
            return DENSITY_GAAS_G_CM3 + slope * self.x_bi
        # WALTHER_PAPER (membership already validated in __post_init__)
        return WALTHER_PAPER_INTERCEPT_G_CM3 + WALTHER_PAPER_SLOPE_G_CM3 * self.x_bi

    def thickness_angstrom(self) -> float:
        """The .sam BOX extents are in ANGSTROMS. 100 nm -> 1000."""
        return self.thickness_nm * 10.0
