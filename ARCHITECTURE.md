# Architecture

This document describes how the code is organised right now. The engine is split into four layers, and each layer only talks to the ones below it:

```
gui.py      ChessGUI, Button      window, mouse, drawing
  |
game.py     Game                  turns, legal moves, castling, checkmate, draws, history, undo
  |
player.py   Player, ComputerPlayer
board.py    Board                 the 8x8 grid, moving pieces, attacked squares, check
  |
pieces.py   Piece + 6 subclasses  how each piece moves
```

The rules of chess live only in `pieces.py`, `board.py` and `game.py`. `gui.py` is the only file that imports pygame, so the engine can be used on its own (or with a different interface) without any dependencies.

## Key design decisions

- **A piece does not know where it is.** The board stores positions. Whenever a piece needs to work out its moves, the board passes in its `(row, col)`. This keeps a piece's state small (colour and whether it has moved) and avoids two copies of the position getting out of sync.
- **Positions are `(row, col)` pairs.** Row 0 is rank 8 (Black's side, top of the screen), row 7 is rank 1 (White's side). Col 0 is file a, col 7 is file h. Text squares like `"e2"` are only used at the edges (in `Game.make_move` and in move history), and are converted with `square_to_position` / `position_to_square` in `board.py`.
- **The board is a plain 8x8 list.** `grid[row][col]` holds a `Piece` object or `None`. There is no separate Cell class; a square's label can be calculated from its row and column whenever it's needed.
- **Movement is shared through two helpers.** `Piece.slide` (rook, bishop, queen) and `Piece.jump` (knight, king) take a list of directions. Each subclass just picks its directions, so the movement logic isn't repeated.
- **Moves and attacks are separate.** `get_attacks` returns the squares a piece threatens. For most pieces this is the same as `get_moves`, but a pawn moves forward and attacks diagonally, so it overrides `get_attacks`. Check detection uses attacks, never legal moves, which avoids an infinite loop (checking legality needs check detection, which would otherwise need legality).
- **Legal moves are tested on a copy of the board.** A candidate move is legal if, after playing it on a `deepcopy` of the board, your own king is not in check. This automatically handles pins, moving into check and escaping check. It's simple and correct, but slow for bots that search several moves ahead.
- **Rules that need the whole position live in Game.** Castling needs to know which squares are attacked, so `Game.get_castling_moves` adds the castling squares to the king's moves instead of `King.get_moves`.
- **Errors are exceptions with useful messages.** `Game.make_move` raises `ValueError` explaining why a move was rejected (empty square, wrong turn, impossible move, would leave king in check). The GUI just shows the message.
- **Undo saves whole boards.** Before each move, `Game` stores a copy of the board. Undo pops the last copy back.
- **Move-by-move state lives on the Board.** The en passant square and the 50-move counter are stored on `Board` and updated in `move_piece`. Because of that, the board copies used for legality testing and undo carry them automatically, and a pawn can see the en passant square in `get_moves` without knowing about `Game`.

## Classes

### 1. Piece (`pieces.py`)

Parent class for all pieces.

**Class variables** (set by each subclass)
- **letter:** one-letter symbol, e.g. `"R"` for rook, `"N"` for knight (`"K"` is the king).
- **name:** readable name, e.g. `"rook"`, used in messages.

**Instance variables**
- **color:** `WHITE` or `BLACK` (the strings `"white"` / `"black"`).
- **has_moved:** `False` until the piece moves. Used for the pawn's double move and for castling.

**Functions**
- **`__init__(color)`:** stores the colour and sets `has_moved` to `False`.
- **`symbol()`:** the letter in upper case for White, lower case for Black (used by the text display).
- **`get_moves(board, row, col)`:** the squares this piece can move to, following its movement rule. Does not check whether the move leaves the king in check. Every subclass must define it.
- **`get_attacks(board, row, col)`:** the squares this piece attacks. Same as `get_moves` unless overridden.
- **`slide(board, row, col, directions)`:** walks in each direction until it reaches the edge, an own piece (stops before it) or an enemy piece (includes it, then stops).
- **`jump(board, row, col, offsets)`:** tries each fixed offset and keeps squares that are on the board and not occupied by an own piece.

Module-level helpers: the direction lists `STRAIGHT`, `DIAGONAL`, `KNIGHT_JUMPS`, and `other_color(color)`.

### 2. The six pieces (`pieces.py`)

Each subclass sets `letter` and `name` and defines `get_moves`. None of them store extra variables.

| Class | Movement |
|---|---|
| `Rook` | `slide` along `STRAIGHT` |
| `Bishop` | `slide` along `DIAGONAL` |
| `Queen` | `slide` along `STRAIGHT + DIAGONAL` |
| `Knight` | `jump` to `KNIGHT_JUMPS` |
| `King` | `jump` one square in all 8 directions (castling is added by `Game`) |
| `Pawn` | One square forward if empty; two squares on its first move if both are empty; diagonal captures; en passant onto `board.en_passant`. `direction()` gives -1 for White (up the screen) and +1 for Black. Overrides `get_attacks` to return the two forward diagonals. |

### 3. Board (`board.py`)

Stores which piece is on which square and answers questions about the position.

**Instance variables**
- **grid:** 8 lists of 8 entries, each a `Piece` or `None`.
- **en_passant:** the square a pawn just skipped with a two-square move, or `None`. It is set by that move and cleared by the next one, so en passant is only possible straight away.
- **halfmove_clock:** moves (by either side) since the last capture or pawn move, for the 50-move rule.

