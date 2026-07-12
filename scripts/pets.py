# -*- coding: utf-8 -*-
"""Validate, audit, and install catalogued Codex pet packages.

The runtime surface is narrow: two files per pet. The production surface carries
the evidence needed to rebuild and challenge those files. See README.md.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from config import (
    ATLAS_SIZE,
    CELL_SIZE,
    DIR_CATALOG,
    DIR_PRODUCTION,
    LOOK_DIRECTIONS,
    PET_IDS,
    ROOT,
    ROW_CONTRACT,
)
from rebuild_atlas import (
    compose_atlas,
    resolve_relative_file,
    rgba_digest,
    sha256_file,
)

ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PRIVATE_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:[\\/]"),
    re.compile(r"(?:^|[\s\"'(=])/(?:Users|home|tmp|private/var/folders)/", re.IGNORECASE),
    re.compile(
        "wx" + "id_|xwechat" + "_files|RW" + "Temp|generated" + "_images",
        re.IGNORECASE,
    ),
)
TEXT_SUFFIXES = {".json", ".md", ".py", ".txt"}
REQUIRED_MANIFEST_KEYS = {
    "id",
    "displayName",
    "description",
    "spriteVersionNumber",
    "spritesheetPath",
}
PRODUCTION_MANIFEST = "production-manifest.json"
EXPECTED_VISUAL_JOBS = (
    "base",
    "idle",
    "running-right",
    "running-left",
    "waving",
    "jumping",
    "failed",
    "waiting",
    "running",
    "review",
    "look-cardinals",
    "look-row-9",
    "look-row-10",
)


class ContractError(RuntimeError):
    """Report one violated repository or Codex runtime invariant."""


@dataclass(frozen=True)
class PetReport:
    pet_id: str
    atlas_path: Path
    visible_pixels: int
    file_sha256: str
    rgba_sha256: str


def load_json(path: Path) -> dict[str, object]:
    """Read one UTF-8 JSON object."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"invalid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON root must be an object: {path}")
    return value


def validate_cells(image: Image.Image) -> int:
    """Enforce the used and transparent slots of the 11-row contract."""

    alpha = image.getchannel("A")
    width, height = CELL_SIZE
    visible_pixels = 0
    for row, (_, used_columns) in enumerate(ROW_CONTRACT):
        for column in range(8):
            box = (
                column * width,
                row * height,
                (column + 1) * width,
                (row + 1) * height,
            )
            histogram = alpha.crop(box).histogram()
            count = sum(histogram[1:])
            if column < used_columns and count == 0:
                raise ContractError(f"required cell is empty: row={row}, column={column}")
            if column >= used_columns and count != 0:
                raise ContractError(
                    f"unused cell is not transparent: row={row}, column={column}"
                )
            visible_pixels += count
    return visible_pixels


def validate_atlas(path: Path, pet_id: str) -> PetReport:
    """Validate one lossless RGBA WebP against the Codex v2 grid."""

    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ContractError(f"{pet_id}: atlas is not a RIFF WebP")
    if int.from_bytes(data[4:8], "little") + 8 != len(data):
        raise ContractError(f"{pet_id}: atlas RIFF length is inconsistent")
    chunks: list[bytes] = []
    offset = 12
    while offset < len(data):
        if offset + 8 > len(data):
            raise ContractError(f"{pet_id}: atlas has a truncated WebP chunk")
        chunk = data[offset : offset + 4]
        length = int.from_bytes(data[offset + 4 : offset + 8], "little")
        offset += 8 + length + (length % 2)
        if offset > len(data):
            raise ContractError(f"{pet_id}: atlas has an invalid WebP chunk length")
        chunks.append(chunk)
    if b"VP8L" not in chunks or b"VP8 " in chunks or b"ANMF" in chunks:
        raise ContractError(f"{pet_id}: atlas must use a non-animated lossless VP8L payload")

    try:
        with Image.open(path) as source:
            source.load()
            if source.format != "WEBP":
                raise ContractError(f"{pet_id}: atlas format is {source.format}, not WEBP")
            if source.mode != "RGBA":
                raise ContractError(f"{pet_id}: atlas mode is {source.mode}, not RGBA")
            if source.size != ATLAS_SIZE:
                raise ContractError(f"{pet_id}: atlas size is {source.size}, not {ATLAS_SIZE}")
            atlas = source.copy()
    except OSError as exc:
        raise ContractError(f"{pet_id}: unreadable atlas: {path}: {exc}") from exc
    return PetReport(
        pet_id=pet_id,
        atlas_path=path,
        visible_pixels=validate_cells(atlas),
        file_sha256=sha256_file(path),
        rgba_sha256=rgba_digest(atlas),
    )


