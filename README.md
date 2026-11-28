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
- A pygame GUI with piece images: click a piece to see its legal moves, click a square to move there
- Finished games are saved automatically to `saved_games/` as JSON files
- Game review: Stockfish scores every move, and you get advice per phase, e.g. "Your opening is strong, however you struggle in the middlegame."

## How to play (GUI)

1. Install the dependency: `pip install -r requirements.txt`
2. From the `explorer-track` folder, start the game: `python main.py` (or `python -m chess.main`)
3. Click one of your pieces (dots show where it can go, rings show captures), then click the square to move to.
4. Use the buttons on the right to start a 2-player game or a game against the computer, undo a move, or resign.
5. Press **Review game** at any point to get feedback on the moves so far (click the board to close it).

## Game review (needs Stockfish)

The review uses the free [Stockfish](https://stockfishchess.org/) engine, which runs on your own computer (no internet needed). Install it once:

```
yay -S stockfish              # Arch Linux (from the AUR)
sudo apt install stockfish    # Ubuntu / Debian
```

For every move, Stockfish scores the position before and after it. The drop in score is the move's "loss" (100 = one pawn). Losses of 0.5, 1 and 3 pawns count as an inaccuracy, a mistake and a blunder. The moves are split into opening (first 10 moves), endgame (queens traded or few pieces left) and middlegame, and the average loss in each phase becomes the advice.

You can also review a saved game from the terminal:

```
python -m chess.analysis saved_games/game_2026-11-27_12-30-00.json
```

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
| `chess/storage.py` | `save_game` / `load_game`: games as JSON files in `saved_games/`. |
| `chess/stockfish.py` | `Stockfish`: starts the Stockfish program and asks it to score positions. |
| `chess/analysis.py` | `GameAnalyzer` scores every move, `Report` turns the scores into advice. |
| `chess/player.py` | `Player` (a person) and `ComputerPlayer` (picks a random legal move). |
| `chess/gui.py` | `ChessGUI`: the pygame window. The only file that knows about drawing and the mouse. |
| `chess/main.py` | Starts the GUI. |
| `main.py` | Shortcut that starts the GUI, so `python main.py` works. |
| `assets/` | Piece images (`white_K.png`, `black_N.png`, ...) used by the GUI, plus the original SVGs in `assets/svg/`. |

## Known limitations

- Promotion always gives a queen; you can't choose another piece.
- Draws are declared automatically (no "claim a draw" or "offer a draw" button).
- The computer opponent always plays Black, and the board doesn't flip in 2-player mode.
- The material-counting (greedy) bot is not written yet.
- The game review needs Stockfish installed, and judges moves only by score (it doesn't explain *why* a move was bad).
- Legal moves are checked by copying the board for every candidate move, which is fine for playing but slow for bots that look several moves ahead.

## Credits

The piece images are the "Cburnett" set by Colin M.L. Burnett (from [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:SVG_chess_pieces), as packaged by [Lichess](https://github.com/lichess-org/lila)), licensed under GPLv2+. They were converted from SVG to PNG for pygame.
