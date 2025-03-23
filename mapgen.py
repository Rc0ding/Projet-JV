import arcade
from typing import List, Dict, Any

class Map:
    def __init__(self) -> None:
        self.width: int = 0
        self.height: int = 0
        self.grid: List[List[str]] = []
        self.next_level: str = ""

    def import_map(self, filename: str) -> None:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines: List[str] = f.readlines()
        except FileNotFoundError:
            print("Erreur : le fichier est introuvable")
            return

        config_lines: List[str] = []
        grid_lines: List[str] = []
        in_grid: bool = False

        for line in lines:
            if line.startswith("---") and not in_grid:
                in_grid = True
                continue
            if in_grid:
                grid_lines.append(line)
            else:
                config_lines.append(line)

        # Remove the last line from grid_lines if it exists
        if grid_lines:
            grid_lines.pop()

        # Parse config lines for width/height if needed
        for line in config_lines:
            if line.startswith("width:"):
                try:
                    self.width = int(line.split(":", 1)[1].strip())
                except ValueError:
                    print("Erreur : la largeur doit être un entier")
                    return
            elif line.startswith("height:"):
                try:
                    self.height = int(line.split(":", 1)[1].strip())
                except ValueError:
                    print("Erreur : la hauteur doit être un entier")
                    return
            elif line.startswith("next-map:"):
                self.next_level = "maps/" + line.split(":", 1)[1].strip().lstrip()

        self.grid = []
        for row_index, line in enumerate(grid_lines):
            # Note: Using list(line) will include newline characters.
            self.grid.append(list(line))

    def build_level(self) -> Dict[str, arcade.SpriteList[arcade.Sprite]]:
        """
        Builds the level assuming your map file lists rows from top to bottom.
        This code reverses self.grid so that row 0 is at the TOP in-game.
        """
        wall_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
        coin_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
        monster_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
        death_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
        exit_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
        player_sprite_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList()

        # We'll just fix the tile size & scale for demonstration:
        tile_size: int = 64
        scale_factor: float = 0.5  # for 128×128 images → 64×64 on screen

        texture_mapping: Dict[str, Dict[str, Any]] = {
            '=': {"texture": ":resources:images/tiles/grassMid.png", "list": wall_list},
            '-': {"texture": ":resources:images/tiles/grassHalf_mid.png", "list": wall_list},
            'x': {"texture": ":resources:images/tiles/boxCrate_double.png", "list": wall_list},
            '*': {"texture": ":resources:images/items/coinGold.png", "list": coin_list},
            # 'o': {"texture": ":resources:images/enemies/slimeBlue.png", "list": monster_list},
            '£': {"texture": ":resources:images/tiles/lava.png", "list": death_list}
        }

        # Reverse self.grid so the top line in the file is row_index=0 (top in the game).
        reversed_grid: List[List[str]] = list(reversed(self.grid))

        for row_index, row in enumerate(reversed_grid):
            for col_index, symbol in enumerate(row):
                # row_index=0 is the top row now, so row_index increases downward
                x: float = col_index * tile_size + tile_size / 2
                y: float = row_index * tile_size + tile_size / 2

                if symbol == 'S':
                    player_sprite = arcade.Sprite(
                        ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
                        scale=scale_factor
                    )
                    player_sprite.center_x = x
                    player_sprite.center_y = y
                    player_sprite_list.append(player_sprite)
                    continue

                elif symbol == 'E':
                    exit_sprite = arcade.Sprite(":resources:images/tiles/signExit.png", scale=scale_factor)
                    exit_sprite.center_x = x
                    exit_sprite.center_y = y
                    exit_list.append(exit_sprite)

                elif symbol in texture_mapping:
                    sprite_info: Dict[str, Any] = texture_mapping[symbol]
                    texture_path: str = sprite_info["texture"]
                    sprite = arcade.Sprite(texture_path, scale=scale_factor)
                    sprite.center_x = x
                    sprite.center_y = y
                    sprite_info["list"].append(sprite)

        if len(player_sprite_list) == 0:
            raise ValueError("No player sprite found in the map (missing 'S' symbol)!")

        return {
            "walls": wall_list,
            "coins": coin_list,
            "monsters": monster_list,
            "death": death_list,
            "player": player_sprite_list,
            "exit": exit_list
        }
