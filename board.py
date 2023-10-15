from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
import numpy as np
import matplotlib
import pylatexenc
from enum import Enum
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
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

class Board:
    BOARD_SIZE = 2
    def __init__(self):
        """
        Constructor for a player's board.
        """
        self.board = [] # 8 x 8 board
        self.ships = {} # list of ships
        self.targeted_indices = [] # Measured/greyed out spaces
        self.past_boards = []
        self.qr = QuantumRegister(self.BOARD_SIZE ** 2)
        self.cr = ClassicalRegister(self.BOARD_SIZE ** 2)
        self.qc = QuantumCircuit(self.qr, self.cr)
        # for i in range(self.BOARD_SIZE):
        #     self.board.append([0 for i in range(self.BOARD_SIZE)])
        #     # superposition for all qubits
        #     for j in range(self.BOARD_SIZE):
        #         self.qc.h(i * self.BOARD_SIZE + j)
        self.reset_board()

    def __str__(self):
        """
        Prints the board.
        """
        st = ("-" * (self.BOARD_SIZE * 2 + 1)) + "\n"
        for row in self.board:
            for space in row:
                st += f"|{space}"
            st += '|\n'
            st += ("-" * (self.BOARD_SIZE * 2 + 1)) + "\n"
        return st

    def get_num_ships(self):
        """
        Returns the number of remaining ships
        """
        return len(self.ships)

    def place_ship(self, bs: BellState, i: int, j: int, dir: Direction):
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
        
        self.ships[bs] = [[i, j], other_index]
        spot_1 = (self.BOARD_SIZE * i + j)
        spot_2 = (self.BOARD_SIZE * other_index[0] + other_index[1])
        self.make_bell_state(spot_1, spot_2, bs)

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
            
    def shoot_ship(self, ship_i, ship_j):
        """
        Logic for shooting a ship.
        Add to targeted, measure, print board
        """
        self.targeted_indices.append(self.BOARD_SIZE * ship_i + ship_j)
        self.measure_board()
        print(self)

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
        self.qc.measure([i for i in range(self.BOARD_SIZE ** 2) if i not in self.targeted_indices],
                        [i for i in range(self.BOARD_SIZE ** 2) if i not in self.targeted_indices])
        #self.qc.draw('mpl')
        #plt.show()


        backend = Aer.get_backend('qasm_simulator')
        counts=execute(self.qc, backend, shots=1).result().get_counts(self.qc)
        result = list(counts.keys())[0]
        print(result)
        for i, value in enumerate(reversed(result)):
            if i not in self.targeted_indices:
                self.board[i // self.BOARD_SIZE][i % self.BOARD_SIZE] = value
            else:
                self.board[i // self.BOARD_SIZE][i % self.BOARD_SIZE] = 'X'
        
        # update state and reset board
        self.reset_board()

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
        Resets the board, measures its new state, and adds that state to the hostory
        """
        self.reset_board()
        self.past_boards.append(self.measure_board())

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
        self.targeted_indices.append(self.BOARD_SIZE * row + col)
        for bs, pair in self.ships.items():
            if (row, col) in pair:
                if all([self.BOARD_SIZE * location[0] + location[1] in self.targeted_indices for location in pair]):
                    self.sink_ship(bs)
                    return TurnResult.SUNK, bs
                return TurnResult.HIT
        return TurnResult.MISS

    def check_conflict(self, row: int, col: int):
        """
        Returns whether the given placement is invalid
        """
        index = self.BOARD_SIZE * row + col
        ship_locs = []
        for pair in self.ships.items():
            ship_locs.append(pair[0])
            ship_locs.append(pair[1])

        if index not in self.targeted_indices:
            if (row, col) not in ship_locs:
                if all([0 <= num <= self.BOARD_SIZE for num in (row, col)]):
                    return False

        return True

    def lost(self):
        """
        Returns true if this player has lost the game.
        """
        return len(self.ships) == 0
