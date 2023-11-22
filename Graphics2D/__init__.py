from .opened_shape import StraightLine, CubicBezierCurve
from .closed_shape import Polygon2D, Rectangle2D, Circle2D  # , ObjectShape3D
import numpy as np


class Canvas2D:
    def __init__(
        self,
        width,
        height,
    ):
        self.pixmap = np.zeros((height, width, 3), dtype=np.uint8)
        self.width = width
        self.height = height
        self.shapes = []
        # self.widget = QPixmap(width, height)
        # self.painter = QPainter(self.widget)

    def show(self, filling_color=None):
        self.clear_pixmap()
        for shape in self.shapes:
            shape.draw()
            if filling_color is not None and hasattr(shape, "filling"):
                shape.filling(filling_color)

        return self.pixmap

    def add_shape(self, shape):
        shape.set_canvas(self)
        self.shapes += [shape]

    def transform(self, transform2d):
        for shape in self.shapes:
            shape.transform(transform2d)

    def set_pixel(self, x, y, color):
        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            self.pixmap[y, x] = color
            return True
        else:
            return False

    def clear_pixmap(self):
        self.pixmap.fill(0)

    def unmount_shapes(self):
        for shape in self.shapes:
            shape.unmount()
        self.shapes = []

    def get_pixmap(self):
        return self.pixmap
