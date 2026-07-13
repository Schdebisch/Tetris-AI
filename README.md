# Tetris-AI
Ein Tetris Spiel, welches selbst oder von einer KI gespielt werden kann.
Die KI wird durch einen evolutionären Algorithmus Trainiert.

## Features

- Vollständig spielbares Tetris
- GUI mit Tkinter
- Manuelle Steuerung per Tastatur
- KI-Steuerung über ein neuronales Netzwerk
- Evolutionäres Training

## Abhängigkeiten
Python 3.10+
numpy
random
time
dataclasses
typing
copy
threading
time
tkinter

## Aufbau
### Game.py
enthält die Steuerung und Visualisierung des Tetris-Spiels.\
Die Klasse TetrisEngine enthält die eigentliche Spiellogik.\
Die Klasse TetrisGame stellt ausschließlich die grafische Darstellung bereit.
### KI.py
enthält Gewichte, Neuronen, die Möglichkeit Modelle zu speichern/laden und Parameter zur Anpassung des Netzes und Evolutonsverhalten.\
Die Parameter setzen sich wie folgt zusammen:
- Bord länge/breite
- Inputs 
  -  Board: 20 * 10 = 200
  - Next Piece: 7
  - Hold Piece: 7 + leer Flag
  - can_hold: 1
  - hold_used: 1
  - Höhen: 10
  - Löcher: 1
  - Aktueller Stein:
    - Name: 1
    - Rotation: 1
  - Gesamt: 230
- Größe Hidden Layers (256, 128,64)
- Outputs (Links, Rechts, Drehen, langsames Fallen, Nichts tun schnelles Fallen)
- Aktivierungsfunktionen (reLU)
- Trainingsverhalten ( Anzahl Epochen, Population, etc.)
### Training.py
Kümmert sich um das Training mittels evolutionären training.\
Wird zum Training direkt ausgeführt.\
Ablauf:
1. Population erzeugen
2. Jede KI spielt mehrere Spiele
3. Fitness berechnen
4. Beste Netzwerke auswählen
5. Mutation
6. Neue Generation erzeugen

### Main.py
Startet das Spiel.\
Falls ein trainiertes Modell gefunden wird, wird dieses geladen und spielt das Spiel.\
Falls nicht, wird das Spiel mit manuellen Keyboard-eingaben gestartet.\
## Tastenkürzel:
- &rarr; rechts
- &larr; links
- &uarr; drehen
- &darr; slow drop (Stein fällt schneller)
- [Space] hard drop (Stein fällt sofort zu boden)
- [c] hold
## Fitnessfunktion
Die Bewertung einer KI setzt sich aus mehreren Faktoren zusammen.\
### Belohnt:
- hoher Score
- viele gelöschte Linien
### Bestraft:
- viele Löcher
- hohe Türme
### Formel
aktuell ist die Formel wie folgt: **Fitness = Score + Linien * 50000 - Löcher * 500 - Höhe * 100.**\
Die Gewichte könen in den Parametern der Training.py angepasst werden.
## Anwendung
Zum starten des Spiels, ohne KI. Muss die Datei, mit der trainierten KI (im Standard fall [.\best_tetris_ai.npz](url)), sofern vorhanden umbenannt, gelöscht oder verschoben werden. Dadurch wird die manuelle Steuerung freigeschaltet.\
Zum starten des Spiels, mit KI, wird die Datei wieder in die Ursprünglich form gebracht oder neu trainiert. Dadurch kann beim starten der KI beim spielen zugeschaut werden.\
Zum trainieren der KI, wird das Skript Training.py aufgerufen. welches die ggf. vorhandene Datei einließt und weiter trainiert.