def validate_package(pet_id: str) -> PetReport:
    """Validate one directly copyable two-file pet directory."""

    package_dir = DIR_CATALOG / pet_id
    entries = sorted(package_dir.iterdir(), key=lambda path: path.name)
    if [path.name for path in entries] != ["pet.json", "spritesheet.webp"] or any(
        not path.is_file() or path.is_symlink() for path in entries
    ):
        raise ContractError(f"{pet_id}: runtime directory must contain two ordinary files")

    manifest = load_json(package_dir / "pet.json")
    missing = REQUIRED_MANIFEST_KEYS.difference(manifest)
    if missing:
        raise ContractError(f"{pet_id}: pet.json lacks {sorted(missing)}")
    if manifest["id"] != pet_id or not ID_PATTERN.fullmatch(str(manifest["id"])):
        raise ContractError(f"{pet_id}: manifest id and directory name diverge")
    if manifest["spriteVersionNumber"] != 2:
        raise ContractError(f"{pet_id}: spriteVersionNumber must be 2")
    if manifest["spritesheetPath"] != "spritesheet.webp":
        raise ContractError(f"{pet_id}: spritesheetPath must be spritesheet.webp")
    for key in ("displayName", "description"):
        if not isinstance(manifest[key], str) or not manifest[key].strip():
            raise ContractError(f"{pet_id}: {key} must be a non-empty string")
    return validate_atlas(package_dir / "spritesheet.webp", pet_id)


def validate_qa(pet_id: str) -> None:
    """Require every deterministic and visual release gate."""

    qa_dir = DIR_PRODUCTION / pet_id / "qa"
    gates = {
        "chroma-despill-extended.json": lambda value: value.get("ok") is True,
        "direction-blind-validation.json": lambda value: value.get("ok") is True,
        "direction-semantics.json": lambda value: value.get("ok") is True,
        "final-visual-qa.json": lambda value: value.get("visual_qa") == "pass",
        "look-continuity.json": lambda value: value.get("ok") is True,
        "review.json": lambda value: value.get("ok") is True,
    }
    for name, predicate in gates.items():
        path = qa_dir / name
        if not predicate(load_json(path)):
            raise ContractError(f"{pet_id}: QA gate failed: {name}")

    semantics = load_json(qa_dir / "direction-semantics.json").get("directions")
    if not isinstance(semantics, list) or len(semantics) != 16:
        raise ContractError(f"{pet_id}: direction review must contain 16 verdicts")
    evidence_fields = ("direction", "verdict", "expected", "observed", "reason")
    for expected_direction, item in zip(LOOK_DIRECTIONS, semantics, strict=True):
        if not isinstance(item, dict) or any(
            not isinstance(item.get(field), str) or not item[field].strip()
            for field in evidence_fields
        ):
            raise ContractError(f"{pet_id}: direction review lacks required evidence")
        if item["direction"] != expected_direction or item["verdict"] not in {"pass", "warning"}:
            raise ContractError(f"{pet_id}: direction review has an invalid verdict sequence")
    if len(list((qa_dir / "previews").glob("*.gif"))) != 9:
        raise ContractError(f"{pet_id}: nine state previews are required")


