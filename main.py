from board import Board, Direction, BellState

b = Board()
#b.measure_board()
b.place_ship(BellState.PHIPLUS, 0,0, Direction.DOWN)
b.entangle_swap(hit_space=2, new_space=1)
b.measure_board()

#b.place_ship(BellState.PHIPLUS, 0, 0, Direction.RIGHT)
print(b)