# ============================================================
# Main.py
# ============================================================
from __future__ import annotations
import copy
import threading
import time

from Game import TetrisGame
from KI import (
    NeuralNetwork,
    SAVE_BEST_MODEL
)
AI_INTERVAL = 0.10
def main():
    stop_event = threading.Event()
    state_lock = threading.Lock()
    latest_state = {}
#
    ai = NeuralNetwork()
    use_ai = False
    try:
        ai.load(SAVE_BEST_MODEL)
        use_ai = True
        print("Trainierte KI geladen.")
    except FileNotFoundError:
        print("Kein trainiertes Modell gefunden. Starte im manuellen Modus (Keyboard-Steuerung).")
    except ValueError as e:
        print(e)
        print("Das gespeicherte Modell passt nicht zur aktuellen KI.")
        return

    def callback(state):
        with state_lock:
            latest_state.clear()
            latest_state.update(
                copy.deepcopy(state)
            )

    game = TetrisGame(
        state_callback=callback,
        visualize=True
    )
    def execute_action(action):
        if game.engine.game_over:
            return
        game.engine.step(action)
        game.engine.tick()

    def ai_worker():
        while not stop_event.is_set():
            with state_lock:
                if not latest_state:
                    time.sleep(AI_INTERVAL)
                    continue
                state = copy.deepcopy(latest_state)
            if state["game_over"]:
                time.sleep(AI_INTERVAL)
                continue
            action, output = ai.predict(state)
            game.window.after(
                0,
                lambda a=action: execute_action(a)
            )
            time.sleep(AI_INTERVAL)
    def console_worker():
        print()
        print("q = Beenden")
        while not stop_event.is_set():
            try:
                command = input()
            except EOFError:
                break
            if command.lower() == "q":
                stop_event.set()
                game.window.after(
                    0,
                    game.close
                )
                break

    threading.Thread(
        target=ai_worker,
        daemon=True
    ).start() if use_ai else None
    threading.Thread(
        target=console_worker,
        daemon=True
    ).start()
    try:
        game.run()
    finally:
        stop_event.set()

if __name__ == "__main__":
    main()