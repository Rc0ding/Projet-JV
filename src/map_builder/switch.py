# src/entities/switch.py
from __future__ import annotations
import arcade
from typing import List, Tuple
from src.map_builder.gates import Gate

class Switch(arcade.Sprite):
    OFF_TEX = ":resources:images/tiles/bridgeA_vertical.png"
    ON_TEX  = ":resources:images/tiles/bridgeB_vertical.png"

    def __init__(self, center: Tuple[float, float], scale: float = 0.5) -> None:
        super().__init__(self.OFF_TEX, scale=scale, center_x=center[0], center_y=center[1])
        self._on: bool = False
        self.targets: List[Gate] = []

    # ---------------------------------------------------------------- public API
    def add_target(self, gate: Gate, open_when_on: bool) -> None:
        """Link a gate to this switch; `open_when_on=True` means
        switch ON ➜ gate OPEN, OFF ➜ gate CLOSED.
        """
        self.targets.append(gate)
        # store mapping rule on gate side if you like; optional
        gate.add_switch(self)

    def trigger(self) -> None:
        """Flip state and drive targets."""
        self._on = not self._on
        self.texture = arcade.load_texture(self.ON_TEX if self._on else self.OFF_TEX)
        for g in self.targets:
            # simple rule: ON => open, OFF => close
            g.set_state(closed=not self._on)
