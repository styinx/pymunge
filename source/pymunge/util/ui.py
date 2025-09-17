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
    WhiteBlack: int = 99
    BlackWhite: int
    GreenBlack: int
    RedBlack: int = 0
    YellowBlack: int = 1
    CyanBlack: int
    StatusBar = WhiteBlack
    Help = RedBlack
    Focus = YellowBlack


class Size:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x: int = x
        self.y: int = y
        self.w: int = w
        self.h: int = h
    
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


class Widget:
    def __init__(self):
        self.win = None
        self.size: Size = Size(x=0, y=0, w=0, h=0)
        self.style: Style = Style()

    def set_text(self, y, x, text: str):
        self.win.addstr(y, x, text, self.style.flags())

    def resize(self, size: Size):
        self.size = size

    def render(self):
        if self.win:
            self.win.refresh()

    def update(self):
        raise NotImplementedError("")

    def draw(self):
        raise NotImplementedError("")


class Layout:
    def __init__(self):
        self.container = None
        self.children = []

    def attach(self, container):
        self.container = container

    def add(self, widget: Widget):
        self.children.append(widget)

    def draw(self):
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

    def draw(self):
        w, h = self.container.size.wh
        cell_w = w // self.cols
        cell_h = h // self.rows
        for widget, (col, row, cw, rh) in self.cells.items():
            x = col * cell_w
            y = row * cell_h
            w = max(10, cell_w * cw)
            h = max(3, cell_h * rh)
            widget.size = Size(x=x, y=y, w=w, h=h)
            widget.win = self.container.win.subwin(*widget.size.hwyx)
            widget.draw()

class Box(Layout):
    def __init__(self, direction: int = Direction.Horizontal):
        super().__init__()

        self.direction = direction

    def draw(self):
        x, y, w, h = self.container.size.xywh

        if self.direction == Direction.Horizontal:
            w = w // len(self.children)
        elif self.direction == Direction.Vertical:
            h = h // len(self.children)

        for child in self.children:
            child.size = Size(x, y, w, h)
            child.win = self.container.win.subwin(*child.size.hwyx)
            child.draw()

            if self.direction == Direction.Horizontal:
                x += w
            elif self.direction == Direction.Vertical:
                y += h


class Event(Enum):
    OnKey: int


class Key(Enum):
    TAB: int = 9
    KP_MINUS: int = 464
    KP_PLUS: int = 465


