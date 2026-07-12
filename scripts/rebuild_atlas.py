# -*- coding: utf-8 -*-
"""Extract and rebuild the release atlas from final RGBA cells.

Image generation is not deterministic. This stage is: the accepted atlas is
split into fixed cells once, each cell is hashed, and assembly only places those
cells back under the Codex v2 grid contract. See README.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath

from PIL import Image

from config import (
    ATLAS_COLUMNS,
    ATLAS_ROWS,
    ATLAS_SIZE,
    CELL_SIZE,
    DIR_BUILD,
    DIR_PRODUCTION,
    PET_IDS,
    ROW_CONTRACT,
)


def sha256_bytes(data: bytes) -> str:
    """Return an uppercase SHA-256 digest."""

    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one file."""

    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def rgba_digest(image: Image.Image) -> str:
    """Hash decoded RGBA pixels rather than encoder-specific bytes."""

    rgba = image.convert("RGBA")
    return sha256_bytes(rgba.tobytes())


def resolve_relative_file(root: Path, value: object, label: str) -> Path:
    """Resolve one canonical POSIX path to an ordinary file below root."""

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty relative path")
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if (
        value != posix.as_posix()
        or posix.is_absolute()
        or windows.is_absolute()
        or windows.drive
        or ".." in posix.parts
        or ".." in windows.parts
    ):
        raise ValueError(f"{label} is not a canonical repository-relative path: {value}")

    root = root.resolve()
    candidate = root.joinpath(*posix.parts)
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError(f"{label} escapes its root or is missing: {value}") from exc
    if candidate.is_symlink() or not resolved.is_file():
        raise ValueError(f"{label} is not an ordinary file: {value}")
    return resolved


