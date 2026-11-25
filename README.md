# _Chess OOP Engine_

This is part of my Coding Cafe course @ Plaksha. I am building a chess engine in Python with a clean OOP design, plus a pygame window to play it in. The long-term goal is a modular engine where you can change what pieces can do, add new pieces and try out different chess bot strategies. Refer to the [proposal](PROPOSAL.md) to know more about it.

## Features

- Full board setup with all six pieces and their movement rules
- Legal move checking: you can't make a move that leaves your own king in check (pins included)
- Check, checkmate and stalemate detection
- Draws by insufficient material, the 50-move rule and threefold repetition
- Castling on both sides, with all its conditions (king and rook unmoved, empty squares between them, king not in check or passing through an attacked square)
- En passant
- Pawn double move on its first move, and promotion (always to a queen for now)
- Undo and resign (undo after resigning takes back the resignation)
- Clear error messages for illegal moves (e.g. "That move would leave your king in check.")
- Two-player mode and a computer opponent that plays random legal moves
- A pygame GUI: click a piece to see its legal moves, click a square to move there

## How to play (GUI)

1. Install the dependency: `pip install -r requirements.txt`
2. From the `explorer-track` folder, start the game: `python main.py` (or `python -m chess.main`)
3. Click one of your pieces (dots show where it can go, rings show captures), then click the square to move to.
4. Use the buttons on the right to start a 2-player game or a game against the computer, undo a move, or resign.

## Using the engine as a library

The engine itself (`board.py`, `pieces.py`, `game.py`, `player.py`) has no dependencies, so you can use it without pygame:

```python
from chess.game import Game

g = Game()
g.make_move("e2", "e4")
g.make_move("e7", "e5")
print(g.board.display())        # text picture of the board
print(g.history)                # ['e2-e4', 'e7-e5']
print(g.game_over, g.result)    # False ''

try:
    g.make_move("e1", "e3")
except ValueError as error:
    print(error)                # A king cannot move from e1 to e3.
```

Other useful methods: `g.get_legal_moves(row, col)`, `g.all_legal_moves(color)`, `g.is_in_check()`, `g.undo()`, `g.resign()`. Squares are written like `"e2"` in `make_move`, and as `(row, col)` pairs inside the engine (row 0 is rank 8, col 0 is file a).

## Project structure

| File | What it does |
|---|---|
| `chess/pieces.py` | `Piece` parent class and the six piece classes (`Pawn`, `Rook`, `Knight`, `Bishop`, `Queen`, `King`). Each piece knows its colour and how it moves. |
| `chess/board.py` | `Board`: the 8x8 grid, starting setup, moving pieces (including castling, en passant and promotion), finding attacked squares and check, insufficient material. |
| `chess/game.py` | `Game`: turns, legal moves, castling rules, checkmate/stalemate/draws, move history, undo and resign. |
| `chess/player.py` | `Player` (a person) and `ComputerPlayer` (picks a random legal move). |
| `chess/gui.py` | `ChessGUI`: the pygame window. The only file that knows about drawing and the mouse. |
| `chess/main.py` | Starts the GUI. |
| `main.py` | Shortcut that starts the GUI, so `python main.py` works. |

## Known limitations

- Promotion always gives a queen; you can't choose another piece.
- Draws are declared automatically (no "claim a draw" or "offer a draw" button).
- The computer opponent always plays Black, and the board doesn't flip in 2-player mode.
- The material-counting (greedy) bot is not written yet.
- Legal moves are checked by copying the board for every candidate move, which is fine for playing but slow for bots that look several moves ahead.
