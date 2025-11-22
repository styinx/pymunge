import curses
from util.enumeration import Enum


class Align(Enum):
    Left: int
    Center: int
    Right: int
    Top: int
    Middle: int
    Bottom: int


class Direction(Enum):
    Vertical: int
    Horizontal: int


class Color(Enum):
    WhiteBlack: int = 1
    BlackWhite: int
    GreenBlack: int
    RedBlack: int
    RedWhite: int
    MagentaWhite: int
    MagentaBlack: int
    GreenWhite: int
    YellowBlack: int
    CyanBlack: int
    StatusBar = "BlackWhite"
    Help = "RedBlack"
    Focus = "YellowBlack"


class Size:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x: int = x
        self.y: int = y
        self.w: int = w
        self.h: int = h

    def __add__(self, size):
        self.x += size.x
        self.y += size.y
        self.w += size.w
        self.h += size.h
        return self

    def __iadd__(self, size):
        return self + size

    def __sub__(self, size):
        self.x -= size.x
        self.y -= size.y
        self.w -= size.w
        self.h -= size.h
        return self

    def __isub__(self, size):
        return self - size
    
    @property
    def xy(self):
        return self.x, self.y

    @property
    def yx(self):
        return self.y, self.x

    @property
    def wh(self):
        return self.w, self.h
    
    @property
    def hw(self):
        return self.h, self.w
    
    @property
    def hwyx(self):
        return self.h, self.w, self.y, self.x

    @property
    def yxhw(self):
        return self.y, self.x, self.h, self.w

    @property
    def xywh(self):
        return self.x, self.y, self.w, self.h


class Style:
    def __init__(self):
        self.border_color: int = Color.WhiteBlack
        self.text_color: int = Color.WhiteBlack
        self.bold: bool = False
        self.italic: bool = False

    def flags(self):
        flags = 0

        if self.bold:
            flags |= curses.A_BOLD

        if self.italic:
            flags |= curses.A_ITALIC

        flags |= curses.color_pair(self.text_color)

        return flags


class Event(Enum):
    OnKey: int


class Key(Enum):
    TAB: int = 9
    KP_MINUS: int = 464
    KP_PLUS: int = 465