def validate_generation_graph(pet_id: str) -> None:
    """Check that each accepted visual job resolves inside its production run."""

    run_dir = DIR_PRODUCTION / pet_id
    graph = load_json(run_dir / "imagegen-jobs.json")
    jobs = graph.get("jobs")
    if graph.get("run_dir") != "." or not isinstance(jobs, list):
        raise ContractError(f"{pet_id}: imagegen job graph is not repository-relative")

    def require_run_file(value: object, label: str) -> Path:
        try:
            return resolve_relative_file(run_dir, value, f"{pet_id} {label}")
        except ValueError as exc:
            raise ContractError(str(exc)) from exc

    observed_jobs: list[str] = []
    for job in jobs:
        if not isinstance(job, dict) or job.get("status") != "complete":
            raise ContractError(f"{pet_id}: incomplete visual job")
        job_id = job.get("id")
        if not isinstance(job_id, str) or not job_id:
            raise ContractError(f"{pet_id}: visual job has no id")
        observed_jobs.append(job_id)
        for field in ("prompt_file", "output_path"):
            require_run_file(job.get(field), f"job {job_id} {field}")
        input_images = job.get("input_images")
        if not isinstance(input_images, list) or not input_images:
            raise ContractError(f"{pet_id}: job {job_id} has no input images")
        for image in input_images:
            if not isinstance(image, dict) or not isinstance(image.get("path"), str):
                raise ContractError(f"{pet_id}: malformed input for job {job_id}")
            require_run_file(image["path"], f"job {job_id} input")
        source_path = job.get("source_path")
        if source_path != job.get("output_path"):
            raise ContractError(f"{pet_id}: temporary generation path was not normalized")
    if tuple(observed_jobs) != EXPECTED_VISUAL_JOBS:
        raise ContractError(f"{pet_id}: visual job sequence diverges from the v2 contract")


def tracked_files(pet_id: str) -> list[Path]:
    """Return the exact file surface bound by one production manifest."""

    run_dir = DIR_PRODUCTION / pet_id
    manifest = (run_dir / PRODUCTION_MANIFEST).resolve()
    files = [
        path
        for path in run_dir.rglob("*")
        if path.is_file() and path.resolve() != manifest
    ]
    files.extend(
        (DIR_CATALOG / pet_id / name) for name in ("pet.json", "spritesheet.webp")
    )
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def write_production_manifest(pet_id: str) -> Path:
    """Bind the public production run and runtime payload by SHA-256."""

    entries = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in tracked_files(pet_id)
    ]
    destination = DIR_PRODUCTION / pet_id / PRODUCTION_MANIFEST
    payload = {
        "schema_version": 1,
        "pet_id": pet_id,
        "files": entries,
    }
    destination.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return destination


def verify_production_manifest(pet_id: str) -> None:
    """Reject missing, extra, or altered production files."""

    manifest_path = DIR_PRODUCTION / pet_id / PRODUCTION_MANIFEST
    entries = load_json(manifest_path).get("files")
    if not isinstance(entries, list):
        raise ContractError(f"{pet_id}: production manifest has no file ledger")
    expected = {path.relative_to(ROOT).as_posix() for path in tracked_files(pet_id)}
    observed: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise ContractError(f"{pet_id}: malformed production manifest entry")
        relative = entry["path"]
        path = (ROOT / relative).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError as exc:
            raise ContractError(f"{pet_id}: manifest path escapes repository: {relative}") from exc
        if not path.is_file():
            raise ContractError(f"{pet_id}: manifest file is missing: {relative}")
        if entry.get("size") != path.stat().st_size or entry.get("sha256") != sha256_file(path):
            raise ContractError(f"{pet_id}: manifest drift: {relative}")
        observed.add(relative)
    if observed != expected:
        raise ContractError(f"{pet_id}: production ledger and file surface diverge")


