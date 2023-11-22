import numpy as np
from .algorithm import model_transform_matrix, perspective_projection_matrix

"""

right-hand system

"""


class MVP:
    def __init__(
        self,
        position,
        up_direction,
        gaze_direction,
        fov=np.radians(45),
        aspect_ratio=16 / 9,
        near=-0.1,
        far=-100,
    ):
        self.M_view = model_transform_matrix(position, up_direction, gaze_direction)
        self.M_persp = perspective_projection_matrix(fov, aspect_ratio, near, far)

    def __call__(self, **post):
        post["M_view"] = self.M_view
        post["M_persp"] = self.M_persp

        return post
