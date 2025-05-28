from __future__ import annotations
from src.entities import base_entity
import math
from typing import Tuple
import random

class Bat(base_entity.Enemy):
    TEXTURE: str = "ressources/bat.png"

    def __init__(
        self,
        pos_px: Tuple[float, float],
        radius_px: int = 150,
        speed: int = 2,
    ) -> None:
        super().__init__(pos_px, speed)
        self._spawn_x, self._spawn_y = pos_px
        self._radius = radius_px

        # First random target inside the circle
        self._pick_new_target()

    # ──────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────
    def _pick_new_target(self) -> None:
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, self._radius)
        self._target_x = self._spawn_x + r * math.cos(angle)
        self._target_y = self._spawn_y + r * math.sin(angle)

        # Determine facing
        old_dir = self._direction
        self._direction = 1 if self._target_x >= self.center_x else -1
        if self._direction != old_dir:
            self.reversy()

    # ──────────────────────────────────────────────────────────────────
    # AI core
    # ──────────────────────────────────────────────────────────────────
    def step(self, delta: float) -> None:
        # Vector towards target
        dx = self._target_x - self.center_x
        dy = self._target_y - self.center_y
        dist = math.hypot(dx, dy)

        # Close enough → choose a new random point
        if dist < self._speed:
            self._pick_new_target()
            return

        # Normalise & move
        vx = self._speed * dx / dist
        vy = self._speed * dy / dist
        self.center_x += vx
        self.center_y += vy
