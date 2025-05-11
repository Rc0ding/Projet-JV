import arcade
import time
from typing import Dict, List, Optional
from mapgen import Map


class GameView(arcade.View):
    """Main in-game view."""

    # Class-level constant for movement speed.
    PLAYER_MOVEMENT_SPEED: int = 5

    def __init__(self) -> None:
        # Magical incantation: initialize the Arcade view
        super().__init__()

        # Choose a nice comfy background color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        self.map_name: str = f"maps/map1.txt"

        # Initialize attributes with dummy defaults so mypy knows they exist.
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

        # Load the game over sound
        self.game_over_sound: arcade.Sound = arcade.load_sound(":resources:sounds/gameover1.wav")

        # Setup our game
        self.setup(self.map_name)

    def setup(self, map_filename: str) -> None:
        self.map = Map()
        self.map.import_map(map_filename)
        new_map: Dict[str, arcade.SpriteList[arcade.Sprite]] = self.map.build_level()

        # Use keys as defined in Map.build_level()
        self.wall_list = new_map["walls"]
        self.coin_list = new_map["coins"]
        self.monster_list = new_map["monsters"]
        for monster in self.monster_list:
            monster.change_x = 1  # Initialize horizontal movement
        self.death_list = new_map["death"]
        self.exit_list = new_map["exit"]
        self.player_sprite_list = new_map["player"]

        # Assume there is at least one player sprite.
        self.player_sprite = self.player_sprite_list[0]
        self.initial_x = self.player_sprite.center_x
        self.initial_y = self.player_sprite.center_y

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, self.wall_list, gravity_constant=0.5
        )
        self.camera = arcade.camera.Camera2D()

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Called when the user presses a key on the keyboard."""
        match key:
            case arcade.key.RIGHT:
                # start moving to the right
                self.player_sprite.change_x = +self.PLAYER_MOVEMENT_SPEED
            case arcade.key.LEFT:
                # start moving to the left
                self.player_sprite.change_x = -self.PLAYER_MOVEMENT_SPEED
            case arcade.key.UP:
                # Petit problème: saut infini - only allow jump if not already moving vertically.
                if self.player_sprite.change_y == 0:
                    self.player_sprite.change_y = +14
            case arcade.key.SPACE:
                # Reset the game by stopping movement and re-running setup.
                self.player_sprite.change_x = 0
                self.player_sprite.change_y = 0
                self.setup(self.map_name)

    def on_key_release(self, key: int, modifiers: int) -> None:
        """Called when the user releases a key on the keyboard."""
        match key:
            case arcade.key.RIGHT | arcade.key.LEFT:
                # stop lateral movement
                self.player_sprite.change_x = 0

    def on_update(self, delta_time: float) -> None:
        """Called once per frame, before drawing.
        
        This is where in-world time "advances", or "ticks".
        """
        # Update the camera's position (adjust type if needed).
        self.camera.position = [self.player_sprite.center_x, 360]  # type: ignore

        coins: List[arcade.Sprite] = arcade.check_for_collision_with_list(
            self.player_sprite, self.coin_list
        )
        if coins:
            for coin in coins:
                coin.remove_from_sprite_lists()
        
        if arcade.check_for_collision_with_list(self.player_sprite, self.death_list):
            arcade.play_sound(self.game_over_sound)
            self.setup(self.map_name)         # simple “restart level”
            return

        # Update the physics engine if it's initialized.
    
        if self.physics_engine is not None:
            self.physics_engine.update()

        for monster in self.monster_list:
            monster.update(delta_time, self.wall_list)        # animate AI
            if arcade.check_for_collision(self.player_sprite, monster):
                arcade.play_sound(self.game_over_sound)
                self.setup(self.map_name)                     # simple “restart”
                return

            
            
    def on_draw(self) -> None:
        """Render the screen."""
        self.clear()  # always start with self.clear()

        with self.camera.activate():
            arcade.draw_sprite(self.player_sprite)
            self.wall_list.draw()
            self.coin_list.draw()
            self.death_list.draw()
            self.monster_list.draw()
            self.exit_list.draw()
