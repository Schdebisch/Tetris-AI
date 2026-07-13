# ============================================================
# Game.py
# ============================================================

from __future__ import annotations
import random
import time
from dataclasses import dataclass
from typing import Optional
import tkinter as tk


# ============================================================
# Parameter
# ============================================================

BOARD_WIDTH = 10 # Anzahl Blöocke in der Breite
BOARD_HEIGHT = 20 # Anzahl Blöocke in der Höhe
CELL_SIZE = 30 #Pixelgröße eines Blocks

# ============================================================
# Tetris Figuren
# ============================================================

PIECES = {
    "I": [
        [(0,1),(1,1),(2,1),(3,1)],
        [(2,0),(2,1),(2,2),(2,3)],
        [(0,2),(1,2),(2,2),(3,2)],
        [(1,0),(1,1),(1,2),(1,3)],
    ],
    "O": [
             [(1,0),(2,0),(1,1),(2,1)]
         ] * 4,
    "T": [
        [(1,0),(0,1),(1,1),(2,1)],
        [(1,0),(1,1),(2,1),(1,2)],
        [(0,1),(1,1),(2,1),(1,2)],
        [(1,0),(0,1),(1,1),(1,2)],
    ],
    "S": [
        [(1,0),(2,0),(0,1),(1,1)],
        [(1,0),(1,1),(2,1),(2,2)],
        [(1,1),(2,1),(0,2),(1,2)],
        [(0,0),(0,1),(1,1),(1,2)],
    ],
    "Z": [
        [(0,0),(1,0),(1,1),(2,1)],
        [(2,0),(1,1),(2,1),(1,2)],
        [(0,1),(1,1),(1,2),(2,2)],
        [(1,0),(0,1),(1,1),(0,2)],
    ],
    "J": [
        [(0,0),(0,1),(1,1),(2,1)],
        [(1,0),(2,0),(1,1),(1,2)],
        [(0,1),(1,1),(2,1),(2,2)],
        [(1,0),(1,1),(0,2),(1,2)],
    ],
    "L": [
        [(2,0),(0,1),(1,1),(2,1)],
        [(1,0),(1,1),(1,2),(2,2)],
        [(0,1),(1,1),(2,1),(0,2)],
        [(0,0),(1,0),(1,1),(1,2)],
    ],
}
PIECE_NAMES = list(PIECES.keys())

@dataclass
class Piece:
    name: str
    rotation: int
    x: int
    y: int

# ============================================================
# Engine
# ============================================================

