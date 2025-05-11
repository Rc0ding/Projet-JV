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

import math
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

import arcade

# ---------------------------------------------------------------------------
# Typing helpers
# ---------------------------------------------------------------------------
Sprite = arcade.Sprite
SpriteList = arcade.SpriteList[Sprite]

# ---------------------------------------------------------------------------
# Global constants
# ---------------------------------------------------------------------------
TILE: int = 64   # logical tile width in‑game (px) after scaling
SCALE: float = 0.5   # 128‑px art → 64‑px on screen

# ---------------------------------------------------------------------------
# 1. Base autonomous enemy class
# ---------------------------------------------------------------------------

class Enemy(arcade.Sprite, ABC):
    TEXTURE: str = ""

    def __init__(self, pos_px: Tuple[float, float], speed: int) -> None:
        super().__init__(self.TEXTURE, SCALE)
        self.center_x, self.center_y = pos_px

        self._speed = speed
        self._direction = 1  # +1 → right, −1 → left
        self._base_y = self.center_y  # for flyers

        # Will be set each frame by *update()*
        self._walls: Optional[SpriteList] = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def reversy(self) -> None:
        self._direction *= -1
        self.scale_x *= -1

    # ------------------------------------------------------------------
    # Life‑cycle (called manually from GameView.on_update)
    # ------------------------------------------------------------------
    @abstractmethod
    def step(self, delta: float) -> None:  # pragma: no cover
        ...

    def post_step(self) -> None:  # empty hook
        ...

    def update(self, delta: float, walls: SpriteList) -> None:  # type: ignore[override]
        self._walls = walls
        self.step(delta)
        self.post_step()

# ---------------------------------------------------------------------------
# 2. Blob – grass‑platform walker (no patrol limits)
# ---------------------------------------------------------------------------

class Blob(Enemy):
    TEXTURE: str = ":resources:images/enemies/slimeBlue.png"

    def __init__(self, pos_px: Tuple[float, float], speed: int = 1) -> None:
        super().__init__(pos_px, speed)

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
        # Predict collision by offsetting bounding box horizontally only
        self.center_x += self._direction * self._speed
        hit = bool(arcade.check_for_collision_with_list(self, self._walls))
        self.center_x -= self._direction * self._speed
        return hit

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

# ---------------------------------------------------------------------------
# 3. Bat – flyer drifting in a sine‑wave
# ---------------------------------------------------------------------------

class Bat(Enemy):
    TEXTURE: str = "ressources/bat.png"

    def __init__(self,
                 pos_px: Tuple[float, float],
                 amplitude_px: int = 48,
                 period_s: float = 2.0,
                 speed: int = 2) -> None:
        super().__init__(pos_px, speed)
        self._ampl = amplitude_px
        self._period = period_s
        self._time = 0.0

    def step(self, delta: float) -> None:
        # Horizontal drift
        self.center_x += self._direction * self._speed

        # Vertical sine‑wave oscillation
        self._time += delta
        self.center_y = self._base_y + self._ampl * math.sin(
            2.0 * math.pi * self._time / self._period
        )

    def post_step(self) -> None:
        # Reverse when leaving nominal level bounds (hard‑coded 0–4000 px)
        if self.left < 0 or self.right > 1200:
            self.reversy()
