from board import Board, Direction, BellState, TurnResult
import time

# some convenient maps for us to use
dirs = {'down': Direction.DOWN, 'up': Direction.UP, 'left': Direction.LEFT, 'right': Direction.RIGHT}
states = {BellState.PHIPLUS: "Φ+", BellState.PHIMINUS: "Φ-", BellState.PSIPLUS: "𝛙+", BellState.PSIMINUS: "𝛙-"}

def init_player_ship(p: int, player: Board, state: BellState):
    """
    Initializes a player ship, validating input. Places itself on the board.
    """
    while True:
        choice = input(f"Player {p}, please place your {states[state]} ship - two space separated integer coordinates.\n").strip().replace(',', ' ')
        while len(choice.split()) != 2:
            print("Invalid coordinates detected. Please enter your coordinates in two numbers separated by a space.")
            choice = input(f"Player {p}, please place your {states[state]} ship - two space separated integer coordinates.\n").strip().replace(',', ' ')
        i, j = map(int, choice.split())
        
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
        print(player.see_ships(), flush=True)

def blank_terminal():
    """
    Helper to blank the terminal.
    """
    print("\033c")
    
def begin_game():
    """
    Prints rules, initializes ships, and returns initialized player objects.
    """
    p1 = Board()
    p2 = Board()
    blank_terminal()
    print(f"Welcome to SuperMunition. The board size is {p1.BOARD_SIZE}.")
    print("Game rules: Each player has each of the 4 Bell states as a 2 square ship.\n")
    print("Each player will place their Bell states on a certain square, specifying a coordinate and a direction.")
    print("Then, players will take turns trying to sink each other's ships.\n")
    print("The turn will begin by allowing the current player to see past board measurements.")
    print("The current player can choose to see a past board or fire a shot. Upon a hit,")
    print("the player will be granted another chance to hit a ship.\n")
    print("If a ship is hit and then missed, entanglement swapping begins. The player whose")
    print("ship was hit is given the chance to swap their ship away to an adjacent square.\n\n")
    # init p1 ships
    for state in states:
        init_player_ship(1, p2, state)
    # print("\n "*40)
    blank_terminal()
    for state in states:
        init_player_ship(2, p1, state)
    blank_terminal()
    
    return p1, p2

def adj(i, j, oi, oj):
    """
    Helper function to return whether a square (i, j) is adjacent to (oi, oj).
    """
    return (abs(i - oi) == 1 and j - oj == 0) or (abs(j - oj) == 1 and i - oi == 0)

def move_ship(p: Board, opponent: Board, surv_bs: BellState):
    """
    Entanglement Swapping helper. Validates input and entanglement swaps to the square the user specifies.
    """
    for loc in p.ships[surv_bs]:
        if Board.BOARD_SIZE * loc[0] + loc[1] in p.ship_hit_indices:
            hit_space = loc
        else:
            pivot = loc
    blank_terminal()
    print("ENTANGLEMENT SWAPPING TIME\nOPPONENT: MAKE YOUR CHOICE\n-\nCURRENT PLAYER: LOOK AWAY")
    time.sleep(5)

    print(p.see_ships(hit_space[0], hit_space[1]))
    print(f"\nYour current {states[surv_bs]} ship is at position ({pivot[0]},{pivot[1]})-({hit_space[0]},{hit_space[1]})")
    print(f"({hit_space[0]},{hit_space[1]}) has been hit. Select a valid space adjacent to ({pivot[0]},{pivot[1]}) for the hit part to rotate to:")
    
    choice = input(f"Please enter your coordinates in two integers separated by a space.\n").strip().replace(',', ' ').split()
    while len(choice) != 2 or p.check_conflict(int(choice[0]), int(choice[1])) or not adj(pivot[0], pivot[1], int(choice[0]), int(choice[1])):
        print("Invalid coordinates detected.\nYou cannot swap to a position your opponent has already guessed or which is not adjacent to the surviving half of the ship. \nPlease enter your coordinates in two numbers separated by a space.")
        choice = input(f"Please place your {states[surv_bs]} ship - two space separated integer coordinates.\n").strip().replace(',', ' ').split()
    i, j = map(int, choice)
    # this is where the magic happens
    p.move_ship(bs=surv_bs, hit_space=hit_space, new_space=(i,j))

    print(p.see_ships()) # print the updated board
    print("ENTANGLEMENT SWAPPING COMPLETE.")
    blank_terminal()

