import numpy as np
from abc import ABCMeta, abstractmethod
from PIL import Image


class TextureProcess(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, **post):
        pass


class TextureDefaultProcess(TextureProcess):
    def __call__(self, **post):
        # texture_image = np.zeros((post["width"], post["height"], 3), dtype=np.uint8)
        vertex_texture_colors = np.ones((len(post["textures"]), 3))

        # vertex_texture_colors.fill(255)
        # vertex_texture_colors /= 255
        # texture_image.fill(255)
        # post["texture_image"] = texture_image
        post["vertex_texture_colors"] = vertex_texture_colors
        return post


class TextureRandomColorProcess(TextureProcess):
    def __call__(self, **post):
        # triangles = post["triangles"]
        vertex_texture_colors = (
            np.random.rand(len(post["textures"]), 3) * 128 + 125
        ) / 255
        # texture_image = np.zeros((width, height, 3), dtype=np.uint8)
        # for x in range(width):
        #    for y in range(height):
        #        if pixel2triangle[x, y] != -1:
        #            # @print(pixel2triangle[x, y])
        #            texture_image[x, y, :] = colors[pixel2triangle[x, y]]
        post["vertex_texture_colors"] = vertex_texture_colors
        return post


class TextureImageProcess(TextureProcess):
    def __init__(self, texture_path):
        image = Image.open(texture_path)
        self.texture_map = np.array(image).transpose((1, 0, 2))
        self.width, self.height, _ = self.texture_map.shape

    def __call__(self, **post):
        (
            texture_width,
            texture_height,
            textures,
        ) = (
            self.width,
            self.height,
            post["textures"],
        )
        textures[:, 1] = 1 - textures[:, 1]
        post["textures"] = textures
        vertex_texture_colors = np.zeros((len(post["textures"]), 3))
        for i, t in enumerate(textures):
            tx, ty = min(int(t[0] * texture_width), texture_width - 1), min(
                int(t[1] * texture_height), texture_height - 1
            )
            vertex_texture_colors[i, :] = self.texture_map[tx, ty]

        post["vertex_texture_colors"] = vertex_texture_colors / 255
        return post
