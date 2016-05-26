import curses
from curses import wrapper


def test_terminal():
    global map_dim

    # Read map into list
    f = open('map', 'r')
    map_test = f.readlines()
    f.close()

    # Save map dimensions
    map_dim = [0, 0]
    map_dim[0] = len(map_test)
    map_dim[1] = len(map_test[0])

    # Test size of terminal
    test_window = curses.initscr()
    max_y, max_x = test_window.getmaxyx()
    if map_dim[0] + 5 > max_y or map_dim[1] + 1 > max_x:
        print("Please make the terminal at least " + str(map_dim[1] + 1) +
              " characters wide and " + str(map_dim[0] + 5) + " lines high.")
        curses.endwin()
        quit()
    else:
        pass


def main_lab(stdscr):
    global q
    global a

    q = -1
    a = 0

    if curses.has_colors():
        curses.start_color()
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_CYAN)
    curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_CYAN)

    curses.curs_set(False)

    stdscr.bkgd(' ', curses.color_pair(6) | curses.A_BOLD)
    stdscr.border(0)

    menu_0 = 'Choose game mode. Press:'
    menu_1 = '1 - Singleplayer'
    menu_2 = '2 - Multiplayer'
    menu_q = 'q - Quit'

    my, mx = stdscr.getmaxyx()
    window_menu = curses.newwin(my, mx, 0, 0)
    window_menu.bkgd(' ', curses.color_pair(7))
    window_menu.box()
    window_menu.addstr(my // 2 - 2, mx // 2 - len(menu_0) // 2, menu_0, curses.A_BOLD)
    window_menu.addstr(my // 2 - 1, mx // 2 - len(menu_1) // 2, menu_1, curses.A_BOLD)
    window_menu.addstr(my // 2, mx // 2 - len(menu_2) // 2, menu_2, curses.A_BOLD)
    window_menu.addstr(my // 2 + 1, mx // 2 - len(menu_q) // 2, menu_q, curses.A_BOLD)
    window_menu.refresh()

    while q != ord('q'):
        q = window_menu.getch()
        if q == ord('1'):
            a = 1
            break
        if q == ord('2'):
            a = 2
            break
        window_menu.refresh()
    curses.endwin()


test_terminal()
wrapper(main_lab)

if a == 1:
    from lab import sp_main
elif a == 2:
    from mp_lab import mp_main
