from board import Board, Direction, BellState, TurnResult

dirs = {'down': Direction.DOWN, 'up': Direction.UP, 'left': Direction.LEFT, 'right': Direction.RIGHT}
states = {BellState.PHIPLUS: "Φ+", BellState.PHIMINUS: "Φ-", BellState.PSIPLUS: "𝛙+", BellState.PSIMINUS: "𝛙-"}

def init_player_ship(p: int, player: Board, state: BellState):
    while True:
        i, j = map(int, input(f"Player {p}, please place your {states[state]} ship - two space separated integer coordinates.\n").strip().replace(',', ' ').split())
        i = int(i)
        j = int(j)
        if i >= 0 and i < Board.BOARD_SIZE and j >= 0 and j < Board.BOARD_SIZE:
            break
        else:
            print("An out of bounds coordinate was specified.")

    dir = input("Please enter a direction for your ship. [up, down, left, right]\n").lower().strip()
    while dir not in dirs:
        print("An incorrect direction was specified. Please specify a valid direction.")
        dir = input("Please enter a direction for your ship. [up, down, left, right]\n").lower().strip()
    
    # checking direction bounds?
    if not player.place_ship(state, i, j, dirs[dir]):
        print("That placement was invalid. Please replace the ship.")
        init_player_ship(p, player, state)
    else:
        print(player.see_ships())

def begin_game():
    p1 = Board()
    p2 = Board()
    print(f"Welcome to SuperMunition. The board size is {p1.BOARD_SIZE}.")
    # init p1 ships
    for state in states:
        init_player_ship(1, p2, state)

    for state in states:
        init_player_ship(2, p1, state)
    
    return p1, p2

def shoot_ship(p: Board, i: int, j: int):
    result = p.get_attack_result(i, j)
    if TurnResult.SUNK in result:
        print(f"You sank ship {states[result[1]]}!")
        print(p.lost())
        if p.lost():
            return True
        i, j = map(int, input("Shoot another square: two space separated integer coordinates.\n").strip().replace(',', ' ').split())
        return shoot_ship(p, i, j)
    elif TurnResult.HIT in result:
        print(f"You hit ship {states[result[1]]}! Shoot another square.")
        i, j = map(int, input("Shoot another square: two space separated integer coordinates.\n").strip().replace(',', ' ').split())
        return shoot_ship(p, i, j)
    else:
        print("You missed.")
    return False

def game_loop(p1: Board, p2: Board):
    while 1:
        # p1 takes a turn, shooting p2's ship
        print("--------------------------------")
        print("----- PLAYER 1 BOARD STATE -----")
        p1.init_board()
        print(p1)
        while input("Would you like to see past boards? (y/n)\n").lower().strip() != "n":
            i = int(input(f"How many turns ago would you like to see? (\"0\" would be the current turn.) There have been {len(p1.past_boards)} turns.\n").strip())
            while not 0 <= i < len(p1.past_boards):
                print("That number of turns ago is invalid.")
                i = int(input("How many turns ago would you like to see?\n").strip())
            print(p1.get_board(-1 - i))
                
            
        print(f"Player 1, shoot a ship.")
        # TODO bounds
        i, j = map(int, input("Two space separated integer coordinates.\n").strip().replace(',', ' ').split())
        #i = int(i)
        #j = int(j)
        if shoot_ship(p1, i, j):
            return 1
        print("--------------------------------")
        print("----- PLAYER 2 BOARD STATE -----")
        p2.init_board()
        print(p2)
        while input("Would you like to see past boards? (y/n)\n").lower().strip() != "n":
            i = int(input(f"How many turns ago would you like to see? There have been {len(p1.past_boards)} turns.\n").strip())
            while not 0 <= i < len(p2.past_boards):
                print("That number of turns ago is invalid.")
                i = int(input("How many turns ago would you like to see?\n").strip())
            print(p2.get_board(-1 - i))
        print(f"Player 2, shoot a ship.")
        # TODO bounds
        i, j = input("Two space separated integer coordinates.\n").strip().replace(',', ' ').split()
        i = int(i)
        j = int(j)
        if shoot_ship(p2, i, j):
            return 2


if __name__ == "__main__":
    while 1:
        p1, p2 = begin_game()
        # ships are placed - start game
        win = game_loop(p1, p2)
        print(f"Player {win} wins!")
        if input("Do you want to play again? (y/n)").lower().strip() == 'n':
            break