# ============================================================
# KI.py
# ============================================================
from __future__ import annotations
import numpy as np
# ============================================================
# KI Parameter
# ============================================================
BOARD_ROWS = 20
BOARD_COLS = 10
# ============================================================
# Board:
#   20 * 10 = 200
# Next Piece:
#   7
# Hold Piece:
#   7 + leer Flag
# can_hold:
#   1
# hold_used:
#   1
# Höhen:
#   10
# Löcher:
#   1
# Aktueller Stein:
#   Name:
#       1
#   Rotation:
#       1
# Gesamt:
#   230
# ============================================================
INPUT_SIZE = 230
HIDDEN_LAYERS = [
    256,
    128,
    64
]
# Aktionen
# 0 = links
# 1 = rechts
# 2 = drehen
# 3 = runter
# 4 = halten
# 5 = hard drop
OUTPUT_SIZE = 6
ACTION_NAMES = [
    "LEFT",
    "RIGHT",
    "ROTATE",
    "DROP",
    "HOLD",
    "HARD_DROP"
]
ACTIVATION_FUNCTION = "relu"

#Evolution
EPOCHS = 200
GAMES_PER_EPOCH = 100
POPULATION_SIZE = 100
ELITE_COUNT = 5
MUTATION_RATE = 0.1
MUTATION_STRENGTH = 0.2
SAVE_BEST_MODEL = ("best_tetris_ai.npz")
PIECES = [
    "I",
    "J",
    "L",
    "O",
    "S",
    "T",
    "Z"
]
def activation(x):
    if ACTIVATION_FUNCTION == "relu":
        return np.maximum(0, x)
    elif ACTIVATION_FUNCTION == "tanh":
        return np.tanh(x)
    elif ACTIVATION_FUNCTION == "sigmoid":
        return (1 /( 1 + np.exp(-x)))
    raise ValueError(
        "Unbekannte Aktivierung"
    )
def softmax(x):
    exp = np.exp(
        x - np.max(x)
    )
    return exp / np.sum(exp)
def one_hot(value, values):
    result = [
        0.0
        for _ in values
    ]
    if value in values:
        result[
            values.index(value)
        ] = 1.0
    return result

def state_to_network_input(state):
    inputs = []
    board = [row[:]for row in state["board"]]
    current = state.get("current_piece")
    if current:
        for x,y in current["cells"]:
            if 0 <= x < BOARD_COLS and 0 <= y < BOARD_ROWS:
                board[y][x] = 2
    for row in board:
        for cell in row:
            if cell == 0:
                inputs.append(0.0)
            elif cell == 2:
                inputs.append(1.0)
            else:
                inputs.append(0.5)
    next_piece = (
        state["next_piece"]["name"]
        if state.get("next_piece")
        else None
    )
    inputs.extend(
        one_hot(
            next_piece,
            PIECES
        )
    )
    hold = state.get("held_piece")
    if hold:
        inputs.extend(one_hot(hold["name"],PIECES))
        inputs.append(0.0)
    else:
        inputs.extend([0.0]*7)
        inputs.append(1.0)
    inputs.append(float(state.get("can_hold",False)))
    inputs.append(float(state.get("hold_used",False)))
    heights = state.get("heights",[0]*10)
    for h in heights:
        inputs.append(h / 20.0)
    inputs.append(state.get("holes",0)/20.0)
    if current:
        inputs.append(PIECES.index(current["name"])/7.0)
        inputs.append(current["rotation"]/4.0)
    else:
        inputs.extend([0.0,0.0])
    return inputs

class NeuralNetwork:
    def __init__(self):
        self.layers = [
            INPUT_SIZE,
            *HIDDEN_LAYERS,
            OUTPUT_SIZE
        ]
        self.weights = []
        self.biases = []
        self.initialize()
    def initialize(self):
        for i in range(len(self.layers)-1):
            inp = self.layers[i]
            out = self.layers[i+1]
            self.weights.append(
                np.random.randn(
                    inp,
                    out
                ) *
                np.sqrt(2/inp))
            self.biases.append(
                np.zeros(
                    out
                )
            )
    def forward(self, inputs):
        x = np.array(
            inputs,
            dtype=np.float32
        )
        for i in range(len(self.weights)):
            x = (x @ self.weights[i] + self.biases[i])
            if i != len(self.weights)-1:
                x = activation(x)
        return softmax(x)
    def predict(self,state):
        inputs = state_to_network_input(
            state
        )
        output = self.forward(inputs)
        action = int(np.argmax(output))
        return action, output
    def clone(self):
        child = NeuralNetwork()
        for i in range(len(self.weights)):
            child.weights[i] = (self.weights[i].copy())
            child.biases[i] = (self.biases[i].copy())
        return child
    def mutate(self):
        for i in range(len(self.weights)):
            mask = (np.random.random(self.weights[i].shape)<MUTATION_RATE)
            self.weights[i] += (mask *
                    np.random.randn(*self.weights[i].shape)
                    * MUTATION_STRENGTH)
        for i in range(len(self.biases)):
            mask = (
                    np.random.random(self.biases[i].shape)
                    < MUTATION_RATE
            )
            self.biases[i] += (
                    mask *
                    np.random.randn(*self.biases[i].shape)
                    * MUTATION_STRENGTH
            )

    def save(self,filename=SAVE_BEST_MODEL):
        data = {}
        for i,w in enumerate(self.weights):
            data[f"w{i}"] = w
        for i,b in enumerate(self.biases):
            data[f"b{i}"] = b
        np.savez(filename,**data)

    def load(self,filename=SAVE_BEST_MODEL):
        data = np.load(filename)
        for i in range(len(self.weights)):
            self.weights[i] = data[f"w{i}"]
            self.biases[i] = data[f"b{i}"]

def fitness_from_score(score):
    return score