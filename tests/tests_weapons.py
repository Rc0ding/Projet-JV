# tests/test_weapons.py
from __future__ import annotations

import math
from pathlib import Path
import sys
import pytest

# ---------------------------------------------------------------------------#
#  Ajoute le dossier src/ dans sys.path (utile pour Pytest au runtime)       #
#  mypy utilisera mypy.ini  (mypy_path = src) pour résoudre les imports.     #
# ---------------------------------------------------------------------------#
ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

import arcade                                      # pyright: ignore[reportMissingImports]
from src.game.player import Player                 # import ok une fois mypy_path fixé
from src.weapons.sword import Sword
from src.weapons.bow import (
    Bow,
    ARROW_SPEED,
    ARROW_GRAVITY,
    ARROW_COOLDOWN,
    ARROW_LIFETIME,
)

# ---------------------------------------------------------------------------#
#  Fixtures                                                                  #
# ---------------------------------------------------------------------------#
@pytest.fixture(scope="module")
def camera() -> arcade.Camera2D:                   # type: ignore[valid-type]
    # La signature exacte dépend des stubs (s’ils existent) ; sans stubs
    # arcade.Camera2D est traité comme Any, donc strict = ok.
    return arcade.Camera2D()

@pytest.fixture
def dummy_player() -> Player:
    # Le constructeur Player exige pos_x / pos_y
    p = Player(pos_x=100, pos_y=200)
    p.update_hit_box()
    return p

# ---------------------------------------------------------------------------#
#  Sword                                                                     #
# ---------------------------------------------------------------------------#
def test_sword_angle_and_pivot(dummy_player: Player, camera: arcade.Camera2D) -> None:
    sword = Sword(dummy_player, camera)
    cursor = arcade.Vec2(400, 200)
    sword.on_mouse_motion(cursor.x, cursor.y, 0, 0)
    sword.update_angle(camera, dummy_player)

    expected = math.degrees(
        math.atan2(cursor.y - dummy_player.center_y, cursor.x - dummy_player.center_x)
    )
    assert abs(sword.angle - expected) < 1e-2

def test_sword_cooldown_logic(dummy_player: Player, camera: arcade.Camera2D) -> None:
    sword = Sword(dummy_player, camera)
    assert sword.ready()
    sword.reset_cooldown()
    sword.update_cooldown(0.05)
    assert not sword.ready()
    sword.update_cooldown(sword.COOLDOWN)
    assert sword.ready()

# ---------------------------------------------------------------------------#
#  Bow                                                                       #
# ---------------------------------------------------------------------------#
def test_bow_spawns_arrow(dummy_player: Player, camera: arcade.Camera2D) -> None:
    bow = Bow(dummy_player, camera)
    bow.on_mouse_press(500, 200, arcade.MOUSE_BUTTON_LEFT, 0)
    assert len(bow.arrows) == 1
    arrow = bow.arrows[0]
    vel_len = math.hypot(arrow._vel.x, arrow._vel.y)
    assert abs(vel_len - ARROW_SPEED) < 1e-3

def test_arrow_gravity_step(dummy_player: Player, camera: arcade.Camera2D) -> None:
    bow = Bow(dummy_player, camera)
    bow.on_mouse_press(500, 200, arcade.MOUSE_BUTTON_LEFT, 0)
    arrow = bow.arrows[0]
    vy0 = arrow._vel.y
    arrow.step(0.5, camera)
    assert abs(arrow._vel.y - (vy0 - ARROW_GRAVITY * 0.5)) < 1e-3

def test_bow_fire_rate(dummy_player: Player, camera: arcade.Camera2D) -> None:
    bow = Bow(dummy_player, camera)
    bow.on_mouse_press(500, 200, arcade.MOUSE_BUTTON_LEFT, 0)
    bow.on_mouse_press(500, 200, arcade.MOUSE_BUTTON_LEFT, 0)
    assert len(bow.arrows) == 1            # cooldown actif
    bow.updating(dummy_player, camera, ARROW_COOLDOWN)
    bow.on_mouse_press(500, 200, arcade.MOUSE_BUTTON_LEFT, 0)
    assert len(bow.arrows) == 2            # tir autorisé

def test_arrow_lifetime(dummy_player: Player, camera: arcade.Camera2D) -> None:
    bow = Bow(dummy_player, camera)
    bow.on_mouse_press(500, 200, arcade.MOUSE_BUTTON_LEFT, 0)
    arrow = bow.arrows[0]
    # 60 FPS * durée de vie → l’arrow devrait disparaître
    for _ in range(int(ARROW_LIFETIME * 60) + 1):
        arrow.step(1 / 60, camera)
    assert arrow not in bow.arrows
