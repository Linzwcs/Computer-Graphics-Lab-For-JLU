from abc import ABCMeta, abstractmethod
import numpy as np
from enum import Enum
from numpy import cos, sin


class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    FRONT = 4
    BACK = 5


class Transform(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, vertices):
        pass

    def __str__(self):
        return str(self.Matrix)


class Transform2D(Transform):
    def __init__(self, Matricx=None):
        self.Matricx = Matricx

    def __call__(self, vertices):
        vertices = np.array(vertices)
        transformed_vertices = vertices @ self.Matrix
        return transformed_vertices[:, :2].tolist()

    def __mul__(self, other):
        return Transform2D(self.Matrix @ other.Matrix)


class Transform2DTranslation(Transform2D):
    def __init__(self, direction, distance):
        """ """
        d = distance
        if direction == Direction.UP:
            self.Matrix = np.array(
                [
                    [1, 0, 0],
                    [0, 1, 0],
                    [0, -d, 1],
                ]
            )

        elif direction == Direction.RIGHT:
            self.Matrix = np.array(
                [
                    [1, 0, 0],
                    [0, 1, 0],
                    [d, 0, 1],
                ]
            )

        elif direction == Direction.DOWN:
            self.Matrix = np.array(
                [
                    [1, 0, 0],
                    [0, 1, 0],
                    [0, d, 1],
                ]
            )

        elif direction == Direction.LEFT:
            self.Matrix = np.array(
                [
                    [1, 0, 0],
                    [0, 1, 0],
                    [-d, 0, 1],
                ]
            )
        else:
            print("2D only support [ up, right, down,  left ] direction!")
            assert False


class Transform2DScale(Transform2D):
    def __init__(self, scale):
        """ """
        s = scale
        self.Matrix = np.array(
            [
                [s, 0, 0],
                [0, s, 0],
                [0, 0, 1],
            ]
        )


class Transform2DRotation(Transform2D):
    def __init__(self, theta):
        """ """
        c, s = cos(theta), sin(theta)
        self.Matrix = np.array(
            [
                [c, s, 0],
                [-s, c, 0],
                [0, 0, 1],
            ]
        )


class Transform3D(Transform):
    def __call__(self, vertices):
        pass
