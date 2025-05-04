import curses


class Color:
    WhiteBlack = 1
    BlackWhite = 2
    GreenBlack = 3
    RedBlack = 4
    StatusBar = BlackWhite
    Help = RedBlack


def gui():
    running = True
    key = 0

    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.start_color()

    screen.keypad(True)

    curses.init_pair(Color.WhiteBlack, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(Color.BlackWhite, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(Color.GreenBlack, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(Color.RedBlack, curses.COLOR_RED, curses.COLOR_BLACK)

    height, width = screen.getmaxyx()
    height_third = height // 3
    width_third = width // 3

    win_proc = curses.newwin(height_third * 2, width_third * 2, 0, 0)
    help = curses.newwin(height_third * 1, width_third * 1, 0, width_third * 2)
    statusbar = curses.newwin(1, width, height - 1, 0)

    screen.clear()
    screen.refresh()

    while running:
        height, width = screen.getmaxyx()

        help.attron(curses.A_BOLD)
        help.attron(curses.color_pair(Color.Help))
        help.addstr(0, 0, 'q - quit')
        help.attroff(curses.color_pair(Color.Help))
        help.attroff(curses.A_BOLD)
        help.refresh()

        # Render status bar
        statusbar.attron(curses.A_BOLD)
        statusbar.attron(curses.color_pair(Color.StatusBar))
        statusbar.addstr(0, 0, 'Statusbar')
        statusbar.attroff(curses.color_pair(Color.StatusBar))
        statusbar.attroff(curses.A_BOLD)
        statusbar.refresh()

        screen.refresh()

        key = screen.getch()

        if key == ord('q'):
            running = False

    curses.nocbreak()
    curses.echo()
    curses.endwin()
