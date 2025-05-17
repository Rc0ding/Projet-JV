# sword.py
from __future__ import annotations
import math
from typing import Tuple
import arcade


class Sword:
    """Sprite d’épée (tout calculé à la main, sans anchor_x / y Arcade)."""

    # Réglez ces deux constantes si besoin
    _PIVOT_RAW: Tuple[int, int] = (32, 10)   # poignée dans le PNG
    _ANGLE_OFFSET: float = -41.2             # sprite Kenney pointe ↑

    def __init__(
        self,
        texture: str = "assets/kenney-voxel-items-png/sword_silver.png",
        scale: float = 0.35,
        offset: Tuple[float, float] = (14, -10),   # main par rapport au centre joueur
    ) -> None:
        self.sprite = arcade.Sprite(texture, scale=scale)

        # Vecteur pivot → centre (χ) en monde
        tex_w, tex_h = self.sprite.texture.width, self.sprite.texture.height
        chi_x = (tex_w / 2 - self._PIVOT_RAW[0]) * scale
        chi_y = (tex_h / 2 - self._PIVOT_RAW[1]) * scale
        self._chi = (chi_x, chi_y)

        self._hand_offset = offset
        self.visible = False
        self.sprite.center_x = self.sprite.center_y = -1_000.0  # hors champ

    # ---------------------------------------------------------------- API
    def on_mouse_press(self, *_):  # type: ignore[override]
        self.visible = True

    def on_mouse_release(self, *_):  # type: ignore[override]
        self.visible = False

    def update_angle(
        self,
        cursor_x: int,
        cursor_y: int,
        camera: arcade.Camera2D,
        player: arcade.Sprite,
    ) -> None:
        """Angle entre la main et le curseur, en degrés Arcade (0°=→, CCW)."""
        if hasattr(camera, "screen_to_world"):
            world_x, world_y = camera.screen_to_world(cursor_x, cursor_y)
        else:  # rétrocompatibilité
            win = arcade.get_window()
            world_x = cursor_x - win.width / 2 + camera.position[0]
            world_y = cursor_y - win.height / 2 + camera.position[1]

        hand_x = player.center_x + self._hand_offset[0]
        hand_y = player.center_y + self._hand_offset[1]

        dx, dy = world_x - hand_x, world_y - hand_y
        self.sprite.angle = math.degrees(math.atan2(dx, dy)) + self._ANGLE_OFFSET

    def update_position(self, player: arcade.Sprite) -> None:
        """
        Place le centre du sprite pour que la poignée reste sur la main.
        Inversion de rotation (horaire) pour correspondre à Arcade.
        """
        θ = math.radians(self.sprite.angle)
        cos_θ, sin_θ = math.cos(θ), math.sin(θ)

        # ------- rotation inversée (sens horaire) ------------------------
        dx =  self._chi[0] * cos_θ + self._chi[1] * sin_θ
        dy = -self._chi[0] * sin_θ + self._chi[1] * cos_θ
        # -----------------------------------------------------------------

        self.sprite.center_x = player.center_x + self._hand_offset[0] + dx
        self.sprite.center_y = player.center_y + self._hand_offset[1] + dy

    # --------------------------------------------------- Debug optionnel
    def debug_draw_pivot(self) -> None:
        θ = math.radians(self.sprite.angle)
        cos_θ, sin_θ = math.cos(θ), math.sin(θ)
        dx =  self._chi[0] * cos_θ + self._chi[1] * sin_θ
        dy = -self._chi[0] * sin_θ + self._chi[1] * cos_θ
        px = self.sprite.center_x - dx
        py = self.sprite.center_y - dy
        arcade.draw_line(px, py, self.sprite.center_x, self.sprite.center_y,
                         arcade.color.RED, 2)

    # --------------------------------------------------- Draw
    def draw(self) -> None:
        if self.visible:
            arcade.draw_sprite(self.sprite)
