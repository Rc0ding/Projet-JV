from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Any
import arcade
from src.game.objects import Object

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

class Enemy(Object, ABC):
    TEXTURE: str = ""

    def __init__(self,  pos_px: Tuple[float, float], speed: int, scale: float = 0.5) -> None:
        super().__init__(texture=self.TEXTURE, scale=scale, health=50)
        self.center_x, self.center_y = pos_px

        self._speed = speed
        self._direction = 1  # +1 → right, −1 → left
        self._base_y = self.center_y  # for flyers

        # Will be set each frame by *update()*
        self._walls: Optional[arcade.SpriteList[arcade.Sprite]] = None


    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def reversy(self) -> None:
        self._direction *= -1
        self.scale_x *= -1
    
    def set_environment(self, walls: arcade.SpriteList[arcade.Sprite]) -> None:
                self._walls = walls    

    # ------------------------------------------------------------------
    # Life‑cycle (called manually from GameView.on_update)
    # ------------------------------------------------------------------
    @abstractmethod
    def step(self, delta: float) -> None:  # pragma: no cover
        ...

    def post_step(self) -> None:  # empty hook
        ...

    def update(self, delta_time: float=1/60, *args:Any,**kwargs:Any) -> None:
        assert self._walls is not None, "Walls must be set before update"
        self.step(delta_time)
