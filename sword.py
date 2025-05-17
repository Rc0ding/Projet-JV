# sword.py
from __future__ import annotations
import math
import arcade
from typing import Tuple


class Sword:
    """
    Petite classe « plug-and-play » qui gère l'épée :
      • chargement du sprite,
      • suivi de la position du joueur,
      • (dé)masquage via clic souris,
      • dessin conditionnel.

    On peut facilement dériver ou étendre la classe plus tard si besoin.
    """

    def __init__(
        self,
        texture: str = "assets/kenney-voxel-items-png/sword_silver.png",
        scale: float = 0.5 * 0.7,
        offset: Tuple[float, float] = (0.0, 0.0),
    ) -> None:
        # Sprite de l'épée
        self.sprite: arcade.Sprite = arcade.Sprite(texture, scale)
        # Décalage éventuel par rapport au centre du joueur (main droite, etc.)
        self._offset: Tuple[float, float] = offset
        # Visibilité courante
        self.visible: bool = False

        # On place l'épée hors-écran par sécurité
        self.sprite.center_x = self.sprite.center_y = -1_000.0

    # --------------------------------------------------------------------- #
    # API publique – appelée depuis GameView
    # --------------------------------------------------------------------- #
    def update_position(self, player: arcade.Sprite) -> None:
        """Fait suivre l'épée au joueur, même si elle est cachée."""
        self.sprite.center_x = player.center_x + self._offset[0]
        self.sprite.center_y = player.center_y + self._offset[1]

    # Les deux méthodes suivantes se branchent directement
    # sur on_mouse_press / on_mouse_release de GameView
    def on_mouse_press(
        self, x: int, y: int, button: int, modifiers: int
    ) -> None:  # noqa: D401 — style Arcade
        """Montre l'épée tant que le bouton est enfoncé."""
        self.visible = True

    def on_mouse_release(
        self, x: int, y: int, button: int, modifiers: int
    ) -> None:
        """Cache l'épée au relâchement du bouton."""
        self.visible = False
    
    def update_angle(
        self,
        cursor_x: int,
        cursor_y: int,
        camera: arcade.Camera2D,
        player: arcade.Sprite,
    ) -> None:
        """
        Oriente l’épée pour qu’elle pointe vers le curseur.

        On convertit la position souris (fenêtre) → monde
        puis on calcule l’angle entre joueur et curseur.
        """
        window = arcade.get_window()
        
        # Conversion écran → monde (caméra 2D)
        world_x = cursor_x - window.width / 2 + camera.position[0]
        world_y = cursor_y - window.height / 2 + camera.position[1]

        dx = world_x - player.center_x
        dy = world_y - player.center_y
        # 0° = droite, 90° = haut
        self.sprite.angle = math.degrees(math.atan2(dx, dy)-(math.pi*(47.7/180)))

    def draw(self) -> None:
        """Dessine l'épée uniquement si `visible` est vrai."""
        if self.visible:
            arcade.draw_sprite(self.sprite)