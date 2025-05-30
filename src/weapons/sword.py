import arcade
from typing import Tuple
import math
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
			scale=0.35,
		)
		

	def environment(self, monster_list:arcade.SpriteList[Enemy]) -> None:
		self._monster_list=monster_list
	"""
	def killing(self) -> list[arcade.Sprite]:
		if self.visible:
			return arcade.check_for_collision_with_list(
				self._monster_list,
			)
		return []"""
	"""
	def sword_update(self, dt:float)-> list[arcade.Sprite]:
		self.updating(dt)
		return self.killing()"""
	