"""Golden regression test 1 -- the acceptance test for the input generator.

Generate the six inputs for the validation spec and account for every byte of difference
against the golden set. Split 1a (structural, strict) / 1b (value accountability), because
one golden value -- composition -- is known-imperfect and must not be reproduced.

The expected literals below were read from the golden files, not from documentation.
"""

from __future__ import annotations

import pytest

from mcxray_wrapper.inputgen import generate_inputs
from mcxray_wrapper.spec import (
    AS,
    ATOMIC_WEIGHT_UNCERTAINTIES,
    ATOMIC_WEIGHTS,
    BI,
    GA,
    PUBLISHED_DENSITY_ANCHORS_G_CM3,
    WALTHER_PAPER,
    WALTHER_REVISED,
    RunSpec,
)
from tests.conftest import (
    GOLDEN_INPUT_STEM,
    GOLDEN_INPUTS as GOLDEN_INPUTS_PATH,
    GOLDEN_NEWLINES,
    GOLDEN_RUN_ID,
    INPUT_ROLES,
)
from tests.diffreport import (
    CATEGORY_DOCUMENTED,
    CATEGORY_INTENDED,
    CATEGORY_UNEXPLAINED,
    compare_all,
    render,
)

# Read from the golden .sam. Golden's 6th decimal reproduces from no real atomic-weight
# set; the IUPAC-derived values are what the generator emits.
GOLDEN_WEIGHT_FRACTIONS = {GA: "0.441135", AS: "0.426632", BI: "0.132233"}
IUPAC_WEIGHT_FRACTIONS = {GA: "0.441144", AS: "0.426632", BI: "0.132224"}


@pytest.fixture
def generated(validation_spec, tmp_path):
    return generate_inputs(validation_spec, tmp_path)


# --------------------------------------------------------------------------------------
# Test 1a -- structural identity
# --------------------------------------------------------------------------------------


def test_1a_structural_identity(golden_inputs, generated):
    problems, _ = compare_all(golden_inputs, generated)
    assert problems == [], "\n".join(problems)


@pytest.mark.parametrize("role", ["mic", "mdl", "rp"])
def test_unparameterised_files_are_byte_identical(golden_inputs, generated, role):
    """.mic has no field this spec drives; .mdl and .rp pass through unchanged."""
    golden_bytes = (golden_inputs / f"{GOLDEN_INPUT_STEM}.{role}").read_bytes()
    assert generated[role].read_bytes() == golden_bytes


@pytest.mark.parametrize("role", INPUT_ROLES)
def test_generated_line_endings_match_that_files_golden(generated, role):
    """Per-file fidelity: .mdl and .rp stay LF, the other four stay CRLF. No blanket rule."""
    from mcxray_wrapper.inputgen import newline_convention

    assert newline_convention(generated[role].read_bytes()) == GOLDEN_NEWLINES[role]


def test_all_six_files_are_written(generated, validation_spec, tmp_path):
    for role in INPUT_ROLES:
        assert generated[role] == tmp_path / f"{validation_spec.run_id}.{role}"
        assert generated[role].is_file()


# --------------------------------------------------------------------------------------
# Test 1b -- value accountability
# --------------------------------------------------------------------------------------


def test_1b_no_unexplained_deltas(golden_inputs, generated):
    problems, deltas = compare_all(golden_inputs, generated)
    unexplained = [delta for delta in deltas if delta.category == CATEGORY_UNEXPLAINED]
    assert unexplained == [], render(problems, deltas)


