# Tami, Adam, Misi
# Labyrinth game
# You need to find a key to open the door that leads you out of the labyrinth

# Import libraries and methods that we need
import curses
import random
import time
from curses import wrapper
from copy import deepcopy


# Checks if terminal is big enough for game, this is independent from wrapper
def mp_test_terminal():
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


# A collection of things that need to be done in the beggining, after mp_read_map()
def mp_initialize():
    global q, \
            win_condition, \
            map_fog_of_war, \
            score_counter, \
            score_top

    # Set global variables
    q = -1
    win_condition = 0
    map_fog_of_war = set()
    score_counter = 0
    score_top = open('score', 'r').readlines()

    # Makes the cursor not blink
    curses.curs_set(False)

    # Speeds up vertical movement.
    curses.nonl()

    # Makes colors
    if curses.has_colors():
        curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_WHITE)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_CYAN)
    curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_CYAN)


# Generates the position of the key, has to run after mp_read_map()
def mp_key_drop():
    global key_rezso_coordinates, key_etus_coordinates
    key_drop = random.sample(space_coordinates, 2)
    key_rezso_coordinates = {key_drop[0]}
    key_etus_coordinates = {key_drop[1]}


# Reads and interprets the map file into memory, we use a lot of global
# variables, maybe there is a better way to do this?
def mp_read_map():
    global map_in_memory, \
            r_pos, \
            e_pos, \
            wall_rezso_coordinates, \
            wall_etus_coordinates, \
            space_coordinates, \
            teleport_coordinates, \
            door_rezso_coordinates, \
            door_etus_coordinates, \
            win_coordinates, \
            start_char_r, \
            start_char_e, \
            wall_char_ver, \
            wall_char_hor, \
            space_char, \
            teleport_char, \
            door_rezso_char, \
            door_etus_char, \
            no_keydrop, \
            win_char

    # Set up variables
    map_in_memory = []
    map_fog_of_war = set()
    wall_rezso_coordinates = set()
    wall_etus_coordinates = set()
    space_coordinates = set()
    teleport_coordinates = set()
    door_rezso_coordinates = set()
    door_etus_coordinates = set()
    key_etus_coordinates = set()
    win_coordinates = set()
    start_char_r = {'R'}
    start_char_e = {'E'}
    wall_char_ver = {'8'}
    wall_char_hor = {'a'}
    space_char = {' '}
    teleport_char = {'T'}
    door_rezso_char = {'D'}
    door_etus_char = {'D'}
    no_keydrop = {'n'}
    win_char = {'W'}

    # Read the map file lines into a list
    f = open('mp_map', 'r')
    map_in_memory = f.readlines()
    f.close()

    # Make a nested list representation of the map for each character and
    # collect map data into the sets
    for j in range(0, len(map_in_memory)):
        for i in range(0, len(map_in_memory[0])):

            # Rezso's starting position
            if map_in_memory[j][i] in start_char_r:
                r_pos = [j, i]

            # Etus' starting position
            if map_in_memory[j][i] in start_char_e:
                e_pos = [j, i]

            # Space where you can move
            if map_in_memory[j][i] in space_char:
                space_coordinates.add((j, i))

            # Teleport beacons
            if map_in_memory[j][i] in teleport_char:
                teleport_coordinates.add((j, i))

            # Door that will open when you find the key
            if map_in_memory[j][i] in door_rezso_char:
                door_rezso_coordinates.add((j, i))
                wall_rezso_coordinates.add((j, i))
                wall_etus_coordinates.add((j, i))

            # Demo door
            if map_in_memory[j][i] in door_etus_char:
                door_etus_coordinates.add((j, i))
                wall_rezso_coordinates.add((j, i))
                wall_etus_coordinates.add((j, i))

            # Where you need to get to win
            if map_in_memory[j][i] in win_char:
                win_coordinates.add((j, i))

            # Where the walls are
            if map_in_memory[j][i] in wall_char_hor:
                wall_rezso_coordinates.add((j, i))
                wall_etus_coordinates.add((j, i))

            if map_in_memory[j][i] in wall_char_ver:
                wall_rezso_coordinates.add((j, i))
                wall_etus_coordinates.add((j, i))


