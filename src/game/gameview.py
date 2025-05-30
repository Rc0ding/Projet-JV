from __future__ import annotations

# ───────────────────────── Imports ──────────────────────────
import arcade
from typing import  Optional

from src.texture_manager import *
from src.map_builder.level_builder import LevelBuilder
from src.map_builder.platforms import Platform
from src.map_builder.switch import Gate, Switch

from src.game.player          import Player
from src.entities.base_entity import Enemy
from src.weapons.sword        import Sword
from src.weapons.bow          import Bow
from src.weapons.weapon       import Weapon

# ───────────────────────── Game view ────────────────────────
class GameView(arcade.View):
	"""Main in-game view."""

	# --------------------- constants ------------------------
	PLAYER_MOVEMENT_SPEED: int = 10

	# --------------------- ctor / setup --------------------
	def __init__(self) -> None:
		super().__init__()

		# camera & background
		self.camera: arcade.Camera2D = arcade.Camera2D()
		self.background              = get_texture_path(BACKGROUND_TEXTURE)
		self.background_color        = arcade.color.BLACK

		# map
		self.map_name: str = "assets/maps/1.txt"

		# runtime collections (dummy init ⇒ typage mypy)
		self.wall_list:      arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
		self.coin_list:      arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
		self.monster_list:   arcade.SpriteList[Enemy]         = arcade.SpriteList()
		self.platforms:      arcade.SpriteList[Platform]      = arcade.SpriteList(use_spatial_hash=True)
		self.gates:          arcade.SpriteList[Gate]          = arcade.SpriteList()
		self.switches:       arcade.SpriteList[Switch]        = arcade.SpriteList(use_spatial_hash=True)
		self.death_list:     arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
		self.exit_list:      arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
		self.player_sprite_list: arcade.SpriteList[Player]    = arcade.SpriteList()

		# single-sprite refs (set in setup())
		self.player_sprite: Player
		self.switch:        Switch
		self.score: int = 0
		# physics & weapons
		self.physics_engine: Optional[arcade.PhysicsEnginePlatformer] = None
		self.sword :  Sword
		self.bow   :  Bow
		self.current_weapon: Weapon
		self.weaponss: arcade.SpriteList[Weapon] = arcade.SpriteList()

		# SFX
		self.game_over_sound = arcade.load_sound(":resources:sounds/gameover1.wav")

		# launch level
		self.setup(self.map_name)

	def setup(self, map_filename: str) -> None:
		"""(Re)charge un niveau complet."""
		new_map = LevelBuilder().build_level(map_filename)

		# ----- sprite lists -----
		self.wall_list      = new_map["walls"]
		self.platforms      = new_map["platforms"]
		self.gates          = new_map["gates"]
		self.switches       = new_map["switches"]
		self.monster_list   = new_map["monsters"]
		self.coin_list      = new_map["coins"]
		self.death_list     = new_map["death"]
		self.exit_list      = new_map["exit"]
		self.player_sprite_list = new_map["player"]


		# ----- player -----
		self.player_sprite      = self.player_sprite_list[0]
		self.initial_x, self.initial_y = self.player_sprite.center_x, self.player_sprite.center_y

		# ----- physics -----
		self.physics_engine = arcade.PhysicsEnginePlatformer(
			player_sprite=self.player_sprite,
			walls=self.wall_list,
			platforms=self.platforms,
			gravity_constant=1,
		)

		# ----- weapons -----
		self.sword  = Sword(self.player_sprite, self.camera)
		self.bow    = Bow(self.player_sprite, self.camera)
		self.current_weapon = self.sword
		self.weaponss = arcade.SpriteList(use_spatial_hash=True)
		self.weaponss.append(self.sword)
		self.weaponss.append(self.bow)

		# enemies need environment reference
		for monster in self.monster_list:
			monster.set_environment(self.wall_list)

		print("Level loaded – switches:", len(self.switches), "gates:", len(self.gates))

	# ───────────────────── Input handlers ───────────────────
	def on_key_press(self, symbol: int, modifiers: int) -> None:
		match symbol:
			case arcade.key.RIGHT:
				self.player_sprite.change_x = +self.PLAYER_MOVEMENT_SPEED
			case arcade.key.LEFT:
				self.player_sprite.change_x = -self.PLAYER_MOVEMENT_SPEED
			case arcade.key.UP:
				self.player_sprite.change_y = +20
			case arcade.key.SPACE:         # reload same map
				self.player_sprite.change_x = self.player_sprite.change_y = 0
				self.setup(self.map_name)
			case arcade.key.R:             # debug damage
				self.player_sprite.take_damage(10)
				for m in self.monster_list:
					m.current_health -= 10
			case arcade.key.T:             # debug heal
				self.player_sprite.heal(10)
				for m in self.monster_list:
					m.current_health += 10
			case _:
				pass

	def on_key_release(self, symbol: int, modifiers: int) -> None:
		if symbol in (arcade.key.RIGHT, arcade.key.LEFT):
			self.player_sprite.change_x = 0

	# simple continuous movement
	def on_key_hold(self, symbol: int, modifiers: int) -> None:
		if symbol == arcade.key.RIGHT:
			self.player_sprite.change_x = +self.PLAYER_MOVEMENT_SPEED
		elif symbol == arcade.key.LEFT:
			self.player_sprite.change_x = -self.PLAYER_MOVEMENT_SPEED

	# mouse: attack / switch weapon
	def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> None:
		if button == arcade.MOUSE_BUTTON_LEFT:
			self.current_weapon.visible = True
			self.current_weapon.on_mouse_press(x, y, button, modifiers)
		elif button == arcade.MOUSE_BUTTON_RIGHT:
			self.current_weapon.visible = False
			self.current_weapon = self.bow if self.current_weapon is self.sword else self.sword

	def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
		if button == arcade.MOUSE_BUTTON_LEFT:
			self.current_weapon.visible = False
			self.current_weapon.on_mouse_release(x, y, button, modifiers)
			self.sword.on_mouse_release(x, y, button, modifiers)

	def on_mouse_motion(self, x: float, y: float, dx: int, dy: int) -> None:
		self.current_weapon.on_mouse_motion(x, y, dx, dy)

	# ───────────────────── Update loop ──────────────────────
	def on_update(self, delta_time: float) -> None:
		# physics step
		if self.physics_engine:
			self.physics_engine.update()

		# ---- monsters ----
		for monster in list(self.monster_list):
			monster.update(delta_time)
			monster.health_bar.updates()

			if monster.current_health <= 0:
				monster.remove_from_sprite_lists()
				continue

			if arcade.check_for_collision(self.player_sprite, monster):
				self.player_sprite.take_damage(20)
				self.player_sprite.invincible = True
				direction = self.player_sprite.center_x > monster.center_x
				self.player_sprite.knockback(2700, delta_time, direction)
				return

		# ---- sword logic & damage ----
		self.sword.updating(self.player_sprite, self.camera)
		self.sword.update_cooldown(delta_time)
		self.bow.updating(self.player_sprite, self.camera)
		for p in arcade.check_for_collision_with_list(self.player_sprite, self.platforms):
			if getattr(p, "is_deadly", False):
				self.setup(self.map_name)       # or whatever routine you already call
				return

		if self.sword.ready():
			for enemy in arcade.check_for_collision_with_list(self.sword, self.monster_list):
				enemy.take_damage(self.sword.DAMAGE)
				if enemy.current_health <= 0:
					enemy.remove_from_sprite_lists()

			for switch in arcade.check_for_collision_with_list(self.sword, self.switches):
				switch.trigger()

			self.sword.reset_cooldown()
		
		for arrow in list(self.bow.arrows):          # safe copy – we may remove items
    # 1) monsters -------------------------------------------------
			victims = arcade.check_for_collision_with_list(
				arrow, self.monster_list)
			for m in victims:
				m.take_damage(self.bow.DAMAGE)
				if m.current_health <= 0:
					m.remove_from_sprite_lists()
					arrow.remove_from_sprite_lists()
					break                                   # arrow spent → stop further checks

		# 2) gates ----------------------------------------------------
			if arrow in self.bow.arrows:             # still alive?
				switch_hit = arcade.check_for_collision_with_list(
					arrow, self.switches)
				if switch_hit:
					switch_hit[0].trigger()
					arrow.remove_from_sprite_lists()

			# ► 3) terrain / platforms -----------------------------------
			#    self.wall_list already contains *both* the static tiles and
			#    the moving Platform sprites because you called
			#    `self.wall_list.extend(self.platforms)` in setup().
			if arrow in self.bow.arrows:             # still alive?
				if arcade.check_for_collision_with_list(arrow, self.wall_list):
					arrow.remove_from_sprite_lists()

		# ---- gates solid / open management ----
		for gate in self.gates:
			if gate.is_open and gate in self.wall_list:
				self.wall_list.remove(gate)
			elif not gate.is_open and gate not in self.wall_list:
				self.wall_list.append(gate)

		# ---- coins ----
		for coin in arcade.check_for_collision_with_list(self.player_sprite, self.coin_list):
			coin.remove_from_sprite_lists()
			score += 1

		# ---- player status ----
		self.player_sprite.update_invincibility(delta_time)
		self.player_sprite.update_health_bar()

		# ---- end-level / death ----
		if (
			arcade.check_for_collision_with_list(self.player_sprite, self.death_list)
			or self.player_sprite.current_health <= 0
			or self.player_sprite.center_y < -300
		):
			self.player_sprite.change_x = self.player_sprite.change_y = 0
			self.setup(self.map_name)
			return

		if arcade.check_for_collision_with_list(self.player_sprite, self.exit_list):
			if self.map_name == "assets/maps/1.txt":
				self.map_name = "assets/maps/2.txt"
			elif self.map_name == "assets/maps/2.txt":
				self.map_name = "assets/maps/3.txt"
			else:
				self.map_name = "assets/maps/1.txt"
			self.setup(self.map_name)  # or load next level, etc.
			return

		# ---- camera follow ----
		self.camera.position = arcade.Vec2(
			self.player_sprite.center_x,
			self.player_sprite.center_y - self.player_sprite.change_y,
		)

	# ───────────────────── Draw loop ────────────────────────
	def on_draw(self) -> None:
		self.clear()
		arcade.draw_texture_rect(self.background, arcade.LBWH(0, 0, 1280, 720))

		with self.camera.activate():
			self.gates.draw()
			self.switches.draw()
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

			self.weaponss.draw()
			self.bow.arrows.draw()