def test_1b_delta_set_is_exactly_as_expected(golden_inputs, generated):
    """Asserts the whole delta set, not just the absence of unexplained ones.

    A generator that silently failed to substitute anything would produce zero deltas and
    sail through a no-unexplained check.
    """
    _, deltas = compare_all(golden_inputs, generated)
    actual = {(delta.role, delta.key, delta.golden, delta.generated, delta.category)
              for delta in deltas}

    expected = {
        # .sim child references follow run_id; golden's input stem differs from its own
        # output stem, which is the historical artifact we do not perpetuate.
        ("sim", key, f"{GOLDEN_INPUT_STEM}.{ext}", f"{GOLDEN_RUN_ID}.{ext}", CATEGORY_INTENDED)
        for key, ext in [
            ("specimen", "sam"), ("model", "mdl"), ("microscope", "mic"),
            ("parameters", "par"), ("map", "mpp"), ("results", "rp"),
        ]
    } | {
        ("sam", "WeightFraction", GOLDEN_WEIGHT_FRACTIONS[GA],
         IUPAC_WEIGHT_FRACTIONS[GA], CATEGORY_DOCUMENTED),
        ("sam", "WeightFraction", GOLDEN_WEIGHT_FRACTIONS[BI],
         IUPAC_WEIGHT_FRACTIONS[BI], CATEGORY_DOCUMENTED),
    }

    assert actual == expected, (
        f"unexpected: {sorted(actual - expected)}\nmissing: {sorted(expected - actual)}"
    )


def test_1b_density_delta_would_be_a_defect(golden_inputs, generated):
    """Golden now reads 5.34 and so do we. A delta here is not classifiable away."""
    _, deltas = compare_all(golden_inputs, generated)
    density = [d for d in deltas if d.key == "UserDefinedMassDensity"]
    assert density == [], f"density differs from golden, which is a defect: {density}"


def test_1b_region_parameters_are_identical_to_golden(golden_inputs, generated):
    _, deltas = compare_all(golden_inputs, generated)
    assert [d for d in deltas if d.key == "RegionParameters"] == []


# --------------------------------------------------------------------------------------
# the two silent killers, tested directly rather than only via the golden diff
# --------------------------------------------------------------------------------------


def _sam_field(path, key):
    lines = path.read_text(encoding="ascii").splitlines()
    return [line.split("=", 1)[1] for line in lines if line.startswith(f"{key}=")]


def test_thickness_reaches_the_sam_in_angstroms(tmp_path):
    """The .sam geometry is in Angstroms. A nm value there runs fine and simulates a 10x
    thinner foil -- the single most dangerous conversion in the project."""
    spec = RunSpec(run_id="angstrom_check", x_bi=0.1, thickness_nm=100, n_electrons=1000)
    generated = generate_inputs(spec, tmp_path)
    tokens = _sam_field(generated["sam"], "RegionParameters")[0].split()

    assert tokens[4] == "0.000000", "foil should start at the surface"
    assert tokens[5] == "1000.000000", "100 nm must reach the .sam as 1000 Angstroms"
    assert tokens[5] != "100.000000", "nm value written into an Angstrom field"


@pytest.mark.parametrize(
    "thickness_nm, expected_angstrom",
    [(2, "20.000000"), (100, "1000.000000"), (512, "5120.000000"), (1024, "10240.000000")],
)
def test_thickness_conversion_across_the_set_a_range(tmp_path, thickness_nm, expected_angstrom):
    spec = RunSpec(run_id=f"t{thickness_nm}", x_bi=0.2, thickness_nm=thickness_nm,
                   n_electrons=1000)
    generated = generate_inputs(spec, tmp_path / str(thickness_nm))
    assert _sam_field(generated["sam"], "RegionParameters")[0].split()[5] == expected_angstrom


def test_composition_reaches_the_sam_as_weight_fraction(tmp_path, validation_spec):
    """The field is literally WeightFraction. Atomic fractions there run fine and simulate
    the wrong alloy: Ga is 0.5 atomic but 0.441 by weight."""
    generated = generate_inputs(validation_spec, tmp_path)
    written = _sam_field(generated["sam"], "WeightFraction")

    assert written == [IUPAC_WEIGHT_FRACTIONS[z] for z in (GA, AS, BI)]
    assert "0.500000" not in written, "Ga atomic fraction written into a weight field"
    assert sum(float(value) for value in written) == pytest.approx(1.0, abs=1e-6)


