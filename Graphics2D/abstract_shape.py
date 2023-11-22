from abc import ABCMeta, abstractmethod

DEFAULT_COLOR = (255, 255, 255)
DEFAULT_FILLING_COLOR = (255, 0, 0)


class Shape(metaclass=ABCMeta):
    def __init__(self):
        self.canvas = None

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def transform(self, transformXD):
        pass

    @abstractmethod
    def set_line_color(self):
        pass

    def set_canvas(self, canvas):
        self.canvas = canvas

    def unmount(self):
        self.canvas = None
