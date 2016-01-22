"""

A command line version of the game 2048

Alan M Jackson


Done
    Multiple powers on the same board (eg 2's, 3's and 4's)
    Differnt colours for 2,3,5
    Switch to choose different games.


Features to do:

    interactive menu

Ideas:

Boards with holes (missing positions)

A square of four cells that form a power of 4 can collapse to a single square 
that's at a half-grid position.

A cross or X pattern of 5 powers can collapse into a single cell in the middle 
- using space bar as the collapse command

The squash command that pushes tiles towards the centre and squashes 4-squares and 5-stars

The centrifuge command that flings tiles to the edges

Hexagonal board with 6 directions of tilt

Two player game

Reverse game (start with the 2048 tile and split it up)

Turn animation off (or reduce frames) for large boards.

3D cube board

Tiles decay over time back to a lower number

The game develops as you play (board grows, other powers are added)

Pentago style board with a rotate-all-sub-boards command

Each tile is its own board and boards can combine

Imaginary numbers - the real part combines on the x-axis, the imaginary on the y-axis

A maze board with internal walls

Call the game "frillion"

The anti-game - combine numbers that are dissimilar resisting the tendency for numbers to end up the same. 

Guess the combination rule.

Puzzle levels, where the board is complex like a platform game, uses gravity modelling and 
there's a fixed sequence of numbers that you have to solve the puzzle for. 

Real-time commands that can interrupt the current move part way through - so it works more like 
a balance marble maze. 

The board loses positions that you don't use often enough and can grow positions near
positions that are used a lot. 

Slowly morphing board. Eg goes from 2 x 6 -> 3 x 5 -> 4 x 4 -> 5 x 3 -> 6 x 2 and back again.

"""

import random
import math
import time
import curses
import argparse

_debug = True
_args = []


DOWN_KEY = 258
UP_KEY = 259
LEFT_KEY = 260
RIGHT_KEY = 261

UP_MOVE = [0,-1]
DOWN_MOVE = [0,1]
LEFT_MOVE = [-1,0]
RIGHT_MOVE = [1,0]


_stdscr = None
_board_scr = None
_DEBUG_SCR = None


_cell_digits = 4
_cell_size_x = _cell_digits + 2
_cell_size_y = 3

_h_border = 2
_v_border = 1


_board_size_x = 4
_board_size_y = 4


_cell_scrs = []

_history = []



class Game:

    def __init__(self, rows=6, cols=6, seeds=((3,0.9),(9,0.1)), 
                 merge_length=3, merge_lengths_func=None):

        if merge_lengths_func == None:
            self.merge_lengths_func = lambda i: [merge_length]
        else:
            self.merge_lengths_func = merge_lengths_func

        self.board = [[None for x in range(cols)] for y in range(rows)]
        self.seeds = seeds


    def initialise(self):
        self.add_seed_tile()
        self.add_seed_tile()


    def make_move(self, vector, animate=False):
        self.board, self.moved = make_move(self.board, vector, self.merge_lengths_func, animate)


    def add_seed_tile(self):
        add_seed_tile(self.board, self.seeds)


    def valid_move_exists(self):
        
        trial_board = copy_board(self.board)
        new_board, something_moved = make_move(trial_board, UP_MOVE, self.merge_lengths_func)
        if something_moved:
            return True

        trial_board = copy_board(self.board)
        new_board, something_moved = make_move(trial_board, DOWN_MOVE, self.merge_lengths_func)
        if something_moved:
            return True

        trial_board = copy_board(self.board)
        new_board, something_moved = make_move(trial_board, LEFT_MOVE, self.merge_lengths_func)
        if something_moved:
            return True

        trial_board = copy_board(self.board)
        new_board, something_moved = make_move(trial_board, RIGHT_MOVE, self.merge_lengths_func)
        if something_moved:
            return True

        return False



def get_empty_cells(board):

    empty_cells = []
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == None:
                empty_cells.append([i, j])

    return empty_cells    



def add_seed_tile(board, seeds):

    seed_list = sorted(seeds, key=lambda seed: seed[1])

    empty_cells = get_empty_cells(board)
    cell = random.choice(empty_cells)

    index = random.random()
    threshold = 0.0
    value = None
    for seed in seed_list:
        threshold += seed[1]
        if index <= threshold:
            value = seed[0]
            break

    board[cell[0]][cell[1]] = value

    return board


def show(text):
    _stdscr.addstr(text)



def create_board_scr(board):

    board_size_x = len(board[0]) * _cell_size_x + 2 * _h_border
    board_size_y = len(board) * _cell_size_y + 2 * _v_border

    max_y, max_x = _stdscr.getmaxyx()
    oy = int((max_y - board_size_y)/2)
    ox = int((max_x - board_size_x)/2)

    return _stdscr.derwin(board_size_y, board_size_x, oy, ox,)


