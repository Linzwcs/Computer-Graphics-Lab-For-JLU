import numpy as np


def model_transform_matrix(
    position,
    up_direction,
    gaze_direction,
):
    e, t, g = position, up_direction, gaze_direction
    T_view = np.array(
        [
            [1, 0, 0, -e[0]],
            [0, 1, 0, -e[1]],
            [0, 0, 1, -e[2]],
            [0, 0, 0, 1],
        ]
    )
    v = np.cross(g[:3], t[:3])

    v = v / np.linalg.norm(v)
    R_view = np.array(
        [
            [v[0], v[1], v[2], 0],
            [t[0], t[1], t[2], 0],
            [-g[0], -g[1], -g[2], 0],
            [0, 0, 0, 1],
        ]
    )

    return R_view @ T_view


def perspective_projection_matrix(
    fov,
    aspect_ratio,
    near,
    far,
):
    n, f = abs(near), abs(far)
    M_persp2ortho = np.array(
        [
            [near, 0, 0, 0],
            [0, near, 0, 0],
            [0, 0, near + far, -near * far],
            [0, 0, 1, 0],
        ]
    )
    h = np.tan(fov / 2) * n * 2
    w = aspect_ratio * h
    M_ortho = np.array(
        [
            [2 / w, 0, 0, 0],
            [0, 2 / h, 0, 0],
            [0, 0, 2 / (f - n), 0],
            [0, 0, 0, 1],
        ]
    ) @ np.array(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, -(near + far) / 2],
            [0, 0, 0, 1],
        ]
    )

    return M_ortho @ M_persp2ortho


def barycentric_coordinates(x, y, v0, v1, v2):
    detT = abs((v1[1] - v2[1]) * (v0[0] - v2[0]) - (v1[0] - v2[0]) * (v0[1] - v2[1]))

    alpha = ((v1[1] - v2[1]) * (x - v2[0]) - (v1[0] - v2[0]) * (y - v2[1])) / detT
    beta = ((v2[1] - v0[1]) * (x - v2[0]) - (v2[0] - v0[0]) * (y - v2[1])) / detT

    gamma = 1 - alpha - beta
    # print(alpha, beta, gamma)
    return alpha, beta, gamma


def perspective_correct_interpolation(barycentric_coords, I0, I1, I2, z0, z1, z2):
    alpha, beta, gamma = barycentric_coords
    z_interpolation = 1 / (alpha / z0 + beta / z1 + gamma / z2)
    I_interpolation = (
        alpha * I0 / z0 + beta * I1 / z1 + gamma * I2 / z2
    ) * z_interpolation
    return I_interpolation


def normalize_vector(vector):
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


def calculate_distance(v1, v2):
    return np.linalg.norm(v1 - v2)


def blinn_Phong_algorithm(I, l, r, n, h, p, kd, ks, ka, Ia):
    # print(n, l, h)
    Ld = kd * (I / (r * r) * max(0.0, np.dot(n, l)))
    Ls = ks * (I / (r * r) * (max(0.0, np.dot(n, h)) ** p))
    La = ka * Ia
    # print(Ld, Ls, La)
    return Ld + Ls + La
