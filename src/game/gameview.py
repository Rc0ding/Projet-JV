from __future__ import annotations
import arcade
from typing import  List, Optional
from src.map_builder.level_builder import LevelBuilder
from src.weapons.sword import Sword          
from src.entities.base_entity import Enemy     # path of your new file
from src.map_builder.platforms import Platform
from src.game.player import Player
from src.texture_manager import *
class GameView(arcade.View):
	"""Main in-game view."""

	PLAYER_MOVEMENT_SPEED: int = 10

	def __init__(self) -> None:
		super().__init__()
		self.background = get_texture_path(BACKGROUND_TEXTURE)
		self.background_color = arcade.color.BLACK

		self.map_name: str = "maps/map2.txt"
		# Dummy defaults for mypy
		self.wall_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
		self.coin_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
		self.monster_list: arcade.SpriteList[Enemy] = arcade.SpriteList()

		self.test:arcade.SpriteList[arcade.Sprite | Platform]= arcade.SpriteList()

		self.death_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
		self.exit_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
		self.player_sprite_list: arcade.SpriteList[Player] = arcade.SpriteList()
		self.player_sprite: Player
		self.initial_x: float = 0.0
		self.initial_y: float = 0.0
	
		self.physics_engine: Optional[arcade.PhysicsEnginePlatformer] = None
		self.camera: arcade.Camera2D = arcade.camera.Camera2D()


		self.game_over_sound: arcade.Sound = arcade.load_sound(":resources:sounds/gameover1.wav")

		# === Sword setup ===
		self.sword : Sword
		self.weaponss: arcade.SpriteList[Sword] = arcade.SpriteList()

		# ===================

		# Build the level
		self.setup(self.map_name)

	def setup(self, map_filename: str) -> None:
		self.map= LevelBuilder().build_level(map_filename)
		new_map = self.map
		self.wall_list    = new_map["walls"]
		self.coin_list    = new_map["coins"]
		self.monster_list = new_map["monsters"]
		self.death_list   = new_map["death"]
		self.exit_list    = new_map["exit"]
		self.player_sprite_list = new_map["player"]
		self.platforms = new_map["platforms"]

		"""""
		no= Platform(":resources:images/tiles/boxCrate_double.png",
						  start_pos=(500, 100), axis="x", direction=False,
						  boundary_a=100, boundary_b=501)
		"""
	

		#self.test.append(yes)
		#self.test.append(no)

		self.player_sprite = self.player_sprite_list[0]
		self.initial_x     = self.player_sprite.center_x
		self.initial_y     = self.player_sprite.center_y
		print("health", self.player_sprite.current_health)
		#self.platforms : arcade.SpriteList[arcade.Sprite]=arcade.SpriteList()

		#self.platforms = arcade.SpriteList(use_spatial_hash=True)

		#self.platforms = new_map["platforms"]

		#self.sword.environment(self.monster_list)
		self.physics_engine = arcade.PhysicsEnginePlatformer(
			player_sprite=self.player_sprite,
			walls=self.wall_list,
			platforms=self.platforms,          # <- HERE
			gravity_constant=1,
		)
		self.sword= Sword(self.player_sprite, self.camera)
		self.weaponss= arcade.SpriteList(use_spatial_hash=True)
		self.weaponss.append(self.sword)
		self.camera = arcade.camera.Camera2D()

		 
		# Physics engine now needs the platform list
		for monster in self.monster_list:
			monster.set_environment(self.wall_list) 

	def on_key_press(self, symbol: int, modifiers: int) -> None:
		match symbol:
			case arcade.key.RIGHT:
				self.player_sprite.change_x = +self.PLAYER_MOVEMENT_SPEED
			case arcade.key.LEFT:
				self.player_sprite.change_x = -self.PLAYER_MOVEMENT_SPEED
			case arcade.key.UP:
				if self.player_sprite.change_y == 0:
					self.player_sprite.change_y = +20
			case arcade.key.SPACE:
				self.player_sprite.change_x = 0
				self.player_sprite.change_y = 0
				self.setup(self.map_name)
			case arcade.key.R:
				self.player_sprite.take_damage(10)  # Reset player health for testing
				for monster in self.monster_list:
					print("Monster health before damage:", monster.current_health)
					monster.current_health -= 10
			case arcade.key.T:
				self.player_sprite.heal(10) # Restore player health for testing
				for monster in self.monster_list:
					monster.current_health += 10
			case _:
				pass


	def on_key_release(self, symbol: int, modifiers: int) -> None:
		match symbol:
			case arcade.key.RIGHT | arcade.key.LEFT:
				self.player_sprite.change_x = 0
			case _:
				pass
	def on_key_hold(self, symbol: int, modifiers: int) -> None:
		"""Handle key hold events for continuous movement."""
		match symbol:
			case arcade.key.RIGHT:
				self.player_sprite.change_x = +self.PLAYER_MOVEMENT_SPEED
			case arcade.key.LEFT:
				self.player_sprite.change_x = -self.PLAYER_MOVEMENT_SPEED
			case _:
				pass
	
	def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
		if button == arcade.MOUSE_BUTTON_LEFT:
			self.sword.visible = True
			self.sword.on_mouse_press(x, y, button, modifiers)
	def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
		if button == arcade.MOUSE_BUTTON_LEFT:
			self.sword.visible = False
			self.sword.on_mouse_release(x, y, button, modifiers)
	def on_mouse_motion(self, x: float, y: float, dx: int, dy: int) -> None:
		self.sword.on_mouse_motion(x, y, dx, dy)

	def on_update(self, delta_time: float) -> None:
	
		# Physics step
		if self.physics_engine is not None:
			self.physics_engine.update()
		# Update moving platforms with delta_time
			#self.platforms.update(delta_time)  ATTENTION NE FAIT BUGGER LE PERSONNAGE
		# Monster AI and collision
		for monster in self.monster_list:
			monster.update(delta_time)
			if monster.current_health <= 0:
				monster.remove_from_sprite_lists()
			monster.health_bar.updates()
			if arcade.check_for_collision(self.player_sprite, monster):
				self.player_sprite.take_damage(20)
				self.player_sprite.invincible = True
				direction: bool = self.player_sprite.center_x > monster.center_x
				self.player_sprite.knockback(2700,delta_time, direction)
				return
		self.sword.updating(self.player_sprite, self.camera)
		"""
		for monster in self.sword.killing():
		   monster.remove_from_sprite_lists()"""

		# L'épée suit TOUT LE TEMPS la position du joueur
		#self.sword.sword_update(delta_time)
		
		# Collect coins
		coins: List[arcade.Sprite] = arcade.check_for_collision_with_list(
			self.player_sprite, self.coin_list
		)
		for coin in coins:
			coin.remove_from_sprite_lists()
		self.player_sprite.update_invincibility(delta_time)


		# Death or exit → reset or next level
		if arcade.check_for_collision_with_list(self.player_sprite, self.death_list) or self.player_sprite.current_health <= 0 or self.player_sprite.center_y < -300:
			self.player_sprite.change_x = 0
			self.player_sprite.change_y = 0
			self.setup(self.map_name)
			return
		if arcade.check_for_collision_with_list(self.player_sprite, self.exit_list):
			self.setup("maps/map2.txt")
			return
		self.player_sprite.update_health_bar()
		# Camera follows player horizontally
		self.camera.position = [self.player_sprite.center_x, 360]  # type: ignore



	def on_draw(self) -> None:
		self.clear()
		arcade.draw_texture_rect(
            	self.background,
            	arcade.LBWH(0, 0, 1280, 720),
        	)
		with self.camera.activate():
			arcade.draw_sprite(self.player_sprite)
			self.wall_list.draw()
			self.coin_list.draw()
			self.death_list.draw()
			self.monster_list.draw()
			self.exit_list.draw()
			self.platforms.draw()
			self.player_sprite.draw_health_bar()
			for monster in self.monster_list:
				monster.draw_health_bar()
			if self.sword.visible:
			    self.weaponss.draw()
		
		


""" def splash(self, text: str, duration: float = 5.0) -> None:
		self.message_text = arcade.Text(
			text,
			x=0,
			y=500,
			color=arcade.color.WHITE,
			font_size=70,
			anchor_x="center",
			anchor_y="center",
		)
		self.message_timer = duration """