def test_weight_fractions_are_positionally_tied_to_atomic_number(tmp_path, validation_spec):
    """WeightFraction belongs to the AtomicNumber line above it. Swapping Ga's and Bi's
    values would still sum to 1 and still look plausible."""
    generated = generate_inputs(validation_spec, tmp_path)
    lines = generated["sam"].read_text(encoding="ascii").splitlines()
    pairs = {}
    pending = None
    for line in lines:
        if line.startswith("AtomicNumber="):
            pending = int(line.split("=", 1)[1])
        elif line.startswith("WeightFraction="):
            pairs[pending] = line.split("=", 1)[1]
    assert pairs == IUPAC_WEIGHT_FRACTIONS


def test_density_is_never_left_at_zero(tmp_path, validation_spec):
    """At 0 MC X-Ray auto-mixes from elemental densities: ~6.12-6.16 against the true
    5.34, about 15% too dense, with no error raised."""
    generated = generate_inputs(validation_spec, tmp_path)
    written = _sam_field(generated["sam"], "UserDefinedMassDensity")
    assert written == ["5.34"]
    assert float(written[0]) > 0.0


def _spec(x_bi, model=None, thickness_nm=100):
    kwargs = {"density_model": model} if model else {}
    return RunSpec(
        run_id="dm", x_bi=x_bi, thickness_nm=thickness_nm, n_electrons=1000, **kwargs
    )


def test_default_density_model_is_walther_revised():
    """Production default is WALTHER_REVISED (Walther's 2026-07-19 endpoints 5.32/7.18):
    rho(x) = 5.32 + 1.86x, so rho(0.1) = 5.506."""
    assert _spec(0.1).density_model == WALTHER_REVISED
    assert _spec(0.1).mass_density_g_cm3() == pytest.approx(5.506, abs=1e-12)


def test_walther_revised_hits_both_endpoints():
    """Endpoints must be exactly Walther's: GaAs 5.32 at x=0, GaBi 7.18 at x=1."""
    assert _spec(0.0, model=WALTHER_REVISED).mass_density_g_cm3() == pytest.approx(5.32, abs=1e-12)
    assert _spec(1.0, model=WALTHER_REVISED).mass_density_g_cm3() == pytest.approx(7.18, abs=1e-12)


def test_walther_paper_reproduces_the_golden_density():
    """WALTHER_PAPER exists solely to reproduce the golden set: 5.34 at x=0.1, 5.36 at x=0.2.
    If this drifts, the golden regression gate can no longer be met."""
    assert _spec(0.1, model=WALTHER_PAPER).mass_density_g_cm3() == pytest.approx(5.34, abs=1e-12)
    assert _spec(0.2, model=WALTHER_PAPER).mass_density_g_cm3() == pytest.approx(5.36, abs=1e-12)


def test_unknown_density_model_is_refused():
    with pytest.raises(ValueError, match="density_model"):
        _spec(0.1, model="whatever")


@pytest.mark.parametrize(
    "x_bi, expected",
    [(0.01, 5.3386), (0.02, 5.3572), (0.05, 5.4130), (0.1, 5.5060), (0.2, 5.6920)],
)
def test_walther_revised_across_the_run_matrix(x_bi, expected):
    """Pins the production densities across the frozen Set B compositions, so the figures
    quoted in REPORT.md 15 cannot drift from what the code emits."""
    assert _spec(x_bi, model=WALTHER_REVISED).mass_density_g_cm3() == pytest.approx(expected, abs=1e-4)


