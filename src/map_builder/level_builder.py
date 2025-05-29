import arcade
from typing import List, Dict, TypedDict
from src.entities.blob import Blob
from src.entities.bat import Bat
from src.entities.base_entity import Enemy
from src.map_builder import map_loader
from src import textures  
from src import constants_proj
from src import helper
from src.map_builder.platform_build import build_platforms
from src.map_builder.platforms import Platform
from src.game.player import Player
#from src.map_builder.gates import Gate
#from src.map_builder.switch import Switch
#from src.helper import grid_to_world

class LevelData(TypedDict):
    walls:     arcade.SpriteList[arcade.Sprite]
    coins:     arcade.SpriteList[arcade.Sprite]
    death:     arcade.SpriteList[arcade.Sprite]
    exit:      arcade.SpriteList[arcade.Sprite]
    player:    arcade.SpriteList[Player]
    monsters:  arcade.SpriteList[Enemy]
    platforms: arcade.SpriteList[Platform]
    #gates:    arcade.SpriteList[Gate]
    #switches: arcade.SpriteList[Switch]

class LevelBuilder:


	    
	def build_level(self,filename:str) -> LevelData:

		meta, rows = map_loader.MapLoader(filename).load()
	
		"""
		Builds the level assuming your map file lists rows from top to bottom.
		This code reverses self.grid so that row 0 is at the TOP in-game.
		"""
		wall_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
		coin_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
		death_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
		exit_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
		player_sprite_list: arcade.SpriteList[Player] = arcade.SpriteList()
		monster_list: arcade.SpriteList[Enemy] = arcade.SpriteList(use_spatial_hash=True)
		platforms: arcade.SpriteList[Platform] = arcade.SpriteList(use_spatial_hash=True)
		#gate_list:   arcade.SpriteList[Gate]   = arcade.SpriteList(use_spatial_hash=True)
		#switch_list: arcade.SpriteList[Switch] = arcade.SpriteList()



		# Reverse self.grid so the top line in the file is row_index=0 (top in the game).
		reversed_grid: List[str] = list(reversed(rows))
		last_ground_tiles: Dict[int, arcade.Sprite] = {}
		boundary_list: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
		#self.platforms:  = arcade.SpriteList(use_spatial_hash=True)

		#platform_sprites = build_platforms(rows, meta,textures.TEXTURES)
		#self.platforms.extend(platform_sprites)

		
		for row_index, row in enumerate(reversed_grid):
			
			#padded_row = row.ljust(meta["width"], " ")

			for col_index, symbol in enumerate(row):
				x,y=helper.grid_to_world(col_index,row_index)

				match symbol:
					# --------------------------------------------------------------
					# Player start
					# --------------------------------------------------------------
					case 'S':
						player_sprite = Player()
						player_sprite.center_x = x
						player_sprite.center_y = y
						player_sprite_list.append(player_sprite)

						continue                           # next grid-cell
					case 'E':
						exit_sprite = arcade.Sprite(
							":resources:images/tiles/signExit.png",
							scale=constants_proj.SCALE_FACTOR
						)
						exit_sprite.center_x = x
						exit_sprite.center_y = y
						exit_list.append(exit_sprite)
						continue

					case 'o':                            # Blob
						blobb = Blob((x, y), speed=1)
						monster_list.append(blobb)
						print("\n")
						print("\n")
						print("Found blob at", x, y)
						print("\n")
						print("\n")
						continue

					case 'b':                            # Bat
						batt = Bat((x, y + 200), radius_px=500, speed=3)
						monster_list.append(batt)

						continue

					# --------------------------------------------------------------
					# Static tiles & collectibles
					# --------------------------------------------------------------
					case glyph if glyph in textures.TEXTURES:
						sprite_info = textures.TEXTURES[glyph]
						sprite = arcade.Sprite(sprite_info, scale=constants_proj.SCALE_FACTOR)
						sprite.center_x = x
						sprite.center_y = y
						if glyph in ("-", "=", "x"):          # sol, plateforme, caisse
							wall_list.append(sprite)
						elif glyph == "*":                    # pièce
							coin_list.append(sprite)
						elif glyph == "£":                    # piège
							death_list.append(sprite)
									# crates act as boundaries
						if glyph == 'x':
							boundary_list.append(sprite)

						# remember last ground tile in each column
						if glyph in ('-', 'x', '='):
							last_ground_tiles[col_index] = sprite

					# --------------------------------------------------------------
					# Anything else → ignore
					# --------------------------------------------------------------
					case _:
						pass
		

		# Build moving platforms from the map
		platform_sprites = build_platforms(
			rows,  # original (not reversed) rows for platform logic
			meta,
			textures.TEXTURES
		)
		for platform in platform_sprites:
			print(f"Platform created at ({platform.center_x}, {platform.center_y}) axis={platform.axis} change_x={platform.change_x} change_y={platform.change_y}, boundary_l={platform.boundary_left}, boundary_r={platform.boundary_right}")
			platforms.append(platform)
		
		
		"""# meta now contains the parsed header dict
		gates_meta    = meta.get("gates", [])        # list[dict]
		switches_meta = meta.get("switches", [])     # list[dict]

		# ---- Gates ---------------------------------------------------
		for g in gates_meta:
			gx, gy = g["x"], g["y"]
			wx, wy = grid_to_world(gx, gy)
			gate = Gate((wx, wy), scale=constants_proj.SCALE_FACTOR)
			if g.get("state", "closed") == "open":
				gate.set_state(False)                # open
			gate_list.append(gate)
			if gate.is_solid:
				wall_list.append(gate)               # solid gates act as walls

		# ---- Switches ------------------------------------------------
		for s in switches_meta:
			sx, sy = s["x"], s["y"]
			wx, wy = grid_to_world(sx, sy)
			sw = Switch((wx, wy), scale=constants_proj.SCALE_FACTOR)

		def _link(actions: list[dict] | None, on_state: bool) -> None:
			if actions is None:
				return
			for act in actions:
				gx, gy = act["x"], act["y"]
				# find the gate obj created earlier
				gate = next((g for g in gate_list if
						g.center_x == grid_to_world(gx, 0)[0] and
						g.center_y == grid_to_world(0, gy)[1]), None)
				if gate:
					sw.add_target(gate, open_when_on=on_state)

				

		_link(s.get("switch_on"),  True)
		_link(s.get("switch_off"), False)
		switch_list.append(sw)"""


		if len(player_sprite_list) == 0:
			raise ValueError("No player sprite found in the map (missing 'S' symbol)!")

		return {
			"walls": wall_list,
			"coins": coin_list,
			"monsters": monster_list,
			"death": death_list,
			"player": player_sprite_list,
			"exit": exit_list,
			"platforms": platforms
			#"gates": gate_list,
    			#"switches": switch_list,
		}

