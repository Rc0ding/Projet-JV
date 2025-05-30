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

from typing import List,Tuple
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
        scale: float = 1.0,
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

class Switch(arcade.Sprite):
    """A lever the player can hit to trigger actions.

    The constructor receives the raw *switch_meta* extracted from the YAML
    header (dictionary) and the list of *gate sprites* already created by the
    level‑builder so it can find and operate the target gates.
    """

    TEXTURE_OFF = LEVEL_OFF_TEXTURE  # relative to this file
    TEXTURE_ON = LEVEL_ON_TEXTURE  # prettier than file constant

    def __init__(
        self,
        position: Tuple[float, float],
        switch_meta: Map.Metadata.SwitchPosition,
        gate_list: List[Gate] | arcade.SpriteList[Gate],
        *,
        scale: float = 1.0,
    ) -> None:
        # ––– base sprite ------------------------------------------------
        super().__init__(self.TEXTURE_OFF, scale=scale, center_x=position[0], center_y=position[1])
        self.append_texture(arcade.load_texture(self.TEXTURE_ON))  # index 1

        # ––– runtime state --------------------------------------------
        self._gate_list = gate_list
        self.is_on: bool = switch_meta.state == switch_meta.State.on
        self.set_texture(1 if self.is_on else 0)
        self._disabled: bool = getattr(switch_meta, "disabled", False)

        self._actions_on:  list[Map.Metadata.SwitchPosition.Action] = (
            switch_meta.switch_on or []
        )
        self._actions_off: list[Map.Metadata.SwitchPosition.Action] = (
            switch_meta.switch_off or []
        )

        # ––– actions ----------------------------------------------------
        self.lever_on  = switch_meta.switch_on  or []   # list[Action]
        self.lever_off = switch_meta.switch_off or []   # list[Action]


    # ------------------------------------------------------------------
    #  Public interface -------------------------------------------------
    # ------------------------------------------------------------------
       # ──────────────────────────────────────────────────────────────
    # public: called by the game when the player activates the lever
    # ──────────────────────────────────────────────────────────────
    def trigger(self) -> None:
        """Flip the lever and run its actions (if not disabled)."""

        if self._disabled:
            return

        # 1) Toggle logical + visual state
        self.is_on = not self.is_on
        self.set_texture(1 if self.is_on else 0)

        # 2) Pick the correct action list and execute each entry
        actions = self._actions_on if self.is_on else self._actions_off
        for act in actions:
            self._execute_action(act)

    # ------------------------------------------------------------------
    #  Internal helpers -------------------------------------------------
    # ------------------------------------------------------------------

    def _execute_action(self, act: Map.Metadata.SwitchPosition.Action) -> None:
        """Run a single Action object on this switch."""
        kind = act.action   # <— enum value of type Kind

        if kind in (
            Map.Metadata.SwitchPosition.Action.Kind.open_gate,
            Map.Metadata.SwitchPosition.Action.Kind.close_gate,
        ):
            gate = self._find_gate(act)
            if gate is None:
                raise RuntimeError(f"Gate not found for action {act!r}")

            gate.set_state(kind == Map.Metadata.SwitchPosition.Action.Kind.close_gate)

        elif kind == Map.Metadata.SwitchPosition.Action.Kind.disable:
            self._disabled = True

        else:
            raise ValueError(f"Unknown switch action: {kind}")

    def _find_gate(
        self, act: Map.Metadata.SwitchPosition.Action
    ) -> Gate | None:
        """Locate a gate by the *grid* coordinates stored in the Action."""
        gx, gy = act.x, act.y
        for gate in self._gate_list:
            if (
                getattr(gate, "meta_x", None) == gx
                and getattr(gate, "meta_y", None) == gy
            ):
                return gate
        return None
