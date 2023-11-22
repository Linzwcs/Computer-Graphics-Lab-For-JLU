from .abstract_shape import Shape, DEFAULT_COLOR, DEFAULT_FILLING_COLOR

# from canvas import Canvas
from .algorithms import bresenham, cubic_bezier


class Opened2DShape(Shape):
    pass


class StraightLine(Opened2DShape):
    def __init__(self, p1, p2, line_color=(255, 255, 255)):
        self.p1 = p1
        self.p2 = p2
        self.line_color = line_color
        self.canvas = None

    def draw(self):
        x1, y1 = self.p1
        x2, y2 = self.p2
        points = bresenham(x1, y1, x2, y2)
        # print(points)
        for p in points:
            self.canvas.set_pixel(p[0], p[1], self.line_color)

    def transform(self, transform2D):
        self.p1, self.p2 = transform2D([[*self.p1, 1], [*self.p2, 1]])

    def set_line_color(self, line_color):
        self.line_color = line_color


class CubicBezierCurve(Opened2DShape):
    def __init__(
        self,
        p0,
        p1,
        p2,
        p3,
        num_segments=100,
        line_color=DEFAULT_COLOR,
        show_auxiliary_line=False,
    ):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.line_color = line_color
        self.num_segments = num_segments
        self.canvas = None

    def draw(self):
        p0, p1, p2, p3 = self.p0, self.p1, self.p2, self.p3
        num_segments = self.num_segments
        for i in range(num_segments):
            t1 = i / num_segments
            t2 = (i + 1) / num_segments
            x1, y1 = cubic_bezier(t1, p0, p1, p2, p3)
            x2, y2 = cubic_bezier(t2, p0, p1, p2, p3)
            line = StraightLine(
                (x1, y1),
                (x2, y2),
                self.line_color,
            )
            line.set_canvas(self.canvas)
            line.draw()

    def transform(self, transform2d):
        ps = transform2d(
            [
                [*self.p0, 1],
                [*self.p1, 1],
                [*self.p2, 1],
                [*self.p3, 1],
            ]
        )
        self.p0, self.p1, self.p2, self.p3 = ps

    def set_line_color(self, line_color):
        self.line_color = line_color
