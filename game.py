from board import Board, Direction, BellState, TurnResult
import time

dirs = {'down': Direction.DOWN, 'up': Direction.UP, 'left': Direction.LEFT, 'right': Direction.RIGHT}
states = {BellState.PHIPLUS: "Φ+", BellState.PHIMINUS: "Φ-", BellState.PSIPLUS: "𝛙+", BellState.PSIMINUS: "𝛙-"}

def init_player_ship(p: int, player: Board, state: BellState):
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
    print("\033c")
    
def begin_game():
    p1 = Board()
    p2 = Board()
    print(f"Welcome to SuperMunition. The board size is {p1.BOARD_SIZE}.")
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
    return (abs(i - oi) == 1 and j - oj == 0) or (abs(j - oj) == 1 and i - oi == 0)

def move_ship(p: Board, opponent: Board, surv_bs: BellState):
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
    p.move_ship(bs=surv_bs, hit_space=hit_space, new_space=(i,j))
    print(p.see_ships())
    print("ENTANGLEMENT SWAPPING COMPLETE.")
    time.sleep(2)
    blank_terminal()

def shoot_ship(p: Board, opponent: Board, i: int, j: int, surv_bs: BellState = None):
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
        time.sleep(2)
        if surv_bs is not None:
            for loc in p.ships[surv_bs]:
                if Board.BOARD_SIZE * loc[0] + loc[1] in p.ship_hit_indices:
                    hit_space = loc
                else:
                    pivot = loc
            if p.movable(pivot[0], pivot[1], hit_space[0], hit_space[1]):
                move_ship(p, opponent, surv_bs)
            else:
                print("The ship is trapped! Go sink it!")
    return False

def game_loop(p1: Board, p2: Board):
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
                i = int(input(f"How many turns ago would you like to see? (\"0\" would be the current turn.) There have been {len(player.past_boards)} turns.\n").strip())
                while not 0 <= i < len(player.past_boards):
                    print("That number of turns ago is invalid.")
                    i = int(input("How many turns ago would you like to see?\n").strip())
                print(player.get_board(-1 - i))
                    
                
            print(f"Player {num}, shoot a ship.")
            choice = input("Two space separated integer coordinates.\n").strip().replace(',', ' ')
            while choice in ('ships'):
                if choice == 'ships':
                    print(player.ships)
                    choice = input("Two space separated integer coordinates.\n").strip().replace(',', ' ')
            i,j = map(int, choice.split())
            if shoot_ship(player, opponent, i, j):
                return num

if __name__ == "__main__":
    while 1:
        p1, p2 = begin_game()
        # ships are placed - start game
        win = game_loop(p1, p2)
        print(f"Player {win} wins!")
        if input("Do you want to play again? (y/n)").lower().strip() == 'n':
            break