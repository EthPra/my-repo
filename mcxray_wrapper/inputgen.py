"""Generate the six MC X-Ray input files for one run, by templating off the golden set.

LOCKED: which fields exist, their order, their spelling (including the misspelled
`DetectorDiffusionLenght`), and every physics-model and output-toggle value. None of that
is synthesised here -- the golden files are loaded and only the fields a RunSpec controls
are substituted. Everything else passes through byte-for-byte.

GENUINE PARAMETERS: composition weight fractions, mass density, BOX Z-extent, ElectronNbr,
BaseFileName, and the child-file names the .sim references.

Why templating rather than synthesis: the golden files are the only known-good definition
of the format. The v1.6 manual is wrong about units, and several fields have unknown
function. Building files field-by-field from documentation risks silently dropping or
mangling them, and errors of that kind do not raise -- they just simulate the wrong thing.

Line endings are NOT harmonised. The four files Ethan authored (.sim/.sam/.mic/.par) are
CRLF; the two the vendor ships (.mdl/.rp) are LF. MC X-Ray read both conventions in the
same successful run, so this is a fidelity detail rather than a correctness one -- but the
rule is still to reproduce what worked and introduce no variation. Templated files inherit
their line endings from their own template, and copied files are never decoded at all.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from mcxray_wrapper.spec import (
    LOCKED_BEAM_ENERGY_KEV,
    LOCKED_DETECTOR_NOISE_EV,
    LOCKED_DETECTOR_PITCH_DEG,
    LOCKED_DETECTOR_TOA_DEG,
    LOCKED_ENERGY_CHANNEL_WIDTH_EV,
    LOCKED_PHOTON_NBR,
    LOCKED_WINDOW_NBR,
    RunSpec,
)

# The golden set doubles as the template set. Read-only.
GOLDEN_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "Golden" / "inputs"
GOLDEN_TEMPLATE_STEM = "GaAsBi_val"

# Roles are the six file extensions. The .sim references all five others by filename.
ROLES = ("sim", "sam", "mic", "par", "mdl", "rp")

# .sim key -> extension of the child file it names. `map` points at a .mpp that need not
# exist; the golden references one that does not. Preserved, not created.
SIM_CHILD_KEYS = {
    "specimen": "sam",
    "model": "mdl",
    "microscope": "mic",
    "parameters": "par",
    "map": "mpp",
    "results": "rp",
}

# Locked values asserted against the golden templates rather than re-emitted, so that a
# template swap that quietly changed the design fails loudly here.
LOCKED_MIC_FIELDS = {
    "BeamEnergy": LOCKED_BEAM_ENERGY_KEV,
    "DetectorTOA": LOCKED_DETECTOR_TOA_DEG,
    "DetectorPitch": LOCKED_DETECTOR_PITCH_DEG,
    "DetectorNoise": LOCKED_DETECTOR_NOISE_EV,
}
LOCKED_PAR_FIELDS = {
    "PhotonNbr": float(LOCKED_PHOTON_NBR),
    "EnergyChannelWidth": float(LOCKED_ENERGY_CHANNEL_WIDTH_EV),
    "WindowNbr": float(LOCKED_WINDOW_NBR),
}

# The misspelling is the key the binary parses. Its presence confirms we are looking at
# the real format and not a "corrected" copy.
MISSPELLED_DETECTOR_KEY = "DetectorDiffusionLenght"


# --------------------------------------------------------------------------------------
# number formatting -- chosen to reproduce the golden files' text exactly
# --------------------------------------------------------------------------------------


def format_fraction(value: float) -> str:
    """6 dp, matching the golden .sam's WeightFraction (e.g. 0.441135)."""
    return f"{value:.6f}"


def format_length(value: float) -> str:
    """6 dp, matching the golden .sam's RegionParameters (e.g. 1000.000000)."""
    return f"{value:.6f}"


def format_density(value: float) -> str:
    """Shortest plain decimal, no trailing zeros. Golden writes `5.34`.

    Deliberately not "%.2f": that also reproduces 5.34, but would silently collapse
    Set B's x=0.002 and x=0.0002 (rho 5.3204 and 5.32004) to 5.32.
    """
    return f"{value:.6f}".rstrip("0").rstrip(".")


# --------------------------------------------------------------------------------------
# line handling -- \n is the only terminator recognised, endings are preserved verbatim
# --------------------------------------------------------------------------------------


def split_keepends(text: str) -> list[tuple[str, str]]:
    """Split into (content, ending) pairs. Ending is '\\r\\n', '\\n', or '' at EOF.

    str.splitlines() is not used: it also splits on \\v, \\f and friends, which these
    files must never be assumed free of.
    """
    parts = text.split("\n")
    lines: list[tuple[str, str]] = []
    for index, part in enumerate(parts):
        if index == len(parts) - 1:
            if part:  # trailing text with no terminator
                lines.append((part, ""))
        elif part.endswith("\r"):
            lines.append((part[:-1], "\r\n"))
        else:
            lines.append((part, "\n"))
    return lines


