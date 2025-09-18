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

PAID_COLOR_LIST = [
    Color(15, 121, 159),
    Color(51, 57, 65),
    Color(74, 66, 132),
    Color(74, 107, 58),
    Color(77, 49, 184),
    Color(90, 148, 74),
    Color(109, 100, 63),
    Color(109, 117, 141),
    Color(122, 113, 196),
    Color(123, 99, 82),
    Color(125, 199, 255),
    Color(132, 197, 115),
    Color(148, 140, 107),
    Color(155, 82, 73),
    Color(156, 132, 49),
    Color(156, 132, 107),
    Color(165, 14, 30),
    Color(170, 170, 170),
    Color(179, 185, 209),
    Color(181, 174, 241),
    Color(187, 250, 242),
    Color(197, 173, 49),
    Color(205, 197, 158),
    Color(209, 128, 81),
    Color(214, 181, 148),
    Color(219, 164, 99),
    Color(228, 92, 26),
    Color(232, 212, 95),
    Color(250, 128, 114),
    Color(250, 182, 164),
    Color(255, 197, 165),
]

if __name__ == '__main__':
    from window import main
    main()