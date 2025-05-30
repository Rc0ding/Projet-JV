from src.texture_manager import PLAYER_TEXTURE
from src.game.objects import Object

class Player(Object):
	"""The main player game object."""

	is_move_initiated: bool
	"""Whether the move was initiated (the key was pressed)
	on a frame where the player was present."""


	PLAYER_MOVEMENT_SPEED:float=30
	PLAYER_JUMP_BUFFER:float=10
	PLAYER_JUMP_SPEED:float=15

	def __init__(self, scale:float=0.5, pos_x:float=0, pos_y:float=0) -> None:

		super().__init__(
			texture=PLAYER_TEXTURE,
			scale=scale,
			pos=(pos_x,pos_y),
			health=100)


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
		
		distance= distance * 0.7
		if distance< 0.01:
			distance=0

		print(f"Knockback applied: change_x={self.change_x}, change_y={self.change_y}")