def extract_cells(pet_id: str) -> Path:
    """Freeze the accepted atlas into hashed release cells."""

    run_dir = DIR_PRODUCTION / pet_id
    atlas_path = run_dir / "final" / "spritesheet-extended.webp"
    cells_root = run_dir / "assembly" / "cells"
    manifest_path = run_dir / "assembly" / "release-cells.json"

    with Image.open(atlas_path) as source:
        source.load()
        atlas = source.convert("RGBA")
    if atlas.size != ATLAS_SIZE:
        raise ValueError(f"{pet_id}: expected atlas {ATLAS_SIZE}, got {atlas.size}")

    width, height = CELL_SIZE
    entries: list[dict[str, object]] = []
    for row, (state, used_columns) in enumerate(ROW_CONTRACT):
        row_dir = cells_root / f"row-{row:02d}-{state}"
        row_dir.mkdir(parents=True, exist_ok=True)
        for column in range(used_columns):
            box = (
                column * width,
                row * height,
                (column + 1) * width,
                (row + 1) * height,
            )
            cell = atlas.crop(box)
            cell_path = row_dir / f"{column:02d}.png"
            cell.save(cell_path, format="PNG", optimize=False, compress_level=9)
            entries.append(
                {
                    "row": row,
                    "column": column,
                    "state": state,
                    "path": cell_path.relative_to(run_dir).as_posix(),
                    "rgba_sha256": rgba_digest(cell),
                    "file_sha256": sha256_file(cell_path),
                }
            )

    manifest = {
        "schema_version": 1,
        "pet_id": pet_id,
        "source": "final/spritesheet-extended.webp",
        "atlas": {
            "width": ATLAS_SIZE[0],
            "height": ATLAS_SIZE[1],
            "columns": ATLAS_COLUMNS,
            "rows": ATLAS_ROWS,
            "cell_width": CELL_SIZE[0],
            "cell_height": CELL_SIZE[1],
        },
        "source_file_sha256": sha256_file(atlas_path),
        "source_rgba_sha256": rgba_digest(atlas),
        "cells": entries,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def compose_atlas(pet_id: str) -> Image.Image:
    """Return an atlas assembled from the frozen release cells."""

    run_dir = DIR_PRODUCTION / pet_id
    manifest_path = run_dir / "assembly" / "release-cells.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    atlas_contract = {
        "width": ATLAS_SIZE[0],
        "height": ATLAS_SIZE[1],
        "columns": ATLAS_COLUMNS,
        "rows": ATLAS_ROWS,
        "cell_width": CELL_SIZE[0],
        "cell_height": CELL_SIZE[1],
    }
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema_version") != 1
        or manifest.get("pet_id") != pet_id
        or manifest.get("atlas") != atlas_contract
    ):
        raise ValueError(f"{pet_id}: assembly manifest contract is invalid")
    entries = manifest.get("cells")
    if not isinstance(entries, list):
        raise ValueError(f"{pet_id}: assembly manifest has no cell list")

    atlas = Image.new("RGBA", ATLAS_SIZE, (0, 0, 0, 0))
    width, height = CELL_SIZE
    seen: set[tuple[int, int]] = set()
    seen_paths: set[Path] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError(f"{pet_id}: malformed assembly cell")
        row = entry.get("row")
        column = entry.get("column")
        if not isinstance(row, int) or isinstance(row, bool):
            raise ValueError(f"{pet_id}: assembly cell has an invalid row")
        if not isinstance(column, int) or isinstance(column, bool):
            raise ValueError(f"{pet_id}: assembly cell has an invalid column")
        if row < 0 or row >= len(ROW_CONTRACT):
            raise ValueError(f"{pet_id}: assembly row is outside the v2 contract: {row}")
        expected_state, used_columns = ROW_CONTRACT[row]
        if entry.get("state") != expected_state or not 0 <= column < used_columns:
            raise ValueError(f"{pet_id}: assembly cell contradicts its row contract")
        key = (row, column)
        if key in seen:
            raise ValueError(f"{pet_id}: duplicate assembly cell {key}")
        seen.add(key)

        cell_path = resolve_relative_file(run_dir, entry.get("path"), f"{pet_id} cell {key}")
        if cell_path in seen_paths:
            raise ValueError(f"{pet_id}: assembly file is reused: {entry.get('path')}")
        seen_paths.add(cell_path)
        if sha256_file(cell_path) != entry.get("file_sha256"):
            raise ValueError(f"{pet_id}: cell file changed: {entry['path']}")
        with Image.open(cell_path) as source:
            source.load()
            if source.format != "PNG" or source.mode != "RGBA":
                raise ValueError(f"{pet_id}: release cell must be an RGBA PNG: {entry['path']}")
            cell = source.convert("RGBA")
        if cell.size != CELL_SIZE:
            raise ValueError(f"{pet_id}: cell {entry['path']} has size {cell.size}")
        if rgba_digest(cell) != entry.get("rgba_sha256"):
            raise ValueError(f"{pet_id}: decoded cell changed: {entry['path']}")
        atlas.alpha_composite(cell, (column * width, row * height))

    expected = {
        (row, column)
        for row, (_, used_columns) in enumerate(ROW_CONTRACT)
        for column in range(used_columns)
    }
    if seen != expected:
        raise ValueError(f"{pet_id}: release cell set does not match the row contract")
    expected_digest = manifest.get("source_rgba_sha256")
    if not isinstance(expected_digest, str) or rgba_digest(atlas) != expected_digest:
        raise ValueError(f"{pet_id}: rebuilt pixels differ from the accepted atlas")
    return atlas


def write_build(pet_id: str, output_root: Path) -> Path:
    """Write one rebuilt lossless WebP and return its path."""

    atlas = compose_atlas(pet_id)
    output_dir = output_root / pet_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "spritesheet.webp"
    atlas.save(output, format="WEBP", lossless=True, quality=100, method=6, exact=True)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract = subparsers.add_parser("extract", help="freeze release cells from final atlases")
    extract.add_argument("pet_id", choices=(*PET_IDS, "all"), default="all", nargs="?")

    build = subparsers.add_parser("build", help="rebuild release atlases from frozen cells")
    build.add_argument("pet_id", choices=(*PET_IDS, "all"), default="all", nargs="?")
    build.add_argument("--output-dir", type=Path, default=DIR_BUILD)

    args = parser.parse_args()
    pet_ids = PET_IDS if args.pet_id == "all" else (args.pet_id,)
    if args.command == "extract":
        for pet_id in pet_ids:
            print(f"[ok] {extract_cells(pet_id)}")
        return
    for pet_id in pet_ids:
        print(f"[ok] {write_build(pet_id, args.output_dir)}")


if __name__ == "__main__":
    main()
