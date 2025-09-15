import curses
from math import log10

# TODO: remove
from os import getcwd
from pathlib import Path
from sys import path as PATH


CWD = Path(getcwd())
BASE_DIR = Path(__file__).parent
PYMUNGE_DIR = BASE_DIR.parent

PATH.append(str(PYMUNGE_DIR))
# TODO: remove end

from util.enum import Enum


class Align(Enum):
    Left: int
    Center: int
    Right: int


class Color(Enum):
    WhiteBlack = 1
    BlackWhite = 2
    GreenBlack = 3
    RedBlack = 4
    StatusBar = BlackWhite
    Help = RedBlack


class Namespace:
    def __init__(self, **kwargs):
        self.set(**kwargs)

    def set(self, **kwargs):
        self.__dict__.update(**kwargs)

    def vals(self):
        return self.__dict__.values()


class Widget:
    def __init__(self):
        self.win = None
        self.geometry = Namespace(x=0, y=0, w=0, h=0)
        self.style = curses.A_BOLD
        self.color = Color.GreenBlack

    def set_text(self, y, x, text: str):
        self.win.addstr(y, x, text, self.style | curses.color_pair(self.color))

    def update(self):
        raise NotImplementedError("")

    def render(self):
        raise NotImplementedError("")


class Layout:
    def __init__(self):
        self.container = None
        self.children = []

    def attach(self, container):
        self.container = container

    def add(self, widget: Widget):
        self.children.append(widget)

    def render(self):
        raise NotImplementedError("")


class Grid(Layout):
    def __init__(self, cols, rows):
        super().__init__()
        self.cols = cols
        self.rows = rows
        self.cells = {}

    def add(self, col: int, row: int, colspan: int, rowspan: int, widget: Widget):
        super().add(widget)
        self.cells[widget] = (col, row, colspan, rowspan)

    def render(self):
        x, y, w, h = self.container.geometry.vals()
        cell_w = w // self.cols
        cell_h = h // self.rows
        for widget, (col, row, cw, rh) in self.cells.items():
            x = col * cell_w
            y = row * cell_h
            w = max(10, cell_w * cw)
            h = max(3, cell_h * rh)
            widget.geometry.set(x=x, y=y, w=w, h=h)
            widget.win = self.container.win.subwin(*reversed(widget.geometry.vals()))
            widget.render()


class Root(Widget):
    """Root application window."""
    def __init__(self):
        super().__init__()

        self.running = True

        self.win = curses.initscr()
        self.win.keypad(True)
        self.win.scrollok(True)

        h, w = self.win.getmaxyx()
        self.geometry.w = w
        self.geometry.h = h

        self.focus = None
        self.statusbar = None

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        curses.start_color()
        curses.use_default_colors()

    def render(self):
        if self.layout:
            self.layout.render()

        if self.statusbar:
            self.statusbar.render()
        
        curses.doupdate()

    def run(self, layout):
        self.layout = layout
        self.layout.attach(self)
        # self.update() resize again

        while self.running:
            self.render()
            c = self.win.getch()
            if c == ord("q"):
                self.running = False

        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def add_statusbar(self):
        self.statusbar = StatusBar()
        return self.statusbar


class Frame(Layout, Widget):
    def __init__(self, title: str = None, align: int = Align.Center, padding: int = 1):
        Layout.__init__(self)
        Widget.__init__(self)
        self.title: str = f'{" " * padding}{title}{" " * padding}'
        self.align: int = align
        self.padding: int = padding

        self.attach(self)

    def render(self):
        if self.align == Align.Left:
            left = 1
        elif self.align == Align.Center:
            left = (self.geometry.w - len(self.title)) // 2 - self.padding
        elif self.align == Align.Right:
            left = (self.geometry.w - len(self.title)) - 1

        self.win.box()
        self.set_text(0, left, self.title[:self.geometry.w-2])

        if self.children:
            child = self.children[0]
            g = self.geometry
            child.geometry = Namespace(x = g.x + 1, y = g.y + 1, w = g.w - 2, h = g.h - 2)
            child.win = self.container.win.subwin(*reversed(child.geometry.vals()))
            child.render()


