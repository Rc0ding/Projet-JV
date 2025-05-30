import arcade
from typing import Tuple
import math
from src.entities.base_entity import Enemy
from src.game.player import Player
from src.texture_manager import SWORD_TEXTURE
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
		self.pivot_raw = pivot_raw

		# compute pivot-to-center vector (_chi) in world units
		tex_w, tex_h = self.texture.width, self.texture.height
		chi_x = (tex_w / 2 - self.pivot_raw[0]) * scale
		chi_y = (tex_h / 2 - self.pivot_raw[1]) * scale
		self._chi = (chi_x, chi_y)

		self._hand_offset = hand_offset
		self._angle_offset = angle_offset
		self.center_x = 200
		self.center_y = 200

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

		# ──────────────────────────────────────────────────────────────────────
	# 1)  Aim: compute the sprite angle from hand → cursor
	# ──────────────────────────────────────────────────────────────────────
	def update_angle(
		self,
		camera: arcade.Camera2D,
		player: Player,
	) -> None:
		"""Angle entre la main et le curseur, en degrés Arcade (0°=→, CCW)."""

		cursor_x, cursor_y,_ = camera.unproject(self._mouse_screen)
		cursor_x_proj= self._mouse_screen[0]
		#print(f"Cursor position: {cursor_x}, {cursor_y}")
		if cursor_x_proj > 640:
			hand_x = player.center_x + self._hand_offset[0]
		else:
			hand_x = player.center_x - self._hand_offset[0]
		hand_y = player.center_y + self._hand_offset[1]
		#print(f"Hand position: {hand_x}, {hand_y}")

		dx, dy = cursor_x - self.center_x, cursor_y - self.center_y
		print("cursor_x:", cursor_x, "cursor_y:", cursor_y)
		print("center_x:", self.center_x, "center_y:", self.center_y)
		print(f"dx: {dx}, dy: {dy}, angle: {math.degrees(math.atan2(dy,dx))}")
		self.angle = -math.degrees(math.atan2(dy,dx)) +42.8

	""" 	def update_position(self, camera:arcade.Camera2D, player: arcade.Sprite) -> None:
	
		Place le centre du sprite pour que la poignée reste sur la main.
		Inversion de rotation (horaire) pour correspondre à Arcade.

		cursor_x, _,_ = camera.unproject(self._mouse_screen)
		θ = math.radians(self.angle)
		# ------- rotation inversée (sens horaire) ------------------------
		d=math.sin(θ)*self.hyp
		print(f"Distance from pivot to cursor: {d}")
		dx = d * math.cos(θ)
		dy = d * math.sin(θ)
		# -----------------------------------------------------------------
		self.center_y = player.center_y + self._hand_offset[1]
		if 640 < cursor_x:
			print(f"LEFT, player: {player.center_x}, cursor: {cursor_x}")
			self.center_x = player.center_x + self._hand_offset[0]
			return
		print(f"RIGHT, player: {player.center_x}, cursor: {cursor_x}")
		self.center_x = player.center_x - self._hand_offset[0] """

	def update_position(self, player: Player, camera: arcade.Camera2D) -> None:
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
		cursor_x,_ = self._mouse_screen
		self.center_y = player.center_y + self._hand_offset[1]+ dy
		if 640 < cursor_x:
			print(f"LEFT, player: {player.center_x}, cursor: {cursor_x}")
			self.center_x = player.center_x + self._hand_offset[0]+dx
			return
		print(f"RIGHT, player: {player.center_x}, cursor: {cursor_x}")
		self.center_x = player.center_x - self._hand_offset[0]+dx
	"""
	def update_transform(self, player: Player, camera: arcade.Camera2D) -> None:
		
		hand_x, hand_y  – world coords of the pivot (player's hand)
		dir_vec         – unit vector pointing from hand to cursor
		

		# rotation
		mouse = camera.unproject(self._mouse_screen)
		dir = arcade.Vec2(
			mouse.x - player.center_x, mouse.y - player.center_y
		).normalize()

		if dir.x < 0:
			start_pos = (
				self.center_x+22,
				self.center_y - 24,
			)
		else:
			start_pos = (
				self.center_x - 22,
				self.center_y - 24,
			)

			self.position = (
				start_pos[0] + dir[0] * self.size[0] * 0.35,
				start_pos[1] + dir[1] * self.size[1] * 0.35,
			)
		self.center_x =self.position[0]
		self.center_y = self.position[1]
	"""

	# ──────────────────────────────────────────────────────────────────────
	# 3)  Frame-level update helper
	# ──────────────────────────────────────────────────────────────────────
	def updating(self, player: Player,camera:arcade.Camera2D) -> None:
		"""Call once per frame from your GameView.on_update()."""
		if self.visible:
			self.update_angle(camera=camera, player=player)
			#self.update_transform(camera=camera, player=player)

	


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
			pivot_raw=(32, 10),       # handle pixel in the image
			angle_offset=10,       # adjust so 0° → right
			hand_offset=(22, -24),     # hand offset from player center
			scale=0.35,
		)
		

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
	