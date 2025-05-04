import sys
import os
import curses
from contextlib import contextmanager


class Style:
    ColorPalette = [
        (curses.COLOR_WHITE, curses.COLOR_BLACK),
        (curses.COLOR_BLACK, curses.COLOR_WHITE),
        (curses.COLOR_RED, curses.COLOR_BLACK),
        (curses.COLOR_GREEN, curses.COLOR_BLACK),
        (curses.COLOR_BLUE, curses.COLOR_BLACK),
    ]

    # yapf: disable
    Colors = [
        WhiteBlack,
        BlackWhite,
        RedBlack,
        GreenBlack,
        BlueBlack
    ] = range(1, len(ColorPalette) + 1)
    # yapf: enable

    ColorHeader = GreenBlack
    ColorFooter = BlackWhite
    ColorHelp = RedBlack
    ColorLog = WhiteBlack

    @staticmethod
    def init():
        curses.start_color()
        for color in Style.Colors[1:]:
            curses.init_pair(color, *Style.ColorPalette[color - 1])


class Container:

    def __init__(self, x: int = 0, y: int = 0, w: int = 0, h: int = 0, capacity: int = 0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.capacity = capacity
        self.text = []

        self.win = curses.newwin(h, w, y, x)

    def __setitem__(self, idx: int, text: str):
        while idx >= self.capacity:
            self.text.append('')
            self.capacity += 1

        self.text[idx] = text
        self.win.addstr(idx, 0, text)

    def update(self, h: int, w: int):
        self.w = w
        self.h = h

    def render(self):
        self.win.refresh()


@contextmanager
def apply(window, *args):
    for style in args:
        window.attron(style)

    try:
        yield

    finally:
        for style in args:
            window.attroff(style)


def main():
    screen = curses.initscr()
    curses.cbreak()
    curses.noecho()

    Style.init()

    key = 0
    running = True

    h, w = screen.getmaxyx()
    w2 = w // 2
    header = Container(0, 0, w, 1)
    footer = Container(0, h - 1, w, 1)
    help = Container(w2, 1, w2, h - 2)

    screen.clear()
    screen.refresh()

    while running:
        h, w = screen.getmaxyx()

        with apply(header.win, curses.color_pair(Style.ColorHeader)):
            with apply(header.win, curses.A_BOLD):
                header[0] = f'pymunge'

        with apply(footer.win, curses.color_pair(Style.ColorFooter)):
            with apply(footer.win, curses.A_BOLD):
                footer[0] = f'Statusbar'

        with apply(help.win, curses.color_pair(Style.ColorHelp)):
            with apply(help.win, curses.A_BOLD):
                help[0] = f'Shortcuts'
            help[1] = f'  q: Quit'
            help[2] = f'j/k: Scroll up/down'
            help[3] = f'↑/↓: Scroll up/down'

        header.render()
        footer.render()
        help.render()

        key = screen.getch()

        if key == ord('q'):
            running = False

    curses.echo()
    curses.nocbreak()
    curses.endwin()


if __name__ == "__main__":
    main()