# Draws the map (walls, exit, etc) on the screen
def mp_draw_map(screen):
    global map_fog_of_war, r_pos, e_pos

    # Add coordinates to map_fog_of_war set
    for x in range(-2, 3):
        for y in range(-2, 3):
            map_fog_of_war.add((r_pos[0] + x, r_pos[1] + y))
            map_fog_of_war.add((e_pos[0] + x, e_pos[1] + y))

    # Draw map from saved nested list
    for j in range(0, len(map_in_memory)):
        for i in range(0, len(map_in_memory[0])):

            # Only draw if Rezso already saw it
            if (j, i) in map_fog_of_war:

                # Empty space where Rezso can move
                if map_in_memory[j][i] in start_char_r or start_char_e or space_char or no_keydrop:
                    screen.addstr(j, i, ' ', curses.color_pair(5))

                # Before picking up key
                if door_rezso_coordinates <= wall_rezso_coordinates:
                    if map_in_memory[j][i] in door_rezso_char:
                        screen.addstr(j, i, '?', curses.color_pair(4))

                    # We draw the key not from the map but from the mp_key_drop()
                    if (j, i) in key_rezso_coordinates:
                        screen.addstr(j, i, 'r', curses.color_pair(5) | curses.A_BOLD)

                # After picking up key
                if door_rezso_coordinates & wall_rezso_coordinates == set():
                    if map_in_memory[j][i] in door_rezso_char:
                        screen.addstr(j, i, '?', curses.color_pair(4))

                    if (j, i) in key_rezso_coordinates:
                        screen.addstr(j, i, ' ', curses.color_pair(4))

                # Before picking up demo key
                if door_etus_coordinates <= wall_etus_coordinates:
                    if map_in_memory[j][i] in door_etus_char:
                        screen.addstr(j, i, '?', curses.color_pair(4))

                    if (j, i) in key_etus_coordinates:
                        screen.addstr(j, i, 'e', curses.color_pair(5) | curses.A_BOLD)

                # After picking up demo key
                if door_etus_coordinates & wall_etus_coordinates == set():
                    if map_in_memory[j][i] in door_etus_char:
                        screen.addstr(j, i, '?', curses.color_pair(4))

                    if (j, i) in key_etus_coordinates:
                        screen.addstr(j, i, ' ', curses.color_pair(4))

                # Teleport
                # Before use
                if (j, i) in teleport_coordinates:

                    if map_in_memory[j][i] in teleport_char:
                            screen.addstr(j, i, '♦', curses.color_pair(3))

                # After use and make sure the last one is drawn as used
                if (j, i) not in teleport_coordinates or {(j, i)} == teleport_coordinates:
                    if map_in_memory[j][i] in teleport_char:
                            screen.addstr(j, i, '♢',
                                          curses.color_pair(3) | curses.A_BOLD)

                # Walls
                if map_in_memory[j][i] in wall_char_hor:
                        screen.addstr(j, i, '▬', curses.color_pair(2))

                if map_in_memory[j][i] in wall_char_ver:
                        screen.addstr(j, i, '▮', curses.color_pair(2))

                # Exit
                if map_in_memory[j][i] in win_char:
                        screen.addstr(j, i, '♦', curses.color_pair(4))


# Draws Rezso on the screen
def mp_draw_rezso(screen):
    screen.addstr(r_pos[0], r_pos[1],
                  'R', curses.color_pair(5) | curses.A_BOLD)


# Draws Etus on the screen
def mp_draw_etus(screen):
    screen.addstr(e_pos[0], e_pos[1],
                  'E', curses.color_pair(5) | curses.A_BOLD)


# Controls the movement of Rezso, the 'R' character on screen
# and Etus, the 'E' character on screen
def mp_movement():
    global r_pos, \
            r_pos_previous, \
            e_pos, \
            e_pos_previous, \
            q, \
            score_counter

    # Save Rezso's and Etus' position
    r_pos_previous = deepcopy(r_pos)
    e_pos_previous = deepcopy(e_pos)

    # Movement itself
    # Rezso
    if q == curses.KEY_UP and r_pos[0] > 0:
        r_pos[0] -= 1
        score_counter += 1
    elif q == curses.KEY_DOWN and r_pos[0] < map_dim[0]-1:
        r_pos[0] += 1
        score_counter += 1
    elif q == curses.KEY_LEFT and r_pos[1] > 0:
        r_pos[1] -= 1
        score_counter += 1
    elif q == curses.KEY_RIGHT and r_pos[1] < map_dim[1]-1:
        r_pos[1] += 1
        score_counter += 1
    # Etus
    if q == ord('w') and e_pos[0] > 0:
        e_pos[0] -= 1
        score_counter += 1
    elif q == ord('s') and e_pos[0] < map_dim[0]-1:
        e_pos[0] += 1
        score_counter += 1
    elif q == ord('a') and e_pos[1] > 0:
        e_pos[1] -= 1
        score_counter += 1
    elif q == ord('d') and e_pos[1] < map_dim[1]-1:
        e_pos[1] += 1
        score_counter += 1
    else:
        pass


