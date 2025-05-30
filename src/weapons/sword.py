import arcade
from src.entities.base_entity import Enemy
from src.game.player import Player
from src.texture_manager import SWORD_TEXTURE
from src.weapons.weapon import Weapon
class Sword(Weapon):
	"""Sword held by the player, with fixed pivot and offsets."""

	_monster_list: arcade.SpriteList[Enemy]

	def __init__(
	self,
	player: Player,
	camera: arcade.Camera2D,
	) -> None:
		super().__init__(
			camera,
			texture=SWORD_TEXTURE,
			pivot_raw=(35, 32),       # handle pixel in the image
			angle_offset= 42.8,       # adjust so 0° → right
			hand_offset=(20, -14),     # hand offset from player center
			scale=0.5,
		)
		self.DAMAGE: int = 25           # points removed on hit
		self.COOLDOWN: float = 0.5    # seconds between two hits
		self._cooldown_timer: float = 0

	def ready(self) -> bool:
		return self._cooldown_timer <= 0 and self.visible

	def update_cooldown(self, dt: float) -> None:
		self._cooldown_timer = max(0, self._cooldown_timer - dt)

	def reset_cooldown(self) -> None:
		self._cooldown_timer = self.COOLDOWN
		
		

	