class TetrisEngine:
    def __init__(self):
        self.rows = BOARD_HEIGHT
        self.cols = BOARD_WIDTH
        self.hard_drop_used = False
        self.board = []
        self.current_piece: Optional[Piece] = None
        self.next_piece = None
        self.hold_piece = None
        self.hold_used = False
        self.score = 0
        self.lines = 0
        self.game_over = False
        self.reset()

    def reset(self):
        self.board = [
            [0 for _ in range(self.cols)]
            for _ in range(self.rows)]
        self.score = 0
        self.lines = 0
        self.game_over = False
        self.hold_piece = None
        self.hold_used = False
        self.hard_drop_used = False
        self.next_piece = self.random_piece()
        self.spawn()

    def random_piece(self):
        return random.choice(PIECE_NAMES)

    def spawn(self):
        name = self.next_piece
        self.hard_drop_used = False
        self.next_piece = self.random_piece()
        piece = Piece(
            name=name,
            rotation=0,
            x=self.cols // 2 - 2,
            y=0)
        
        if self.valid(piece):
            self.current_piece = piece
        else:
            self.game_over = True

    def cells(self, piece):
        return [(piece.x + x,piece.y + y)
            for x,y in PIECES[piece.name][piece.rotation]
        ]

    def valid(self, piece):
        for x,y in self.cells(piece):
            if x < 0 or x >= self.cols:
                return False
            if y >= self.rows:
                return False
            if y >= 0 and self.board[y][x]:
                return False
        return True

    def move(self, dx, dy):
        if self.game_over:
            return False
        if self.current_piece is None:
            return False
        candidate = Piece(
            name=self.current_piece.name,
            rotation=self.current_piece.rotation,
            x=self.current_piece.x + dx,
            y=self.current_piece.y + dy
        )
        if self.valid(candidate):
            self.current_piece = candidate
            return True
        return False

    def rotate(self):
        if self.game_over:
            return False
        if self.current_piece is None:
            return False
        new_rotation = (self.current_piece.rotation + 1) % 4
        candidate = Piece(
            name=self.current_piece.name,
            rotation=new_rotation,
            x=self.current_piece.x,
            y=self.current_piece.y)

        for offset in [0,-1,1,-2,2]:
            test = Piece(
                name=candidate.name,
                rotation=candidate.rotation,
                x=candidate.x + offset,
                y=candidate.y
            )
            if self.valid(test):
                self.current_piece = test
                return True
        return False

    def soft_drop(self):
        if self.move(0,1):
            self.score += 1
            return True
        return False

    def hard_drop(self):
        if self.game_over:
            return
        if self.hard_drop_used:
            return
        self.hard_drop_used = True
        distance = 0
        while self.move(0, 1):
            distance += 1
        self.score += distance * 2
        self.lock()


    def hold(self):
        if (self.game_over or self.hold_used or self.current_piece is None):
            return
        current = self.current_piece.name
        if self.hold_piece is None:
            self.hold_piece = current
            self.spawn()
        else:
            old_hold = self.hold_piece
            self.hold_piece = current
            candidate = Piece(
                name=old_hold,
                rotation=0,
                x=self.cols//2-2,
                y=0
            )

            if self.valid(candidate):
                self.current_piece = candidate
            else:
                self.game_over = True
        self.hold_used = True

    def step(self, action):
        if self.game_over:
            return self.get_state()
        if action == 0:
            self.move(-1,0)
        elif action == 1:
            self.move(1,0)
        elif action == 2:
            self.rotate()
        elif action == 3:
            self.soft_drop()
        elif action == 4:
            self.hold()
        elif action == 5:
            time.sleep(0.1)
            #self.hard_drop()
            #self.hard_drop_used = False
        return self.get_state()

    def tick(self):
        if self.game_over:
            return
        if not self.move(0,1):
            self.lock()

    def lock(self):
        if self.current_piece is None:
            return
        for x,y in self.cells(self.current_piece):
            if y < 0:
                self.game_over = True
                continue
            self.board[y][x] = 1
        cleared = self.clear_lines()
        if cleared:
            self.lines += cleared
            rewards = {
                1: 100,
                2: 300,
                3: 500,
                4: 800
            }
            self.score += rewards.get(
                cleared,
                cleared * 250
            )
        self.spawn()
        self.hold_used = False

    def clear_lines(self):
        old_length = len(self.board)
        self.board = [
            row
            for row in self.board
            if 0 in row
        ]
        removed = old_length - len(self.board)
        while len(self.board) < old_length:
            self.board.insert(
                0,
                [0 for _ in range(self.cols)]
            )
        return removed

    def get_column_heights(self):
        heights = []
        for x in range(self.cols):
            height = 0
            for y in range(self.rows):
                if self.board[y][x]:
                    height = self.rows - y
                    break
            heights.append(height)
        return heights

    def get_holes(self):
        holes = 0
        for x in range(self.cols):
            block_found = False
            for y in range(self.rows):
                if self.board[y][x]:
                    block_found = True
                elif block_found:
                    holes += 1
        return holes

    def get_state(self):
        current = None
        if self.current_piece:
            current = {
                "name":
                    self.current_piece.name,
                "rotation":
                    self.current_piece.rotation,
                "x":
                    self.current_piece.x,
                "y":
                    self.current_piece.y,
                "cells":
                    self.cells(self.current_piece)
            }
        return {
            "board":
                [row[:] for row in self.board],
            "current_piece":current,
            "next_piece":{"name":self.next_piece},
            "held_piece":(
                {"name":self.hold_piece}
                if self.hold_piece
                else None
                ),
            "can_hold":(not self.hold_used  and not self.game_over),
            "hold_used":self.hold_used,
            "score":self.score,
            "lines_cleared":self.lines,
            "heights":self.get_column_heights(),
            "holes":self.get_holes(),
            "game_over":self.game_over
        }


