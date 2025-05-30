from __future__ import annotations

"""MapLoader – reads a level text file consisting of a YAML header followed by
an ASCII grid, separated by a line containing only "---".

It returns a `Map.Metadata` instance – **exactly the nested class the engine
already defines** – plus the rectangular list of grid rows.
"""
from pathlib import Path
from typing import Any, Dict

import yaml

# ────────────────────────────────────────────────────────────
#  Canonical Map / Metadata model supplied by the user
# ────────────────────────────────────────────────────────────



# ────────────────────────────────────────────────────────────
#  Loader
# ────────────────────────────────────────────────────────────

class MapLoader:
    """Read <header YAML> --- <ASCII grid> and return (`Meta`, rows)."""

    def __init__(self, filename: str | Path):
        self.path = Path(filename)

    # public --------------------------------------------------
    def load(self) -> tuple[Dict[str, Any], list[str]]:
        if not self.path.exists():
            raise FileNotFoundError(self.path)

        header_str, ascii_block = self.path.read_text(encoding="utf-8").split("---", 1)

        meta = self._parse_header(header_str)

        rows: list[str] = [
            line.rstrip("\n").ljust(meta["width"], " ")
            for line in ascii_block.splitlines()
        ]
        if rows and rows[-1].isspace():
            rows.pop()

        if len(rows) < meta["height"] or any(len(row) > meta["width"] for row in rows):
            print(f"YAML: {meta['height']} rows, grid: {len(rows)} rows, width: {meta['width']}")
            raise ValueError("YAML height and grid height differ")

        return meta, rows

    # private -------------------------------------------------
    def _parse_header(self, header: str) -> Dict[str, Any]:
        """Return the YAML header as an ordinary dict."""
        return yaml.safe_load(header) or {}
