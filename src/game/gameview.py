from __future__ import annotations
import arcade
from typing import  List, Optional
from src.map_builder.level_builder import LevelBuilder
from src.weapons.sword import Sword          
from src.entities.base_entity import Enemy     # path of your new file
from src.map_builder.platforms import Platform


class GameView(arcade.View):
    """Main in-game view."""

    PLAYER_MOVEMENT_SPEED: int = 5

    def __init__(self) -> None:
        super().__init__()
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        self.map_name: str = "maps/map3.txt"

        # Dummy defaults for mypy
        self.wall_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
        self.coin_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()
        self.monster_list: arcade.SpriteList[Enemy] = arcade.SpriteList()

        self.test:arcade.SpriteList[arcade.Sprite | Platform]= arcade.SpriteList()

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
        self.sword : Sword = Sword(self.player_sprite, self.camera)
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

        yes=arcade.Sprite(":resources:images/tiles/boxCrate_double.png", scale=0.5)
        yes.center_x = 100
        yes.center_y = 100
        yes.change_x = 1
        yes.boundary_left= 100
        yes.boundary_right = 500

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

        #self.platforms : arcade.SpriteList[arcade.Sprite]=arcade.SpriteList()


        #self.platforms = arcade.SpriteList(use_spatial_hash=True)

        #self.platforms = new_map["platforms"]

        #self.sword.environment(self.monster_list)
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player_sprite,
            walls=self.wall_list,
            platforms=self.platforms,          # <- HERE
            gravity_constant=0.8,
        )
        
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
                    self.player_sprite.change_y = +14
            case arcade.key.SPACE:
                self.player_sprite.change_x = 0
                self.player_sprite.change_y = 0
                self.setup(self.map_name)
            case _:
                pass

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.RIGHT | arcade.key.LEFT:
                self.player_sprite.change_x = 0
            case _:
                pass
    
    
    def on_update(self, delta_time: float) -> None:

        # Physics step
        if self.physics_engine is not None:
            self.physics_engine.update()
        # Update moving platforms with delta_time
        self.platforms.update(delta_time)

        # Monster AI and collision
        for monster in self.monster_list:
            monster.update(delta_time)
            if arcade.check_for_collision(self.player_sprite, monster):
                arcade.play_sound(self.game_over_sound)
                self.setup(self.map_name)
                return
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

        # Death or exit → reset or next level
        if arcade.check_for_collision_with_list(self.player_sprite, self.death_list):
            arcade.play_sound(self.game_over_sound)
            self.setup(self.map_name)
            return
        if arcade.check_for_collision_with_list(self.player_sprite, self.exit_list):
            self.setup("maps/map2.txt")
            return
        # Camera follows player horizontally
        self.camera.position = [self.player_sprite.center_x, 360]  # type: ignore



    def on_draw(self) -> None:
        self.clear()
        with self.camera.activate():
            arcade.draw_sprite(self.player_sprite)
            self.wall_list.draw()
            self.coin_list.draw()
            self.death_list.draw()
            self.monster_list.draw()
            self.exit_list.draw()
            self.platforms.draw()
            #self.sword.draw()
        
        


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