def draw_cell(y, x, number, board_scr, y_offset=0, x_offset=0):

            cell_scr = board_scr.derwin(_cell_size_y, _cell_size_x, 
                             _v_border + y * _cell_size_y + y_offset, 
                             _h_border + x * _cell_size_x + x_offset)
            
            if number != None:
                cell_str = str(number).center(_cell_digits)
                cell_scr.attrset(curses.color_pair(
                    ((int(math.log(number, 2)) + ((number % 2) * 3))  % 7) + 1))

            else:
                cell_str = " ".center(_cell_digits)
                cell_scr.attrset(curses.color_pair(0))
            
            cell_scr.addstr(1, 1, cell_str)

            cell_scr.box()
            cell_scr.refresh()

            return cell_scr


def show_board(board, board_scr):
    global _cell_scrs


    _cell_scrs = [[None for i in range(len(board[0]))] for j in range(len(board))]


    board_scr.box()
    board_scr.refresh()

    for y in range(len(board)):
        for x in range(len(board[0])):
            _cell_scrs[y][x] = draw_cell(y, x, board[y][x], board_scr)





def add_flags_to_board(board):
    flagged_board = []
    for row in board:
        new_row = []
        for item in row:
            new_row.append([item, False])

        flagged_board.append(new_row)

    return flagged_board


def remove_flags_from_board(board):
    unflagged_board = []

    for row in board:
        new_row = []
        for item in row:
            new_row.append(item[0])

        unflagged_board.append(new_row)

    return unflagged_board



def animate_cells(cell_animation_frames, dy, dx, board_scr):

    # Takes a list of animation frames. 
    # Each animation frame is a list of cells to animate.
    # An item in the cell animation list contains:
    # [y, x, number, cell_scr]
    # eg:
    #
    #   |----------------FRAME---------|
    #   | |----CELL----|               |
    # [ [ [1, 1, 9, scr], [1, 2, 9, scr] ], [ [1, 1, 9, scr] ]  ]


    if len(cell_animation_frames) > 0:

        for cell_animation_list in cell_animation_frames:


            if len(cell_animation_list) > 0:

                y_offset = dy
                x_offset = dx * 2
                steps = 0
                if dy != 0:
                    steps = _cell_size_y

                if dx != 0:
                    steps = int(_cell_size_x / 2)

                for i in range(steps):
                    for cell in cell_animation_list:
                        cell[3].clear()
                        #cell[3].refresh()
                        cell[3] = draw_cell(cell[0], cell[1], cell[2], board_scr, y_offset, x_offset)
                
                    board_scr.refresh()
                    time.sleep(.03)
                    y_offset += dy
                    x_offset += dx * 2

                #redraw the empty cell in the wake of the moving cell

                #create a dict of moved cells
                moved_cells = {}
                for cell in cell_animation_list:
                    key = (cell[0], cell[1])
                    moved_cells[key] = True

                for cell in cell_animation_list:
                    # Check there isn't a cell moving behind this one 
                    key = (cell[0] - dy, cell[1] - dx)
                    if moved_cells.has_key(key) == False:
                        draw_cell(cell[0], cell[1], None, board_scr)




def power_merge_lengths(cell_value):
    """
    Returns a list of possible merge lengths based on the cell value.
    If the cell is a power of something then that is a valid merge lenght.
    """

    possible_merges = []
    for m in range(2, min(10, cell_value + 1)):
        # If the cell is a power of two it can do a two cell merge,
        # if it's a power of 3 it can do a three cell merge etc.
        if math.log(cell_value, m) % 1 == 0:
            possible_merges.append(m)

    return possible_merges



