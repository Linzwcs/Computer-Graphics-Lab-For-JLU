from abc import ABCMeta, abstractmethod
import numpy as np
from .algorithm import (
    perspective_correct_interpolation,
    normalize_vector,
    blinn_Phong_algorithm,
    calculate_distance,
)


class Lighting(metaclass=ABCMeta):
    def __init__(self, position, indensity):
        self.position = np.array([*position, 1])
        self.indensity = np.float64(indensity)
        print(self.position)

    @abstractmethod
    def __call__(self):
        pass


class BaseLighting(Lighting):
    def __init__(self, position=(0, 0, 0), indensity=0):
        super().__init__(position, indensity)

    def __call__(self, **post):
        post["lighting_texture_color"] = post[
            "vertex_texture_colors"
        ]  # assume no light render
        return post


class BlinnPhongLighting(Lighting):
    def __init__(
        self,
        position=(0, 0, 0),
        indensity=40,
        ks=(1, 1, 1),
        ka=(0.05, 0.05, 0.05),
        Ia=1,
        p=32,
    ):
        super().__init__(position, indensity)
        self.Ia = np.float64(Ia)
        self.ka = np.array(ka, dtype=np.float64)
        self.ks = np.array(ks, dtype=np.float64)
        self.p = p

    def __call__(self, **post):
        (
            width,
            height,
            vertexs,
            textures,
            triangles,
            M_view,
            pixel2triangle,
            # pixel2barycentric_coords,
            # pixel2Z_position,
            vertex_normal_vectors,
            vertex_texture_colors,
            pixel2texture_idx,
        ) = (
            post["width"],
            post["height"],
            post["vertexs"],
            post["textures"],
            post["triangles"],
            post["M_view"],
            post["pixel2triangle"],
            # post["pixel2barycentric_coords"],
            # post["pixel2Z_position"],
            post["vertex_normal_vectors"],
            post["vertex_texture_colors"],
            post["pixel2texture_idx"],
        )

        trans_light_position = M_view @ self.position
        trans_light_position = trans_light_position / trans_light_position[3]
        post["trans_light_position"] = trans_light_position

        assert len(vertexs) == len(vertex_normal_vectors)
        """
        define:
            L : direction of light
            V : direction of eyes
            H : Half vector of near normal
            vnv: vertex normal vector
            v: vertex position
            vt: vertex texture
        """

        Ls, Rs, Hs = [], [], []
        ks, ka, indensity, p, Ia = (self.ks, self.ka, self.indensity, self.p, self.Ia)

        for v in vertexs:
            L = normalize_vector(trans_light_position - v)
            R = calculate_distance(trans_light_position, v)
            V = normalize_vector(-v)
            H = normalize_vector((L + V))
            Ls += [L]
            Rs += [R]
            Hs += [H]

        lighting_texture_color = np.zeros((len(textures), 3))

        for x in range(width):
            for y in range(height):
                if pixel2triangle[x, y] != -1:
                    triangle = triangles[pixel2triangle[x, y]]
                    texture_idxs = pixel2texture_idx[x, y]
                    for tri_idx, tex_idx in zip(triangle, texture_idxs):
                        vnv = vertex_normal_vectors[tri_idx]
                        tex = vertex_texture_colors[tex_idx]

                        I = blinn_Phong_algorithm(
                            indensity,
                            Ls[tri_idx],
                            Rs[tri_idx],
                            vnv,
                            Hs[tri_idx],
                            p,
                            tex,
                            ks,
                            ka,
                            Ia,
                        )

                        lighting_texture_color[tex_idx, :] = I
        post["lighting_texture_color"] = lighting_texture_color
        # image = np.zeros((width, height, 3))
        # for x in range(width):
        #    for y in range(height):
        #        if pixel2triangle[x, y] != -1:
        #            triangle = triangles[pixel2triangle[x, y]]
        #            texture_idx = pixel2texture_idx[x, y]

        #            I0, I1, I2 = lighting_texture_color[texture_idx]
        # print(x, y, I0, I1, I2)
        #            v0, v1, v2 = vertexs[triangle]
        #            barycentric_coords = pixel2barycentric_coords[x, y]
        #            z0_persp, z1_persp, z2_persp = pixel2Z_position[x, y]

        #           color = perspective_correct_interpolation(
        #                barycentric_coords, I0, I1, I2, z0_persp, z1_persp, z2_persp
        #            )
        #           image[x, y, :] = color * 255
        # post["image"] = np.uint8(np.clip(image, 0, 255))
        return post