class Root(Widget):
    """Root application window."""
    def __init__(self):
        super().__init__()

        self.running = True

        self.win = curses.initscr()
        self.win.keypad(True)
        self.win.scrollok(True)

        h, w = self.win.getmaxyx()
        self.size.w = w
        self.size.h = h

        self.focus = None
        self.statusbar = None

        self.events = {}

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        curses.start_color()
        curses.use_default_colors()

        curses.init_pair(Color.WhiteBlack, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(Color.BlackWhite, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(Color.GreenBlack, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(Color.RedBlack, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(Color.YellowBlack, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(Color.CyanBlack, curses.COLOR_CYAN, curses.COLOR_BLACK)


    def draw(self):
        self.win.erase()

        w, h = self.size.wh

        if self.layout:
            self.layout.draw()

        if self.statusbar:
            self.statusbar.size = Size(0, h, w, 1)
            self.statusbar.win = self.win.subwin(*self.statusbar.size.hwyx)
            self.statusbar.draw()
        
        curses.doupdate()

    def run(self, layout):
        self.layout = layout
        self.layout.attach(self)
        # self.update() resize again

        if self.statusbar:
            self.size.h -= 1

        while self.running:
            self.draw()
            c = self.win.getch()
            print(c)
            
            self.fire_event(Event.OnKey, c)

        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def on_event(self, event: int, arg, cb):
        if event not in self.events:
            self.events[event] = {}

        if arg:
            self.events[event][arg] = cb
        else:
            self.events[event] = cb

    def fire_event(self, event, arg, *args, **kwargs):
        if event in self.events:
            cb = None
            if arg:
                if arg in self.events[event]:
                    cb = self.events[event][arg]
            else:
                cb = self.events[event]

            if cb:
                cb(*args, **kwargs)

    def on_key(self, key: int, cb):
        self.on_event(Event.OnKey, key, cb)

    def fire_key(self, key: int):
        self.fire_event(Event.OnKey, key)

    def add_statusbar(self):
        self.statusbar = StatusBar()
        self.statusbar.size = Size(self.size.x, self.size.h - 1, self.size.w, 1)
        self.statusbar.win = self.win.subwin(*self.statusbar.size.hwyx)
        return self.statusbar

    def quit(self):
        self.running = False

    def cycle_focus(self):
        pass


class Frame(Layout, Widget):
    def __init__(self, title: str = None, align: int = Align.Center, padding: int = 1):
        Layout.__init__(self)
        Widget.__init__(self)
        self.title: str = f'{" " * padding}{title}{" " * padding}'
        self.align: int = align
        self.padding: int = padding

        self.attach(self)

    def draw(self):
        if self.align == Align.Left:
            left = 1
        elif self.align == Align.Center:
            left = (self.size.w - len(self.title)) // 2 - self.padding
        elif self.align == Align.Right:
            left = (self.size.w - len(self.title)) - 1

        self.win.box()
        self.set_text(0, left, self.title[:self.size.w-2])

        if self.children:
            child = self.children[0]
            g = self.size
            child.size = Size(g.x + 1, g.y + 1, g.w - 2, g.h - 2)
            child.win = self.container.win.subwin(*child.size.hwyx)
            child.draw()


class Label(Widget):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def draw(self):
        self.set_text(0, 0, self.text[:self.size.w])


class ProgressBar(Widget):
    class Type(Enum):
        Absolute: int
        Relative: int

    def __init__(self, min=0, max=100, step=1, align=Align.Right, type=Type.Relative, **kwargs):
        super().__init__(**kwargs)
        self.bar_filled = '█'
        self.bar_empty = '░'
        self.align = align
        self.type = type

        self.min = min
        self.max = max
        self.step = step
        self.progress = min

    def draw(self):
        x, y, w, h = self.size.xywh

        # progress ratio
        progress = (self.progress - self.min) / (self.max - self.min)
        progress = max(0.0, min(1.0, progress))

        # text label
        if self.type == ProgressBar.Type.Absolute:
            digits = int(log10(self.max) + 1)
            text = f'[{self.progress:>{digits}d}/{self.max:>{digits}d}]'
        else:
            text = f'{int(progress * 100):>3d}%'

        # bar string
        bar_width = w - 2 - (0 if self.align == Align.Center else len(text))
        filled = int(bar_width * progress)
        empty = bar_width - filled
        bar = self.bar_filled * filled + self.bar_empty * empty

        # alignment
        if self.align == Align.Center:
            self.set_text(0, 1, bar)
            self.set_text(0, 1 + (bar_width - len(text)) // 2, text)
        elif self.align == Align.Left:
            self.set_text(0, 1, text + ' ')
            self.set_text(0, 1 + len(text) + 1, bar)
        elif self.align == Align.Right:
            self.set_text(0, 1, bar)
            self.set_text(0, 1 + len(bar), ' ' + text)

        self.win.refresh()

    def add(self, steps=1):
        self.progress = min(self.progress + self.step * steps, self.max)

    def sub(self, steps=1):
        self.progress = max(self.progress - self.step * steps, self.min)



class StatusBar(Widget):
    def __init__(self):
        super().__init__()

        self.cols = []

    def add(self, cb, align: int = Align.Center):
        self.cols.append([cb, align])

    def draw(self):
        w = self.size.w

        self.win.bkgd(' ', curses.color_pair(Color.StatusBar))

        if not self.cols:
            return

        col_w = w // len(self.cols)
        x_off = 0

        for cb, align in self.cols:
            text = str(cb())
            text = text[:col_w - 1]

            if align == Align.Left:
                x = x_off
            elif align == Align.Center:
                x = x_off + max(0, (col_w - len(text)) // 2)
            elif align == Align.Right:
                x = x_off + max(0, col_w - len(text))

            self.win.addstr(0, x, text)
            x_off += col_w


class Log(Widget):
    def __init__(self):
        super().__init__()
        self.lines = []

    def add_line(self, line):
        self.lines.append(line)

    def draw(self):
        self.win.box()
    
        max_lines = self.size.h - 2
        visible = self.lines[-max_lines:]
        for i, line in enumerate(visible):
            self.set_text(i + 1, 1, line[: self.size.h - 2])

class Table(Widget):
    def __init__(self, cells: list):
        super().__init__()
        self.cells = cells

    def draw(self):
        for y, row in enumerate(self.cells[:self.size.h]):
            w = self.size.w // max(1, len(row))
            for x, cell in enumerate(row):
                self.set_text(y, x * w, cell)


def gui():
    root = Root()

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

    p1 = ProgressBar(align=Align.Left)
    p2 = ProgressBar(align=Align.Center)
    p3 = ProgressBar(align=Align.Right)
    p4 = ProgressBar(align=Align.Left, type=ProgressBar.Type.Absolute)
    p5 = ProgressBar(align=Align.Center, type=ProgressBar.Type.Absolute)
    p6 = ProgressBar(align=Align.Right, type=ProgressBar.Type.Absolute)

    p1.style.text_color = Color.GreenBlack
    p2.style.text_color = Color.RedBlack

    grid = Grid(cols=4, rows=4)
    grid.add(0, 0, 1, 1, p1)
    grid.add(1, 0, 1, 1, p2)
    grid.add(2, 0, 1, 1, p3)
    grid.add(0, 1, 1, 1, p4)
    grid.add(1, 1, 1, 1, p5)
    grid.add(2, 1, 1, 1, p6)
    grid.add(0, 2, 1, 1, Frame('left', Align.Left))
    grid.add(1, 2, 1, 1, Frame('center', Align.Center))
    grid.add(2, 2, 1, 1, Frame('right', Align.Right))
    grid.add(0, 3, 1, 1, help)
    grid.add(1, 3, 1, 1, log)
    grid.add(2, 3, 1, 1, Label("Label"))

    status_bar = root.add_statusbar()

    def dec():
        p1.sub()
        p2.sub()
        p3.sub()
        p4.sub()
        p5.sub()
        p6.sub()

    def inc():
        p1.add()
        p2.add()
        p3.add()
        p4.add()
        p5.add()
        p6.add()

    def A():
        return 'A'

    def B():
        return 'B'

    def C():
        return 'C'

    root.on_key(ord('q'), root.quit)
    root.on_key(Key.TAB, root.cycle_focus)
    root.on_key(Key.KP_MINUS, dec)
    root.on_key(Key.KP_PLUS, inc)

    status_bar.add(A)
    status_bar.add(B)
    status_bar.add(C)

    root.run(grid)


if __name__ == '__main__':
    gui()
