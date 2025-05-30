from __future__ import annotations
"""Bow weapon – now uses exactly the **same aim maths** as *Sword* and is
visible when active.

Key fixes
~~~~~~~~~
* Added the bow itself to the caller’s *weaponss* list – otherwise it was
  never drawn.
* The projectile initial velocity is taken from the **hand→cursor** vector, the
  same one *Weapon.update_angle* relies on, so arrows always leave the bow
  tangentially.
* `arcade.Vec2` is immutable: we build a **new** vector for gravity each frame.
* Arrow sprite is oriented directly from the bow’s angle at the moment of
  release – no more drifting offsets.
"""

from typing import Tuple, Any
import math
import arcade

from src.game.objects import Object
from src.game.player import Player
from src.weapons.weapon import Weapon
from src.texture_manager import BOW_TEXTURE, ARROW_TEXTURE

# ---------------------------------------------------------------------------
#  Tunables
# ---------------------------------------------------------------------------
ARROW_SPEED    = 900.0   # px / s
ARROW_GRAVITY  = 900 # px / s², downward
ARROW_LIFETIME = 6.0     # seconds before auto‑destroy
ARROW_COOLDOWN = 0.1    # seconds between shots
ARROW_SCALE    = 0.30


class Bow(Weapon):
    """A wooden bow spurting gravity-affected arrows.

    **Bug-fix**: the bow’s transform is now kept up-to-date even when the
    sprite is invisible, so newly fired arrows always start from the correct
    hand position.  (The previous version only refreshed the transform while
    ``visible`` was *True*, so if you moved between shots the arrow would be
    spawned at the *old* coordinates.)
    """

    # ------------------------------------------------------------------
    #  Nested Arrow sprite
    # ------------------------------------------------------------------
    class Arrow(Object):
        def __init__(self, start: Tuple[float, float], direction: arcade.Vec2, angle: float) -> None:
            super().__init__(texture=ARROW_TEXTURE, scale=ARROW_SCALE, pos=start, health=1)
            self._vel: arcade.Vec2 = direction.normalize() * ARROW_SPEED
            self.angle = angle
            self._life = ARROW_LIFETIME
            self._aim_vec: arcade.Vec2 = arcade.Vec2(1, 0)

        def step(self, dt: float,camera:arcade.Camera2D) -> None:
            self.center_x += self._vel.x * dt
            self.center_y += self._vel.y * dt
            self._vel = arcade.Vec2(self._vel.x, self._vel.y - ARROW_GRAVITY * dt)

            self._life -= dt
            vx, vy= self._vel
            self.death()

            self.angle = -math.degrees(math.atan2(vy,vx)) +42.8

            # Check collisions with walls
            
        
        def death(self):
            if self.center_y<-100:
                self.remove_from_sprite_lists()
            



    # ------------------------------------------------------------------
    #  Bow logic
    # ------------------------------------------------------------------
    def __init__(self, player: Player, camera: arcade.Camera2D) -> None:
        super().__init__(camera=camera,
                         texture=BOW_TEXTURE,
                         pivot_raw=(64, 64),
                         angle_offset=-42.8,
                         hand_offset=(20, -14),
                         scale=0.35)
        self._player = player
      
        self._cooldown = 0.0
        self.arrows: arcade.SpriteList[Bow.Arrow] = arcade.SpriteList(use_spatial_hash=True)

    # .................................................................
    #  Mouse events
    # .................................................................
    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
        super().on_mouse_press(x, y, button, modifiers)
        if button == arcade.MOUSE_BUTTON_LEFT and self._cooldown <= 0:
            # Ensure the bow transform matches the *current* player position
            self.update_angle(camera=self.camera, player=self._player)
            self.update_position(player=self._player, camera=self.camera)
            self._shoot_arrow()
            self._cooldown = ARROW_COOLDOWN

    # .................................................................
    #  Public per-frame update
    # .................................................................
    def updating(self, player: Player, camera: arcade.Camera2D, dt: float = 1 / 60) -> None:  # noqa: D401
        # Keep transform updated even when invisible so future shots start from
        # the right place.
        self.update_angle(camera=camera, player=player)
        self.update_position(player=player, camera=camera)
        self.camera=camera
        if self._cooldown > 0:
            self._cooldown = max(0.0, self._cooldown - dt)
        

        for arrow in list(self.arrows):
            arrow.step(dt,camera=camera)

    # .................................................................
    #  Helpers
    # .................................................................
    def _shoot_arrow(self) -> None:
        """Spawn one projectile from the bow’s centre toward the cursor."""
        # Direction vector – hand → cursor (already calculated by update_angle)
        cursor_wx, cursor_wy, _ = self.camera.unproject(self._mouse_screen)
        dir_vec = arcade.Vec2(cursor_wx - self.center_x, cursor_wy - self.center_y)


        if dir_vec.length() == 0:
            dir_vec = arcade.Vec2(1, 0)

        start_pos = (self.center_x, self.center_y)
        arrow = Bow.Arrow(start_pos, dir_vec, self.angle)
        self.arrows.append(arrow)

