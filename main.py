import pathlib

from utils import Color

RESULT_PATH = pathlib.Path(__file__).parent / 'res'
MASK = False
DETECTED_RECTS = False

COLOR_LIST = [
    Color(0, 0, 0),
    Color(12, 129, 110),
    Color(12, 129, 110),
    Color(40, 80, 158),
    Color(60, 60, 60),
    Color(64, 147, 228),
    Color(96, 0, 24),
    Color(96, 247, 242),
    Color(104, 70, 52),
    Color(120, 12, 153),
    Color(120, 120, 120),
    Color(135, 255, 94),
    Color(149, 104, 42),
    Color(153, 177, 251),
    Color(170, 56, 185),
    Color(170, 170, 170),
    Color(203, 0, 122),
    Color(210, 210, 210),
    Color(214, 181, 148),
    Color(224, 159, 249),
    Color(236, 31, 128),
    Color(236, 31, 128),
    Color(237, 28, 36),
    Color(243, 141, 169),
    Color(246, 170, 9),
    Color(248, 178, 119),
    Color(255, 250, 188),
    Color(255, 255, 255),
]

if __name__ == '__main__':
    from window import main
    main()