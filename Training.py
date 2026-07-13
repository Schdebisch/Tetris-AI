# ============================================================
# Training.py
# ============================================================
from __future__ import annotations
import random
from pathlib import Path
from concurrent.futures import (
    ProcessPoolExecutor,
    as_completed
)
from Game import TetrisEngine
from KI import (
    NeuralNetwork,
    EPOCHS,
    GAMES_PER_EPOCH,
    POPULATION_SIZE,
    ELITE_COUNT,
    SAVE_BEST_MODEL,
)

# Trainingsparameter

MAX_STEPS = 5000

# Fitness Gewichtung
LINE_WEIGHT = 50000
HOLES_WEIGHT = -500
HEIGHT_WEIGHT = -100

# Eltern Auswahl
PARENT_WEIGHTS = [
    ELITE_COUNT - i
    for i in range(ELITE_COUNT)
]

def fitness(score, lines, holes, height):
    return (score
            + lines * LINE_WEIGHT
            + holes * HOLES_WEIGHT
            + height * HEIGHT_WEIGHT)

def play_game(ai):
    engine = TetrisEngine()
    steps = 0
    while (not engine.game_over
            and steps < MAX_STEPS):
        state = engine.get_state()
        action, _ = ai.predict(state)
        engine.step(action)
        engine.tick()
        steps += 1
    return {"score": engine.score,
        "lines": engine.lines,
        "holes": engine.get_holes(),
        "height": max(engine.get_column_heights())}

def evaluate_ai(data):
    index, ai = data
    scores = []
    lines = []
    holes = []
    heights = []
    for _ in range(GAMES_PER_EPOCH):
        result = play_game(ai)
        scores.append(result["score"])
        lines.append(result["lines"])
        holes.append(result["holes"])
        heights.append(result["height"])
    avg_score = sum(scores) / len(scores)
    avg_lines = sum(lines) / len(lines)
    avg_holes = sum(holes) / len(holes)
    avg_height = sum(heights) / len(heights)
    return (
        index,
        avg_score,
        avg_lines,
        fitness(avg_score,
            avg_lines,
            avg_holes,
            avg_height),
        ai)

def train():
    print("=" * 60)
    print("             TETRIS KI TRAINING")
    print("=" * 60)
    population = []
    global_best_fitness = -10000000
    global_best_score = 0
    global_best_lines = 0

    if Path(SAVE_BEST_MODEL).exists():
        print("Gespeichertes Modell gefunden.")
        best_ai = NeuralNetwork()
        best_ai.load(
            SAVE_BEST_MODEL
        )
        population.append(
            best_ai
        )
        while len(population) < POPULATION_SIZE:
            child = best_ai.clone()
            child.mutate()
            population.append(
                child
            )
    else:
        print("Neue Population wird erzeugt.")
        population = [
            NeuralNetwork()
            for _ in range(POPULATION_SIZE)]

    for epoch in range(1,EPOCHS + 1):
        print()
        print("=" * 60)
        print( f"Epoch {epoch}/{EPOCHS}")
        print("=" * 60)
        tasks = [
            (index,ai)
            for index,ai in enumerate(
                population,
                start=1)
        ]
        results = []
        with ProcessPoolExecutor() as executor:
            futures = [
                executor.submit(
                    evaluate_ai,
                    task
                )
                for task in tasks
            ]
            finished = 0
            for future in as_completed(futures):
                result = future.result()
                results.append(
                    result
                )
                finished += 1
                index,score,lines,fit,_ = result
                print(
                    f"[{finished:3}/{POPULATION_SIZE}] "
                    f"KI {index:3} | "
                    f"Fitness={fit:10.0f} | "
                    f"Score={score:8.0f} | "
                    f"Lines={lines:6.2f}"
                )

        results.sort(
            key=lambda x:x[3],
            reverse=True
        )
        best = results[0]
        worst = results[-1]
        if best[3] > global_best_fitness:
            global_best_fitness = best[3]
            global_best_score = best[1]
            global_best_lines = best[2]
            best[4].save(SAVE_BEST_MODEL)
            print("\nNeue beste KI gespeichert!")
        print()
        print("-"*60)
        print("Beste KI")
        print(f"Fitness : {best[3]:10.0f}")
        print(f"Score   : {best[1]:10.0f}")
        print(f"Lines   : {best[2]:10.2f}")
        print()
        print("Historisch")
        print(f"Fitness : {global_best_fitness:10.0f}")
        print(f"Score   : {global_best_score:10.0f}")
        print(f"Lines   : {global_best_lines:10.2f}")

        elites = [
            result[4]
            for result in results[:ELITE_COUNT]
        ]
        new_population = []
        for elite in elites:
            new_population.append(
                elite.clone()
            )

        while len(new_population) < POPULATION_SIZE:
            parent = random.choices(
                elites,
                weights=PARENT_WEIGHTS,
                k=1
            )[0]
            child = parent.clone()
            mutation_count = random.choice([1,1,1,2,3])
            for _ in range(mutation_count):
                child.mutate()
            new_population.append(child)
        population = new_population
        print()
        print(f"Neue Generation: {len(population)}")


if __name__ == "__main__":
    train()