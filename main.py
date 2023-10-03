from board import Board, Direction, BellState

b = Board()

b.place_ship(BellState.PHIPLUS, 0, 0, Direction.RIGHT)
print(b.qc)
print(b)