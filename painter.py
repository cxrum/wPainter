import time

import keyboard
import numpy as np
import win32api
import win32con
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtGui import QColor

from utils import PixelNode, Area, Point


def rgb2bgr(rgb):
    r = rgb[0]
    g = rgb[1]
    b = rgb[2]
    return np.array([b, g, r])

class Painter:
    def __init__(self, node: PixelNode, area: Area = None):
        self.nodes = node
        self.area = area
        self.current_index = 0
        self.current_x = 0
        self.current_y = 0

    def next_point(self) -> Point:
        pixels = self.nodes.xy
        if self.current_index >= len(pixels):
            return pixels[-1]
        return pixels[self.current_index]

    def draw_next_point(self, take_color = False):

        pixels = self.nodes.xy
        pixel = pixels[self.current_index]

        self.current_x = pixel.x
        self.current_y = pixel.y

        if take_color:
            self.take_color(self.current_x, self.current_y)

        self._lk_click(self.current_x,  self.current_y)
        self.current_index += 1

    def has_next(self) -> bool:
        return self.current_index < len(self.nodes.xy)


    def take_color(self, x, y):
        self._rk_click(x, y)
        time.sleep(0.5)
        self._i_hotkey(x,y)
        time.sleep(0.5)
        self._lk_click(x,y)
        time.sleep(0.5)

    def _i_hotkey(self, x, y):
        win32api.SetCursorPos((x, y))
        time.sleep(0.05)
        keyboard.send('i')
        time.sleep(0.05)
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
    update_color = pyqtSignal(object)  # signal to update color
    finished = pyqtSignal()
    update_progress = pyqtSignal(int)
    pixels_count = pyqtSignal(int)

    def __init__(self, nodes: list[PixelNode], area, user_max_pixels):
        super().__init__()
        self.nodes = nodes
        self.area = area
        self.max_pixels = user_max_pixels
        self.running = True

    def run(self):
        pixel_counter = 0
        try:
            filtered_nodes: list[PixelNode] = []
            _max_pixels = 0

            for node in self.nodes:
                painter = Painter(node, area=self.area)
                new_cords: list[Point] = []
                while painter.has_next():
                    next_point = painter.next_point()
                    if self.area.is_entry(next_point.x, next_point.y):
                        new_cords.append(next_point)
                        _max_pixels += 1
                    painter.current_index += 1

                new_node = PixelNode(node.color, new_cords)
                filtered_nodes.append(new_node)

            self.max_pixels = min(_max_pixels, self.max_pixels)
            self.pixels_count.emit(self.max_pixels )

            for node in filtered_nodes:
                if not self.running or pixel_counter >= self.max_pixels:
                    break

                color = node.color
                self.update_color.emit(QColor(*color.rgb()))
                time.sleep(0.1)

                painter = Painter(node, area=self.area)
                take_color = True

                while painter.has_next():
                    if not self.running or pixel_counter >= self.max_pixels:
                        break

                    if win32api.GetAsyncKeyState(ord('R')) < 0:
                        print("Stopped!")
                        self.running = False
                        break

                    next_point = painter.next_point()

                    if self.area.is_entry(next_point.x, next_point.y):
                        painter.draw_next_point(take_color)
                        take_color = False
                        pixel_counter += 1
                        self.update_progress.emit(pixel_counter)
                        time.sleep(0.08)
                    else:
                        painter.current_index += 1
        except Exception as e:
            print("Painter stopped:", e)
        finally:
            self.finished.emit()