# Decides what happens when Rezso moves into an entity, e.g. a wall
def mp_checker():
    global win_condition, \
            r_pos, r_pos_previous, \
            e_pos, e_pos_previous, \
            wall_rezso_coordinates, \
            wall_etus_coordinates, \
            door_rezso_coordinates, \
            teleport_coordinates

    # Makes walls impenetrable
    if (r_pos[0], r_pos[1]) in wall_rezso_coordinates:
        r_pos = deepcopy(r_pos_previous)

    if (e_pos[0], e_pos[1]) in wall_etus_coordinates:
        e_pos = deepcopy(e_pos_previous)

    # Doesn't let Rezso and Etus be in the same position
    if (r_pos[0], r_pos[1]) == (e_pos[0], e_pos[1]):
        r_pos = deepcopy(r_pos_previous)
        e_pos = deepcopy(e_pos_previous)

    # Removes the doors blocking the exit when you pick up the key
    if (r_pos[0], r_pos[1]) in key_rezso_coordinates:
        wall_rezso_coordinates -= door_rezso_coordinates

    if (e_pos[0], e_pos[1]) in key_etus_coordinates:
        wall_etus_coordinates -= door_etus_coordinates

    # Teleports Rezso to a random beacon, but you can only use one beacon once
    if (r_pos[0], r_pos[1]) in teleport_coordinates and (r_pos_previous[0],
                                                         r_pos_previous[1]) not in teleport_coordinates:
        teleport_coordinates -= {(r_pos[0], r_pos[1])}
        r_pos_previous = deepcopy(r_pos)
        try:
            r = random.sample(teleport_coordinates, 1)
            r_pos[0] = r[0][0]
            r_pos[1] = r[0][1]
        except ValueError:
            pass

    # Teleports Etus to a random beacon, but you can only use one beacon once
    if (e_pos[0], e_pos[1]) in teleport_coordinates and (e_pos_previous[0],
                                                         e_pos_previous[1]) not in teleport_coordinates:
        teleport_coordinates -= {(e_pos[0], e_pos[1])}
        e_pos_previous = deepcopy(e_pos)
        try:
            r = random.sample(teleport_coordinates, 1)
            e_pos[0] = r[0][0]
            e_pos[1] = r[0][1]
        except ValueError:
            pass

    # Win condition
    if (r_pos[0], r_pos[1]) in win_coordinates:
        win_condition = 1
    if (e_pos[0], e_pos[1]) in win_coordinates:
        win_condition = 2


# Draw the scores and the info
def mp_draw_score(stdscr):
    my, mx = stdscr.getmaxyx()
    info_string_1 = 'Use the arrow keys to move with Rezső.'
    info_string_2 = 'Use the WASD keys to move with Etus.'
    info_string_3 = 'Press \'q\' to quit.'
    stdscr.addstr(my-4, mx // 2 - len(info_string_1) // 2, info_string_1, curses.color_pair(6))
    stdscr.addstr(my-3, mx // 2 - len(info_string_2) // 2, info_string_2, curses.color_pair(6))
    stdscr.addstr(my-2, mx // 2 - len(info_string_3) // 2, info_string_3, curses.color_pair(6))


# What happens when you win
def mp_win(stdscr):
    global map_fog_of_war

    # Write top score in file
    if score_counter < int(score_top[0]):
        f = open('score', 'w')
        f.write(str(score_counter))
        f.close()

    # Draw win screen
    if win_condition == 1:
        endstring = 'EPIC WIN, REZSŐ'
    if win_condition == 2:
        endstring = 'EPIC WIN, ETUS'

    my, mx = stdscr.getmaxyx()
    window_win = curses.newwin(my, mx, 0, 0)
    window_win.bkgd(' ', curses.color_pair(7))
    window_win.box()
    window_win.addstr(my // 2, mx // 2 - len(endstring), endstring, curses.A_BOLD)
    map_fog_of_war = set()
    window_win.refresh()
    time.sleep(3)


# Define the mp_main() function for the wrapper
def mp_main(stdscr):
    # We need to pass global variables to the wrapper, which is called outside
    # this function
    global q

    mp_read_map()
    mp_initialize()
    mp_key_drop()

    # Background settings
    stdscr.bkgd(' ', curses.color_pair(6) | curses.A_BOLD)
    stdscr.border(0)

    # Make window for map so it can be nice and centered
    my, mx = stdscr.getmaxyx()
    screen = curses.newwin(map_dim[0], map_dim[1]+1, (my - map_dim[0]) // 2, (mx - map_dim[1]) // 2)
    screen.bkgd(' ', curses.color_pair(6))
    screen.keypad(1)
    screen.refresh()

    # The actual game
    while q != ord('q') and win_condition == 0:
        screen.clear()
        stdscr.clear()
        mp_draw_score(stdscr)
        mp_draw_map(screen)
        mp_draw_rezso(screen)
        mp_draw_etus(screen)
        stdscr.refresh()
        screen.refresh()
        q = screen.getch()
        mp_movement()
        mp_checker()

    if win_condition > 0:
        mp_win(stdscr)
    curses.endwin()

mp_test_terminal()
wrapper(mp_main)