def audit_privacy() -> None:
    """Reject workstation paths and temporary account identifiers."""

    violations: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(
            part in {"build", ".git", "pet-build", "__pycache__"}
            for part in path.relative_to(ROOT).parts
        ):
            continue
        text = path.read_text(encoding="utf-8")
        if any(pattern.search(text) for pattern in PRIVATE_PATH_PATTERNS):
            violations.append(path.relative_to(ROOT).as_posix())
    if violations:
        raise ContractError(f"private path markers remain: {violations}")


def audit_pet(pet_id: str) -> PetReport:
    """Tie runtime bytes to production output, QA, and rebuilt pixels."""

    report = validate_package(pet_id)
    run_dir = DIR_PRODUCTION / pet_id
    final_report = validate_atlas(run_dir / "final" / "spritesheet-extended.webp", pet_id)
    if report.file_sha256 != final_report.file_sha256:
        raise ContractError(f"{pet_id}: runtime and production WebP bytes diverge")

    rebuilt = compose_atlas(pet_id)
    if rgba_digest(rebuilt) != report.rgba_sha256:
        raise ContractError(f"{pet_id}: frozen release cells do not rebuild runtime pixels")
    validation = load_json(run_dir / "final" / "validation-extended.json")
    if validation.get("ok") is not True:
        raise ContractError(f"{pet_id}: atlas validation ledger reports failure")
    validate_qa(pet_id)
    validate_generation_graph(pet_id)
    verify_production_manifest(pet_id)
    return report


def install_pet(pet_id: str, codex_home: Path) -> PetReport:
    """Stage and recoverably replace one local Codex pet."""

    report = audit_pet(pet_id)
    source = DIR_CATALOG / pet_id
    pets_root = codex_home.expanduser().resolve() / "pets"
    pets_root.mkdir(parents=True, exist_ok=True)
    destination = pets_root / pet_id
    backup = pets_root / f".{pet_id}.backup"

    if backup.exists() and not destination.exists():
        backup.replace(destination)
    elif backup.exists():
        shutil.rmtree(backup)

    with tempfile.TemporaryDirectory(prefix=f".{pet_id}-", dir=pets_root) as temporary:
        staging = Path(temporary) / pet_id
        shutil.copytree(source, staging)
        if destination.exists():
            destination.replace(backup)
        try:
            staging.replace(destination)
        except OSError:
            if backup.exists() and not destination.exists():
                backup.replace(destination)
            raise
        if backup.exists():
            shutil.rmtree(backup)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate runtime payloads")
    validate.add_argument("pet_id", choices=(*PET_IDS, "all"), default="all", nargs="?")

    subparsers.add_parser("manifest", help="refresh production SHA-256 ledgers")
    subparsers.add_parser("audit", help="run runtime, rebuild, QA, ledger, and privacy gates")

    install = subparsers.add_parser("install", help="install one pet into CODEX_HOME")
    install.add_argument("pet_id", choices=PET_IDS)
    install.add_argument(
        "--codex-home",
        type=Path,
        default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")),
    )

    args = parser.parse_args()
    try:
        if args.command == "manifest":
            for pet_id in PET_IDS:
                print(f"[ok] {write_production_manifest(pet_id)}")
            return
        if args.command == "install":
            report = install_pet(args.pet_id, args.codex_home)
            print(f"[ok] installed {report.pet_id}: {report.file_sha256}")
            return

        pet_ids = PET_IDS if getattr(args, "pet_id", "all") == "all" else (args.pet_id,)
        reports = []
        if args.command == "validate":
            reports = [validate_package(pet_id) for pet_id in pet_ids]
        else:
            reports = [audit_pet(pet_id) for pet_id in PET_IDS]
            audit_privacy()
        for report in reports:
            print(
                f"[ok] {report.pet_id}: {report.visible_pixels:,} visible pixels; "
                f"sha256={report.file_sha256}"
            )
    except (ContractError, OSError, ValueError) as exc:
        print(f"[error] {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