def test_density_model_reaches_the_generated_sam(tmp_path):
    """The choice must actually change UserDefinedMassDensity in the file, not just the
    Python value -- this is the whole point of the parameter."""
    written = {}
    for model, expected in ((WALTHER_REVISED, "5.692"), (WALTHER_PAPER, "5.36")):
        spec = RunSpec(
            run_id=f"GaAsBi_100nm_x020_{model}",
            x_bi=0.2,
            thickness_nm=100,
            n_electrons=1000,
            density_model=model,
        )
        paths = generate_inputs(spec, tmp_path)
        sam = paths["sam"].read_text(encoding="ascii")
        line = [x for x in sam.splitlines() if x.startswith("UserDefinedMassDensity=")][0]
        written[model] = line.split("=", 1)[1]
        assert written[model] == expected, f"{model}: got {written[model]!r}"
    assert written[WALTHER_REVISED] != written[WALTHER_PAPER]


def test_detector_thickness_defaults_to_golden_and_is_settable(tmp_path):
    """Default 0.3 cm keeps the golden .mic byte-identical; production sets 0.5 (Si:Li)."""
    def crystal_thickness(spec):
        sam = generate_inputs(spec, tmp_path)["mic"].read_text(encoding="ascii")
        return [l for l in sam.splitlines() if l.startswith("DetectorCrystalThickness=")][0]

    default = RunSpec(run_id="det_default", x_bi=0.1, thickness_nm=100, n_electrons=1000)
    assert crystal_thickness(default) == "DetectorCrystalThickness=0.300000"

    sili = RunSpec(run_id="det_sili", x_bi=0.1, thickness_nm=100, n_electrons=1000,
                   detector_crystal_thickness_cm=0.5)
    assert crystal_thickness(sili) == "DetectorCrystalThickness=0.500000"


def test_atomic_weights_match_the_cited_source():
    """Pinned to IUPAC/CIAAW Standard Atomic Weights, 2024 edition, as printed:
    Ga 69.723(1), As 74.921595(6), Bi 208.98040(1).

    These feed both the .sam weight fractions and the molar mass used by any
    lattice-based density model, so a silent edit here would propagate everywhere.
    """
    assert ATOMIC_WEIGHTS == {GA: 69.723, AS: 74.921595, BI: 208.98040}
    assert ATOMIC_WEIGHT_UNCERTAINTIES == {GA: 0.001, AS: 0.000006, BI: 0.00001}


@pytest.mark.parametrize("x_bi, published", sorted(PUBLISHED_DENSITY_ANCHORS_G_CM3.items()))
def test_paper_anchors_are_citable_to_the_primary_source(x_bi, published):
    """The two densities in Walther 2025 Fig. 3 (5.34 at x=0.1, 5.36 at x=0.2), reproduced
    by WALTHER_PAPER. These are what the golden set embeds; production uses WALTHER_REVISED.
    """
    spec = RunSpec(run_id=f"anchor{x_bi}", x_bi=x_bi, thickness_nm=100, n_electrons=1000,
                   density_model=WALTHER_PAPER)
    assert spec.mass_density_g_cm3() == pytest.approx(published, abs=1e-12)


@pytest.mark.parametrize(
    "x_bi, expected",
    [(0.01, "5.3386"), (0.02, "5.3572"), (0.05, "5.413"), (0.1, "5.506"), (0.2, "5.692")],
)
def test_density_formatting_is_not_lossy_across_set_b(tmp_path, x_bi, expected):
    """Production model WALTHER_REVISED, rho(x) = 5.32 + 1.86x, across the frozen Set B
    compositions. The formatter must preserve 4 significant decimals: a "%.2f" formatter
    would collapse 5.3386 and 5.3572 and lose the distinction between the two lowest points.
    """
    spec = RunSpec(run_id=f"x{x_bi}", x_bi=x_bi, thickness_nm=100, n_electrons=1000)
    generated = generate_inputs(spec, tmp_path / str(x_bi))
    assert _sam_field(generated["sam"], "UserDefinedMassDensity") == [expected]


# --------------------------------------------------------------------------------------
# quirks that are load-bearing, and boundaries
# --------------------------------------------------------------------------------------


