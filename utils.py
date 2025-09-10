import numpy as np

class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def bgr(self):
        return np.array([int(self.b), int(self.g), int(self.r)], dtype=np.uint8)

    def rgb(self):
        return np.array([int(self.r), int(self.g), int(self.b)], dtype=np.uint8)

    def __eq__(self, other):
        if isinstance(other, Color):
            return self.r == other.r and self.g == other.g and self.b == other.b
        return False

class PixelNode:
    def __init__(self, color: Color, xy: list[Point]):
        self.color = color
        self.xy = xy

class ColorPixel:
    def __init__(self, color: Color, point: Point, width: int = 0, height: int = 0):
        self.color = color
        self.point = point
        self.width = width
        self.height = height


class Area:
    def __init__(self, width, height, left_x, left_y):
        self.width = width
        self.height = height
        self.left_x = left_x
        self.left_y = left_y

    def is_entry(self, x, y) -> bool:
        return (self.left_x <= x <= self.left_x + self.width) and \
            (self.left_y <= y <= self.left_y + self.height)