def make_move(board, vector, merge_lengths_func=None, animate=False):
    rows = len(board)
    cols = len(board[0])
    dx = vector[0]
    dy = vector[1]
    something_moved = False
    fboard = add_flags_to_board(board)

    #if no merging function is given, assume the functions is merging two equal cells
    if merge_lengths_func == None:
        merge_lengths_func = lambda a: [2]


    #If the vector is moving up or down
    if dy != 0:
        for i in range(len(board)-1):
            
            # Set the order of iterating over the board to 
            # get the right merging behaviour.
            if dy < 0:
                low_index = 0
                high_index = len(board)
                direction = 1
            else:
                low_index = len(board) - 1
                high_index = -1
                direction = -1

            # animate a row of cells at a time
            cells_to_animate = [[]]


            # Iterate over the cells on the board.
            # y,x is the desitination cell to move or merge into. 
            for y in range(low_index, high_index, direction):
                for x in range(len(board[0])):
                    

                    if y - dy >= 0 and y - dy < rows:
                        #if the destination cell is empty then move
                        if fboard[y][x][0] == None and fboard[y - dy][x][0] != None:
                            fboard[y][x][0] = fboard[y - dy][x][0]
                            fboard[y][x][1] = fboard[y - dy][x][1]
                            number = fboard[y - dy][x][0]
                            fboard[y - dy][x][0] = None
                            fboard[y - dy][x][1] = False
                            something_moved = True
                            if animate:
                                cells_to_animate[0].append([y - dy, x, number, _cell_scrs[y - dy][x]])

                        #if there is a valid merging of cells then move
                        elif fboard[y][x][0] != None and not fboard[y][x][1]:


                            possible_merges = merge_lengths_func(fboard[y][x][0])

                            #is there a valid merge?
                            #Try all the possible merges starting with the largest
                            valid_merge = False
                            possible_merges.sort(reverse=True)
                            for merge in possible_merges:
                                valid_merge = True
                                for j in range(1, merge):
                                    merge_y = y + j * -dy
                                    if merge_y < 0 or merge_y >= rows:
                                        valid_merge = False
                                        break
                                    if fboard[merge_y][x][1]:   #if already merged this turn
                                        valid_merge = False
                                        break
                                    if fboard[y][x][0] != fboard[merge_y][x][0]:
                                        valid_merge = False
                                        break
                                if valid_merge:
                                    break


                            if valid_merge:
                                while len(cells_to_animate) < merge - 1:
                                    cells_to_animate.append([])

                                number = fboard[y][x][0] * merge
                                fboard[y][x][0] = number
                                fboard[y][x][1] = True

                                for k in range(1, merge):
                                    fboard[y - dy * k][x][0] = None
                                    fboard[y - dy * k][x][1] = False
                                    if animate:
                                        cells_to_animate[merge - 1 - k].append([y - dy * k, x, 
                                            number, _cell_scrs[y - dy * k][x]])

                                something_moved = True


            if len(cells_to_animate[0]) > 0:
                animate_cells(cells_to_animate, dy, dx, _board_scr)


    #If the vector is moving left or right
    if dx != 0:

        for i in range(len(board[0])-1):

            #animate a column of cells at a time
            cells_to_animate = [[]]
            for y in range(len(board)):

                if dx < 0:
                    low_index = 0
                    high_index = len(board[0])
                    direction = 1
                else:
                    low_index = len(board[0]) - 1
                    high_index = -1
                    direction = -1

                for x in range(low_index, high_index, direction):
                    
                    if x - dx >= 0 and x - dx < cols:
                        #if the destination cell is empty
                        if fboard[y][x][0] == None and fboard[y][x - dx][0] != None:
                            fboard[y][x][0] = fboard[y][x - dx][0]
                            fboard[y][x][1] = fboard[y][x - dx][1]
                            number = fboard[y][x - dx][0]
                            fboard[y][x - dx][0] = None
                            fboard[y][x - dx][1] = False
                            something_moved = True
                            if animate:
                                cells_to_animate[0].append([y, x - dx, number, _cell_scrs[y][x - dx]])

                        #if there is a valid merging of cells then move
                        elif fboard[y][x][0] != None and not fboard[y][x][1]:


                            possible_merges = merge_lengths_func(fboard[y][x][0])

                            #is there a valid merge?
                            #Try all the possible merges starting with the largest
                            valid_merge = False
                            possible_merges.sort(reverse=True)
                            for merge in possible_merges:
                                valid_merge = True
                                for j in range(1, merge):
                                    merge_x = x + j * -dx
                                    if merge_x < 0 or merge_x >= cols:
                                        valid_merge = False
                                        break
                                    if fboard[y][merge_x][1]:   #if already merged this turn
                                        valid_merge = False
                                        break
                                    if fboard[y][x][0] != fboard[y][merge_x][0]:
                                        valid_merge = False
                                        break
                                if valid_merge:
                                    break


                            if valid_merge:
                                while len(cells_to_animate) < merge - 1:
                                    cells_to_animate.append([])

                                number = fboard[y][x][0] * merge
                                fboard[y][x][0] = number
                                fboard[y][x][1] = True
                                for k in range(1, merge):
                                    fboard[y][x - dx * k][0] = None
                                    fboard[y][x - dx * k][1] = False

                                    if animate:
                                        cells_to_animate[merge - 1 - k].append([y, x - dx * k, 
                                            number, _cell_scrs[y][x - dx * k]])

                                something_moved = True


            if len(cells_to_animate) > 0:
                animate_cells(cells_to_animate, dy, dx, _board_scr)


    board = remove_flags_from_board(fboard)

    return (board, something_moved)


def copy_board(board):
    new_board = []
    new_row = []

    for row in board:
        new_row = list(row)
        new_board.append(new_row)

    return new_board


def save_history(board):
    _history.append(copy_board(board))


def pop_history(board):
#    if len(_history) > 0:
#        board = _history.pop()
    board = _history.pop()