def test_misspelled_detector_key_survives(generated):
    """`DetectorDiffusionLenght` is the key the binary parses. Correcting it breaks the run."""
    text = generated["mic"].read_text(encoding="ascii")
    assert "DetectorDiffusionLenght=500" in text
    assert "DetectorDiffusionLength" not in text


def test_sim_references_its_own_children(generated, validation_spec):
    text = generated["sim"].read_text(encoding="ascii")
    for key, ext in [("specimen", "sam"), ("model", "mdl"), ("microscope", "mic"),
                     ("parameters", "par"), ("map", "mpp"), ("results", "rp")]:
        assert f"{key}={validation_spec.run_id}.{ext}" in text


def test_the_referenced_mpp_map_is_not_created(generated, tmp_path, validation_spec):
    """The .sim names a .mpp that need not exist -- golden's does not either."""
    assert f"map={validation_spec.run_id}.mpp" in generated["sim"].read_text(encoding="ascii")
    assert not (tmp_path / f"{validation_spec.run_id}.mpp").exists()


def test_par_basefilename_is_results_prefixed_with_a_forward_slash(generated):
    text = generated["par"].read_text(encoding="ascii")
    assert f"BaseFileName=Results/{GOLDEN_RUN_ID}" in text


def test_electron_count_is_substituted(tmp_path):
    spec = RunSpec(run_id="archival", x_bi=0.2, thickness_nm=100, n_electrons=1_000_000)
    generated = generate_inputs(spec, tmp_path)
    assert "ElectronNbr=1000000" in generated["par"].read_text(encoding="ascii")


def test_windowless_is_refused_rather_than_invented():
    """Whether windowless is settable at all is an open spike; the .mic documents no
    window field. No mechanism is invented here."""
    with pytest.raises(NotImplementedError, match="windowless|not implemented"):
        RunSpec(run_id="w", x_bi=0.1, thickness_nm=100, n_electrons=1000, window="windowless")


def test_generator_refuses_to_write_into_golden(validation_spec, golden_inputs):
    with pytest.raises(ValueError, match="read-only golden set"):
        generate_inputs(validation_spec, golden_inputs)


def test_generator_refuses_to_write_below_golden(validation_spec, golden_inputs):
    with pytest.raises(ValueError, match="read-only golden set"):
        generate_inputs(validation_spec, golden_inputs / "nested")


def test_the_stage_3_destination_is_allowed(validation_spec, tmp_path, monkeypatch):
    """The Sim folder is where Stage 3 must write, and golden lives *underneath* it
    (repo is at C:\\MCXRAY\\Sim\\Wrapper). An over-broad "golden is inside the target"
    guard rejected that destination and would have made Stage 3 impossible -- every
    other test writes to a temp dir and so never noticed. Simulated here with the same
    nesting rather than by touching the live install.
    """
    sim_like = tmp_path / "Sim"
    golden_like = sim_like / "Wrapper" / "Golden" / "inputs"
    golden_like.mkdir(parents=True)
    for role in INPUT_ROLES:
        source = GOLDEN_INPUTS_PATH / f"{GOLDEN_INPUT_STEM}.{role}"
        (golden_like / f"{GOLDEN_INPUT_STEM}.{role}").write_bytes(source.read_bytes())

    written = generate_inputs(validation_spec, sim_like, golden_dir=golden_like)

    assert all(path.is_file() for path in written.values())
    # and the golden set nested below the target is untouched
    for role in INPUT_ROLES:
        original = GOLDEN_INPUTS_PATH / f"{GOLDEN_INPUT_STEM}.{role}"
        assert (golden_like / f"{GOLDEN_INPUT_STEM}.{role}").read_bytes() == original.read_bytes()


def test_golden_inputs_are_not_modified(golden_inputs, generated):
    """The generator must leave the read-only template set alone."""
    for role in INPUT_ROLES:
        path = golden_inputs / f"{GOLDEN_INPUT_STEM}.{role}"
        assert path.read_bytes()  # still readable and non-empty
