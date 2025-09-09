import sys

import numpy
from PIL import ImageGrab
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QBrush, QColor, QIntValidator
from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QVBoxLayout, QFrame, QLabel, QPushButton, \
    QLineEdit, QProgressBar, QHBoxLayout

from main import COLOR_LIST
from painter import PainterWorker
from parser import PixelParser
from utils import Area, PixelNode

OUTLINE_WIDTH = 16
OUTLINE_COLOR = Qt.red

SCREEN_BORDER_MARGIN = 200

doc = """

R -- Stop drawing
"""

def screenshot():
    return ImageGrab.grab().convert('RGB')

class ColorIcon(QWidget):
    def __init__(self, initial_color=QColor(255, 0, 0), width = 12, height = 12, parent=None):
        super().__init__(parent)
        self.color = initial_color
        self.setFixedSize(width, height)

    def set_color(self, color):
        self.color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.black)
        painter.drawRect(0, 0, self.width(), self.height())

class GameOverlay(QWidget):

    def _min_width(self):
        return SCREEN_BORDER_MARGIN

    def _max_width(self):
        return self.width() - SCREEN_BORDER_MARGIN

    def _min_height(self):
        return SCREEN_BORDER_MARGIN

    def _max_height(self):
        return self.height() - SCREEN_BORDER_MARGIN

    def __init__(self):
        super().__init__()


        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()

        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        self.setGeometry(0, 0, screen_width, screen_height)

        self.w_slider_value = self._min_width()
        self.h_slider_value = self._min_height()

        self.slider_container = QFrame(self)
        self.slider_container.setStyleSheet("background-color: white; border-radius: 10px;")
        self.slider_container.setMinimumWidth(300)

        layout = QVBoxLayout(self.slider_container)
        layout.setContentsMargins(15, 15, 15, 15)

        self.width_slider = QSlider(Qt.Horizontal)
        self.width_slider.setRange(self._min_width(), self._max_width())
        self.width_slider.setValue(self.w_slider_value)
        self.width_slider.valueChanged.connect(self.update_w_slider_value)

        self.height_slider = QSlider(Qt.Horizontal)
        self.height_slider.setRange(self._min_height(), self._max_height())
        self.height_slider.setValue(self.h_slider_value)
        self.height_slider.valueChanged.connect(self.update_h_slider_value)

        self.wlabel = QLabel(f"Width Value: {self.w_slider_value}", self.slider_container)
        self.wlabel.setStyleSheet("color: black; font-size: 14px;")

        self.hlabel = QLabel(f"Height Value: {self.h_slider_value}", self.slider_container)
        self.hlabel.setStyleSheet("color: black; font-size: 14px;")

        self.documentation = QLabel(doc, self.slider_container)
        self.documentation.setStyleSheet("color: black; font-size: 14px;")

        self.start_button = QPushButton("Start paint",self)
        self.start_button.clicked.connect(self.start_painter)
        self.start_button.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;   /* Blue background */
                        color: white;                /* White text */
                        border-radius: 10px;         /* Rounded corners */
                        padding: 8px 16px;           /* Inner padding */
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                    QPushButton:pressed {
                        background-color: #1c5985;
                    }
                """)

        self.input_pixel_count = QLineEdit(self)
        self.input_pixel_count.setValidator(QIntValidator(0, 9999, self))
        self.input_pixel_count.setText("123")
        self.input_pixel_count.setStyleSheet("""
                    QLineEdit {
                        border: 2px solid #3498db;
                        border-radius: 6px;
                        padding: 4px;
                        font-size: 16px;
                    }
                """)


        self.pixel_amount_label = QLabel("Amount of available pixels:", self.slider_container)
        self.pixel_amount_label.setStyleSheet("color: black; font-size: 14px;")

        self.progress_label = QLabel("Progres", self.slider_container)
        self.progress_label.setStyleSheet("color: black; font-size: 14px;")

        self.progress = QProgressBar(self)
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.progress.setStyleSheet("color: black; font-size: 14px;")

        current_color_layout = QHBoxLayout()

        self.current_color_label = QLabel("Current color:", self.slider_container)
        self.current_color_label.setStyleSheet("color: black; font-size: 14px;")

        self.color_icon = ColorIcon()

        current_color_layout.addWidget(self.current_color_label)
        current_color_layout.addWidget(self.color_icon)

        current_color_layout.setAlignment(Qt.AlignLeft)


        layout.addWidget(self.progress)

        layout.addWidget(self.wlabel)
        layout.addWidget(self.width_slider)

        layout.addWidget(self.hlabel)
        layout.addWidget(self.height_slider)

        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress)
        layout.addLayout(current_color_layout)

        layout.addWidget(self.start_button)

        layout.addWidget(self.pixel_amount_label)
        layout.addWidget(self.input_pixel_count)

        layout.addWidget(self.documentation)

        self.show()

        container_x = screen_width - self.slider_container.width() - 60
        container_y = screen_height - self.slider_container.width() - 100
        self.slider_container.move(container_x, container_y)


        self.matrix: list[list] = []
        self.xs: list[int] = []
        self.ys: list[int] = []
        self.nodes: list[PixelNode] = []

        self.area = None
        self.update_area()

        self.cnt = 0

    def update_area(self):
        center_x = self.width() // 2
        center_y = self.height() // 2

        left_x = center_x - self.w_slider_value // 2
        left_y = center_y - self.h_slider_value // 2

        self.area = Area(self.w_slider_value, self.h_slider_value, left_x, left_y)

    def update_w_slider_value(self, value):
        self.w_slider_value = value
        self.wlabel.setText(f"Rect width: {self.w_slider_value}")
        self.update_area()

    def update_h_slider_value(self, value):
        self.h_slider_value = value
        self.hlabel.setText(f"Rect height: {self.h_slider_value}")
        self.update_area()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.drawRect(self.rect())

        center_x = self.width() // 2
        center_y = self.height() // 2

        painter.setPen(QColor(OUTLINE_COLOR))
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.drawRect(center_x - self.w_slider_value // 2, center_y - self.h_slider_value // 2,
                         self.w_slider_value, self.h_slider_value)

        if self.matrix:
            self.display_rects(painter, self.matrix, self.xs, self.ys, self.area)

    def build_matrix(self, nodes: list[PixelNode], tolerance: int = 5):
        arr = []
        for node in nodes:
            for point in node.xy:
                arr.append((point.x, point.y, node.color))

        if not arr:
            return [], [], []

        def cluster(values):
            values = sorted(values)
            if not values:
                return []
            groups = []
            current = [values[0]]
            for v in values[1:]:
                if abs(v - current[-1]) <= tolerance:
                    current.append(v)
                else:
                    groups.append(round(sum(current) / len(current)))
                    current = [v]
            groups.append(round(sum(current) / len(current)))
            return groups

        xs = cluster([x for x, y, c in arr])
        ys = cluster([y for x, y, c in arr])

        matrix = [[None for _ in xs] for _ in ys]

        for x, y, color in arr:
            xi = min(range(len(xs)), key=lambda i: abs(xs[i] - x))
            yi = min(range(len(ys)), key=lambda i: abs(ys[i] - y))
            matrix[yi][xi] = color

        return matrix, xs, ys

    def display_rects(self, painter: QPainter, matrix: list[list], xs: list[int], ys: list[int],
                      area: Area | None = None):
        painter.setPen(QColor(OUTLINE_COLOR))
        painter.setBrush(QBrush(Qt.red))

        size = 1
        max_pixels = int(self.input_pixel_count.text())
        drawn = 0

        for yi, row in enumerate(matrix):
            y = ys[yi]
            for xi, color in enumerate(row):
                if color is None:
                    continue
                x = xs[xi]

                if area is not None and not area.is_entry(x, y):
                    continue

                if isinstance(color, QColor):
                    painter.setBrush(QBrush(color))
                else:
                    painter.setBrush(QBrush(Qt.red))

                painter.drawRect(x - size // 2, y - size // 2, size, size)

                drawn += 1
                if drawn >= max_pixels:
                    return

    def start_painter(self):
        img = screenshot()
        open_cv_image = numpy.array(img)
        parser = PixelParser(open_cv_image)
        _nodes = parser.nodes_for_colors(colors=COLOR_LIST)

        matrix, xs, ys = self.build_matrix(_nodes)
        self.nodes = _nodes
        self.matrix = matrix
        self.xs = xs
        self.ys = ys
        self.update()

        max_pixels = int(self.input_pixel_count.text())
        self.worker = PainterWorker(nodes, area, max_pixels)
        self.worker.update_color.connect(self.color_icon.set_color)
        self.worker.update_progress.connect(self.progress.setValue)
        self.worker.pixels_count.connect(self.set_progress_maximum)

        self.worker.start()

    def set_progress_maximum(self, value):
        max_pixels = int(self.input_pixel_count.text())
        self.progress.setMaximum(min(max_pixels, value))

def main():
    app = QApplication(sys.argv)
    overlay = GameOverlay()

    timer = QTimer()
    timer.timeout.connect(overlay.update)
    timer.start(16)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()