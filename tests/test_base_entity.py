import unittest
from unittest.mock import MagicMock, patch
import arcade


from src.entities.base_entity import Enemy, SCALE

# A concrete implementation of Enemy for testing purposes
class ConcreteEnemy(Enemy):
    TEXTURE = ":resources:/images/enemies/slimeBlue.png"

    def __init__(self, pos_px: tuple[float, float], speed: int) -> None:
        super().__init__(pos_px, speed)
        self.step_called = False
        self.step_delta = 0.0

    def step(self, delta: float) -> None:
        self.step_called = True
        self.step_delta = delta

class TestEnemy(unittest.TestCase):

    def setUp(self)->None:
        # Patch arcade.load_texture to avoid file loading issues in tests
        self.load_texture_patch = patch('arcade.load_texture')
        self.mock_load_texture = self.load_texture_patch.start()
        self.mock_texture = MagicMock(spec=arcade.Texture)
        self.mock_texture.width = 64
        self.mock_texture.height = 64
        self.mock_load_texture.return_value = self.mock_texture

        self.initial_pos = (100.0, 150.0)
        self.speed = 5
        self.enemy = ConcreteEnemy(self.initial_pos, self.speed)

    def tearDown(self)->None:
        self.load_texture_patch.stop()

    def test_enemy_initialization(self)->None:
        self.assertEqual(self.enemy.center_x, self.initial_pos[0])
        self.assertEqual(self.enemy.center_y, self.initial_pos[1])
        self.assertEqual(getattr(self.enemy, '_speed'), self.speed)
        self.assertEqual(getattr(self.enemy, '_direction'), 1)
        self.assertEqual(getattr(self.enemy, '_base_y'), self.initial_pos[1])
        self.assertIsNone(getattr(self.enemy, '_walls'))
        # Check if super().__init__ was called with texture and scale by ensuring load_texture was called with TEXTURE
        self.mock_load_texture.assert_called_with(ConcreteEnemy.TEXTURE)
        self.assertEqual(self.enemy.scale, SCALE)


    def test_reversy(self)->None:
        initial_direction = getattr(self.enemy, '_direction')
        initial_scale_x = self.enemy.scale_x

        self.enemy.reversy()
        self.assertEqual(getattr(self.enemy, '_direction'), -initial_direction)
        self.assertEqual(self.enemy.scale_x, -initial_scale_x)

        self.enemy.reversy()
        self.assertEqual(getattr(self.enemy, '_direction'), initial_direction)
        self.assertEqual(self.enemy.scale_x, initial_scale_x)

    def test_set_environment(self)->None:
        mock_walls = MagicMock(spec=arcade.SpriteList)
        self.enemy.set_environment(mock_walls)
        self.assertEqual(getattr(self.enemy, '_walls'), mock_walls)
    def test_update_calls_step(self)->None:
        mock_walls = MagicMock(spec=arcade.SpriteList)
        self.enemy.set_environment(mock_walls)
        delta_time = 0.1

        self.enemy.update(delta_time)

        self.assertTrue(self.enemy.step_called)

        self.assertEqual(self.enemy.step_delta, delta_time)
    """
    def test_update_raises_assertion_error_if_walls_not_set(self)->None:
        self.enemy.set_environment(cast(arcade.SpriteList, None))  # Ensure walls are None using public method
        with self.assertRaisesRegex(AssertionError, "Walls not injected!"):
            self.enemy.update(0.1)
            self.enemy.update(0.1)
    """
    def test_post_step(self)->None:
        # Test that post_step can be called without errors
        try:
            self.enemy.post_step()
        except Exception as e:
            self.fail(f"post_step raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()