def create_seed_distribution(seed_values, distribution):
    total_probability = 0

    distribution_list = []

    for i in range(len(seed_values)):
        probability = (1 - total_probability)

        if i < len(seed_values) - 1:
            probability = probability * distribution

        distribution_list.append((seed_values[i], probability))
        total_probability += probability

    return tuple(distribution_list)



def main(stdscr):
    global _stdscr, _board_scr, _DEBUG_SCR

    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)


    curses.curs_set(0)
    _stdscr = stdscr
    _DEBUG_SCR = stdscr.subwin(_stdscr.getmaxyx()[0] - 12, 0)

    #set up game...

    quit = False

    while quit != True:
        quit = not(_args.interactive)
    
        game_kwargs = {}
        distribution = 0.75

        if _args.distribution != None:
            distribution = _args.distribution

        if _args.basic != None:
            power = _args.basic

            game_kwargs['rows'] = power*2
            game_kwargs['cols'] = power*2

            if _args.multiple:

                seed_values = []
                for i in range(2, power + 1):
                    seed_values.append(i)

                game_kwargs['seeds'] = create_seed_distribution(seed_values, distribution)

            else:

                game_kwargs['merge_length'] = power
                game_kwargs['seeds'] = ((power, 0.9), (power**2, 0.1))


        if _args.rows != None:
            game_kwargs['rows'] = _args.rows

        if _args.cols != None:
            game_kwargs['cols'] = _args.cols

        if _args.multiple:
            game_kwargs['merge_lengths_func'] = power_merge_lengths

        if _args.seeds != None and len(_args.seeds) > 0:
            game_kwargs['seeds'] = create_seed_distribution(_args.seeds, distribution)



        game = Game(**game_kwargs)

        #game = Game()
        #game = Game(rows=6, cols=6, seeds=((3,0.9),(9,0.1)), merge_length=3)
        #game = Game(rows=6, cols=6, seeds=((4,0.9),(16,0.1)), merge_length=4)
        #game = Game(rows=6, cols=6, seeds=((2,0.85),(3,0.15)), merge_lengths_func=power_merge_lengths)
        #game = Game(rows=7, cols=7, seeds=((5,1),), merge_lengths_func=power_merge_lengths)
        #game = Game(rows=5, cols=5, seeds=((3,1),), merge_lengths_func=power_merge_lengths)



        _board_scr = create_board_scr(game.board)

        game.initialise()


        show_board(game.board, _board_scr)
        
        while game.valid_move_exists():
            vector = []
            command_chr = _stdscr.getch()
            if command_chr == UP_KEY or command_chr == ord("k"):
                vector = UP_MOVE
            elif command_chr == DOWN_KEY or command_chr == ord("j"):
                vector = DOWN_MOVE
            elif command_chr == LEFT_KEY or command_chr == ord("h"):
                vector = LEFT_MOVE
            elif command_chr == RIGHT_KEY or command_chr == ord("l"):
                vector = RIGHT_MOVE
            #elif chr(command_chr) == "z":
            #    pop_history(_board)


            #save_history(_board)
            if vector != []:
                game.make_move(vector, animate=True)
                if game.moved:
                    game.add_seed_tile()
            #    else:
            #        pop_history(_board)
            #else:
            #    pop_history(_board)

            show_board(game.board, _board_scr)

        show("\n\n")
        show(" ==================== GAME OVER ==================== ".center(_stdscr.getmaxyx()[1]))
        _stdscr.getch()

        _stdscr.clear()
        _stdscr.refresh()



def DEBUG(msg, wait=False):
    if _debug:
        y, x = _DEBUG_SCR.getyx()
        max_y, max_x = _DEBUG_SCR.getmaxyx()

        if y >= max_y - 3:
            _DEBUG_SCR.clear()
            _DEBUG_SCR.move(0, 0)


        _DEBUG_SCR.addstr(str(msg) + "\n")
        _DEBUG_SCR.refresh()

        if wait:
            _DEBUG_SCR.getch()


def probability_arg(arg_str):
    prob = float(arg_str)

    if prob < 0 or prob > 1.0:
        msg = "Probablility must be between 0 and 1."
        raise argparse.ArgumentTypeError(msg)

    return prob


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='A game of combining sliding numeric tiles.')
    argparser.add_argument('-b', '--basic', type=int)
    argparser.add_argument('-r', '--rows', type=int)
    argparser.add_argument('-c', '--cols', type=int)
    argparser.add_argument('-d', '--distribution', type=probability_arg)
    argparser.add_argument('-m', '--multiple', action='store_true')
    argparser.add_argument('-i', '--interactive', action='store_true')
    argparser.add_argument('-s', '--seeds', type=int, nargs='*')
    _args = argparser.parse_args()

    curses.wrapper(main)
