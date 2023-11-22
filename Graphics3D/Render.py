import numpy as np
from .algorithm import perspective_correct_interpolation
from abc import ABCMeta, abstractmethod
import random


class Render(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, **post):
        pass


class DefaultRender(Render):
    def __call__(self, **post):
        (
            width,
            height,
            pixel2triangle,
            pixel2Z_position,
            pixel2texture_idx,
            lighting_texture_color,
        ) = (
            post["width"],
            post["height"],
            post["pixel2triangle"],
            post["pixel2Z_position"],
            post["pixel2texture_idx"],
            post["lighting_texture_color"],
        )
        image = np.zeros((width, height, 3))
        for x in range(width):
            for y in range(height):
                if pixel2triangle[x, y] != -1:
                    texture_idx = pixel2texture_idx[x, y]
                    I0, I1, I2 = lighting_texture_color[texture_idx]
                    z0_persp, z1_persp, z2_persp = pixel2Z_position[x, y]
                    color = I0
                    image[x, y, :] = color * 255

        post["image"] = np.uint8(np.clip(image, 0, 255))
        return post


class BlinnPhongRender(Render):
    def __call__(self, **post):
        (
            width,
            height,
            # vertexs,
            # triangles,
            pixel2triangle,
            pixel2barycentric_coords,
            pixel2Z_position,
            pixel2texture_idx,
            lighting_texture_color,
        ) = (
            post["width"],
            post["height"],
            # post["vertexs"],
            # post["triangles"],
            post["pixel2triangle"],
            post["pixel2barycentric_coords"],
            post["pixel2Z_position"],
            post["pixel2texture_idx"],
            post["lighting_texture_color"],
        )
        image = np.zeros((width, height, 3))
        for x in range(width):
            for y in range(height):
                if pixel2triangle[x, y] != -1:
                    # triangle = triangles[pixel2triangle[x, y]]
                    texture_idx = pixel2texture_idx[x, y]
                    I0, I1, I2 = lighting_texture_color[texture_idx]
                    # print(x, y, I0, I1, I2)
                    # v0, v1, v2 = vertexs[triangle]
                    barycentric_coords = pixel2barycentric_coords[x, y]
                    z0_persp, z1_persp, z2_persp = pixel2Z_position[x, y]
                    color = perspective_correct_interpolation(
                        barycentric_coords, I0, I1, I2, z0_persp, z1_persp, z2_persp
                    )
                    image[x, y, :] = color * 255

        post["image"] = np.uint8(np.clip(image, 0, 255))
        return post
