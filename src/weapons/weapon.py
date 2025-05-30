import arcade
from typing import Tuple
import math
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
		self.pivot_raw = pivot_raw
		self.DAMAGE: int = 25           # points removed on hit
		self.COOLDOWN: float = 0.5    # seconds between two hits
		self._cooldown_timer: float = 0

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
			print("wesh")
		if button == arcade.MOUSE_BUTTON_RIGHT:
			print("wesh")
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

		dx, dy = cursor_x - hand_x, cursor_y - hand_y
		self.angle = -math.degrees(math.atan2(dy,dx)) +self._angle_offset


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

	
	def ready(self) -> bool:
		return self._cooldown_timer <= 0 and self.visible

	def update_cooldown(self, dt: float) -> None:
		self._cooldown_timer = max(0, self._cooldown_timer - dt)

	def reset_cooldown(self) -> None:
		self._cooldown_timer = self.COOLDOWN
	# ──────────────────────────────────────────────────────────────────────
	# 3)  Frame-level update helper
	# ──────────────────────────────────────────────────────────────────────
	def updating(self, player: Player,camera:arcade.Camera2D) -> None:
		"""Call once per frame from your GameView.on_update()."""
		if self.visible:
			self.update_angle(camera=camera, player=player)
			self.update_position(camera=camera,player=player)

	

