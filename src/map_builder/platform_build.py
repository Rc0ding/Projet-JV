"""
platform_build.py  – standalone, mypy-strict friendly.
Build MovingPlatform sprites for one level without external helpers.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Generator, Any

from src.map_builder.platforms import Platform
from src.helper import grid_to_world, grid_row


# ──────────────────────────────────────────────────────────────
# ASCII glyph sets (leave as is)
# ──────────────────────────────────────────────────────────────
ELIGIBLE = {"=", "-", "x", "£", "E", "^"}   # block glyphs
ARROWS_H = {"←", "→"}
ARROWS_V = {"↑", "↓"}

# ──────────────────────────────────────────────────────────────
# Tiny in-file helpers – replace former src.helper.*
# ──────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────
# Public entry – build platforms
# ──────────────────────────────────────────────────────────────
def build_platforms(
    rows: List[str],
    meta: dict[str, Any],
    tile_textures: Dict[str, str],
) -> List[Platform]:
    """
    Return a list of MovingPlatform sprites built from an ASCII map.
    `meta` MUST contain at least: tile, scale.
    
    The function:
      - Processes the ASCII rows of the level.
      - Identifies eligible blocks.
      - Collects horizontal and vertical arrow series.
      - Matches arrow series with blocks to determine platform direction and boundaries.
      - Creates Platform instances based on discovered data.
    """
    # Create a working copy of rows.
    meta_with_rows = rows
    # Extract the width value from meta.
    width = meta["width"]
    #print("Building platforms from rows:", meta_with_rows)
    #print("Unique chars in rows:", sorted({c for line in rows for c in line}))

    # Label connected blocks of eligible characters.
    blocks = _label_blocks(meta_with_rows, width)
    #print(f"Blocks found: {blocks}")
    # Extract arrow series for horizontal and vertical directions.
    series_h, series_v = _collect_arrow_series(meta_with_rows, width)
    #print(f"Horizontal arrow series: {series_h}")
    #print(f"Vertical arrow series: {series_v}")
    # Initialize list to hold created platforms.
    sprites: List[Platform] = []
    wx: float
    wy: float
    """
    # Debug loop to print eligible characters.
    for y, line in enumerate(rows):
        for x, ch in enumerate(line):
            if ch in ELIGIBLE:
                print("ELIGIBLE char", ch, "at", (x, y))
    """
    # Total number of rows for coordinate calculations.
    length = len(rows)
    # Process each block (group of connected cells)
    for cells in blocks.values():
        # Determine the minimal and maximal column and row indices in the block.
        #col_min = min(c for c, _ in cells)
        #col_max = max(c for c, _ in cells)


        # Try to find a horizontal arrow series adjacent to the block.
        chosen: tuple[int, Tuple[int, int], int] | None = fuse_series_for_block(cells, series_h, axis="x")
        axis = "x"
        # If no horizontal series was found, try vertical.
        if chosen is None:
            chosen = fuse_vertical_series_for_block(cells, series_v)
            axis = "y"
        # If still no series is found, skip this block.
        if chosen is None:
            continue

        # Unpack the arrow series details.
        _, (ser_min, ser_max), direction = chosen

        if axis == "x":
            # Calculate grid offsets for horizontal series.
            g_left, g_right = ser_min, ser_max 
            block_cols = [col for col, _ in cells]
            block_min = min(block_cols)
            block_max = max(block_cols)

            for col, row in cells:
                # Calculate per-tile bounds
                a = g_left+( col - block_min)
                b = g_right -( block_max - col)
                b_left, b_right = grid_row(a, b)
                #print(f"Processing cell ({col}, {row}) with bounds ({b_left}, {b_right}), a={a}, b={b}")
                wx, wy = grid_to_world(col, length - row - 1)
                sprites.append(
                    Platform(
                        texture=tile_textures[rows[row][col]],
                        start_pos=(wx, wy),
                        axis="x",
                        direction=direction == 1,
                        boundary_a=b_left,
                        boundary_b=b_right,
                    )
                )
        else:
    # Calculate grid offsets for vertical series.
            g_top, g_bottom = ser_min, ser_max
            block_rows = [row for _, row in cells]
            block_min = min(block_rows)
            block_max = max(block_rows)

            for col, row in cells:
                # Calculate per-tile bounds
                a = g_top + (row - block_min)
                b = g_bottom - (block_max - row)
                b_top, b_bottom = grid_row(a, b)
                wx, wy = grid_to_world(col, length - row - 1)
                print("Unknown map char:", repr(rows[row][col]))
                sprites.append(
                    Platform(
                        texture=tile_textures[rows[row][col]],
                        start_pos=(wx, wy),
                        axis="y",
                        direction=direction == 1,
                        boundary_a=b_top,
                        boundary_b=b_bottom,
                    )
                )    
    # Return the list of created platform sprites.
    return sprites


# ──────────────────────────────────────────────────────────────
# Internals (unchanged logic, strict-typed)
# ──────────────────────────────────────────────────────────────
GridPos = Tuple[int, int]
SeriesH = Dict[Tuple[int, Tuple[int, int]], int]
SeriesV = Dict[Tuple[int, Tuple[int, int]], int]


def _label_blocks(rows: List[str], width: int) -> Dict[int, List[GridPos]]:
    h, w = len(rows), width
    seen: list[list[bool]] = [[False] * w for _ in range(h)]
    blocks: Dict[int, list[GridPos]] = {}
    current = 0
    def neigh(c: int, r: int) -> Generator[GridPos, None, None]:
        if c > 0:      yield c - 1, r
        if c < w - 1:  yield c + 1, r
        if r > 0:      yield c, r - 1
        if r < h - 1:  yield c, r + 1

    for r in range(h):
        #print(f"Row {r} of {h}: {rows[r]}")
        for c in range(w):
            #print(f"  Col {c} of {w}: {rows[r][c]}")
            if seen[r][c] or rows[r][c] not in ELIGIBLE:
                continue
            #print(f"  Found new block at ({c}, {r})")
            queue: list[GridPos] = [(c, r)]
            blocks[current] = []
            seen[r][c] = True
            while queue:
                cc, rr = queue.pop()
                blocks[current].append((cc, rr))
                for nc, nr in neigh(cc, rr):
                    if not seen[nr][nc] and rows[nr][nc] in ELIGIBLE:
                        seen[nr][nc] = True
                        queue.append((nc, nr))   # MARCHE PAS SI PREMEIRE LIGNE PAS VIDE ??
            current += 1
    return blocks



def _collect_arrow_series(rows: List[str], width:int) -> Tuple[SeriesH, SeriesV]:
    h, w = len(rows), width
    #print(f"Collecting arrow series in {h} rows and {w} cols")
    series_h: SeriesH = {}
    series_v: SeriesV = {}


    for r in range(h):
        c = 0
        while c < w and c < len(rows[r]):
            #print(f"Checking char at ({c}, {len(rows[r])})")
            ch = rows[r][c]
            if ch in ARROWS_H:
                start = c
                direction = 1 if ch == "→" else -1
                #print("test",c+1, len(rows[r]))
                while c + 1 < w and c + 1 < len(rows[r]) and rows[r][c + 1] == ch:
                    c += 1
                series_h[(r, (start, c))] = direction
            c += 1

    for c in range(w):
        r = 0
        while r < h and c < len(rows[r]):
            #print(f"Checking char at ({c}, {len(rows[r])})")
            ch = rows[r][c]
            if ch in ARROWS_V:
                start = r
                direction = 1 if ch == "↑" else -1
                #print("test",c, len(rows[r+1]))
                while r + 1 < h and c < len(rows[r+1]) and rows[r + 1][c] == ch:
                    r += 1
                #print(f"Col {c}, Row {r}: {ch}")
                series_v[(c, (start, r))] = direction
            r += 1
 
    return series_h, series_v


def find_series_for_block(
    cells: List[GridPos],
    series_dict: SeriesH | SeriesV,
    axis: str,
) -> tuple[int, Tuple[int, int], int] | None:
    if axis == "x":
        for (row, (start, end)), direction in series_dict.items():
            entry_col = start - 1 if direction == 1 else end + 1
            if sum(1 for c, r in cells if r == row and c == entry_col) == 1:
                return row, (start, end), direction
    else:
        for (col, (start, end)), direction in series_dict.items():
            entry_row = start - 1 if direction == 1 else end + 1
            if sum(1 for c, r in cells if c == col and r == entry_row) == 1:
                return col, (start, end), direction
    return None

def fuse_series_for_block(
    cells: List[GridPos],
    series_dict: SeriesH,
    axis: str,
) -> tuple[int, Tuple[int, int], int] | None:
    """Fuse all contiguous arrow series adjacent to the block into one."""
    if axis != "x":
        return None  # Only horizontal for now

    row_indices = set(r for _, r in cells)

    for row in row_indices:
        # Find all series on this row adjacent to the block
        series: List[Tuple[int, int, int]] = []
        for (ser_row, (start, end)), direction in series_dict.items():
            if ser_row != row:
                continue
            entry_col = start - 1 if direction == 1 else end + 1
            if any(r == row and c == entry_col for c, r in cells):
                series.append((start, end, direction))
        if not series:
            continue
        # Fuse all contiguous series
        min_start = min(s for s, _, _ in series)
        max_end = max(e for _, e, _ in series)
        # Use direction of the first series (could be improved)
        directiond: int = series[0][2]
        return row, (min_start, max_end), directiond
    return None

def fuse_vertical_series_for_block(
    cells: list[tuple[int, int]],
    series_dict: SeriesV,
) -> tuple[int, tuple[int, int], int] | None:
    # Only vertical axis
    col_indices = set(c for c, _ in cells)
    for col in col_indices:
        # Find all series on this col adjacent to the block
        series: list[tuple[int, int, int]] = []
        for (ser_col, (start, end)), direction in series_dict.items():
            if ser_col != col:
                continue
            entry_row = start - 1 if direction == 1 else end + 1
            if any(c == col and r == entry_row for c, r in cells):
                series.append((start, end, direction))
        if not series:
            continue
        min_start = min(s for s, _, _ in series)
        max_end = max(e for _, e, _ in series)
        direction = series[0][2]
        return col, (min_start, max_end), direction
    return None