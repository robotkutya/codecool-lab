# Tami, Adam, Misi
# Labyrinth game
# You need to find a key to open the door that leads you out of the labyrinth

# Import libraries and methods that we need
import curses, random, time
from curses import wrapper
from copy import deepcopy

# Checks if terminal is big enough for map, this is independent from wrapper
def testTerminal():
    global map_dim

    # Read map into list
    f = open('map', 'r')
    map_test = f.readlines()
    f.close()

    # Save map dimensions
    map_dim = [0,0]
    map_dim[0] = len(map_test)
    map_dim[1] = len(map_test[0])

    # Test size of terminal
    test_window = curses.initscr()
    max_y, max_x = test_window.getmaxyx()
    if map_dim[0] + 3 > max_y or map_dim[1] > max_x:
        print("Please make the terminal at least " + str(map_dim[1]) +
        " characters wide and " + str(map_dim[0]+2) + " lines high.")
        curses.endwin()
        quit()
    else:
        pass

# A collection of things that need to be done in the beggining, after readMap()
def initialize():
    global q, win_condition, map_fog_of_war

    # Set global variables
    q = -1
    win_condition = 0
    map_fog_of_war = set()

    # Makes the cursor not blink
    curses.curs_set(False)

    # Makes colors
    if curses.has_colors():
        curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_WHITE)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_CYAN)
    curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_WHITE)

# Generates the position of the key, has to run after readMap()
def keyDrop():
    global key_drop_coordinates
    key_drop = random.sample(space_coordinates, 1)
    key_drop_coordinates = {key_drop[0]}

# Reads and interprets the map file into memory, we use a lot of global
# variables, maybe there is a better way to do this?
def readMap():
    global map_in_memory, R_pos, wall_coordinates, space_coordinates, teleport_coordinates, door_coordinates, door_demo_coordinates, key_demo_coordinates, win_coordinates, start_char, wall_char_ver, wall_char_hor, space_char, teleport_char, door_char, door_demo_char, key_demo_char, win_char

    # Set up variables
    map_in_memory = []
    map_fog_of_war = set()
    wall_coordinates = set()
    space_coordinates = set()
    teleport_coordinates = set()
    door_coordinates = set()
    door_demo_coordinates = set()
    key_demo_coordinates = set()
    win_coordinates = set()
    start_char = {'S'}
    wall_char_ver = {'8'}
    wall_char_hor = {'a'}
    space_char = {' '}
    teleport_char = {'T'}
    door_char = {'D'}
    door_demo_char = {'K'}
    key_demo_char = {'k'}
    win_char = {'W'}

    # Read the map file lines into a list
    f = open('map', 'r')
    map_in_memory = f.readlines()
    f.close()

    # Make a nested list representation of the map for each character and
    # collect map data into the sets
    for j in range(0,len(map_in_memory)):
        for i in range(0,len(map_in_memory[0])):

            # Rezso's starting position
            if map_in_memory[j][i] in start_char:
                R_pos = [j,i]

            # Space where you can move
            if map_in_memory[j][i] in space_char:
                space_coordinates.add((j, i))

            # Teleport beacons
            if map_in_memory[j][i] in teleport_char:
                teleport_coordinates.add((j, i))

            # Door that will open when you find the key
            if map_in_memory[j][i] in door_char:
                door_coordinates.add((j, i))
                wall_coordinates.add((j, i))

            # Demo door
            if map_in_memory[j][i] in door_demo_char:
                door_demo_coordinates.add((j, i))
                wall_coordinates.add((j, i))

            # Key for demo door
            if map_in_memory[j][i] in key_demo_char:
                key_demo_coordinates.add((j, i))

            # Where you need to get to win
            if map_in_memory[j][i] in win_char:
                win_coordinates.add((j, i))

            # Where the walls are
            if map_in_memory[j][i] in wall_char_hor:
                wall_coordinates.add((j, i))

            if map_in_memory[j][i] in wall_char_ver:
                wall_coordinates.add((j, i))

