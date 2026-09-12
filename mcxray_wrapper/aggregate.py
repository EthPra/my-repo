"""Stage 5 -- aggregator + provenance manifest.

Turns a list of RunSpecs plus their simulator outputs into two deliverables:

  1. a combined RAW-intensity table -- every parsed line from every run, one row per line
     per run, with each run's spec parameters attached as columns; and

  2. a provenance manifest -- one row per run, linking run_id to its spec (x, thickness,
     density model, density, electrons, detector) and to the input/output files on disk.

LOAD-BEARING RULE (CLAUDE.md governance): this stores RAW intensities only. No ratios, no
k-factors, no corrections. Those are Stage 6, a separate module that reads this table. The
open atomic-data questions (Lalpha2 folding, Bi M-lines) mean any derived number may need
re-deriving; that must be possible from this table without re-running simulations.

Provenance is VERIFIED, not just labelled: for each run the stored .sam is re-read and its
density and weight fractions are checked against the spec. A mismatch -- the file on disk
not matching the run it claims to be -- fails loudly rather than being aggregated silently.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from mcxray_wrapper.parser import parse_xray_intensities
from mcxray_wrapper.spec import GA, RunSpec

# The six input roles and the output stem suffix, for provenance linking.
INPUT_ROLES = ("sim", "sam", "mic", "par", "mdl", "rp")
INTENSITY_SUFFIX = "_XrayIntensities.csv"

# Spec columns attached to every intensity row, so the combined table is self-contained
# for downstream analysis (Stage 6 needs x and thickness beside each intensity).
SPEC_COLUMNS = (
    "run_id",
    "x_bi",
    "thickness_nm",
    "n_electrons",
    "density_model",
    "mass_density_g_cm3",
    "detector_crystal_thickness_cm",
)

# Provenance check tolerance. The .sam carries weight fractions to 6 dp and density trimmed;
# re-deriving from the spec should reproduce them exactly, so this only guards float noise.
_PROVENANCE_TOL = 5e-6


@dataclass(frozen=True)
class RunProvenance:
    """One run's spec, resolved file paths, and whether its stored .sam matches the spec."""

    spec: RunSpec
    input_files: dict[str, Path]
    intensity_csv: Path
    output_files: list[Path]
    sam_matches_spec: bool


def _spec_row(spec: RunSpec) -> dict:
    return {
        "run_id": spec.run_id,
        "x_bi": spec.x_bi,
        "thickness_nm": spec.thickness_nm,
        "n_electrons": spec.n_electrons,
        "density_model": spec.density_model,
        "mass_density_g_cm3": spec.mass_density_g_cm3(),
        "detector_crystal_thickness_cm": spec.detector_crystal_thickness_cm,
    }


def _verify_sam(spec: RunSpec, sam_path: Path) -> bool:
    """Re-read the stored .sam and confirm it is the file this spec would generate:
    density and the Ga weight fraction must match. Guards against a run_id pointing at the
    wrong file."""
    if not sam_path.is_file():
        return False
    text = sam_path.read_text(encoding="ascii")
    fields: dict[str, str] = {}
    last_z: int | None = None
    ga_weight: float | None = None
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key == "AtomicNumber":
            last_z = int(value)
        elif key == "WeightFraction" and last_z == GA:
            ga_weight = float(value)
        elif key == "UserDefinedMassDensity":
            fields["rho"] = value
    if ga_weight is None or "rho" not in fields:
        return False
    rho_ok = abs(float(fields["rho"]) - spec.mass_density_g_cm3()) < _PROVENANCE_TOL
    ga_ok = abs(ga_weight - spec.weight_fractions()[GA]) < _PROVENANCE_TOL
    return rho_ok and ga_ok


def resolve_provenance(spec: RunSpec, sim_dir: Path, results_dir: Path) -> RunProvenance:
    """Locate a run's inputs (in sim_dir) and outputs (in results_dir) and verify the .sam."""
    inputs = {role: sim_dir / f"{spec.run_id}.{role}" for role in INPUT_ROLES}
    intensity_csv = results_dir / f"{spec.run_id}{INTENSITY_SUFFIX}"
    outputs = sorted(results_dir.glob(f"{spec.run_id}_*"))
    return RunProvenance(
        spec=spec,
        input_files=inputs,
        intensity_csv=intensity_csv,
        output_files=outputs,
        sam_matches_spec=_verify_sam(spec, inputs["sam"]),
    )


def aggregate_runs(
    specs: list[RunSpec],
    sim_dir: Path,
    results_dir: Path,
    output_dir: Path,
) -> dict[str, Path]:
    """Aggregate the runs into a combined raw-intensity table and a provenance manifest.

    Writes into output_dir (created if absent; never inside results_dir). Returns the paths
    of the two files written. Raises if any run's output is missing or its .sam does not
    match the spec -- provenance failures are not aggregated.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    provenances = [resolve_provenance(s, sim_dir, results_dir) for s in specs]

    problems = []
    for p in provenances:
        if not p.intensity_csv.is_file():
            problems.append(f"{p.spec.run_id}: missing {p.intensity_csv.name}")
        elif not p.sam_matches_spec:
            problems.append(f"{p.spec.run_id}: stored .sam does not match the spec")
    if problems:
        raise ValueError("provenance check failed:\n  " + "\n  ".join(problems))

    # 1. Combined raw-intensity table: parse each run, attach spec columns, concatenate.
    frames = []
    for p in provenances:
        df = parse_xray_intensities(p.intensity_csv, p.spec.run_id)
        spec_row = _spec_row(p.spec)
        for col in SPEC_COLUMNS:
            if col == "run_id":
                continue  # parser already added it
            df[col] = spec_row[col]
        # Order: spec metadata first, then the raw parsed columns.
        lead = [c for c in SPEC_COLUMNS if c in df.columns]
        rest = [c for c in df.columns if c not in lead]
        frames.append(df[lead + rest])
    combined = pd.concat(frames, ignore_index=True)
    combined_path = output_dir / "combined_intensities.csv"
    combined.to_csv(combined_path, index=False)

    # 2. Provenance manifest: one row per run, with paths and the integrity flag.
    manifest = {
        "description": "Stage 5 provenance manifest -- raw intensities only, no derived values",
        "n_runs": len(provenances),
        "combined_table": combined_path.name,
        "runs": [
            {
                **_spec_row(p.spec),
                "sam_matches_spec": p.sam_matches_spec,
                "intensity_csv": str(p.intensity_csv),
                "input_files": {r: str(path) for r, path in p.input_files.items()},
                "n_output_files": len(p.output_files),
            }
            for p in provenances
        ],
    }
    manifest_path = output_dir / "provenance_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return {"combined_table": combined_path, "manifest": manifest_path}
