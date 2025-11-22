from util.enumeration import Enum
from util.curses.util import Align, Color, Direction, Event, Key, Size, Style
import curses
from math import log10



class Widget:
    def __init__(self):
        self.win = None
        self.size: Size = Size(x=0, y=0, w=0, h=0)
        self.style: Style = Style()
        self.parent = None
        self.prev = None
        self.next = None

    def set_text(self, y, x, text: str):
        if self.win:
            self.win.addstr(y, x, text, self.style.flags())

        return self

    def render(self):
        if self.win:
            self.win.refresh()

        return self

    def resize(self, size: Size):
        self.size = size

        return self

    def restyle(self, style: Style):
        self.style = style

        return self

    def draw(self):
        raise NotImplementedError("")

# Layouts


class Layout(Widget):
    def __init__(self):
        super().__init__()

        self.children = []

    def resize(self, size: Size):
        self.size = size

        for child in self.children:
            child.resize(size)

        return self


    def add(self, widget: Widget):
        self.children.append(widget)

        return self

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

        return self

    def resize(self, size: Size):
        self.size = size

        cell_w = size.w // self.cols
        cell_h = size.h // self.rows
        for widget, (col, row, cw, rh) in self.cells.items():
            x = col * cell_w
            y = row * cell_h
            w = max(10, cell_w * cw)
            h = max(3, cell_h * rh)
            widget.resize(Size(x=x, y=y, w=w, h=h))

        return self

    def draw(self):
        for widget in self.cells.keys():
            widget.win = self.win.subwin(*widget.size.hwyx)
            widget.draw()

        return self


class Box(Layout):
    def __init__(self, direction: int = Direction.Horizontal):
        super().__init__()

        self.direction = direction

    def resize(self, size: Size):
        self.size = size

        x, y, w, h = self.size.xywh

        if len(self.children):
            if self.direction == Direction.Horizontal:
                w = w // len(self.children)
            elif self.direction == Direction.Vertical:
                h = h // len(self.children)

        for child in self.children:
            child.size = Size(x, y, w, h)

            if self.direction == Direction.Horizontal:
                x += w
            elif self.direction == Direction.Vertical:
                y += h

        return self

    def draw(self):
        for child in self.children:
            child.win = self.win.subwin(*child.size.hwyx)
            child.draw()

        return self


# Widgets


class Frame(Layout):
    def __init__(self, title: str = None, align: int = Align.Center, padding: int = 1):
        super().__init__()
        self.title: str = f'{" " * padding}{title}{" " * padding}'
        self.align: int = align
        self.padding: int = padding
        self.left: int = 0

    def resize(self, size: Size):
        self.size = size

        if self.align == Align.Left:
            self.left = self.padding
        elif self.align == Align.Center:
            self.left = (self.size.w - len(self.title)) // 2 - self.padding
        elif self.align == Align.Right:
            self.left = (self.size.w - len(self.title)) - self.padding

        if self.children:
            self.children[0].size = Size(
                self.size.x + self.padding, self.size.y + self.padding,
                self.size.w - 2 * self.padding, self.size.h - 2 * self.padding)

    def draw(self):
        self.win.box()
        self.set_text(
            0, self.left, self.title[:self.size.w - 2 * self.padding])

        if self.children:
            self.children[0].win = self.win.subwin(*self.children[0].size.hwyx)
            self.children[0].draw()


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

    def add(self, steps=1):
        self.progress = min(self.progress + self.step * steps, self.max)

    def sub(self, steps=1):
        self.progress = max(self.progress - self.step * steps, self.min)


class StatusBar(Box):
    def __init__(self):
        super().__init__(Direction.Horizontal)

    def draw(self):
        self.win.bkgd(' ', curses.color_pair(Color.StatusBar))

        super().draw()


class Log(Widget):
    def __init__(self):
        super().__init__()
        self.lines = []

    def add_line(self, line):
        self.lines.append(line)

    def draw(self):
        self.win.box()
        for i, line in enumerate(self.lines[-(self.size.h - 2):]):
            self.set_text(i + 1, 1, line[:self.size.w - 2])


class Table(Widget):
    def __init__(self, cells: list):
        super().__init__()
        self.cells = cells

    def draw(self):
        for y, row in enumerate(self.cells[:self.size.h]):
            w = self.size.w // max(1, len(row))
            for x, cell in enumerate(row):
                self.set_text(y, x * w, cell)


# Root


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
        self.layout = None

        self.events = {}

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.mousemask(curses.ALL_MOUSE_EVENTS |
                         curses.REPORT_MOUSE_POSITION)
        curses.start_color()
        curses.use_default_colors()

        curses.init_pair(Color.WhiteBlack, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(Color.BlackWhite, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(Color.GreenBlack, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(Color.RedBlack, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(Color.YellowBlack, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(Color.CyanBlack, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(Color.RedWhite, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(Color.GreenWhite, curses.COLOR_GREEN, curses.COLOR_WHITE)
        curses.init_pair(Color.MagentaWhite, curses.COLOR_MAGENTA, curses.COLOR_WHITE)
        curses.init_pair(Color.MagentaBlack, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    def set_layout(self, layout: Layout):
        if self.layout:
            self.layout.parent = None

        self.layout = layout
        layout.parent = self

        if self.win:
            layout.win = self.win.subwin(*self.size.hwyx)

        return self

    def resize(self, size: Size):
        self.size = size

        if self.statusbar:
            if self.layout:
                self.layout.resize(Size(size.x, size.y, size.w, size.h - 1))
            self.statusbar.resize(Size(size.x, size.h - 1, size.w, 1))

        else:
            if self.layout:
                self.layout.resize(size)

        return self

    def draw(self):
        self.win.erase()

        w, h = self.size.wh

        if self.layout:
            self.layout.draw()

        if self.statusbar:
            self.statusbar.win = self.win.subwin(*self.statusbar.size.hwyx)
            self.statusbar.draw()

        curses.doupdate()

        return self

    def run(self):
        h, w = self.win.getmaxyx()

        self.resize(Size(0, 0, w, h))

        while self.running:
            self.draw()
            c = self.win.getch()

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

        return self

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
        return self.on_event(Event.OnKey, key, cb)

    def fire_key(self, key: int):
        self.fire_event(Event.OnKey, key)

    def add_statusbar(self):
        self.statusbar = StatusBar()
        self.statusbar.size = Size(
            self.size.x, self.size.h - 1, self.size.w, 1)
        self.statusbar.win = self.win.subwin(*self.statusbar.size.hwyx)
        return self.statusbar

    def quit(self):
        self.running = False

    def cycle_focus(self):
        pass

