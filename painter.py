import time

import keyboard
import numpy as np
import win32api
import win32con
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtGui import QColor

from utils import PixelNode, Area, Point, ColorPixel, Color


def rgb2bgr(rgb):
    r = rgb[0]
    g = rgb[1]
    b = rgb[2]
    return np.array([b, g, r])

class Painter:
    def __init__(self, delay = 0.2):
        self.delay = delay

    def draw_point(self, point: Point, take_color):
        if take_color:
            self.take_color(point.x, point.y)
            time.sleep(0.5)
        self._lk_click(point.x, point.y)


    def take_color(self, x, y):
        _l = max(0.2, self.delay)
        self._rk_click(x, y)
        self._i_hotkey(x,y)
        time.sleep(_l)
        self._lk_click(x,y)
        time.sleep(_l)

    def _i_hotkey(self, x, y):
        win32api.SetCursorPos((x, y))
        time.sleep(self.delay + 0.2)
        keyboard.send('i')
        time.sleep(self.delay + 0.2)
        keyboard.send('i')

    def _lk_click(self, x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    def _rk_click(self, x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)


class PainterWorker(QThread):
    update_color = pyqtSignal(object)
    finished = pyqtSignal()
    update_progress = pyqtSignal(int)

    def __init__(self, pixels: list[ColorPixel], total_pixels, area, delay = 0.05):
        super().__init__()
        self.pixels = pixels
        self.area = area
        self.total_pixels = total_pixels
        self.running = True
        self.delay = delay

    def run(self):
        pixel_counter = 0
        painter = Painter(self.delay)

        try:
            _prev_color = None

            for pixel in self.pixels:
                if not self.running or pixel_counter >= self.total_pixels:
                    break

                color = pixel.color

                if self.area.is_entry(pixel.point.x, pixel.point.y):
                    self.update_color.emit(QColor(*color.rgb()))

                    take_color = False
                    if _prev_color is None or _prev_color != color:
                        _prev_color = color
                        take_color = True

                    painter.draw_point(pixel.point, take_color)
                    time.sleep(self.delay)

                    pixel_counter += 1
                    self.update_progress.emit(pixel_counter)

                if keyboard.is_pressed('r'):
                    self.running = False
                    break

        except Exception as e:
            print("Painter stopped:", e)
        finally:
            self.finished.emit()



