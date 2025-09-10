import statistics

import cv2 as cv
import numpy

from main import MASK, RESULT_PATH, DETECTED_RECTS
from utils import Color, PixelNode, Point, ColorPixel, Rect, Area


def save_image(path, img):
    cv.imwrite(str(path), img)

def _is_square_fit(area, rects_areas, k=0.5) -> bool:
    avg = statistics.mean(rects_areas)
    _max = avg * (1 - k)
    return min(rects_areas) <= area <= _max

class PixelParser:

    def __init__(self, img, area: Area):
        self.img = img
        self.rects_areas = []
        self.area = area


    def matrix_points_parse(self, colors: list[Color], sort_by_color = False) -> list[ColorPixel]:
        all_pixels: list[ColorPixel] = []

        for _color in colors:
            rects = self.parse_points_for_color(_color, rect_checking=False)
            for rect in rects:
                area = rect.w * rect.h
                if area not in self.rects_areas:
                    self.rects_areas.append(area)

        self.rects_areas.sort()
        print(self.rects_areas)

        for _color in colors:
            rects = self.parse_points_for_color(_color)

            for rect in rects:
                all_pixels.append(ColorPixel(_color, Point(rect.x, rect.y), rect.w, rect.h))

            all_pixels.sort(key=lambda px: (px.point.y, px.point.x))

        if sort_by_color:
            all_pixels.sort(key=lambda px: (px.color.r, px.color.g, px.color.b))

        return all_pixels



    def parse_points_for_color(self, _color: Color, tolerance = 5, rect_checking = True) -> list[Rect]:
        res: list[Rect] = []

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

        for c in cnts:
            peri = cv.arcLength(c, True)
            approx = cv.approxPolyDP(c, 0.15 * peri, True)
            if len(approx) == 4:
                x, y, w, h = cv.boundingRect(approx)

                if self.area.is_entry(x, y):
                    if rect_checking:
                        if _is_square_fit(w*h, self.rects_areas) :
                            cv.rectangle(dst, (x, y), (x + w, y + h), (0, 0, 255), 1)
                            res.append(Rect(x+int(w//2), y+int(h//2), w, h))
                    else:
                        res.append(Rect(x + int(w // 2), y + int(h // 2), w, h))

        if DETECTED_RECTS:
            save_image(RESULT_PATH / f"{_color.r} {_color.g} {_color.b} res.png", dst)

        return res
