from board import Board, Direction, BellState

dirs = {'down': Direction.DOWN, 'up': Direction.UP, 'left': Direction.LEFT, 'right': Direction.RIGHT}
p1 = Board()
p2 = Board()

def init_player_ships():
    while True:
        i, j = input("Player 1, please place your Φ+ ship - two space separated integer coordinates.\n").split(" ")
        i = int(i)
        j = int(j)
        if i >= 0 and i < Board.BOARD_SIZE and j >= 0 and j < Board.BOARD_SIZE:
            break
        else:
            print("An out of bounds coordinate was specified.")

    dir = input("Please enter a direction for your ship. [up, down, left, right]\n").lower()
    while dir not in dirs:
        print("An incorrect direction was specified. Please specify a valid direction.")
        dir = input("Please enter a direction for your ship. [up, down, left, right]\n").lower()
    
    p1.place_ship(BellState.PHIPLUS, i, j, Direction.DOWN)

if __name__ == "__main__":
    while 1:
        print(f"Welcome to SuperMunition. The board size is {p1.BOARD_SIZE}.")
        init_player_ships()
        