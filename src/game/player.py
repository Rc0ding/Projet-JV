from src.texture_manager import PLAYER_TEXTURE
from src.game.objects import Object

class Player(Object):
	"""The main player game object."""

	is_move_initiated: bool
	"""Whether the move was initiated (the key was pressed)
	on a frame where the player was present."""


	PLAYER_MOVEMENT_SPEED:float=10
	PLAYER_JUMP_BUFFER:float=10

	def __init__(self, scale:float=0.5, pos_x:float=0, pos_y:float=0) -> None:

		super().__init__(
			texture=PLAYER_TEXTURE,
			scale=scale,
			pos=(pos_x,pos_y),
			health=100           # stays inside GameObject, never reaches Sprite
		)

		#self.__buffered_jump_timer: float = 0
	
	def knockback(self, distance:float,delta_time:float,direction:bool) -> None:
		"""Apply knockback to the object."""
		if direction:
			self.center_x += distance * delta_time
		else:
			self.center_x -= distance * delta_time
		self.change_x=0
		self.change_y=0
		self.center_y += distance * delta_time
		
		distance= distance * 0.9
		if distance< 0.01:
			distance=0

		print(f"Knockback applied: change_x={self.change_x}, change_y={self.change_y}")
	

	"""
	def on_key_press(self, symbol: int, modifiers: int) -> None:
		match symbol:
			case arcade.key.RIGHT:
				self.change_x += self.PLAYER_MOVEMENT_SPEED
				self.is_move_initiated = True
			case arcade.key.LEFT:
				self.change_x -= self.PLAYER_MOVEMENT_SPEED
				self.is_move_initiated = True
			case arcade.key.UP:
				self.__buffered_jump_timer = self.PLAYER_JUMP_BUFFER
			case _:
				pass
	

	def on_key_release(self, symbol: int, modifiers: int) -> None:
		match symbol:
			case arcade.key.RIGHT:
				if (
				self.is_move_initiated
				):  # See in __init__ for explanation (yes, there is one)
					self.change_x -= self.PLAYER_MOVEMENT_SPEED
			case arcade.key.LEFT:
				if self.is_move_initiated:
					self.change_x += self.PLAYER_MOVEMENT_SPEED

	
	
	
	def update(self, delta_time: float = 1 / 60) -> None:

		if (ong and self.__buffered_jump_timer > 0):  # A jump was buffered and we're considered on ground
			
			self.change_y = self.PLAYER_JUMP_SPEED

			self.__buffered_jump_timer = 0
		elif self.__buffered_jump_timer > 0:
			self.__buffered_jump_timer -= delta_time
		"""

