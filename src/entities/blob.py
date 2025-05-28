"""entities.py – Edge‑safe enemies for the platformer.

**Blob – v4 (robust edge detection)**
-------------------------------------
The blob now predicts its *next bounding box* before moving:
* It virtually shifts its rectangle ``speed`` pixels forward, then checks
  whether **every horizontal quarter‑point under that box** is still
  above ground. If *any* sample lacks ground → it reverses.
* It also predicts a wall collision the same way.

This approach is robust for any integer speed ≤ `TILE/4` and prevents the
sprite from hanging over lava or void by more than a couple of pixels.
"""
from __future__ import annotations

from typing import List,Tuple
from src.entities import base_entity
import arcade


# ---------------------------------------------------------------------------
# 2. Blob – grass‑platform walker (no patrol limits)
# ---------------------------------------------------------------------------

class Blob(base_entity.Enemy):
    TEXTURE: str = ":resources:images/enemies/slimeBlue.png"

    def __init__(self, pos_px: Tuple[float, float], speed: int = 1) -> None:
        super().__init__(pos_px, speed)
        self._walls: arcade.SpriteList[arcade.Sprite] | None

    # ------------------------------------------------------------------
    # Prediction helpers
    # ------------------------------------------------------------------
    def _ground_samples(self, next_center_x: float) -> List[bool]:
        """Return a list of booleans: ground under ¼‑width steps of next box."""
        assert self._walls is not None
        samples: List[bool] = []
        quarter = self.width / 4
        for offset in (-self.width / 2 + quarter, 0, self.width / 2 - quarter, self.width / 2):
            x = next_center_x + offset * self._direction / abs(self._direction)
            y = self.bottom - 1
            samples.append(bool(arcade.get_sprites_at_point((x, y), self._walls)))
        return samples

    def _collision_ahead(self) -> bool:
        assert self._walls is not None
        self.center_x += self._direction * self._speed
        collisions: list[arcade.Sprite] = arcade.check_for_collision_with_list(self, self._walls)
        self.center_x -= self._direction * self._speed
        return bool(collisions)

    # ------------------------------------------------------------------
    # AI core
    # ------------------------------------------------------------------
    def step(self, delta: float) -> None:  # noqa: ARG002 – *delta* unused
        next_center_x = self.center_x + self._direction * self._speed

        # Check future collision & ground coverage
        collision_next = self._collision_ahead()
        ground_ok = all(self._ground_samples(next_center_x))

        if collision_next or not ground_ok:
            self.reversy()
            return

        # Safe → move
        self.center_x = next_center_x
