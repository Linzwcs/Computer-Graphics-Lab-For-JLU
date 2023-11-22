from .config import WATERMARK, CANVAS_WIDTH, CANVAS_HEIGHT
import numpy as np
from abc import ABCMeta, abstractmethod

# from config import CANVAS_WIDTH, CANVAS_HEIGHT
from tqdm import tqdm


def bresenham(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    steep = dy > dx
    if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    error = dx / 2
    ystep = 1 if y1 < y2 else -1
    y = y1

    points = []
    for i in range(int(dx) + 1):
        if steep:
            points.append((int(y), int(x1 + i)))
        else:
            points.append((int(x1 + i), int(y)))
        error -= dy
        if error < 0:
            y += ystep
            error += dx
    # print(points)
    return points


def cubic_bezier(t, p0, p1, p2, p3):
    x = (
        (1 - t) ** 3 * p0[0]
        + 3 * (1 - t) ** 2 * t * p1[0]
        + 3 * (1 - t) * t**2 * p2[0]
        + t**3 * p3[0]
    )
    y = (
        (1 - t) ** 3 * p0[1]
        + 3 * (1 - t) ** 2 * t * p1[1]
        + 3 * (1 - t) * t**2 * p2[1]
        + t**3 * p3[1]
    )
    return int(x), int(y)


def bresenham_circle(center_x, center_y, radius):
    """ """
    x = 0
    y = radius
    p = 3 - 2 * radius

    points = []

    while x <= y:
        points.append((int(center_x + x), int(center_y + y)))
        points.append((int(center_x - x), int(center_y + y)))
        points.append((int(center_x + x), int(center_y - y)))
        points.append((int(center_x - x), int(center_y - y)))
        points.append((int(center_x + y), int(center_y + x)))
        points.append((int(center_x - y), int(center_y + x)))
        points.append((int(center_x + y), int(center_y - x)))
        points.append((int(center_x - y), int(center_y - x)))

        if p < 0:
            p += 4 * x + 6
        else:
            p += 4 * (x - y) + 10
            y -= 1
        x += 1
    return points


class WatermarkDirector:
    def __init__(self, watermark_func):
        graphics = np.ones((CANVAS_HEIGHT, CANVAS_WIDTH, 3))
        height, width, channel = WATERMARK.shape
        H, W, C = graphics.shape
        for h_start in range(0, H, height):
            for w_start in range(0, W, width):
                h_end, w_end = min(h_start + height, H), min(w_start + width, W)
                trunc_h, trunc_w = (h_end - h_start), (w_end - w_start)
                graphics[h_start:h_end, w_start:w_end, :] *= WATERMARK[
                    :trunc_h, :trunc_w, :
                ]
        # @graphics:np.ndarray
        graphics = graphics.mean(axis=-1, dtype=np.int8)
        self.graphics = graphics
        self.watermark_func = watermark_func

    def in_graphics(self, x, y):
        H, W = self.graphics.shape
        if x >= 0 and x < W and y >= 0 and y < H:
            return True
        else:
            return False

    def __call__(self, *args, **kwargs):
        points = self.watermark_func(*args, **kwargs)
        points = [p for p in points if self.in_graphics(p[0], p[1])]
        return [p for p in points if self.graphics[p[1], p[0]] > 0]


@WatermarkDirector
def line_sweep_filling(vertices):
    class Edge:
        def __init__(self, ymin, ymax, x, inverse_slope):
            self.ymin = ymin
            self.ymax = ymax
            self.x = x
            self.inverse_slope = inverse_slope

    def add_edge_to_edge_table(edge_table, edge):
        if edge.ymin in edge_table:
            edge_table[edge.ymin].append(edge)
        else:
            edge_table[edge.ymin] = [edge]

    def initialize_edge_table(vertices):
        edge_table = {}
        num_vertices = len(vertices)
        for i in range(num_vertices):
            current_vertex = vertices[i]
            next_vertex = vertices[(i + 1) % num_vertices]

            if current_vertex[1] != next_vertex[1]:  # Skip horizontal edges
                if current_vertex[1] > next_vertex[1]:
                    current_vertex, next_vertex = next_vertex, current_vertex

                ymin = current_vertex[1]
                ymax = next_vertex[1]
                x = current_vertex[0]
                inverse_slope = (next_vertex[0] - current_vertex[0]) / (
                    next_vertex[1] - current_vertex[1]
                )
                edge = Edge(ymin, ymax, x, inverse_slope)
                add_edge_to_edge_table(edge_table, edge)
        return edge_table

    edge_table = initialize_edge_table(vertices)
    active_edges = []
    y = min(edge_table.keys())
    pixels = []

    while edge_table or active_edges:
        if y in edge_table:
            active_edges.extend(edge_table.pop(y))

        active_edges.sort(key=lambda edge: edge.x)

        for i in range(0, len(active_edges), 2):
            x_start = int(active_edges[i].x)
            x_end = int(active_edges[i + 1].x)
            pixels += [(x, y) for x in range(x_start, x_end + 1)]
        y += 1
        active_edges = [edge for edge in active_edges if edge.ymax != y]
        for edge in active_edges:
            edge.x += edge.inverse_slope

    return pixels


@WatermarkDirector
def circle_filling(vertices, c):
    dx, dy = [1, 0, -1, 0], [0, -1, 0, 1]
    vertices = set(vertices)
    candidate_queue = [c]
    visited = set()
    while len(candidate_queue):
        p = candidate_queue.pop()
        # print(p)
        visited.add(tuple(p))
        for i in range(4):
            px, py = p
            new_px, new_py = int(px + dx[i]), int(py + dy[i])
            if ((new_px, new_py) in visited) or ((new_px, new_py) in vertices):
                continue
            else:
                candidate_queue.append((new_px, new_py))
                visited.add((new_px, new_py))
    return list(visited)


# Z_DEEPEST = -1.1
#
#
# def z_buffer(vertices, triangles, colors, MSAA=2):
#    width, height = CANVAS_WIDTH, CANVAS_HEIGHT
#
#    orthe_to_screen_projection_matrix = np.array(
#        [
#            [width / 2, 0, 0, width / 2],
#            [0, height / 2, 0, height / 2],
#            [0, 0, 1, 0],
#            [0, 0, 0, 1],
#        ]
#    )
#
#    z_buffer = np.full((width, height), Z_DEEPEST)
#    image = np.zeros((width, height, 3), dtype=np.uint8)
#    package = list(zip(triangles, colors))
#    for triangle, color in tqdm(package):
#        triangle_matrix = vertices[triangle]
#
#        screen_triangle_matirx = (
#            orthe_to_screen_projection_matrix @ triangle_matrix.T
#        ).T
#
#        screen_triangle_matirx = screen_triangle_matirx / np.expand_dims(
#            screen_triangle_matirx[:, 3], axis=1
#        )
#
#        t0, t1, t2 = screen_triangle_matirx
#        x0, y0, z0 = t0[:3]
#        x1, y1, z1 = t1[:3]
#        x2, y2, z2 = t2[:3]
#
#        min_x, max_x = int(max(0, min(x0, x1, x2))), int(
#            min(width - 1, max(x0, x1, x2))
#        )
#        min_y, max_y = int(max(0, min(y0, y1, y2))), int(
#            min(height - 1, max(y0, y1, y2))
#        )
#        for x in range(min_x, max_x + 1):
#            for y in range(min_y, max_y + 1):
#                if MSAA is None:
#                    barycentric_coords = barycentric_coordinates(
#                        x + 0.5, y + 0.5, t0, t1, t2
#                    )
#                    if all(0 <= coord <= 1 for coord in barycentric_coords):
#                        depth = interpolate_depth(barycentric_coords, z0, z1, z2)
#                        if depth > z_buffer[x, y]:
#                            z_buffer[x, y] = depth
#                            image[x, y] = color
#                else:
#                    assert type(MSAA) is int
#                    msaa_z, msaa_delta, filling_points = Z_DEEPEST, 1 / MSAA, 0
#                    for i in range(MSAA):
#                        for j in range(MSAA):
#                            msaa_x = x + (2 * i + 1) * msaa_delta / 2
#                            msaa_y = y + (2 * j + 1) * msaa_delta / 2
#                            barycentric_coords = barycentric_coordinates(
#                                msaa_x, msaa_y, t0, t1, t2
#                            )
#                            if all(0 <= coord <= 1 for coord in barycentric_coords):
#                                depth = interpolate_depth(
#                                    barycentric_coords, z0, z1, z2
#                                )
#                                msaa_z = max(depth, msaa_z)
#                                filling_points += 1
#                    if msaa_z > z_buffer[x, y]:
#                        z_buffer[x, y] = msaa_z
#                        image[x, y] = color * (filling_points / (MSAA**2))
#
#    return image.transpose((1, 0, 2))
#
#
# def barycentric_coordinates(x, y, v0, v1, v2):
#    detT = abs((v1[1] - v2[1]) * (v0[0] - v2[0]) - (v1[0] - v2[0]) * (v0[1] - v2[1]))
#
#    alpha = ((v1[1] - v2[1]) * (x - v2[0]) - (v1[0] - v2[0]) * (y - v2[1])) / detT
#    beta = ((v2[1] - v0[1]) * (x - v2[0]) - (v2[0] - v0[0]) * (y - v2[1])) / detT
#
#    gamma = 1 - alpha - beta
#    # print(alpha, beta, gamma)
#    return alpha, beta, gamma
#
#
# def interpolate_depth(barycentric_coords, z0, z1, z2):
#    alpha, beta, gamma = barycentric_coords
#    return alpha * z0 + beta * z1 + gamma * z2
