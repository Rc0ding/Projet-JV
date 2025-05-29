
from src.constants_proj import TILESIZE
from typing import Tuple

def grid_to_world(col:float, row:float, tile:float=TILESIZE)-> Tuple[float, float]:
		x = col * tile + tile / 2
		y = row * tile + tile / 2
		return x, y
def grid_row(left:float, right:float, tile:float=TILESIZE) -> Tuple[float, float]:
		"""Convert grid coordinates to world coordinates for a row."""
		return left * tile + tile / 2, right * tile + tile / 2

def grid_col(bottom:float, top:float, tile:float=TILESIZE) -> Tuple[float, float]:
		"""Convert grid coordinates to world coordinates for a column."""
		return bottom * tile + tile / 2, top * tile + tile / 2

