import arcade
from typing import Tuple
import math
from src.entities.base_entity import Enemy
from src.game.player import Player
class Weapon(arcade.Sprite):
	"""
	Generic weapon base that handles pivot math automatically.

	Subclasses only need to supply:
	- pivot_raw: pixel (px) coordinate of the handle pivot in the source image
	- angle_offset: degrees to add so the sprite’s 0° points toward the cursor
	- hand_offset: world offset (px) from the player center to the pivot
	"""
	def __init__(
	self,
	camera: arcade.Camera2D,

	texture: str,
	pivot_raw: Tuple[float, float],
	angle_offset: float,
	hand_offset: Tuple[float, float] = (14.0, -10.0),
	scale: float = 0.350,
	) -> None:
		super().__init__(texture, scale=scale)
		self.camera = camera
		self.visible = False
		self._mouse_screen: Tuple[float, float] = (0, 0)

		# compute pivot-to-center vector (_chi) in world units
		w, h = self.texture.width, self.texture.height
		cx, cy = w / 2, h / 2
		chi_x = (cx - pivot_raw[0]) * scale
		chi_y = (cy - pivot_raw[1]) * scale
		self._chi = (chi_x, chi_y)

		self._hand_offset = hand_offset
		self._angle_offset = angle_offset

	def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
		self._mouse_screen = (x, y)
		if button == arcade.MOUSE_BUTTON_LEFT:
			self.visible = True

	def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
		self._mouse_screen = (x, y)
		if button == arcade.MOUSE_BUTTON_LEFT:
			self.visible = False

	def on_mouse_motion(self, x: float, y: float, dx: int, dy: int) -> None:
		self._mouse_screen = (x, y)

	def update_angle(
        self,
        camera: arcade.Camera2D,
        player: Player,
   	) -> None:
		"""Angle entre la main et le curseur, en degrés Arcade (0°=→, CCW)."""

		  # rétrocompatibilité
		win = arcade.get_window()
		cursor_x, cursor_y = self._mouse_screen
		world_x = cursor_x - win.width / 2 + camera.position[0]
		world_y = cursor_y - win.height / 2 + camera.position[1]

		hand_x = player.center_x + self._hand_offset[0]
		hand_y = player.center_y + self._hand_offset[1]

		dx, dy = world_x - hand_x, world_y - hand_y
		self.angle = math.degrees(math.atan2(dx, dy))

	def update_position(self, player: arcade.Sprite) -> None:
		"""
		Place le centre du sprite pour que la poignée reste sur la main.
		Inversion de rotation (horaire) pour correspondre à Arcade.
		"""
		θ = math.radians(self.angle)
		cos_θ, sin_θ = math.cos(θ), math.sin(θ)

		# ------- rotation inversée (sens horaire) ------------------------
		dx =  self._chi[0] * cos_θ + self._chi[1] * sin_θ
		dy = -self._chi[0] * sin_θ + self._chi[1] * cos_θ
		# -----------------------------------------------------------------

		self.center_x = player.center_x + self._hand_offset[0] + dx
		self.center_y = player.center_y + self._hand_offset[1] + dy
	def updating(self, player: Player) -> None:
		"""Update the weapon position and angle based on player and mouse."""
		if self.visible:
			self.update_angle( self.camera, player)
			self.update_position(player)
	


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
			texture="assets/kenney-voxel-items-png/sword_silver.png",
			pivot_raw=(32, 10),       # handle pixel in the image
			angle_offset=-41.2,       # adjust so 0° → right
			hand_offset=(14, -10),     # hand offset from player center
			scale=0.9,
		)
		self._Sprite: arcade.Sprite= arcade.Sprite(path_or_texture=self.texture, scale=self.scale)

	def environment(self, monster_list:arcade.SpriteList[Enemy]) -> None:
		self._monster_list=monster_list
	
	def killing(self) -> list[arcade.Sprite]:
		if self.visible:
			return arcade.check_for_collision_with_list(
				self._Sprite,
				self._monster_list,
			)
		return []
	"""
	def sword_update(self, dt:float)-> list[arcade.Sprite]:
		self.updating(dt)
		return self.killing()"""
	