# tests/test_weapons.py
from __future__ import annotations

import math
import arcade  # type: ignore[misc]  # arcade n’a pas de stubs officiels
import pytest

from src.game.player import Player
from src.weapons.sword import Sword
from src.weapons.bow import (
    Bow,
    ARROW_SPEED,
    ARROW_GRAVITY,
    ARROW_COOLDOWN,
    ARROW_LIFETIME,
)

# ---------------------------------------------------------------------------
#  Helpers / fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def camera() -> arcade.Camera2D:
    """Caméra factice couvrant l’écran entier."""
    return arcade.Camera2D(viewport=(0, 0, 1280, 720))


@pytest.fixture
def dummy_player(camera: arcade.Camera2D) -> Player:
    """Joueur minimal à la bonne position pour les tests."""
    p = Player(pos_x=100, pos_y=200)
    p.update_hit_box()  # keep Arcade happy
    return p


# ---------------------------------------------------------------------------
#  Sword tests
# ---------------------------------------------------------------------------


def test_sword_angle_and_pivot(
    dummy_player: Player, camera: arcade.Camera2D
) -> None:
    sword = Sword(dummy_player, camera)
    sword.visible = True  # ready() tient compte de « visible »
    sword.update_angle(camera, dummy_player)
    sword.update_position(dummy_player, camera)

    # Simule un curseur en (400, 200)
    cursor = arcade.Vec2(400, 200)
    sword.on_mouse_motion(cursor.x, cursor.y, 0, 0)
    sword.update_angle(camera, dummy_player)

    expected = math.degrees(
        math.atan2(cursor.y - dummy_player.center_y, cursor.x - dummy_player.center_x)
    )
    assert abs(sword.angle - expected) < 0.01


def test_sword_cooldown_logic(
    dummy_player: Player, camera: arcade.Camera2D
) -> None:
    sword = Sword(dummy_player, camera)
    sword.visible = True
    assert sword.ready()
    sword.reset_cooldown()
    sword.update_cooldown(0.1)
    assert not sword.ready()
    sword.update_cooldown(sword.COOLDOWN)
    assert sword.ready()


# ---------------------------------------------------------------------------
#  Bow tests
# ---------------------------------------------------------------------------


def test_bow_spawns_arrow(
    dummy_player: Player, camera: arcade.Camera2D
) -> None:
    bow = Bow(dummy_player, camera)
    bow.on_mouse_press(500, 200, arcade.MOUSE_BUTTON_LEFT, 0)
    assert len(bow.arrows) == 1
    arrow = bow.arrows[0]
    vel_len = math.hypot(
        arrow._vel.x, arrow._vel.y  # type: ignore[attr-defined]
    )
    assert abs(vel_len - ARROW_SPEED) < 1e-3


def test_arrow_gravity_step(
    dummy_player: Player, camera: arcade.Camera2D
) -> None:
    bow = Bow(dummy_player, camera)
    bow.on_mouse_press(500, 200, arcade.MOUSE_BUTTON_LEFT, 0)
    arrow = bow.arrows[0]
    vy_initial = arrow._vel.y  # type: ignore[attr-defined]
    arrow.step(0.5, camera)
    expected_vy = vy_initial - ARROW_GRAVITY * 0.5
    assert abs(arrow._vel.y - expected_vy) < 1e-3  # type: ignore[attr-defined]


def test_bow_fire_rate(
    dummy_player: Player, camera: arcade.Camera2D
) -> None:
    bow = Bow(dummy_player, camera)

    # 1er tir
    bow.on_mouse_press(500, 200, arcade.MOUSE_BUTTON_LEFT, 0)
    # 2e tir immédiat : bloqué par le cooldown
    bow.on_mouse_press(500, 200, arcade.MOUSE_BUTTON_LEFT, 0)
    assert len(bow.arrows) == 1

    # Avance le temps d’un cooldown complet puis tire à nouveau
    bow.updating(dummy_player, camera, ARROW_COOLDOWN)
    bow.on_mouse_press(500, 200, arcade.MOUSE_BUTTON_LEFT, 0)
    assert len(bow.arrows) == 2


def test_arrow_lifetime(
    dummy_player: Player, camera: arcade.Camera2D
) -> None:
    """L’arrow doit avoir épuisé son timer de vie après ARROW_LIFETIME secondes."""
    bow = Bow(dummy_player, camera)
    bow.on_mouse_press(500, 200, arcade.MOUSE_BUTTON_LEFT, 0)
    arrow = bow.arrows[0]

    for _ in range(int(ARROW_LIFETIME * 60)):
        arrow.step(1 / 60, camera)

    assert arrow._life <= 0  # type: ignore[attr-defined]
    # Reste valable même si l’arrow a déjà été retirée de bow.arrows
    if arrow in bow.arrows:
        assert arrow._life <= 0
