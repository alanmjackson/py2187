''' 
unit test for py2187.py
@author: Alan M Jackson 
'''

import unittest

import py2187


N = None

class Test(unittest.TestCase):
    
    def test_multiple_combinations(self):
        board = [
                 [None, None, None, None],
                 [None, None, None, None],
                 [None, None, None, None],
                 [2,    2,    2,    2   ]
                ]

        expected_board = [
                 [None, None, None, None],
                 [None, None, None, None],
                 [None, None, None, None],
                 [4,    4,    None, None]
                ]

        shifted_board, shifted = py2187.make_move(board, [-1, 0])
        self.assertTrue(shifted_board == expected_board)



    def test_multi_combinations2(self):
        board = [
                 [2,    None, None, None],
                 [None, None, None, None],
                 [2,    None, None, None],
                 [2,    None, None, None]
                ]

        expected_board = [
                 [None, None, None, None],
                 [None, None, None, None],
                 [2,    None, None, None],
                 [4,    None, None, None]
                ]        

        shifted_board, shifted = py2187.make_move(board, [0, 1])
        self.assertTrue(shifted_board == expected_board)


    def test_multi_combinations3(self):
        board = [
                 [None, None, None, None],
                 [None, None, None, None],
                 [None, None, None, None],
                 [2,    None, 2,    2   ]
                ]

        expected_board = [
                 [None, None, None, None],
                 [None, None, None, None],
                 [None, None, None, None],
                 [None, None, 2,    4   ]
                ]        

        shifted_board, shifted = py2187.make_move(board, [1, 0])
        self.assertTrue(shifted_board == expected_board)


    def test_multi_different_combinations(self):
        board = [
                 [2,    None, None, None],
                 [2,    None, None, None],
                 [4,    None, None, None],
                 [4,    None, None, None]
                ]

        expected_board = [
                 [None, None, None, None],
                 [None, None, None, None],
                 [4,    None, None, None],
                 [8,    None, None, None]
                ]        

        shifted_board, shifted = py2187.make_move(board, [0, 1])
        self.assertTrue(shifted_board == expected_board)



    def test_creating_other_board_sizes(self):

        game = py2187.Game(rows=5, cols=5)

        self.assertTrue(len(game.board) == 5)
        self.assertTrue(len(game.board[0]) == 5)
        self.assertTrue(game.board[0][0] == None)


    def test_moving_other_board_sizes(self):

        game = py2187.Game(rows=5, cols=5, merge_length=2)        

        board = [
                 [2,    None, None, None, None],
                 [2,    None, None, None, None],
                 [4,    None, None, None, None],
                 [4,    None, None, None, 2],
                 [8,    None, None, None, 2],
                ]

        expected_board = [
                 [None, None, None, None, None],
                 [None, None, None, None, None],
                 [4,    None, None, None, None],
                 [8,    None, None, None, None],
                 [8,    None, None, None, 4],
                ]        


        game.board = board
        game.make_move([0, 1])
        self.assertTrue(game.board == expected_board)


    def test_seeds(self):

        game = py2187.Game(seeds=((7, 1),))

        game.add_seed_tile()
        game.add_seed_tile()

        tile_count = 0
        for row in game.board:
            for cell in row:
                if cell == 7:
                    tile_count += 1

        self.assertTrue(tile_count == 2)


    def test_powers_of_three_game(self):

        game = py2187.Game(rows=5, cols=5, seeds=((3,1)), merge_length=3)

        board = [
                 [3,    None, None, None, None],
                 [3,    None, None, None, None],
                 [3,    None, None, None, None],
                 [9,    None, None, None, None],
                 [9,    None, None, None, None],
                ]

        expected_board = [
                 [None, None, None, None, None],
                 [None, None, None, None, None],
                 [9,    None, None, None, None],
                 [9,    None, None, None, None],
                 [9,    None, None, None, None],
                ]        

        game.board = board
        game.make_move([0, 1])
        self.assertTrue(game.board == expected_board)


    def test_powers_of_three_game_horiz(self):

        game = py2187.Game(rows=5, cols=5, seeds=((3,1)), merge_length=3)

        board = [
                 [3,    3,    9,    9,    9],
                 [None, None, None, None, None],
                 [None, None, None, None, None],
                 [None, None, None, None, None],
                 [None, None, None, None, None],
                ]

        expected_board = [
                 [None, None, 3,    3,    27],
                 [None, None, None, None, None],
                 [None, None, None, None, None],
                 [None, None, None, None, None],
                 [None, None, None, None, None],
                ]        

        game.board = board
        game.make_move([1, 0])
        self.assertTrue(game.board == expected_board)


    def test_power_merge_lengths_func(self):

        merge_lengths = py2187.power_merge_lengths(2)
        self.assertTrue(merge_lengths == [2])

        merge_lengths = py2187.power_merge_lengths(4)
        self.assertTrue(merge_lengths == [2, 4])

        merge_lengths = py2187.power_merge_lengths(3)
        self.assertTrue(merge_lengths == [3])

        merge_lengths = py2187.power_merge_lengths(9)
        self.assertTrue(merge_lengths == [3, 9])

        merge_lengths = py2187.power_merge_lengths(64)
        self.assertTrue(merge_lengths == [2, 4, 8])

        merge_lengths = py2187.power_merge_lengths(13)
        self.assertTrue(merge_lengths == [])





    def test_powers_of_two_and_three_game_horiz(self):

        merge_lengths_func = py2187.power_merge_lengths

        game = py2187.Game(rows=5, cols=5, seeds=((2,60),(3,30),(4,10)), 
                             merge_lengths_func=merge_lengths_func)

        board = [
                 [2,    2,    9,    9,    9],
                 [9,    9,    2,    2,    2],
                 [None, None, None, None, None],
                 [None, None, None, None, None],
                 [None, None, None, None, None],
                ]

        expected_board = [
                 [None, None, None, 4,    27],
                 [None, 9,    9,    2,    4],
                 [None, None, None, None, None],
                 [None, None, None, None, None],
                 [None, None, None, None, None],
                ]        

        self.assertTrue(game.merge_lengths_func == py2187.power_merge_lengths)

        game.board = board
        game.make_move([1, 0])
        self.assertTrue(game.board == expected_board)


    def test_powers_of_two_and_three_game_vert(self):

        merge_lengths_func = py2187.power_merge_lengths

        game = py2187.Game(rows=5, cols=5, seeds=((2,60),(3,30),(4,10)), 
                             merge_lengths_func=merge_lengths_func)



        board = [
                 [2, 2, N, N, N],
                 [9, 9, N, N, N],
                 [9, 2, N, N, N],
                 [9, 2, N, N, N],
                 [2, 9, N, N, N],
                ]

        expected_board = [
                 [N,  N, N, N, N],
                 [N,  2, N, N, N],
                 [2,  9, N, N, N],
                 [27, 4, N, N, N],
                 [2,  9, N, N, N],
                ]        

        self.assertTrue(game.merge_lengths_func == py2187.power_merge_lengths)

        game.board = board
        game.make_move([0, 1])
        self.assertTrue(game.board == expected_board)



    def test_merging_powers_of_four_vert(self):

        merge_lengths_func = py2187.power_merge_lengths

        game = py2187.Game(rows=5, cols=5, seeds=((2,60),(3,30),(4,10)), 
                             merge_lengths_func=merge_lengths_func)



        board = [
                 [2,  N,  N,  N,  N],
                 [4,  N,  N,  N,  N],
                 [4,  N,  N,  N,  N],
                 [4,  N,  N,  N,  N],
                 [4,  N,  N,  N,  N],
                ]

        expected_board = [
                 [N,  N,  N,  N,  N],
                 [N,  N,  N,  N,  N],
                 [N,  N,  N,  N,  N],
                 [2,  N,  N,  N,  N],
                 [16, N,  N,  N,  N],
                ]        

        self.assertTrue(game.merge_lengths_func == py2187.power_merge_lengths)

        game.board = board
        game.make_move([0, 1])
        self.assertTrue(game.board == expected_board)


    def test_merging_powers_of_four_horiz(self):

        merge_lengths_func = py2187.power_merge_lengths

        game = py2187.Game(rows=5, cols=5, seeds=((2,60),(3,30),(4,10)), 
                             merge_lengths_func=merge_lengths_func)



        board = [
                 [2,  4,  4,  4,  4],
                 [N,  N,  N,  N,  N],
                 [N,  N,  N,  N,  N],
                 [N,  N,  N,  N,  N],
                 [N,  N,  N,  N,  N],
                ]

        expected_board = [
                 [N,  N,  N,  2, 16],
                 [N,  N,  N,  N,  N],
                 [N,  N,  N,  N,  N],
                 [N,  N,  N,  N,  N],
                 [N, N,  N,  N,  N],
                ]        

        self.assertTrue(game.merge_lengths_func == py2187.power_merge_lengths)

        game.board = board
        print_board(board, "initial board")
        game.make_move([1, 0])
        print_board(expected_board, "expected_board")
        print_board(game.board, "game.board")
        self.assertTrue(game.board == expected_board)



def print_board(board, msg="board"):
    print(msg)
    for line in board:
        line_str = ""
        for item in line:
            line_str += str(item).center(6)

        print(line_str)
    print("----")



if __name__ == "__main__":
    unittest.main()
    


