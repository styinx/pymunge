# TODO: remove
from os import getcwd
from pathlib import Path
from sys import path as PATH


CWD = Path(getcwd())
BASE_DIR = Path(__file__).parent
PYMUNGE_DIR = BASE_DIR.parent

PATH.append(str(PYMUNGE_DIR))
# TODO: remove end

from util.curses.util import Align, Color, Direction, Key, Style
from util.curses.widgets import Root, Box, Table, ProgressBar, Frame, Label, Grid, Log


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

    style1 = Style()
    style1.bold = True
    style1.text_color = Color.MagentaWhite

    style2 = Style()
    style2.text_color = Color.MagentaBlack

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

    b = Box(Direction.Vertical)
    b.add(ProgressBar().restyle(style2))
    b.add(Label("asd").restyle(style2))
    b.add(Label("dsa").restyle(style2))

    grid.add(3, 0, 1, 2, b)

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

    root.on_key(ord('q'), root.quit)
    root.on_key(Key.TAB, root.cycle_focus)
    root.on_key(Key.KP_MINUS, dec)
    root.on_key(Key.KP_PLUS, inc)

    status_bar.add(Label("dasd").restyle(style1))
    status_bar.add(Label("OK").restyle(style1))

    root.set_layout(grid)
    root.run()


if __name__ == '__main__':
    gui()