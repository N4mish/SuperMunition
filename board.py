from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
import numpy as np
from enum import Enum
from qiskit.visualization import plot_histogram
import copy
from typing import Tuple


class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

class BellState(Enum):
    PHIPLUS = 0
    PHIMINUS = 1
    PSIPLUS = 2
    PSIMINUS = 3

class TurnResult(Enum):
    HIT = 0
    SUNK = 1
    MISS = 2
    INVALID = 3

states = {BellState.PHIPLUS: "Φ+", BellState.PHIMINUS: "Φ-", BellState.PSIPLUS: "𝛙+", BellState.PSIMINUS: "𝛙-"}

class Board:
    BOARD_SIZE = 8 
    def __init__(self):
        """
        Constructor for a player's board.
        """
        self.board: [[int]] = [] # 8 x 8 board
        self.ships: {BellState:[[int]]} = {} # list of ships
        self.miss_indices = [] # Measured/greyed out spaces
        self.past_boards = []
        self.ship_hit_indices = {}
        self.qr = QuantumRegister(self.BOARD_SIZE ** 2)
        self.cr = ClassicalRegister(self.BOARD_SIZE ** 2)
        self.qc = QuantumCircuit(self.qr, self.cr)
        for i in range(self.BOARD_SIZE):
            self.board.append([0 for j in range(self.BOARD_SIZE)])
        self.init_board()

    def __str__(self):
        """
        Prints the board.
        """
        st = ("-" * (self.BOARD_SIZE * 3 + 1)) + "\n"
        for row in self.board:
            for space in row:
                st += f"|{space}"
            st += '|\n'
            st += ("-" * (self.BOARD_SIZE * 3 + 1)) + "\n"
        return st

    def get_board(self, index = -1):
        """
        Returns the past board with a given index, defaulting to -1
        """
        st = ("-" * (self.BOARD_SIZE * 3 + 1)) + "\n"
        for row in self.past_boards[index]:
            for space in row:
                st += f"|{space}"
            st += '|\n'
            st += ("-" * (self.BOARD_SIZE * 3 + 1)) + "\n"
        return st

    def see_ships(self, i = -1, j = -1):
        """
        Returns a string representation of the board with ship locations
        """
        ship_locs = {}
        for bs, pair in self.ships.items():
            for loc in pair:
                ship_locs[loc[0] * self.BOARD_SIZE + loc[1]] = states[bs]
        st = ("-" * (self.BOARD_SIZE * 3 + 1)) + "\n"
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                loc = row * self.BOARD_SIZE + col
                if i == row and j == col:
                    st += "|O "
                elif loc in self.miss_indices or loc in self.ship_hit_indices:
                    st += f"|X "
                elif loc in list(ship_locs.keys()):
                    st += f"|{ship_locs[loc]}"
                else:
                    st += f"|  "
            st += '|\n'
            st += ("-" * (self.BOARD_SIZE * 3 + 1)) + "\n"
        return st

    def get_num_ships(self):
        """
        Returns the number of remaining ships
        """
        return len(self.ships)

    def place_ship(self, bs: BellState, i: int, j: int, dir: Direction)->bool:
        """
        Places a ship at the specified coordinates and direction, entangling the qubits.
        """
        # TODO ASSUMING INDICES ARE IN BOUNDS
        # TODO bounds checking in user code
        if dir == Direction.UP:
            other_index = [i - 1, j]
        elif dir == Direction.DOWN:
            other_index = [i + 1, j]
        elif dir == Direction.LEFT:
            other_index = [i, j - 1]
        else:
            other_index = [i, j + 1]
        
        if self.check_conflict(i, j) or self.check_conflict(other_index[0], other_index[1]):
            return False
        self.ships[bs] = [[i, j], other_index]
        spot_1 = (self.BOARD_SIZE * i + j)
        spot_2 = (self.BOARD_SIZE * other_index[0] + other_index[1])
        self.make_bell_state(spot_1, spot_2, bs)
        return True

    def sink_ship(self, bs: BellState):
        """
        Removes a ship once it is sunk
        """
        del self.ships[bs]
        
    def make_bell_state(self, ship_1: int, ship_2: int, bs: BellState):
        """
        Given two absolute ship specifiers ((BOARD_SIZE * i) + j), sets up a bell state between 
        them.
        """
        self.qc.h(self.qr[ship_2]) # cancel out original hadamard
        self.qc.cx(self.qr[ship_1], self.qr[ship_2])
        if bs == BellState.PSIPLUS:
            self.qc.x(self.qr[ship_1])
        elif bs == BellState.PHIMINUS:
            self.qc.z(self.qr[ship_1])
        elif bs == BellState.PSIMINUS:
            self.qc.x(self.qr[ship_1])
            self.qc.z(self.qr[ship_1])
            
    #def shoot_ship(self, ship_i, ship_j):
    #    """
    #    Logic for shooting a ship.
    #    Add to targeted, measure, print board
    #    """
    #    self.targeted_indices.append(self.BOARD_SIZE * ship_i + ship_j)
    #    self.measure_board()

    def measure_board(self):
        """
        Measures all spots on the board, excluding previously targeted squares. Updates
        the board state variable accordingly.
        """
        # for i in range(self.BOARD_SIZE):
        #     for j in range(self.BOARD_SIZE):
        #         index = i * self.BOARD_SIZE + j
        #         if index not in self.targeted:
        #             self.qc.measure(index, index)
        self.qc.measure([i for i in range(self.BOARD_SIZE ** 2) if i not in self.miss_indices],
                        [i for i in range(self.BOARD_SIZE ** 2) if i not in self.miss_indices])


        backend = Aer.get_backend('qasm_simulator')
        counts=execute(self.qc, backend, shots=1).result().get_counts(self.qc)
        result = list(counts.keys())[0]

        for i, value in enumerate(reversed(result)):
            if i in self.miss_indices:
                self.board[i // self.BOARD_SIZE][i % self.BOARD_SIZE] = 'X '
            elif i in self.ship_hit_indices.keys():
                self.board[i // self.BOARD_SIZE][i % self.BOARD_SIZE] = f"{states[self.ship_hit_indices[i]]}"
            else:
                self.board[i // self.BOARD_SIZE][i % self.BOARD_SIZE] = f"{value} "

        return copy.deepcopy(self.board)

    def reset_board(self):
        """
        Resets the board to a full superposition, restoring any entangled pairs (ships) 
        on the board.
        """
        self.qr = QuantumRegister(self.BOARD_SIZE ** 2)
        self.cr = ClassicalRegister(self.BOARD_SIZE ** 2)
        self.qc = QuantumCircuit(self.qr, self.cr)

        for i in range(self.BOARD_SIZE ** 2):
            self.qc.h(i)
        
        for bs in self.ships:
            self.make_bell_state(
                                self.BOARD_SIZE * self.ships[bs][0][0] + self.ships[bs][0][1],
                                self.BOARD_SIZE * self.ships[bs][1][0] + self.ships[bs][1][1],
                                bs
            )

    def init_board(self):
        """
        Resets the board, measures its new state, and adds that state to the history
        """
        self.reset_board()
        self.past_boards.append(self.measure_board())
    
    def movable(self, i, j, hi, hj):
        """
        Returns true if ship square is movable, false if not.
        """
        dirs = [[-1, 0, 1, 0], [0, 1, 0, -1]]
        for x in range(len(dirs[0])):
            if not (i + dirs[0][x] == hi and j + dirs[1][x] == hj) and not self.check_conflict(i + dirs[0][x], j + dirs[1][x]):
                return True
        return False

    def move_ship(self, bs: BellState, hit_space: Tuple[int, int], new_space: Tuple[int, int]):
        """
        Moves a ship to a new position in the case that it was only partially hit
        """
        
        self._entangle_swap(self.BOARD_SIZE * hit_space[0] + hit_space[1],
                            self.BOARD_SIZE * new_space[0] + new_space[1])
        current_pair = self.ships[bs]
        pivot_space = current_pair[0] if current_pair[1] == hit_space else current_pair[1]
        self.ships[bs] = [pivot_space, new_space]

    def _entangle_swap(self, hit_index, new_index, pivot_index = None, extra_index = None):
        """
        Implements entanglement swapping
        """
        self.qc.swap(hit_index, new_index)

    def get_attack_result(self, row: int, col: int):
        """
        Returns the result of an attack on a given space
        """
        index = self.BOARD_SIZE * row + col
        if index in self.miss_indices or index in self.ship_hit_indices.keys() or not all([0 <= num < self.BOARD_SIZE for num in (row, col)]):
            return (TurnResult.INVALID, None)
        for bs, pair in self.ships.items():
            if [row, col] in pair:
                self.ship_hit_indices[index] = bs
                if all([self.BOARD_SIZE * location[0] + location[1] in self.ship_hit_indices for location in pair]):
                    self.sink_ship(bs)
                    return (TurnResult.SUNK, bs)
                return (TurnResult.HIT, bs)

        self.miss_indices.append(index)
        return (TurnResult.MISS, None)

    def check_conflict(self, row: int, col: int):
        """
        Returns whether the given placement is invalid
        """
        index = self.BOARD_SIZE * row + col
        ship_locs = []
        for pair in self.ships.values():
            ship_locs.append(pair[0])
            ship_locs.append(pair[1])
            
        if index not in self.miss_indices:
            if [row, col] not in ship_locs:
                if all([0 <= num < self.BOARD_SIZE for num in (row, col)]):
                    return False

        return True

    def lost(self):
        """
        Returns true if this player has lost the game.
        """
        return len(self.ships) == 0
