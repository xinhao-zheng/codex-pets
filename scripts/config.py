# -*- coding: utf-8 -*-
"""Define the repository paths and Codex v2 atlas contract.

The module derives constants only; it creates no files. See README.md.
"""

from __future__ import annotations

from pathlib import Path

# Repository root. Every public path derives from this anchor.
ROOT = Path(__file__).resolve().parent.parent
# Runtime packages are flat root members, matching direct-copy catalog semantics.
DIR_CATALOG = ROOT
DIR_PRODUCTION = ROOT / "production"
DIR_BUILD = ROOT / "build"

PET_IDS = (
    "cyber-otter-2077",
    "cyber-otter-2077-pixel-edition",
)

ATLAS_SIZE = (1536, 2288)
CELL_SIZE = (192, 208)
ATLAS_COLUMNS = 8
ATLAS_ROWS = 11

# Row 0 carries six idle frames and one neutral cell. Later rows carry only
# their declared state frames; every remaining slot must stay transparent.
ROW_CONTRACT = (
    ("idle", 7),
    ("running-right", 8),
    ("running-left", 8),
    ("waving", 4),
    ("jumping", 5),
    ("failed", 8),
    ("waiting", 6),
    ("running", 6),
    ("review", 6),
    ("look-row-9", 8),
    ("look-row-10", 8),
)

LOOK_DIRECTIONS = (
    "000",
    "022.5",
    "045",
    "067.5",
    "090",
    "112.5",
    "135",
    "157.5",
    "180",
    "202.5",
    "225",
    "247.5",
    "270",
    "292.5",
    "315",
    "337.5",
)