def shoot_ship(p: Board, opponent: Board, i: int, j: int, surv_bs: BellState = None):
    """
    Helper to shoot a ship at i, j. Tracks if a Bell state survives and invokes swapping accordingly.
    """
    result = p.get_attack_result(i, j)

    if TurnResult.INVALID in result:
        print("Invalid shot. You cannot target spots twice and all shots must be in bounds.")
        choice = input("Shoot another square: two space separated integer coordinates.\n").strip().replace(',', ' ')
        while choice in ('ships'):
            if choice == 'ships':
                print(p.ships)
                choice = input("Shoot another square: two space separated integer coordinates.\n").strip().replace(',', ' ')
        i, j = map(int, choice.split())
        return shoot_ship(p, opponent, i, j, surv_bs=surv_bs)
    
    elif TurnResult.SUNK in result:
        print(f"You sank ship {states[result[1]]}!")
        if p.lost():
            return True
        choice = input("Shoot another square: two space separated integer coordinates.\n").strip().replace(',', ' ')
        while choice in ('ships'):
            if choice == 'ships':
                print(p.ships)
                choice = input("Shoot another square: two space separated integer coordinates.\n").strip().replace(',', ' ')
        i, j = map(int, choice.split())
        return shoot_ship(p, opponent, i, j)
    
    elif TurnResult.HIT in result:
        print(f"You hit ship {states[result[1]]}! Shoot another square.")
        choice = input("Shoot another square: two space separated integer coordinates.\n").strip().replace(',', ' ')
        while choice in ('ships'):
            if choice == 'ships':
                print(p.ships)
                choice = input("Shoot another square: two space separated integer coordinates.\n").strip().replace(',', ' ')
        i, j = map(int, choice.split())
        return shoot_ship(p, opponent, i, j, surv_bs = result[1])
    
    else:
        print("You missed.")
        if surv_bs is not None:
            for loc in p.ships[surv_bs]:
                if Board.BOARD_SIZE * loc[0] + loc[1] in p.ship_hit_indices:
                    hit_space = loc
                else:
                    pivot = loc
            if p.movable(pivot[0], pivot[1], hit_space[0], hit_space[1]):
                time.sleep(2)
                move_ship(p, opponent, surv_bs)
            else:
                print("The ship is trapped! Sink it on your next turn!")
    return False

def game_loop(p1: Board, p2: Board):
    """
    Primary game loop. Calls helpers for each stage of the game and continues until a player has 
    lost.
    """
    while 1:
        players = (p1, p2)
        for player in players:
            num  = 1 if player == p1 else 2
            opponent = p1 if player == p2 else p2
            blank_terminal()
            print("--------------------------------")
            print(f"----- PLAYER {num} BOARD STATE -----")
            player.init_board()
            print(player)
            while input("Would you like to see past boards? (y/n)\n").lower().strip() != "n":
                i = input(f"How many turns ago would you like to see? (\"0\" would be the current turn.) There have been {len(player.past_boards)} turns.\n").strip()
                while not i.isdecimal or not 0 <= int(i) < len(player.past_boards):
                    print("That number of turns ago is invalid.")
                    i = int(input("How many turns ago would you like to see?\n").strip())
                print(player.get_board(-1 - int(i)))
                    
                
            print(f"Player {num}, shoot a ship.")
            choice = input("Two space separated integer coordinates.\n").strip().replace(',', ' ')
            while choice in ('ships'):
                if choice == 'ships':
                    print(player.ships)
                    choice = input("Two space separated integer coordinates.\n").strip().replace(',', ' ')
            i,j = map(int, choice.split())
            if shoot_ship(player, opponent, i, j):
                return num
            time.sleep(3)

# main function to kick off the game.
if __name__ == "__main__":
    while 1:
        p1, p2 = begin_game()
        # ships are placed - start game
        win = game_loop(p1, p2)
        print(f"Player {win} wins!")
        if input("Do you want to play again? (y/n)").lower().strip() == 'n':
            break