def join_keepends(lines: list[tuple[str, str]]) -> str:
    return "".join(content + ending for content, ending in lines)


def newline_convention(data: bytes) -> str:
    """'CRLF', 'LF', 'MIXED' or 'NONE'. Asserted rather than assumed."""
    crlf = data.count(b"\r\n")
    bare_lf = data.replace(b"\r\n", b"").count(b"\n")
    bare_cr = data.replace(b"\r\n", b"").count(b"\r")
    if bare_cr:
        return "MIXED"
    if crlf and bare_lf:
        return "MIXED"
    if crlf:
        return "CRLF"
    if bare_lf:
        return "LF"
    return "NONE"


def _split_field(content: str) -> tuple[str, str]:
    """'Key=value' -> ('Key', 'value'). Non-field lines yield ('', content)."""
    key, sep, value = content.partition("=")
    if not sep:
        return "", content
    return key, value


# --------------------------------------------------------------------------------------
# per-file rewriters
# --------------------------------------------------------------------------------------


def _rewrite_sim(text: str, spec: RunSpec) -> str:
    lines = split_keepends(text)
    out: list[tuple[str, str]] = []
    substituted: set[str] = set()
    for content, ending in lines:
        key, _ = _split_field(content)
        if key in SIM_CHILD_KEYS:
            content = f"{key}={spec.run_id}.{SIM_CHILD_KEYS[key]}"
            substituted.add(key)
        out.append((content, ending))
    missing = set(SIM_CHILD_KEYS) - substituted
    if missing:
        raise ValueError(f"golden .sim is missing child-file keys: {sorted(missing)}")
    return join_keepends(out)


def _rewrite_region_parameters(value: str, spec: RunSpec) -> str:
    """BOX extents: minX maxX minY maxY minZ maxZ, in ANGSTROMS.

    Only maxZ is ours. The other five tokens are passed through as their original strings
    rather than parsed and reformatted, so they cannot drift through a float round-trip.
    """
    tokens = value.split()
    if len(tokens) != 6:
        raise ValueError(f"expected 6 BOX extents, got {len(tokens)}: {value!r}")
    z_min = float(tokens[4])
    if z_min != 0.0:
        raise ValueError(
            f"golden BOX Zmin is {z_min}, expected 0.0; the foil does not start at the "
            "surface and thickness_nm no longer means what this code assumes"
        )
    tokens[5] = format_length(spec.thickness_angstrom())
    return " ".join(tokens)


def _rewrite_sam(text: str, spec: RunSpec) -> str:
    weights = spec.weight_fractions()
    lines = split_keepends(text)
    out: list[tuple[str, str]] = []
    pending_z: int | None = None
    written: set[int] = set()
    saw_density = False
    saw_region = False

    for content, ending in lines:
        key, value = _split_field(content)
        if key == "AtomicNumber":
            pending_z = int(value)
            if pending_z not in weights:
                raise ValueError(
                    f"golden .sam declares Z={pending_z}, which the spec has no weight "
                    f"fraction for (spec covers {sorted(weights)})"
                )
        elif key == "WeightFraction":
            # WeightFraction is positional: it belongs to the AtomicNumber above it.
            if pending_z is None:
                raise ValueError("golden .sam has a WeightFraction before any AtomicNumber")
            content = f"WeightFraction={format_fraction(weights[pending_z])}"
            written.add(pending_z)
            pending_z = None
        elif key == "UserDefinedMassDensity":
            content = f"UserDefinedMassDensity={format_density(spec.mass_density_g_cm3())}"
            saw_density = True
        elif key == "RegionParameters":
            content = f"RegionParameters={_rewrite_region_parameters(value, spec)}"
            saw_region = True
        out.append((content, ending))

    if written != set(weights):
        raise ValueError(
            f"golden .sam declares elements {sorted(written)}, spec expects {sorted(weights)}"
        )
    if not saw_density:
        raise ValueError("golden .sam has no UserDefinedMassDensity field")
    if not saw_region:
        raise ValueError("golden .sam has no RegionParameters field")
    return join_keepends(out)


