import arcade
from typing import Tuple
from src.constants_proj import SCALE_FACTOR

class Object(arcade.Sprite):
	def __init__(
	self,
	texture: str,
	scale: float = 1.0,
	pos: Tuple[float, float] = (0, 0),   # (x, y) in world units
	health: int = 1) -> None:

		super().__init__(texture, scale=scale, center_x=pos[0], center_y=pos[1]
		)
		self.__max_health = health  # Private maximum health
		self.__current_health = health  # Private current health
		self.health_bar = Object.HealthBar(self)
		self.healthes: arcade.SpriteList[arcade.Sprite] = self.health_bar.sprite_list
		self.__invincible: bool = False  # Private invincibility flag
		self.__invincible_timer: float = 0.0  # Timer for invincibility duration


	# HealthBar class encapsulating the health bar functionality
	class HealthBar:
		def __init__(self, owner: "Object") -> None:
			self.owner = owner
			self.sprite = arcade.Sprite("assets/heathbar.png", scale=0.5)
			self.sprite_list :arcade.SpriteList[arcade. Sprite]=arcade.SpriteList(use_spatial_hash=True)
			self.sprite_list.append(self.sprite)
			self.fill_height = 20 * SCALE_FACTOR  # height of the fill
			self.fill_width = 75 * SCALE_FACTOR  # width of the fill
			self.bar_y = self.owner.center_y + self.owner.height / 2 + 10* SCALE_FACTOR  # 10 pixels above the owner
			self.bar_x = self.owner.center_x
			

		def updates(self) -> None:
			# Update health bar position above the owner
			self.bar_y = self.owner.center_y + self.owner.height / 2 + 10* SCALE_FACTOR  # 10 pixels above the owner
			self.bar_x = self.owner.center_x
			self.sprite.center_y = self.bar_y
			self.sprite.center_x = self.bar_x
			if self.owner.max_health:
				self.health_percentage = self.owner.current_health / self.owner.max_health
			else:
				self.health_percentage = 0
			self.fill_width = 75 * round(self.health_percentage,1)* SCALE_FACTOR  # width of the fill based on health percentage

		def draws(self) -> None:
			# Draw the dynamic health fill only if health is not full
			if self.owner.current_health < self.owner.max_health:
				arcade.draw_lbwh_rectangle_filled(
					left=self.bar_x-38*SCALE_FACTOR,
					bottom=self.bar_y-10*SCALE_FACTOR,
					width=self.fill_width,
					height=self.fill_height,
					color=arcade.color.RED_DEVIL)
				self.sprite_list.draw()
				
			
		def to_decimal(self,health_pecentages:float) -> float:
			"""returns the health percentage truncated to 1 decimal place"""
			return round(health_pecentages, 1)

	# Modified Object class methods for health management using HealthBar
	# Getter for max_health
	@property
	def max_health(self) -> int:
		return self.__max_health

	# Getter for current_health
	@property
	def current_health(self) -> int:
		return self.__current_health

	# Setter for current_health (with validation)
	@current_health.setter
	def current_health(self, value: int) -> None:
		self.__current_health = max(0, min(self.__max_health, value))
		if self.__current_health == 0:
			self.on_death()

	def take_damage(self, amount: int) -> None:
		"""Reduce health by the given amount."""
		if self.invincible:
			return
		self.current_health -= amount

	def heal(self, amount: int) -> None:
		"""Increase health by the given amount."""
		if max(self.current_health + amount, 0) > self.max_health:
			amount = self.max_health - self.current_health
		self.current_health += amount

	def on_death(self) -> bool:
		"""Handle the death of the object."""
		return True

	def update_health_bar(self) -> None:
		"""Update the health bar with the current health status."""
		self.health_bar.updates()

	def draw_health_bar(self) -> None:
		"""Draw the health bar."""
		self.health_bar.draws()
	
	@property
	def invincible(self) -> bool:
		"""Check if the player is invincible."""
		# The invincible property is True if either the flag is set,
		# or the timer is still counting down.
		return self.__invincible or self.__invincible_timer > 0

	@invincible.setter
	def invincible(self, value: bool) -> None:
		"""Set the player's invincibility status.
		   When set to True, the player remains invincible for 3 seconds.
		"""
		if value == self.__invincible:
			return
		self.__invincible = value
		if value:
			self.__invincible_timer = 0.3 # Duration of invincibility in seconds
		else:
			self.__invincible_timer = 0

	def update_invincibility(self, delta_time: float) -> None:
		"""Update the invincibility timer using delta time."""
		if self.__invincible_timer > 0:
			self.__invincible_timer -= delta_time

			if self.__invincible_timer <= 0:
				self.__invincible_timer = 0
				self.__invincible = False
	"""ATTENTION LAVE NE TUE PAS PERSO SI IL EST INVINCIBLE"""
	
