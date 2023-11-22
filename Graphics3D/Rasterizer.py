import numpy as np
from tqdm import tqdm
from .algorithm import barycentric_coordinates, perspective_correct_interpolation

RASTERIZE_COLOR = 1
Z_DEEPEST = -1.1


class Rasterizer:
    def __call__(self, **post):
        (
            width,
            height,
            vertexs,
            triangles,
            face_texture_idxs,
        ) = (
            post["width"],
            post["height"],
            post["vertexs_persp"],
            post["triangles"],
            post["face_texture_idxs"],
        )

        orthe_to_screen_projection_matrix = np.array(
            [
                [width / 2, 0, 0, width / 2],
                [0, height / 2, 0, height / 2],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        )

        z_buffer = np.full((width, height), Z_DEEPEST)
        pixel2triangle = np.zeros((width, height), dtype=np.int32)
        pixel2triangle.fill(-1)
        pixel2barycentric_coords = np.zeros((width, height, 3))
        pixel2Z_position = np.zeros((width, height, 3))
        pixel2texture_idx = np.zeros((width, height, 3), dtype=np.int32)
        idx_with_trangles = list(enumerate(triangles))

        for idx, triangle in tqdm(idx_with_trangles, desc="rasterize"):
            triangle_matrix = vertexs[triangle]

            screen_triangle_matirx = (
                orthe_to_screen_projection_matrix @ triangle_matrix.T
            ).T
            screen_triangle_matirx = screen_triangle_matirx / np.expand_dims(
                screen_triangle_matirx[:, 3], axis=1
            )

            t0, t1, t2 = screen_triangle_matirx
            x0, y0, z0 = t0[:3]
            x1, y1, z1 = t1[:3]
            x2, y2, z2 = t2[:3]

            min_x, max_x = int(max(0, min(x0, x1, x2))), int(
                min(width - 1, max(x0, x1, x2))
            )
            min_y, max_y = int(max(0, min(y0, y1, y2))), int(
                min(height - 1, max(y0, y1, y2))
            )

            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    barycentric_coords = barycentric_coordinates(
                        x + 0.5, y + 0.5, t0, t1, t2
                    )
                    if all(0 <= coord <= 1 for coord in barycentric_coords):
                        depth = perspective_correct_interpolation(
                            barycentric_coords, z0, z1, z2, z0, z1, z2
                        )
                        if depth > z_buffer[x, y]:
                            z_buffer[x, y] = depth
                            pixel2triangle[x, y] = idx
                            pixel2barycentric_coords[x, y] = list(barycentric_coords)
                            pixel2Z_position[x, y] = [z0, z1, z2]
                            pixel2texture_idx[x, y, :] = face_texture_idxs[idx]

        post["pixel2triangle"] = pixel2triangle
        post["pixel2barycentric_coords"] = pixel2barycentric_coords
        post["pixel2Z_position"] = pixel2Z_position
        post["pixel2texture_idx"] = pixel2texture_idx
        return post
