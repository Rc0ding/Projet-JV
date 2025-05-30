import arcade
from src.weapons.sword import Sword
from src.game.player import Player
import pytest

def test_environment_sets_monster_list(window: arcade.Window) -> None:
    """environment() doit stocker la liste de monstres dans _monster_list."""
    player = Player()
    camera = arcade.camera.Camera2D()
    sword = Sword(player, camera)

    monsters = arcade.SpriteList()
    sword.environment(monsters)

    assert sword._monster_list is monsters


def test_mouse_press_and_release_toggle_visibility(window: arcade.Window) -> None:
    """Le clic gauche active l’épée, puis la relâche désactive."""
    player = Player()
    camera = arcade.camera.Camera2D()
    sword = Sword(player, camera)

    # Au démarrage, invisible
    assert not sword.visible

    # Clic gauche → visible
    sword.on_mouse_press(100, 150, arcade.MOUSE_BUTTON_LEFT, 0)
    assert sword.visible

    # Relâchement clic gauche → invisible
    sword.on_mouse_release(100, 150, arcade.MOUSE_BUTTON_LEFT, 0)
    assert not sword.visible


def test_updating_moves_only_when_visible(window: arcade.Window) -> None:
    """updating() ne change position que si visible==True."""
    player = Player()
    camera = arcade.camera.Camera2D()
    sword = Sword(player, camera)

    # Place l'épée à une position de référence
    sword.center_x = 50.0
    sword.center_y = 75.0
    orig_x, orig_y = sword.center_x, sword.center_y

    # Simuler mouvement de souris
    sword.on_mouse_motion(300, 400, 0, 0)
    # Invisible : updating ne touche pas aux coords
    sword.updating(player, camera)
    assert sword.center_x == orig_x
    assert sword.center_y == orig_y

    # Rendre visible et mettre à jour → position modifiée
    sword.on_mouse_press(300, 400, arcade.MOUSE_BUTTON_LEFT, 0)
    sword.updating(player, camera)
    assert (sword.center_x, sword.center_y) != (orig_x, orig_y)
