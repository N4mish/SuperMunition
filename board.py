from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import numpy as np
import matplotlib
import pylatexenc
from enum import Enum

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

class Board:
    def __init__(self):
        self.BOARD_SIZE = 8
        self.board = [] # 8 x 8 board
        self.ships = {} # list of ships
        self.measured = [] # Measured/greyed out spaces
        self.qr = QuantumRegister(self.BOARD_SIZE ** 2)
        self.cr = ClassicalRegister(self.BOARD_SIZE ** 2)
        self.qc = QuantumCircuit(self.qr, self.cr)
        for i in range(self.BOARD_SIZE):
            self.board.append([0 for i in range(self.BOARD_SIZE)])
            # superposition for all qubits
            for j in range(self.BOARD_SIZE):
                self.qc.h(i * self.BOARD_SIZE + j)

        print(self.qc)

    def __str__(self):
        """
        Prints the board.
        """
        st = ("-"*(self.BOARD_SIZE*2+1))+"\n"
        for row in self.board:
            for space in row:
                st += f"|{space}"
            st += '|\n'
            st += ("-"*(self.BOARD_SIZE*2+1))+"\n"
        return st

    def place_ship(self, bs: BellState, i: int, j: int, dir: Direction):
        # TODO ASSUMING INDICES ARE IN BOUNDS
        if dir == Direction.UP:
            other_index = [i - 1, j]
        elif dir == Direction.DOWN:
            other_index = [i + 1, j]
        elif dir == Direction.LEFT:
            other_index = [i, j - 1]
        else:
            other_index = [i, j + 1]
        
        self.ships[bs] = [[i, j], other_index]
        self.make_bell_state((self.BOARD_SIZE * i + j), (self.BOARD_SIZE * other_index[0] + other_index[1]), bs)
        
    def make_bell_state(self, ship_1: int, ship_2: int, bs: BellState):
        """
        Given two absolute ship specifiers ((BOARD_SIZE * i) + j), sets up a bell state between 
        them.
        """
        self.qc.cx(self.qr[ship_1], self.qr[ship_2])
        if bs == BellState.PSIPLUS:
            self.qc.x(self.qr[ship_1])
        elif bs == BellState.PHIMINUS:
            self.qc.z(self.qr[ship_1])
        elif bs == BellState.PSIMINUS:
            self.qc.x(self.qr[ship_1])
            self.qc.z(self.qr[ship_1])
            
        
        


