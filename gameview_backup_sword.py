import arcade
from __future__ import annotations
import time
from typing import Dict, List, Optional
from mapgen import Map
from sword import Sword

class GameView(arcade.View):
    """Main in-game view."""

    PLAYER_MOVEMENT_SPEED: int = 5

    def __init__(self) -> None:
        super().__init__()
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        self.map_name: str = "maps/map1.txt"

        # Dummy defaults for mypy
        self.map: Map
        self.wall_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
        self.coin_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
        self.monster_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
        self.death_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
        self.exit_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
        self.player_sprite_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
        self.player_sprite: arcade.Sprite = arcade.Sprite()
        self.initial_x: float = 0.0
        self.initial_y: float = 0.0
        self.physics_engine: Optional[arcade.PhysicsEnginePlatformer] = None
        self.camera: arcade.Camera2D = arcade.camera.Camera2D()

        self.game_over_sound: arcade.Sound = arcade.load_sound(":resources:sounds/gameover1.wav")

        # === Sword setup ===
        self.sword_sprite = arcade.Sprite(
            "assets/kenney-voxel-items-png/sword_silver.png",
            scale=0.5 * 0.7,
        )
        self.sword_list = arcade.SpriteList()
        self.sword_list.append(self.sword_sprite)
        # Control whether we draw the sword
        self.show_sword: bool = False
        # ===================

        # Build the level
        self.setup(self.map_name)

    def setup(self, map_filename: str) -> None:
        self.map = Map()
        self.map.import_map(map_filename)
        new_map: Dict[str, arcade.SpriteList[arcade.Sprite]] = self.map.build_level()

        self.wall_list    = new_map["walls"]
        self.coin_list    = new_map["coins"]
        self.monster_list = new_map["monsters"]
        for monster in self.monster_list:
            monster.change_x = 1
        self.death_list   = new_map["death"]
        self.exit_list    = new_map["exit"]
        self.player_sprite_list = new_map["player"]

        self.player_sprite = self.player_sprite_list[0]
        self.initial_x     = self.player_sprite.center_x
        self.initial_y     = self.player_sprite.center_y

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, self.wall_list, gravity_constant=0.5
        )
        self.camera = arcade.camera.Camera2D()

        self.splash("Hello world!", 5)

        # Position sword initially off-screen
        self.sword_sprite.center_x = -100
        self.sword_sprite.center_y = -100

    def splash(self, text: str, duration: float = 5.0) -> None:
        self.message_text = arcade.Text(
            text,
            x=0,
            y=500,
            color=arcade.color.WHITE,
            font_size=70,
            anchor_x="center",
            anchor_y="center",
        )
        self.message_timer = duration

    def on_key_press(self, key: int, modifiers: int) -> None:
        match key:
            case arcade.key.RIGHT:
                self.player_sprite.change_x = +self.PLAYER_MOVEMENT_SPEED
            case arcade.key.LEFT:
                self.player_sprite.change_x = -self.PLAYER_MOVEMENT_SPEED
            case arcade.key.UP:
                if self.player_sprite.change_y == 0:
                    self.player_sprite.change_y = +14
            case arcade.key.SPACE:
                self.player_sprite.change_x = 0
                self.player_sprite.change_y = 0
                self.setup(self.map_name)

    def on_key_release(self, key: int, modifiers: int) -> None:
        match key:
            case arcade.key.RIGHT | arcade.key.LEFT:
                self.player_sprite.change_x = 0

    def on_update(self, delta_time: float) -> None:
        # Camera follows player horizontally
        self.camera.position = [self.player_sprite.center_x, 360]  # type: ignore

        # Collect coins
        coins: List[arcade.Sprite] = arcade.check_for_collision_with_list(
            self.player_sprite, self.coin_list
        )
        for coin in coins:
            coin.remove_from_sprite_lists()

        # Death or exit → reset or next level
        if arcade.check_for_collision_with_list(self.player_sprite, self.death_list):
            arcade.play_sound(self.game_over_sound)
            self.setup(self.map_name)
            return
        if arcade.check_for_collision_with_list(self.player_sprite, self.exit_list):
            self.setup("maps/map2.txt")
            return

        # Physics step
        if self.physics_engine is not None:
            self.physics_engine.update()

        # Monster AI and collision
        for monster in self.monster_list:
            monster.update(delta_time, self.wall_list)
            if arcade.check_for_collision(self.player_sprite, monster):
                arcade.play_sound(self.game_over_sound)
                self.setup(self.map_name)
                return

        # Always keep sword positioned at player if visible
        self.sword_sprite.center_x = self.player_sprite.center_x
        self.sword_sprite.center_y = self.player_sprite.center_y

    # Modified
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Show the sword while the mouse button is held."""
        self.show_sword = True

    # Modified
    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Hide the sword when the mouse button is released."""
        self.show_sword = False

    def display_sword(self) -> None:
        """Draw the sword (if flagged visible)."""
        if self.show_sword:
            self.sword_list.draw()

    def on_draw(self) -> None:
        self.clear()
        with self.camera.activate():
            arcade.draw_sprite(self.player_sprite)
            self.wall_list.draw()
            self.coin_list.draw()
            self.death_list.draw()
            self.monster_list.draw()
            self.exit_list.draw()

            # Only draw sword when requested
            self.display_sword()