def _rewrite_par(text: str, spec: RunSpec) -> str:
    _assert_locked_fields(text, LOCKED_PAR_FIELDS, ".par")
    lines = split_keepends(text)
    out: list[tuple[str, str]] = []
    substituted: set[str] = set()
    for content, ending in lines:
        key, _ = _split_field(content)
        if key == "BaseFileName":
            # Forward slash and the Results/ prefix are the golden's own convention.
            content = f"BaseFileName=Results/{spec.run_id}"
            substituted.add(key)
        elif key == "ElectronNbr":
            content = f"ElectronNbr={spec.n_electrons}"
            substituted.add(key)
        out.append((content, ending))
    missing = {"BaseFileName", "ElectronNbr"} - substituted
    if missing:
        raise ValueError(f"golden .par is missing fields: {sorted(missing)}")
    return join_keepends(out)


def _assert_locked_fields(text: str, expected: dict[str, float], label: str) -> None:
    found: dict[str, float] = {}
    for content, _ in split_keepends(text):
        key, value = _split_field(content)
        if key in expected:
            found[key] = float(value)
    missing = set(expected) - set(found)
    if missing:
        raise ValueError(f"golden {label} is missing locked fields: {sorted(missing)}")
    for key, want in expected.items():
        if found[key] != want:
            raise ValueError(
                f"golden {label} has {key}={found[key]}, but the experimental design locks "
                f"it to {want}. The template no longer matches the design."
            )


def _rewrite_mic(text: str, spec: RunSpec) -> str:
    # Same guards the byte-copy used to run, now that the .mic is templated for one field.
    _assert_locked_fields(text, LOCKED_MIC_FIELDS, ".mic")
    keys = {_split_field(content)[0] for content, _ in split_keepends(text)}
    if MISSPELLED_DETECTOR_KEY not in keys:
        raise ValueError(
            f"golden .mic has no {MISSPELLED_DETECTOR_KEY!r} field. That misspelling is the "
            "key the binary parses; its absence means this is not the real format."
        )
    # Only DetectorCrystalThickness is substituted (0.6f reproduces golden's "0.300000").
    # Crystal radius and everything else pass through byte-for-byte -- Walther confirmed the
    # 0.3 cm radius is fine, so it is left exactly as the golden template has it.
    lines = split_keepends(text)
    out: list[tuple[str, str]] = []
    substituted = False
    for content, ending in lines:
        key, _ = _split_field(content)
        if key == "DetectorCrystalThickness":
            content = f"DetectorCrystalThickness={spec.detector_crystal_thickness_cm:.6f}"
            substituted = True
        out.append((content, ending))
    if not substituted:
        raise ValueError("golden .mic is missing DetectorCrystalThickness")
    return join_keepends(out)


# --------------------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------------------

_TEMPLATED = {"sim": _rewrite_sim, "sam": _rewrite_sam, "par": _rewrite_par, "mic": _rewrite_mic}
_CHECKED_COPIES = {"mdl": None, "rp": None}


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def generate_inputs(
    spec: RunSpec,
    target_dir: Path | str,
    golden_dir: Path | str = GOLDEN_TEMPLATE_DIR,
) -> dict[str, Path]:
    """Write the six input files for `spec` into `target_dir`; return {role: path}.

    `target_dir` is always explicit and has no default. At Stage 3 it will be the Sim
    folder itself (that is where the exe resolves .sim child files from), but choosing
    that destination is not this module's business.
    """
    target_dir = Path(target_dir)
    golden_dir = Path(golden_dir)

    # Refuse only if the target is the golden set or sits inside it. Deliberately NOT
    # "golden sits inside the target": this repo lives at C:\MCXRAY\Sim\Wrapper, so golden
    # is a descendant of C:\MCXRAY\Sim -- which is the very directory Stage 3 must write
    # to, since that is where the exe resolves .sim child files from. Writing six files
    # into Sim\ cannot touch Sim\Wrapper\Golden\inputs\; only the check below can tell
    # those apart.
    if _is_within(target_dir, golden_dir):
        raise ValueError(f"refusing to write into the read-only golden set: {target_dir}")

    target_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}

    for role in ROLES:
        template_path = golden_dir / f"{GOLDEN_TEMPLATE_STEM}.{role}"
        if not template_path.is_file():
            raise FileNotFoundError(f"golden template missing: {template_path}")
        destination = target_dir / f"{spec.run_id}.{role}"
        raw = template_path.read_bytes()

        convention = newline_convention(raw)
        if convention == "MIXED":
            raise ValueError(f"golden template has mixed line endings: {template_path}")

        if role in _TEMPLATED:
            text = raw.decode("ascii")
            if join_keepends(split_keepends(text)) != text:
                raise ValueError(f"line splitter is not lossless on {template_path}")
            rewritten = _TEMPLATED[role](text, spec)
            destination.write_bytes(rewritten.encode("ascii"))
        else:
            check = _CHECKED_COPIES[role]
            if check is not None:
                check(raw.decode("ascii"))
            # Copied, never decoded and re-encoded: byte-for-byte by construction.
            shutil.copyfile(template_path, destination)

        written[role] = destination

    return written
