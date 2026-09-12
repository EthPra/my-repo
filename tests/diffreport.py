"""Byte-accountable diff between generated and golden input files.

Split into two, because byte-identity is the wrong bar: one golden value (composition) is
known-imperfect, so demanding byte-identity everywhere would force the generator to
reproduce a transcription error.

  Test 1a -- structural identity. STRICT, zero tolerance. Same field names, same order,
             same line count, same line-ending convention, and every non-parameterised
             line byte-for-byte. This is where the real protection lives: the Angstrom
             trap, the weight-fraction trap and the misspelled-key trap are all structural.

  Test 1b -- value accountability. For parameterised fields only, every difference is
             classified. Nothing is silently tolerated: a wrong unit conversion and a
             cosmetic formatting change look identical unless every delta is surfaced.

Categories:
  1 INTENDED    -- a field RunSpec drives. Allowed, must be enumerated.
  2 FORMATTING  -- parsed numeric values identical, text differs. Allowed, must be listed.
  3 DOCUMENTED  -- the one known golden imperfection (composition), within tolerance.
                   Whitelisted to WeightFraction only; anything else claiming it FAILS.
  4 UNEXPLAINED -- FAILS.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mcxray_wrapper.inputgen import (
    GOLDEN_TEMPLATE_STEM,
    ROLES,
    SIM_CHILD_KEYS,
    newline_convention,
    split_keepends,
)

CATEGORY_INTENDED = 1
CATEGORY_FORMATTING = 2
CATEGORY_DOCUMENTED = 3
CATEGORY_UNEXPLAINED = 4

CATEGORY_NAMES = {
    CATEGORY_INTENDED: "INTENDED",
    CATEGORY_FORMATTING: "FORMATTING",
    CATEGORY_DOCUMENTED: "DOCUMENTED",
    CATEGORY_UNEXPLAINED: "UNEXPLAINED",
}

# Only these fields may differ at all. A delta on any other line is a structural failure,
# caught by Test 1a before classification is even reached.
PARAMETERISED_FIELDS: dict[str, set[str]] = {
    "sim": set(SIM_CHILD_KEYS),
    "sam": {"WeightFraction", "UserDefinedMassDensity", "RegionParameters"},
    "par": {"BaseFileName", "ElectronNbr"},
    "mic": set(),
    "mdl": set(),
    "rp": set(),
}

# Composition only. Golden's 6th decimal does not reproduce from any real atomic-weight
# set; the deviation is +/-9e-6, compensating between Ga and Bi, both sets summing to
# exactly 1.000000. Transcription residue, ~2e-5 relative. The generator emits the IUPAC
# values and this delta is documented, not matched.
WEIGHT_FRACTION_TOLERANCE = 1e-4


@dataclass(frozen=True)
class Delta:
    role: str
    line_no: int
    key: str
    golden: str
    generated: str
    category: int
    reason: str

    def render(self) -> str:
        return (
            f"  [{self.category} {CATEGORY_NAMES[self.category]}] {self.role}:{self.line_no} "
            f"{self.key}\n"
            f"      golden    : {self.golden}\n"
            f"      generated : {self.generated}\n"
            f"      reason    : {self.reason}"
        )


def _split_field(content: str) -> tuple[str, str]:
    key, sep, value = content.partition("=")
    if not sep:
        return "", content
    return key, value


def _numerically_identical(left: str, right: str) -> bool:
    """True when both sides parse as the same sequence of numbers."""
    left_tokens, right_tokens = left.split(), right.split()
    if len(left_tokens) != len(right_tokens) or not left_tokens:
        return False
    try:
        return all(float(a) == float(b) for a, b in zip(left_tokens, right_tokens))
    except ValueError:
        return False


def structural_problems(golden: bytes, generated: bytes, role: str) -> list[str]:
    """Test 1a. Empty list means structurally identical."""
    problems: list[str] = []

    golden_convention = newline_convention(golden)
    generated_convention = newline_convention(generated)
    if generated_convention != golden_convention:
        problems.append(
            f"{role}: line endings are {generated_convention}, golden is {golden_convention}"
        )
    if golden.endswith(b"\r\n") != generated.endswith(b"\r\n"):
        problems.append(f"{role}: trailing CRLF at EOF differs from golden")
    if golden.endswith(b"\n") != generated.endswith(b"\n"):
        problems.append(f"{role}: trailing newline at EOF differs from golden")

    golden_lines = split_keepends(golden.decode("ascii"))
    generated_lines = split_keepends(generated.decode("ascii"))
    if len(golden_lines) != len(generated_lines):
        problems.append(
            f"{role}: {len(generated_lines)} lines, golden has {len(golden_lines)}"
        )
        return problems

    golden_keys = [_split_field(content)[0] for content, _ in golden_lines]
    generated_keys = [_split_field(content)[0] for content, _ in generated_lines]
    if golden_keys != generated_keys:
        only_golden = set(golden_keys) - set(generated_keys)
        only_generated = set(generated_keys) - set(golden_keys)
        if only_golden:
            problems.append(f"{role}: fields missing from generated: {sorted(only_golden)}")
        if only_generated:
            problems.append(f"{role}: fields not in golden: {sorted(only_generated)}")
        if not only_golden and not only_generated:
            problems.append(f"{role}: field ordering differs from golden")

    parameterised = PARAMETERISED_FIELDS[role]
    for index, ((g_content, g_end), (n_content, n_end)) in enumerate(
        zip(golden_lines, generated_lines), start=1
    ):
        key = _split_field(g_content)[0]
        if key in parameterised:
            continue
        if g_content != n_content:
            problems.append(
                f"{role}:{index}: non-parameterised line differs\n"
                f"      golden    : {g_content!r}\n"
                f"      generated : {n_content!r}"
            )
        if g_end != n_end:
            problems.append(f"{role}:{index}: line ending differs from golden")

    return problems


def _classify(role: str, key: str, golden: str, generated: str) -> tuple[int, str]:
    if role == "sim" and key in SIM_CHILD_KEYS:
        return CATEGORY_INTENDED, "child-file reference follows run_id"
    if role == "par" and key == "BaseFileName":
        return CATEGORY_INTENDED, "output basename follows run_id"
    if role == "par" and key == "ElectronNbr":
        return CATEGORY_INTENDED, "trajectory count is a RunSpec parameter"

    if _numerically_identical(golden, generated):
        return CATEGORY_FORMATTING, "same parsed value, different text"

    if role == "sam" and key == "WeightFraction":
        try:
            delta = float(generated) - float(golden)
        except ValueError:
            return CATEGORY_UNEXPLAINED, "WeightFraction is not numeric"
        if abs(delta) <= WEIGHT_FRACTION_TOLERANCE:
            return (
                CATEGORY_DOCUMENTED,
                f"golden carries transcription residue; delta {delta:+.0e}, "
                f"within {WEIGHT_FRACTION_TOLERANCE:.0e}",
            )
        return (
            CATEGORY_UNEXPLAINED,
            f"WeightFraction delta {delta:+.3e} exceeds {WEIGHT_FRACTION_TOLERANCE:.0e}",
        )

    return CATEGORY_UNEXPLAINED, "not accounted for by any allowed category"


def value_deltas(golden: bytes, generated: bytes, role: str) -> list[Delta]:
    """Test 1b. One Delta per differing parameterised field."""
    golden_lines = split_keepends(golden.decode("ascii"))
    generated_lines = split_keepends(generated.decode("ascii"))
    parameterised = PARAMETERISED_FIELDS[role]
    deltas: list[Delta] = []

    for index, ((g_content, _), (n_content, _)) in enumerate(
        zip(golden_lines, generated_lines), start=1
    ):
        key, g_value = _split_field(g_content)
        if key not in parameterised or g_content == n_content:
            continue
        n_value = _split_field(n_content)[1]
        category, reason = _classify(role, key, g_value, n_value)
        deltas.append(
            Delta(
                role=role,
                line_no=index,
                key=key,
                golden=g_value,
                generated=n_value,
                category=category,
                reason=reason,
            )
        )
    return deltas


def compare_all(golden_dir: Path, generated: dict[str, Path]) -> tuple[list[str], list[Delta]]:
    """Compare by role, not by filename -- the golden's input stem differs from its own
    output stem, which is a historical artifact and is not perpetuated."""
    problems: list[str] = []
    deltas: list[Delta] = []
    for role in ROLES:
        golden_bytes = (golden_dir / f"{GOLDEN_TEMPLATE_STEM}.{role}").read_bytes()
        generated_bytes = generated[role].read_bytes()
        problems += structural_problems(golden_bytes, generated_bytes, role)
        deltas += value_deltas(golden_bytes, generated_bytes, role)
    return problems, deltas


def render(problems: list[str], deltas: list[Delta]) -> str:
    lines = ["Test 1a -- structural identity (strict, zero tolerance)"]
    if problems:
        lines += [f"  FAIL {problem}" for problem in problems]
    else:
        lines.append("  PASS  all six files: same fields, same order, same line endings,")
        lines.append("        every non-parameterised line byte-for-byte identical.")

    lines.append("")
    lines.append("Test 1b -- value accountability (parameterised fields only)")
    if not deltas:
        lines.append("  (no deltas)")
    for role in ROLES:
        role_deltas = [delta for delta in deltas if delta.role == role]
        if not role_deltas:
            continue
        lines.append(f"  --- .{role} ---")
        lines += [delta.render() for delta in role_deltas]

    counts = {category: 0 for category in CATEGORY_NAMES}
    for delta in deltas:
        counts[delta.category] += 1
    lines.append("")
    lines.append("  totals: " + ", ".join(
        f"{count} {CATEGORY_NAMES[category]}" for category, count in counts.items()
    ))

    unexplained = counts[CATEGORY_UNEXPLAINED]
    verdict = "PASS" if not problems and unexplained == 0 else "FAIL"
    lines.append("")
    lines.append(f"VERDICT: {verdict}  (gate: 1a clean and zero UNEXPLAINED)")
    return "\n".join(lines)


def main() -> None:
    import tempfile

    from tests.conftest import GOLDEN_INPUTS, validation_run_spec
    from mcxray_wrapper.inputgen import generate_inputs

    with tempfile.TemporaryDirectory() as tmp:
        generated = generate_inputs(validation_run_spec(), Path(tmp))
        problems, deltas = compare_all(GOLDEN_INPUTS, generated)
        print(render(problems, deltas))


if __name__ == "__main__":
    main()