# Draws the map (walls, exit, etc) on the screen
def drawMap(screen):
    global map_fog_of_war

    # Add coordinates to map_fog_of_war set
    for x in range(-2, 3):
        for y in range(-2, 3):
            map_fog_of_war.add((R_pos[0] + x, R_pos[1] + y))

    # Draw map from saved nested list
    for j in range(0,len(map_in_memory)):
        for i in range(0,len(map_in_memory[0])):

            # Only draw if Rezso already saw it
            if (j,i) in map_fog_of_war:

                # Empty space where Rezso can move
                if map_in_memory[j][i] in start_char:
                    screen.addstr(j, i, ' ', curses.color_pair(5))

                if map_in_memory[j][i] in space_char:
                    screen.addstr(j, i, ' ', curses.color_pair(5))

                # Before picking up key
                if door_coordinates <= wall_coordinates:
                    if map_in_memory[j][i] in door_char:
                        screen.addstr(j, i, '?', curses.color_pair(4))

                    # We draw the key not from the map but from the keyDrop()
                    if (j,i) in key_drop_coordinates:
                        screen.addstr(j, i, 'k', curses.color_pair(4))

                # After picking up key
                if door_coordinates & wall_coordinates == set():
                    if map_in_memory[j][i] in door_char:
                        screen.addstr(j, i, ' ', curses.color_pair(4))

                    if (j,i) in key_drop_coordinates:
                        screen.addstr(j, i, ' ', curses.color_pair(4))

                # Before picking up demo key
                if door_demo_coordinates <= wall_coordinates:
                    if map_in_memory[j][i] in door_demo_char:
                        screen.addstr(j, i, '?', curses.color_pair(4))

                    if (j,i) in key_demo_coordinates:
                        screen.addstr(j, i, 'k', curses.color_pair(4))

                # After picking up demo key
                if door_demo_coordinates & wall_coordinates == set():
                    if map_in_memory[j][i] in door_demo_char:
                        screen.addstr(j, i, ' ', curses.color_pair(4))

                    if (j,i) in key_demo_coordinates:
                        screen.addstr(j, i, ' ', curses.color_pair(4))

                # Teleport
                # Before use
                if (j, i) in teleport_coordinates:

                    if map_in_memory[j][i] in teleport_char:
                            screen.addstr(j, i, '♦', curses.color_pair(3))

                # After use
                if (j, i) not in teleport_coordinates:
                    if map_in_memory[j][i] in teleport_char:
                            screen.addstr(j, i, '⋄', curses.color_pair(3))

                # Walls
                if map_in_memory[j][i] in wall_char_hor:
                        screen.addstr(j, i, '▬', curses.color_pair(2))

                if map_in_memory[j][i] in wall_char_ver:
                        screen.addstr(j, i, '▮', curses.color_pair(2))

                # Exit
                if map_in_memory[j][i] in win_char:
                        screen.addstr(j, i, 'X', curses.color_pair(4))

# Draws Rezso on the screen
def drawRezso(screen):
    screen.addstr(R_pos[0], R_pos[1], 'R', curses.color_pair(5))

# Controls the movement of Rezso, the 'R' character on screen
def movement():
    global R_pos, R_pos_previous, q

    # Save Rezso's position
    R_pos_previous = deepcopy(R_pos)

    # Movement itself
    if q == curses.KEY_UP and R_pos[0] > 0:
        R_pos[0] -= 1
    elif q == curses.KEY_DOWN and R_pos[0] < map_dim[0]-1:
        R_pos[0] += 1
    elif q == curses.KEY_LEFT and R_pos[1] > 0:
        R_pos[1] -= 1
    elif q == curses.KEY_RIGHT and R_pos[1] < map_dim[1]-1:
        R_pos[1] += 1
    else:
        pass

# Decides what happens when Rezso moves into an entity, e.g. a wall
def checker():
    global win_condition, R_pos, R_pos_previous, wall_coordinates, door_coordinates, teleport_coordinates

    # Makes walls impenetrable
    if (R_pos[0], R_pos[1]) in wall_coordinates:
        R_pos = deepcopy(R_pos_previous)

    # Removes the doors blocking the exit when you pick up the key
    if (R_pos[0], R_pos[1]) in key_drop_coordinates:
        wall_coordinates -= door_coordinates

    if (R_pos[0], R_pos[1]) in key_demo_coordinates:
        wall_coordinates -= door_demo_coordinates

    # Teleports you to a random beacon, but you can only use one beacon once
    if (R_pos[0], R_pos[1]) in teleport_coordinates:
        teleport_coordinates -= {(R_pos[0], R_pos[1])}
        try:
            r = random.sample(teleport_coordinates, 1)
            R_pos[0] = r[0][0]
            R_pos[1] = r[0][1]
        except ValueError:
            pass

    # Win condition
    if (R_pos[0], R_pos[1]) in win_coordinates:
        win_condition = 1

# What happens when you win
def win(stdscr):
    endstring = 'EPIC WIN'
    my, mx = stdscr.getmaxyx()
    window_win = curses.newwin(3, len(endstring) + 4, my // 2 - 2, mx // 2 - len(endstring) // 2)
    window_win.bkgd(' ', curses.color_pair(7))
    window_win.clear()
    window_win.addstr(1, 2, endstring, curses.color_pair(2))
    window_win.refresh()
    time.sleep(3)


# Define the main() function for the wrapper
def main(stdscr):
    # We need to pass global variables to the wrapper, which is called outside
    # this function
    global q

    readMap()
    initialize()
    keyDrop()

    # Make window for background
    my, mx = stdscr.getmaxyx()
    window_background = curses.newwin(my, mx, 0, 0)
    window_background.bkgd(' ', curses.color_pair(6))
    info_string = 'Press \'q\' to quit. Use the arrow keys to move with Rezső.'
    window_background.addstr(my-2, mx // 2 - len(info_string) // 2, info_string, curses.color_pair(6))
    window_background.refresh()

    # Make window for map so it can be nice and centered
    screen = curses.newwin(map_dim[0], map_dim[1], (my - map_dim[0]) // 2, (mx - map_dim[1]) // 2)
    screen.bkgd(' ', curses.color_pair(6))
    screen.keypad(1)

    # The actual game
    while q != ord('q') and win_condition == 0:
        screen.clear()
        drawMap(screen)
        drawRezso(screen)
        q = screen.getch()
        movement()
        checker()
        screen.refresh()

    #if win_condition == 1:
    win(stdscr)
    curses.endwin()

# Use the wrapper to avoid bugs and test before
testTerminal()
wrapper(main)