**Functions**
- **`__init__()`:** creates an empty grid.
- **`setup()`:** places the 32 pieces on their starting squares.
- **`is_inside(row, col)`:** whether a square is on the board.
- **`get_piece(row, col)` / `place_piece(piece, row, col)`:** read or set a square.
- **`move_piece(start, end)`:** moves a piece without checking legality and returns any captured piece. Sets `has_moved`, updates `en_passant` and `halfmove_clock`. Also handles the side effects of special moves: removes the captured pawn in an en passant capture, moves the rook when the king moves two squares (castling), and replaces a pawn reaching the last row with a queen (promotion).
- **`find_king(color)`:** the `(row, col)` of that colour's king.
- **`is_square_attacked(row, col, by_color)`:** whether any piece of `by_color` attacks the square, using `get_attacks`.
- **`is_in_check(color)`:** whether that colour's king is attacked.
- **`has_insufficient_material()`:** whether neither side can checkmate (king vs king, king + one bishop or knight vs king, or only bishops all on the same square colour).
- **`can_capture_en_passant()`:** whether an en passant capture is actually possible right now (a pawn stands beside the one that just moved two squares).
- **`position_key()`:** a summary of the position (pieces, castling rights, a usable en passant square), used to detect repetitions.
- **`display()`:** the board as text, with ranks and files labelled.

Module-level helpers: `square_to_position("e2")` gives `(6, 4)` (raises `ValueError` for bad input), and `position_to_square(6, 4)` gives `"e2"`.

### 4. Game (`game.py`)

Coordinates one game: whose turn it is, which moves are legal, and when the game ends.

**Instance variables**
- **board:** the current `Board`.
- **players:** a dictionary `{WHITE: Player, BLACK: Player}`.
- **current_color:** whose turn it is (White starts).
- **history:** moves played as text, e.g. `["e2-e4", "e7-e5", "d4xe5"]` (`x` marks a capture).
- **saved_boards:** a copy of the board before each move, for undo.
- **game_over:** `True` once the game has ended.
- **result:** a message such as `"Checkmate! White wins."`, empty while the game is running.
- **resigned:** `True` if the game ended by resignation, so undo knows to take back the resignation instead of a move.
- **positions:** the `position_key()` of every position so far (with whose turn it is), for threefold repetition.

**Functions**
- **`__init__(white_player=None, black_player=None)`:** sets up the board and creates default human players if none are given.
- **`current_player()`:** the `Player` whose turn it is.
- **`get_legal_moves(row, col)`:** the piece's moves (plus castling for a king), keeping only those that don't leave its own king in check.
- **`get_castling_moves(row, col)`:** castling squares for the king, if the king and rook haven't moved, the squares between are empty, and the king is not in check and doesn't pass through or land on an attacked square.
- **`all_legal_moves(color)`:** every legal move for a colour, as `((row, col), (row, col))` pairs.
- **`is_in_check()`:** whether the player to move is in check.
- **`is_checkmate(color)` / `is_stalemate(color)`:** no legal moves, with or without being in check.
- **`make_move(start_text, end_text)`:** plays a move given as text (e.g. `"e2", "e4"`). Raises `ValueError` with a reason if it isn't allowed. Saves the board for undo, records history, switches turn and checks for the end of the game. Returns any captured piece.
- **`position_key()`:** the board's position key plus whose turn it is.
- **`check_game_over()`:** sets `game_over` and `result` on checkmate, stalemate, insufficient material, the 50-move rule (100 moves in total without a capture or pawn move) or threefold repetition. Draws are declared automatically.
- **`undo()`:** restores the previous board, turn and position list. If the game ended by resignation, it only takes back the resignation.
- **`resign()`:** the player to move gives up.

### 5. Player and ComputerPlayer (`player.py`)

- **Player:** stores `name` and `color`. `is_computer()` returns `False`.
- **ComputerPlayer(Player):** inherits name and colour, overrides `is_computer()` to return `True`, and adds `choose_move(game)`, which picks a random legal move and returns it as text, e.g. `("g8", "f6")`.

New bot strategies can be added as more `Player` subclasses with their own `choose_move`. The GUI only relies on `is_computer()` and `choose_move()`.

### 6. ChessGUI and Button (`gui.py`)

- **Button:** a labelled rectangle with `is_clicked(x, y)` and `draw(screen, font)`.
- **ChessGUI:** owns the pygame window and the current `Game`.
  - Variables: `game`, `selected` (the clicked piece's square), `highlights` (its legal moves), `message` (status text), `buttons`.
  - Input: `handle_click` decides whether a click is a button, selecting a piece or a move; `select`, `try_move`, `press_button`, `undo` (against the computer it takes back both moves), `computer_turn`.
  - Drawing: `draw_board` (squares, selection, red king in check), `draw_pieces` (a circle with the piece letter), `draw_move_markers` (dots for moves, rings for captures), `draw_panel` (status, move history, buttons).
  - `run()`: the main loop, which handles events, draws at up to 30 frames per second and lets the computer move after a short delay.

## How a move flows through the code

1. The player clicks a piece. `ChessGUI.select` asks `Game.get_legal_moves` and shows the squares.
2. The player clicks a destination. `ChessGUI.try_move` calls `Game.make_move("e2", "e4")`.
3. `Game` converts the text to positions, checks the turn and legality, saves the board, and calls `Board.move_piece`.
4. `Game` records the move, switches `current_color` and runs `check_game_over`.
5. The GUI updates its message (check, checkmate, stalemate or whose turn) and redraws.

## Not built yet / future design

- **Promotion choice:** `move_piece` currently always creates a queen.
- **Faster search:** making and undoing moves in place instead of copying the board, so bots can look several moves ahead.
- **Modular abilities:** the original design idea was to describe movement as reusable ability objects attached to each piece (e.g. `Queen` with `[Slide(STRAIGHT), Slide(DIAGONAL)]`), so a piece's powers could be changed or combined without writing a new class. The `slide`/`jump` helpers with direction lists are the first step towards this.
