import os
import random
import time
import sys
import threading
import select

lock = threading.Lock()

# down below, I call the ANSI CODE, which allows me to add colors to my game (it's an equivalent for Colorama, and doesn't need any library to run)
RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

# here comes basic colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
BLACK = "\033[30m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE_LIGHT_GREY = "\033[37m"

# then there are the ones called "high" colors (bright), helps for better textures and color plays
HIGH_RED = "\033[91m"
HIGH_GREEN = "\033[92m"
HIGH_YELLOW = "\033[93m"
HIGH_BLUE = "\033[94m"
HIGH_MAGENTA = "\033[95m"
HIGH_CYAN = "\033[96m"
HIGH_WHITE = "\033[97m"


# here, I define the game map with ASCII characters
MAP_LOGIC = [
    "################################",
    "#......................##......#",
    "#.####.#####.######.##.##.######",
    "#.####.#####.######.##.##.######",
    "#..............................#",
    "#.####.##.###############...####",
    "#..............................#",
    "#.####.##.##.##############.####",
    "#......##.##...................#",
    "######.##.##.###.##########..###",
    "#............##..#######.....###",
    "#.######.#####..####.....#######",
    "#..............................#",
    "################################"
]


# then I initialize pixel & gohsts positions, I also add walls and "empty" spaces, which are in fact the dots pixel has to eat to gain points
PIXEL = "P"
GHOST = "G"
EMPTY = "."
WALL = "#"

# here are the possible directions for the player
UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)

# I chose to define a default postion for pixel, so I initialize his "spawn" down below
pixel_pos = (1, 1) # <= pixel's spawn
ghosts_pos = [(3, 3), (5, 8), (9,2), (4,8), (6,7)]  # <= gohsts's spawn


def timed_input(prompt, timeout=0.5):
    print(prompt, end='', flush=True)
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        return sys.stdin.readline().strip().lower()
    return None

def start():
    print(f"""             ##########################################################
             #                                                        #
             #                                                        #
             #        Welcome to Pixel vs ghosts :                    #
             #  You play as Pixel, IPI's idol, and your job is to     #
             #  eat as much as bamboo as you can, without being       #
             #  touched by a ghost (G)                                #
             #                                                        #
             #                                                        #
             # type {HIGH_GREEN}'yes' to play{RESET}  //  {HIGH_RED}'no' to leave{RESET}                  #
             #                                                        #
             ##########################################################""")
    
    choice = input("\nReady to play : ").lower()
    if choice == "yes":
        ghost_thread = threading.Thread(target=ghost_loop, daemon=True)
        ghost_thread.start()
        game_loop()
    else:
        print(f"{HIGH_RED}See you next time!{RESET}")
        sys.exit()


# down below, I define the function "draw_map" that I'll use to (like its name) draw the map in ASCII in the user's shell
def draw_map(pixel_pos, ghosts_pos):
    os.system('cls' if os.name == 'nt' else 'clear')
    for y, row in enumerate(MAP_LOGIC):
        row_display = ""
        for x, char in enumerate(row):
            pos = (y, x)
            if pos == pixel_pos:
                row_display += f"{HIGH_YELLOW}{PIXEL}{RESET}"
            elif pos in ghosts_pos:
                row_display += f"{HIGH_RED}{GHOST}{RESET}"
            elif char == WALL:
                row_display += f"{BLUE}{WALL}{RESET}"
            elif char == EMPTY:
                row_display += f"{WHITE_LIGHT_GREY}{EMPTY}{RESET}"
            else:
                row_display += " "
        print(row_display)

# down below, I making and using this function to move pixel
def move_pixel(pixel_pos, direction):
    y, x = pixel_pos
    dy, dx = direction
    new_pos = (y + dy, x + dx)

    # I verify if the new movements are in the limit of the map
    if 0 <= new_pos[0] < len(MAP_LOGIC) and 0 <= new_pos[1] < len(MAP_LOGIC[0]):
        # verify if the new movement is against a wall
        if MAP_LOGIC[new_pos[0]][new_pos[1]] != WALL:
            return new_pos
    
    return pixel_pos  

# function to move ghosts
def move_ghosts(ghosts_pos):
    new_ghosts_pos = []
    for ghost_pos in ghosts_pos:
        y, x = ghost_pos
        direction = random.choice([UP, DOWN, LEFT, RIGHT])
        dy, dx = direction
        new_pos = (y + dy, x + dx)
        
        if 0 <= new_pos[0] < len(MAP_LOGIC) and 0 <= new_pos[1] < len(MAP_LOGIC[0]):
            if MAP_LOGIC[new_pos[0]][new_pos[1]] != WALL:
                new_ghosts_pos.append(new_pos)
            else:
                new_ghosts_pos.append(ghost_pos)
        else:
            new_ghosts_pos.append(ghost_pos)

    return new_ghosts_pos

def ghost_loop():
    global ghosts_pos
    while True:
        time.sleep(0.5)
        with lock:
            ghosts_pos = move_ghosts(ghosts_pos)


# main loop of the game
def game_loop():
    global pixel_pos, ghosts_pos
    score = 0

    while True:
        with lock:
            draw_map(pixel_pos, ghosts_pos)

        print(f"Bamboos eaten by Pixel : {score}")
        
        move = timed_input("Make Pixel move by using => z, q, s, d :  ")
        
        with lock:
            draw_map(pixel_pos, ghosts_pos)

        if move == "z":
            pixel_pos = move_pixel(pixel_pos, UP)
        elif move == "q":
            pixel_pos = move_pixel(pixel_pos, LEFT)
        elif move == "s":
            pixel_pos = move_pixel(pixel_pos, DOWN)
        elif move == "d":
            pixel_pos = move_pixel(pixel_pos, RIGHT)

        # verify if the player touch a ghost
        with lock:
            if pixel_pos in ghosts_pos:
                print("GAME OVER! A ghost hit you!")
                sys.exit()

        # score manager
        y, x = pixel_pos
        if MAP_LOGIC[y][x] == EMPTY:
            score += 1
            MAP_LOGIC[y] = MAP_LOGIC[y][:x] + " " + MAP_LOGIC[y][x + 1:]
            
            if not any("." in row for row in MAP_LOGIC):
                 draw_map(pixel_pos, ghosts_pos)
                 print(f"{HIGH_GREEN}Congratulations! You won! All bamboos are eaten.{RESET}")


if __name__ == "__main__":
    start()