class Label(Widget):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def render(self):
        self.set_text(0, 0, self.text[:self.geometry.w])


class ProgressBar(Widget):
    class Type(Enum):
        Absolute: int
        Relative: int

    def __init__(self, step: int = 0, steps: int = 100, align: int = Align.Right, type: int = Type.Relative):
        super().__init__()
        self.step: int = step
        self.steps: int = steps
        self.align: int = align
        self.type: int = type

    def render(self):
        w = self.geometry.w - 2
        x = 1
        progress = self.step / self.steps

        if self.type == ProgressBar.Type.Absolute:
            digits = int(log10(self.steps) + 1)
            text = f'[{self.step:>{digits}d}/{self.steps:>{digits}d}]'
        elif self.type == ProgressBar.Type.Relative:
            text = f'{int(progress * 100):>d}%'

        if self.align == Align.Center:
            bar = '█' * int(progress * w) + '░' * int(w - progress * w)
            self.set_text(0, x, bar)
            self.set_text(0, x + (w - len(text)) // 2, text)

        else:
            text_len = len(text) + 1
            avail_w = w - text_len
            bar = '█' * int(avail_w * progress) + '░' * int(avail_w - avail_w * progress)

            if self.align == Align.Left:
                self.set_text(0, x, text + ' ')
                self.set_text(0, x + text_len, bar)
            elif self.align == Align.Right:
                self.set_text(0, x, bar)
                self.set_text(0, x + len(bar), ' ' + text)


class StatusBar(Widget):
    def __init__(self):
        super().__init__()

        self.cols = []

    def render(self):
        self.win.bkgd(' ', curses.color_pair(Color.StatusBar))
        self.set_text(0, 1, 'asd')


class Log(Widget):
    def __init__(self):
        super().__init__()
        self.lines = []

    def add_line(self, line):
        self.lines.append(line)

    def render(self):
        self.win.box()
    
        max_lines = self.geometry.h - 2
        visible = self.lines[-max_lines:]
        for i, line in enumerate(visible):
            self.set_text(i + 1, 1, line[: self.geometry.h - 2])

class Table(Widget):
    def __init__(self, cells: list):
        super().__init__()
        self.cells = cells

    def render(self):
        for y, row in enumerate(self.cells[:self.geometry.h]):
            w = self.geometry.w // max(1, len(row))
            for x, cell in enumerate(row):
                self.set_text(y, x * w, cell)


def gui():
    root = Root()

    curses.init_pair(Color.WhiteBlack, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(Color.BlackWhite, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(Color.GreenBlack, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(Color.RedBlack, curses.COLOR_RED, curses.COLOR_BLACK)

    bindings = Table([
        ['CTRL+c', 'Quit'],
        ['q', 'Quit'],
        ['p', 'Pause'],
        [],
        ['← ↓ ↑ →', 'Navigate view'],
        ['h j k l', 'Navigate view'],
        [],
        ['CTRL+<...>', 'Navigate focus'],
        ['ESC', 'Clear focus'],
        ['TAB', 'Cycle focus'],
    ])

    help = Frame('Key bindings')
    help.add(bindings)

    log = Log()
    for i in range(30):
        log.add_line(f'{i}. line')

    grid = Grid(cols=4, rows=4)
    grid.add(0, 0, 1, 1, ProgressBar(step=25, align=Align.Left))
    grid.add(1, 0, 1, 1, ProgressBar(step=50, align=Align.Right))
    grid.add(2, 0, 1, 1, ProgressBar(step=75, align=Align.Center))
    grid.add(3, 0, 1, 1, ProgressBar(step=66, align=Align.Center, type=ProgressBar.Type.Absolute))
    grid.add(0, 1, 1, 1, Frame('left', Align.Left))
    grid.add(1, 1, 1, 1, Frame('center', Align.Center))
    grid.add(2, 1, 1, 1, Frame('right', Align.Right))
    grid.add(0, 2, 1, 1, help)
    grid.add(1, 2, 1, 1, log)
    grid.add(2, 2, 1, 1, Label("Label"))
    grid.add(0, 3, 4, 1, StatusBar())

    root.run(grid)


if __name__ == '__main__':
    gui()
