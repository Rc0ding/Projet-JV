import arcade
import time

class GameView(arcade.View):
        """Main in-game view."""

        
        def __init__(self) -> None:
                # Magical incantion: initialize the Arcade view
                super().__init__()

                # Choose a nice comfy background color
                self.background_color = arcade.csscolor.CORNFLOWER_BLUE

                # Setup our game
                self.setup()
                


        physics_engine: arcade.PhysicsEnginePlatformer
        player_sprite: arcade.Sprite
        
        ### LISTE DES OBJETS
        wall_list: arcade.SpriteList[arcade.Sprite]
        
        wall_list=arcade.SpriteList(use_spatial_hash=True)

        coin_list:arcade.SpriteList[arcade.Sprite]
        
        coin_list=arcade.SpriteList(use_spatial_hash=True)

        lava_list:arcade.SpriteList[arcade.Sprite]
        
        lava_list=arcade.SpriteList(use_spatial_hash=True)
        
        camera: arcade.camera.Camera2D
        
        PLAYER_MOVEMENT_SPEED:int=10
        
        gameoversound = arcade.load_sound(r".\ressources\gameover.mp3")



        #":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"

        def setup(self)-> None:
                """Set up the game here."""
                self.player_sprite = arcade.Sprite(
                r".\ressources\perso.png",
                center_x=64,
                center_y=128,
                scale=0.075
                )
                
                for i in range(21):
                        grass=arcade.Sprite(":resources:images/tiles/grassMid.png", 0.5, 64*i,32)
                        self.wall_list.append(grass)
                
                lava=arcade.Sprite(":resources:/images/tiles/lava.png", 0.5,1344,32)
                self.lava_list.append(lava)
                
                
                for i in range(1,4):
                        self.wall_list.append(arcade.Sprite(":resources:images/tiles/boxCrate_double.png",0.5,256*i,96))
                
                self.coin_list.append(arcade.Sprite(r".\ressources\noahlan.png",0.55,350,100))
                self.coin_list.append(arcade.Sprite(r".\ressources\noahlan.png",0.55,512,164))
                
                self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,self.wall_list,0.5)
                self.camera= arcade.camera.Camera2D()
                
        


        
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
                                #petit probleme saut infini
                                if self.player_sprite.change_y==0:
                                        self.player_sprite.change_y= +10
                        
                        #remets le jeu à zero        
                        case arcade.key.SPACE:
                                self.player_sprite.change_x=0
                                self.player_sprite.change_y=0
                                self.setup()



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
                
        
                self.camera.position=[self.player_sprite.position[0],360] # type: ignore
                
                coins:list[arcade.Sprite]
                        
                coins=arcade.check_for_collision_with_list(self.player_sprite,self.coin_list)
                
                lava=arcade.check_for_collision_with_list(self.player_sprite,self.lava_list)
                
                if len(lava)!=0:
                        self.gameover()
                
                if len(coins)!=0:
                        for coin in coins:
                                coin.remove_from_sprite_lists()
                
                self.physics_engine.update()              
                
                
        def gameover(self) -> None:
                cx=self.player_sprite.center_x
                cy=self.player_sprite.center_y
                self.player_sprite = arcade.Sprite(r".\ressources\persofeu.PNG",scale=0.075,center_x=cx,center_y=cy)
                time.sleep(0.5)       
                print(self.player_sprite.texture.file_path)
                arcade.play_sound(self.gameoversound)
                time.sleep(2.14)
                self.player_sprite.change_x=0
                self.player_sprite.change_y=0
                self.player_sprite = arcade.Sprite(r".\ressources\perso.png",scale=0.075,center_x=cx,center_y=cy)
                self.setup()
                
        def on_draw(self) -> None:
                
                """Render the screen."""
                self.clear() # always start with self.clear()
                        
                
                with self.camera.activate():
                        arcade.draw_sprite(self.player_sprite)
                        self.wall_list.draw()
                        self.coin_list.draw()
                        self.lava_list.draw()
