from __future__ import annotations

"""gate_switch.py – self‑contained Gate / Switch sprites that **do not** depend on
any GameObject base class.

Usage recap (minimal):

    gate = Gate((wx, wy), state="closed", scale=SCALE)
    switch = Switch((sx, sy), meta_switch, gate_list, scale=SCALE)

    # add to sprite lists
    wall_list.append(gate)          # only if gate starts closed / solid
    interactive_list.append(switch) # e.g. for collision checks

During the game loop, call

    switch.update()

or simply let Arcade’s SpriteList do it.  When the player attacks / collides
with the switch, call `switch.trigger()` – it will toggle its state and execute
all actions defined in *meta_switch* (see the Map YAML format below).

---------------------------------------------------------------------
Map‑header YAML fields that these classes expect (all **optional**) –

```yaml
switches:
  - x: 12        # grid column
    y: 5         # grid row
    state: on    # or "off" (default)
    switch_on:   # executed when the lever is pushed *into* the ON position
      - action: open_gate
        x: 30
        y: 5
  - x: 18
    y: 3
    state: off
    switch_off:  # executed when the lever returns to OFF
      - action: close_gate
        x: 30
        y: 5

gates:
  - x: 30
    y: 5
    state: closed   # or "open"
```

Coordinate system: the same (col, row) used for the ASCII grid, *top left = (0,0)*.
---------------------------------------------------------------------
The code purposefully avoids any tight coupling to the rest of your codebase –
it requires only `arcade` and a reference to the gate list so it can find the
right Gate to operate on.
"""
import arcade
from typing import List,Tuple, Union, Any, Dict
from src.texture_manager import *


# ──────────────────────────────────────────────────────────────────────
#  Gate sprite – a block that can disappear / re‑appear
# ──────────────────────────────────────────────────────────────────────

class Gate(arcade.Sprite):
    """Solid tile that can open (become intangible and invisible).

    When *open* is True the sprite is hidden; callers are responsible for
    removing / re‑adding it to the *walls* SpriteList used by the physics
    engine so it stops colliding with the player.
    """

    def __init__(
        self,
        position: Tuple[float, float],
        *,
        state: str = "closed",     # "open" or "closed"
        scale: float = 0.5,
        texture: str = GATE_TEXTURE,  # default texture name
    ) -> None:
        super().__init__(texture, scale=scale, center_x=position[0], center_y=position[1])
        self.is_open: bool = state == "open"
        self.visible = not self.is_open

    # ------------------------------------------------------------------
    # public helpers ----------------------------------------------------
    # ------------------------------------------------------------------

    def set_state(self, closed: bool) -> None:
        """Set gate closed (solid/visible) or open (hidden)."""
        self.is_open = not closed
        self.visible = closed  # visible == solid in a 2D platformer

    def toggle(self) -> None:
        """Convenience shortcut."""
        self.set_state(self.is_open)  # invert

    # The physics‑engine sprite list must be managed *outside* – we cannot
    # know which list the caller is using.  Recommended pattern:
    #
    #     if gate.is_open:
    #         walls.remove(gate)
    #     else:
    #         walls.append(gate)
    #

# ──────────────────────────────────────────────────────────────────────
#  Switch sprite – animated lever that executes actions
# ──────────────────────────────────────────────────────────────────────


SpriteListOrList = Union[List["Gate"], arcade.SpriteList[Gate]]  # helper alias


class Switch(arcade.Sprite):
    """
    Lever / switch sprite driven only by the raw YAML‐dict *switch_meta*.

    * ``switch_meta`` is the dictionary taken directly from the map header:
      ``{ "x": 3, "y": 8, "state": "on", "switch_on": [...], ... }``.
    * ``gate_list`` is the sprite list containing every Gate that may be
      targeted by this switch.
    """

    TEXTURE_OFF = LEVER_OFF_TEXTURE
    TEXTURE_ON  = LEVER_ON_TEXTURE

    # ------------------------------------------------------------------
    #  Construction
    # ------------------------------------------------------------------
    def __init__(
        self,
        position: Tuple[float, float],
        switch_meta: Dict[str, Any]={},
        gate_list: SpriteListOrList=arcade.SpriteList(),
        *,
        scale: float = 0.5,
    ) -> None:

        # --- base sprite ------------------------------------------------
        super().__init__(filename=self.TEXTURE_OFF,
                         scale=scale,
                         center_x=position[0],
                         center_y=position[1])
        self.append_texture(arcade.load_texture(self.TEXTURE_OFF))
        self.append_texture(arcade.load_texture(self.TEXTURE_ON))  # index 1

        # --- runtime state ----------------------------------------------
        self._meta: Dict[str, Any]   = switch_meta        # keep the dict
        self._gate_list              = gate_list
        self.meta_x: int = switch_meta.get("x", 0)
        self.meta_y: int = switch_meta.get("y", 0)
        self.is_on: bool = switch_meta.get("state", "off") == "on"
        self.set_texture(1 if self.is_on else 0)

    # ------------------------------------------------------------------
    #  Public interface
    # ------------------------------------------------------------------
    def trigger(self) -> None:
        """Flip the switch and execute its actions (unless disabled)."""

        # 1) toggle logical + visual state
        self.is_on = not self.is_on
        self.set_texture(1 if self.is_on else 0)

        # 2) execute appropriate action list
        for gate in self._gate_list:
            print("gate:", gate, "is_open:", gate.is_open,"at", gate.center_x, gate.center_y)
            gate.toggle()

    def debug_switch(self, position: Tuple[float, float], state: bool, gates: arcade.SpriteList[Gate]) -> None:
        """Debugging helper to visualize switch state."""
        self.center_x, self.center_y = position
        self.is_on = state
        self.set_texture(1 if self.is_on else 0)
        self._gate_list = gates
