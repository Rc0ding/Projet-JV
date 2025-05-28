import arcade

class Player(arcade.Sprite):
	"""The main player game object."""

	is_move_initiated: bool
	"""Whether the move was initiated (the key was pressed)
	on a frame where the player was present."""


	PLAYER_MOVEMENT_SPEED:float=10
	PLAYER_JUMP_BUFFER:float=10

	def __init__(self,texture:str, pos_x:float, pos_y:float) -> None:

		super().__init__(texture, scale=0.5)
		self.center_x=pos_x
		self.center_y=pos_y
		self.is_move_initiated = False
		#self.__buffered_jump_timer: float = 0
		
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

