from .abstract_shape import Shape, DEFAULT_COLOR, DEFAULT_FILLING_COLOR
from .opened_shape import StraightLine
from abc import ABCMeta, abstractmethod
from .algorithms import bresenham_circle, line_sweep_filling, circle_filling
import numpy as np


class Closed2DShape(Shape):
    @abstractmethod
    def filling(self):
        pass

    @abstractmethod
    def transform(self, transform2d):
        pass

    def set_line_color(self, color):
        self.line_color = color


# class Closed3DShape(Shape):
#    @abstractmethod
#    def filling(self):
#        pass
#
#    @abstractmethod
#    def transform(self, transform2d):
#        pass
#
#    def set_line_color(self, color):
#        self.line_color = color


class Triangle2D(Closed2DShape):
    def __init__(self, p1, p2, p3, line_color=DEFAULT_COLOR):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.line_color = line_color
        self.vertices = [self.p1, self.p2, self.p3]

    def draw(self):
        assert self.canvas is not None
        anchor_points = [self.p1, self.p2, self.p3]
        for i in range(len(anchor_points)):
            line = StraightLine(
                anchor_points[i],
                anchor_points[(i + 1) % len(anchor_points)],
                self.line_color,
            )
            line.set_canvas(self.canvas)
            line.draw()

    def filling(self, color=DEFAULT_FILLING_COLOR):
        pixels = line_sweep_filling([self.p1, self.p2, self.p3])
        for p in pixels:
            self.canvas.set_pixel(p[0], p[1], color)

    def transform(self, transform2d):
        self.vertices = transform2d([[*v, 1] for v in self.vertices])


class Rectangle2D(Closed2DShape):
    def __init__(self, p1, p2, line_color=DEFAULT_COLOR):
        p11 = p1
        p22 = p2
        p12 = (p2[0], p1[1])
        p21 = (p1[0], p2[1])
        self.vertices = [p11, p12, p22, p21]
        self.line_color = line_color

    def draw(self):
        assert self.canvas is not None
        anchor_points = self.vertices
        for i in range(len(anchor_points)):
            line = StraightLine(
                anchor_points[i],
                anchor_points[(i + 1) % len(anchor_points)],
                self.line_color,
            )
            line.set_canvas(self.canvas)
            line.draw()

    def filling(self, color=DEFAULT_FILLING_COLOR):
        pixels = line_sweep_filling([(int(_[0]), int(_[1])) for _ in self.vertices])
        for p in pixels:
            self.canvas.set_pixel(p[0], p[1], color)

    def transform(self, transform2d):
        self.vertices = transform2d([[*v, 1] for v in self.vertices])


class Polygon2D(Closed2DShape):
    def __init__(self, vertices: list, line_color=DEFAULT_COLOR):
        self.vertices = vertices
        self.line_color = line_color

    def draw(self):
        assert self.canvas is not None
        anchor_points = self.vertices + self.vertices[:1]
        for i in range(len(anchor_points) - 1):
            line = StraightLine(
                anchor_points[i],
                anchor_points[i + 1],
                self.line_color,
            )
            line.set_canvas(self.canvas)
            line.draw()

    def transform(self, transform2d):
        self.vertices = transform2d([[*v, 1] for v in self.vertices])

    def filling(self, color=DEFAULT_FILLING_COLOR):
        pixels = line_sweep_filling(self.vertices)
        for p in pixels:
            self.canvas.set_pixel(p[0], p[1], color)


class Circle2D(Closed2DShape):
    def __init__(self, c, r, line_color=DEFAULT_COLOR):
        self.c = c  # center of circle
        self.r = r  # radius
        self.line_color = line_color
        self.border_points = None

    def draw(self):
        assert self.canvas is not None
        if self.border_points is None:
            self.__update_border_points()
        for p in self.border_points:
            # print(p)
            self.canvas.set_pixel(p[0], p[1], self.line_color)

    def transform(self, transform2d):
        if self.border_points is None:
            self.__update_border_points()
        points = transform2d([[*self.c, 1], [self.r, 0, 0]])
        self.c = points[0][:2]
        self.r = np.linalg.norm(points[1][:2])
        self.__update_border_points()

    def __update_border_points(self):
        self.border_points = bresenham_circle(
            int(self.c[0]), int(self.c[1]), int(self.r)
        )

    def filling(self, color=DEFAULT_FILLING_COLOR):
        if self.border_points is None:
            self.__update_border_points()
        # print(None)
        c = [int(self.c[0]), int(self.c[1])]
        pixels = circle_filling(self.border_points, c)
        for p in pixels:
            self.canvas.set_pixel(p[0], p[1], color)


# class ObjectShape3D(Closed3DShape):
#    def __init__(self, vertices, triangles, colors, line_color=DEFAULT_COLOR):
#        """
#        p1: 4 dims vector
#        """
#        self.vertices = np.array([[*v, 1] for v in vertices])
#        self.triangles = np.array(triangles)
#        self.colors = np.array(colors)
#
#    def draw(self):
#        projection_matrix = self.canvas.get_projection_matrix()
#
#        self.vertices = (projection_matrix @ self.vertices.T).T
#        # print(self.vertices)
#        self.vertices = self.vertices / np.expand_dims(self.vertices[:, 3], axis=1)
#        # print(self.vertices)
#        image = z_buffer(self.vertices, self.triangles, self.colors)
#
#        print(image.sum())
#        self.canvas.set_pixelmap(image)
#
#    def filling(self):
#        pass
#
#    def transform(self):
#        pass
#
#    def set_canvas(self, canvas):
#        self.canvas = canvas
#        self.vertices = (canvas.get_M_view() @ self.vertices.T).T
