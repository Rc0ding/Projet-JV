import arcade
from typing import Tuple


class Platform(arcade.Sprite):
    """One tile that belongs to a larger coherent block."""
    SPEED_PX_PER_FRAME = 1 #  global constant

    def __init__(self, texture:str,start_pos:Tuple[float,float],axis:str,direction:bool,
                 boundary_a:float, boundary_b:float)-> None:
        super().__init__(texture, scale=0.5,
                         center_x=start_pos[0], center_y=start_pos[1])
        self.axis = axis              # "x" or "y"
        self.direction = direction        # True = +dir, False = −dir
        self.boundary_left = boundary_a  # world coords  (min on that axis)
        self.boundary_right = boundary_b  # world coords  (max on that axis)
        if self.axis == "x":
            self.change_x = self.SPEED_PX_PER_FRAME if direction else -self.SPEED_PX_PER_FRAME
        elif self.axis == "y":
            self.change_y = self.SPEED_PX_PER_FRAME if direction else -self.SPEED_PX_PER_FRAME
        else: raise ValueError("Axis must be 'x' or 'y'.")

        
    def get_speed(self) -> float:
        return self.SPEED_PX_PER_FRAME if self.direction else -self.SPEED_PX_PER_FRAME
    

