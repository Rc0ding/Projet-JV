"""FOR SIMPLER TEXTURE MANAGEMENT"""
from src.texture_manager import *

_SCALE_FACTOR = 0.5  # global constant for scaling textures

_SCALE_BATS = 1.25

TEXTURES = {
    "=": GROUND_TEXTURE,
    "-": HALF_GROUND_TEXTURE,
    "x": CRATE_TEXTURE,
    "*": COIN_TEXTURE ,
    "£": LAVA_TEXTURE,
    "E": PORTAL_TEXTURE
}