import time

import numpy
import cv2 as cv
import numpy as np
from PIL import ImageGrab

from main import MASK, RESULT_PATH, DETECTED_RECTS
from painter import Painter
from utils import Color, PixelNode, Point


def save_image(path, img):
    cv.imwrite(str(path), img)

def _is_square_fit(area, avg_area, rects_areas) -> bool:
    return min(rects_areas) <= area <= avg_area

class PixelParser:

    def __init__(self, img):
        self.img = img

    def nodes_for_colors(self, colors: list[Color]) -> list[PixelNode]:
        res: list[PixelNode] = []

        for _color in colors:
            points = self.points_for_color(_color)
            res.append(PixelNode(_color, points))

        return res

    def points_for_color(self, _color: Color, tolerance = 15) -> list[Point]:
        res: list[Point] = []

        dst = cv.cvtColor(self.img, cv.COLOR_RGB2BGR)

        lower = numpy.array([
            max(0, _color.b - tolerance),
            max(0, _color.g - tolerance),
            max(0, _color.r - tolerance)
        ])
        upper = numpy.array([
            min(255, _color.b + tolerance),
            min(255, _color.g + tolerance),
            min(255, _color.r + tolerance)
        ])

        mask = cv.inRange(dst, lower, upper)

        cnts = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        if MASK:
            save_image(RESULT_PATH / f"{_color.r} {_color.g} {_color.b} mask.png", mask)

        avg_area  = 0.0
        rects_areas = []

        for c in cnts:
            peri = cv.arcLength(c, True)
            approx = cv.approxPolyDP(c, 0.15 * peri, True)
            if len(approx) == 4:
                x, y, w, h = cv.boundingRect(approx)

                if w*h not in rects_areas:
                    rects_areas.append(w*h)
                    _sum = 0
                    for area in rects_areas:
                        _sum += area
                    avg_area = _sum / len(rects_areas)

                if _is_square_fit(w*h, avg_area, rects_areas):
                    cv.rectangle(dst, (x, y), (x + w, y + h), (0, 0, 255), 1)
                    res.append(Point(x+int(w//2), y+int(h//2)))

        print(rects_areas)

        if DETECTED_RECTS:
            save_image(RESULT_PATH / f"{_color.r} {_color.g} {_color.b} res.png", dst)

        return res
