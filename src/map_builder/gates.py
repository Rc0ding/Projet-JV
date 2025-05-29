# src/entities/gate.py
from __future__ import annotations
import arcade
from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:   # avoid cycle at runtime
    from src.map_builder.switch import Switch

class Gate(arcade.Sprite):
    """A single-tile door that can be open (no collision) or closed (solid)."""

    CLOSED_TEX = ":resources:images/tiles/bridgeB.png"
    OPEN_TEX   = ":resources:images/tiles/bridgeA.png"

    def __init__(self, center: Tuple[float, float], scale: float = 0.5) -> None:
        super().__init__(self.CLOSED_TEX, scale=scale, center_x=center[0], center_y=center[1])
        self.closed: bool = True
        self._linked_switches: List["Switch"] = []

    # called by Switch to register itself
    def add_switch(self, sw: "Switch") -> None:
        self._linked_switches.append(sw)

    # ------------------------------------------------ public API
    def toggle(self) -> None:
        self.set_state(not self.closed)

    def set_state(self, closed: bool) -> None:
        if self.closed == closed:
            return
        self.closed = closed
        self.texture = arcade.load_texture(self.CLOSED_TEX if closed else self.OPEN_TEX)

    # ------------------------------------------------ helpers for LevelBuilder
    @property
    def is_solid(self) -> bool:
        return self.closed
