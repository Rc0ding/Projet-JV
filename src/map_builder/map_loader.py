from pathlib import Path
from typing import List

Meta = dict[str,int]



class MapLoader:

	def __init__(self, filename: str):
		self.path = Path(filename)


	def load(self) -> tuple[Meta, List[str]]:
		"""Return (meta, rows) where rows is top-to-bottom."""
		if not self.path.exists():
			raise FileNotFoundError(self.path)

		with self.path.open(encoding="utf-8") as f:
			header, ascii_block = f.read().split("---", 1)

		meta: Meta = self._parse_header(header.splitlines())
		rows: List[str] = [line.rstrip("\n") for line in ascii_block.splitlines()]
		
		rows.pop()

		if len(rows) != meta["height"] or max(len(row) for row in rows) > meta["width"]:
			raise ValueError("YAML height and grid height differ")
		print(f"MapLoader: {self.path} loaded with {meta['width']}x{meta['height']} grid")
		return meta, rows


	def _parse_header(self,lines: List[str]) -> Meta:
		meta: Meta = {"width": 0, "height": 1}
		for line in lines:

			if ":" not in line: # verify that line contains a key-value pair
				continue
			
			key, value = (part.strip() for part in line.split(":", 1))
			match key:                       # pattern matching is on syllabus
				case "width"  | "height":
					print(f"Parsing {key}={value}")
					meta[key] += int(value)
				case _:
					pass
		
		return meta