class TetrisGame:
    """
    GUI Wrapper für TetrisEngine.

    Die GUI dient nur zur Darstellung.
    Die komplette Spiellogik bleibt in TetrisEngine.
    """
    def __init__(self,state_callback=None,visualize=True):
        self.engine = TetrisEngine()
        self.callback = state_callback
        self.visualize = visualize
        self.running = True
        self.window = tk.Tk()
        self.window.title("Tetris KI")
        self.canvas = None
        if visualize:
            self.canvas = tk.Canvas(
                self.window,
                width=BOARD_WIDTH * CELL_SIZE + 220,
                height=BOARD_HEIGHT * CELL_SIZE,
                bg="black"
            )
            self.canvas.pack()
        self.window.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )
        self.window.bind_all("<Key>", self.on_key)
        self.window.after(50,self.loop)

    def loop(self):
        if not self.running:
            return
        if not self.engine.game_over:
            self.engine.tick()
        self.render()
        self.emit()
        self.window.after(500,self.loop)

    def render(self):
        if not self.visualize:
            return
        self.canvas.delete("all")
        state = self.engine.get_state()
        board = state["board"]

        for y,row in enumerate(board):
            for x,value in enumerate(row):
                color = "#202020"
                if value:
                    color = "#00d4ff"
                self.canvas.create_rectangle(
                    x * CELL_SIZE,
                    y * CELL_SIZE,
                    (x+1) * CELL_SIZE,
                    (y+1) * CELL_SIZE,
                    fill=color,
                    outline="#333333"
                )

        piece = state["current_piece"]
        if piece:
            for x,y in piece["cells"]:
                if y >= 0:
                    self.canvas.create_rectangle(
                        x * CELL_SIZE,
                        y * CELL_SIZE,
                        (x+1) * CELL_SIZE,
                        (y+1) * CELL_SIZE,
                        fill="#ffd43b",
                        outline="white"
                    )

        offset = BOARD_WIDTH * CELL_SIZE + 20
        texts = [
            f"Score: {state['score']}",
            f"Lines: {state['lines_cleared']}",
            f"Next: {state['next_piece']['name']}",
            f"Hold: {state['held_piece']['name'] if state['held_piece'] else '-'}",
            f"Holes: {state['holes']}"
        ]
        for index,text in enumerate(texts):
            self.canvas.create_text(
                offset,
                30 + index * 30,
                anchor="w",
                text=text,
                fill="white",
                font=("Arial",14)
            )
        if state["game_over"]:
            self.canvas.create_text(
                BOARD_WIDTH * CELL_SIZE // 2,
                BOARD_HEIGHT * CELL_SIZE // 2,
                text="GAME OVER",
                fill="red",
                font=("Arial",24,"bold")
            )

    def emit(self):
        if self.callback:
            self.callback(
                self.engine.get_state()
            )
    def run(self):
        self.window.mainloop()
    def close(self):
        self.running = False
        self.window.destroy()

    def on_key(self, event):
        if self.engine.game_over:
            return
        key = event.keysym.lower()
        if key == "left":
            self.engine.step(0)

        elif key == "right":
            self.engine.step(1)

        elif key == "up":
            self.engine.step(2)

        elif key == "down":
            self.engine.step(3)

        elif key == "space":
            # hard drop
            self.engine.hard_drop()

        elif key == "c":
            self.engine.hold()

        elif key == "q":
            self.close()

        # update visuals and emit state
        self.render()
        self.emit()