import arcade
from typing import Tuple
import math
from src.entities.base_entity import Enemy

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
	player: arcade.Sprite,
	camera: arcade.Camera2D,

	texture: str,
	pivot_raw: Tuple[float, float],
	angle_offset: float,
	hand_offset: Tuple[float, float] = (0.0, 0.0),
	scale: float = 1.0,
	) -> None:
		super().__init__(texture, scale=scale)
		self.player = player
		self.camera = camera
		self.visible = False
		self._mouse_screen: Tuple[int, int] = (0, 0)

		# compute pivot-to-center vector (_chi) in world units
		w, h = self.texture.width, self.texture.height
		cx, cy = w / 2, h / 2
		chi_x = (cx - pivot_raw[0]) * scale
		chi_y = (cy - pivot_raw[1]) * scale
		self._chi = (chi_x, chi_y)

		self._hand_offset = hand_offset
		self._angle_offset = angle_offset

	def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
		self._mouse_screen = (x, y)
		if button == arcade.MOUSE_BUTTON_LEFT:
			self.visible = True

	def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
		self._mouse_screen = (x, y)
		if button == arcade.MOUSE_BUTTON_LEFT:
			self.visible = False

	def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
		self._mouse_screen = (x, y)

	def updating(self, dt:float) -> None:
		"""
		Called each frame: rotates and repositions the sprite so that its pivot
		remains on the player’s hand and the blade points at the mouse.
		"""
		if not self.visible:
			return
		# convert screen mouse to world
		mx, my, _ = self.camera.unproject(self._mouse_screen)
		# compute hand world pos
		hx = self.player.center_x + self._hand_offset[0]
		hy = self.player.center_y + self._hand_offset[1]
		# compute aiming angle
		dx, dy = mx - hx, my - hy
		angle = math.degrees(math.atan2(dy, dx)) + self._angle_offset
		self.angle = angle
		# rotate chi vector to find sprite center
		rad = math.radians(angle)
		cos_t, sin_t = math.cos(rad), math.sin(rad)
		dx_chi = self._chi[0] * cos_t - self._chi[1] * sin_t
		dy_chi = self._chi[0] * sin_t + self._chi[1] * cos_t
		# place center so pivot sits at hand
		self.center_x = hx + dx_chi
		self.center_y = hy + dy_chi


class Sword(Weapon):
	"""Sword held by the player, with fixed pivot and offsets."""

	_monster_list: arcade.SpriteList[arcade.Sprite]

	def __init__(
	self,
	player: arcade.Sprite,
	camera: arcade.Camera2D,
	) -> None:
		super().__init__(
			player,
			camera,
			texture="assets/kenney-voxel-items-png/sword_silver.png",
			pivot_raw=(32, 10),       # handle pixel in the image
			angle_offset=-41.2,       # adjust so 0° → right
			hand_offset=(14, -10),     # hand offset from player center
			scale=0.35,
		)
		self._Sprite: arcade.Sprite= arcade.Sprite(path_or_texture=self.texture, scale=self.scale)

	def environment(self, monster_list:arcade.SpriteList[Enemy]) -> None:
		self._monster_list=monster_list
	
	def killing(self)->list[arcade.Sprite]:
		slain:list[arcade.Sprite]
		if self._visible and slain is not None:
			slain = arcade.check_for_collision_with_list(
				self._Sprite,
				self._monster_list,
			)
		return slain

	def sword_update(self, dt:float)-> list[arcade.Sprite]:
		self.updating(dt)
		return self.killing()
		
