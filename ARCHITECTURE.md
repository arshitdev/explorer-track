## Important Classes
- Piece
    - abilities: cross, straight, jump, l-shape, step, ahead, crosskill
    - it will not know where it is!
- Board
    - 2d array of 64 cell
    - dictionary (cell -> piece)?
    - instantiate 32 pieces
    - instantiate 64 cells
    - place intial pieces on the board
    - know where all the pieces are
    - 
- GameEngine
    - Players
    - Turn
    - Checkmate
    - is move valid?
- Moves
    - Variables: piece, startcell, endcell
- Cell
    - colNumber, rowNumber
    - getColAlphabet()
    - piece: null if empty 
    - row number

- Player
    - name, stats...

- Ability

## Class Descriptions

1. Piece Class
    - This class will have every chess piece and their abilities (how it moves) like cross, L shape, jump etc. But a piece doesn't know where it is on the board!
2. Board Class
    - The board class will basically render the entire chess board and have 64 cells, with 32 pieces and would place the pieces at their start position whenever a new game is played. Board would know where each piece is!
3. GameEngine
    - The GameEngine class will keep a track of the players who are currently playing against each other and keep a track of also whose turn is it next. While doing so, it will also check if a player has been checkmated and check if the move which player wants to play is legal or not.
4. Moves
    - The Moves class would have piece, startPos, and endPos as its member variables and would basically define a move from a specific piece from point A to point B.
5. Cell
    - A cell would be a part of the 8x8 Chess Board and would hold information like if the cell contains any piece or not. It would have a column number, row number for indexing and would show the final positions as (a,b,c,d,e,f,g,h,) x (1,2,3,4,5,6,7,8)
6. Player
    - The Player Class would hold the stats, name of the Player playing the match
7. Ability
    - ENUM, list of abilities supported

## TODO by Tommorow
for each class, list the variables which will capture the information needed by that class and functions which will cover all its responsibilities.

## Class with their variables

1. **Piece**

   Stores the information shared by all pieces. Pawn, Rook, Knight, Bishop, Queen, and King inherit these variables and configure their own abilities.

   - **color:** Describes whether the piece belongs to the white or black side. Helps identify friendly and opposing pieces and configure forward movement.
   - **abilities:** A collection of Ability objects describing how the piece moves, captures, and performs special moves.
   - **has_moved:** A Boolean recording whether the piece has moved before. Helps determine eligibility for a pawn’s initial double move and castling.
   - **value — optional:** Stores the piece’s material value for the optional material-counting bot.

   The subclass identifies the piece’s type, so a separate `type` variable is unnecessary. Its position belongs to Board. The six standard piece subclasses do not require additional stored variables solely to express their different movement rules.

2. **Board**

   Stores the board’s cells and provides access to the pieces occupying them.

   - **cells:** A two-dimensional collection of the 64 Cell objects. Each Cell stores its current occupying piece, allowing Board to find pieces and inspect the position.

   A separate collection of piece positions is unnecessary with this representation. Board can obtain that information from its cells.

3. **GameEngine**

   Coordinates players, turns, move legality, move application, and game results.

   - **board:** The Board object representing the current position.
   - **players:** An ordered collection of the participating Player objects.
   - **turn:** The index of the player whose turn it is.
   - **history:** An ordered list of Moves objects recording the moves played.
   - **en_passant:** The current en passant permission, containing the eligible pawn and the target cell, or `None`. It is updated after every move so the permission lasts only for the immediate reply.

   Check, checkmate, and stalemate can be calculated from the current position. Castling eligibility is checked using the king’s and rook’s moved state, their positions, empty intervening cells, and attacked squares.

4. **Moves**

   Describes a proposed or completed move, including captures, promotion, and effects on additional pieces.

   - **piece:** The Piece object making the main move.
   - **startcell:** The Cell from which that piece moves.
   - **endcell:** The Cell to which that piece moves.
   - **captured_piece:** The Piece object captured by the main move, or `None`. This also identifies an en passant victim, which occupies a different cell from the destination.
   - **promotion:** The selected replacement piece type when a pawn promotes, or `None` for a move without promotion.
   - **additional_changes:** A collection of extra piece movements or removals caused by the move. Each entry identifies the affected piece, its starting cell, and its destination; a missing destination represents removal. For example, castling records the rook’s movement here alongside the king’s main move.

   `additional_changes` contains effects not already represented by the main move or `captured_piece`. Each affected piece should be described once. Abilities describe these effects, and GameEngine validates and applies them.

5. **Cell**

   Represents one square on the board.

   - **rowNumber:** The cell’s row index.
   - **colNumber:** The cell’s column index.
   - **piece:** The Piece object occupying the cell, or `None` when it is empty.

   A label such as `e4` can be calculated from the row and column, so it does not need a separate stored variable.

6. **Player**

   Stores information about a participant and how they choose moves.

   - **name:** The player’s display name.
   - **color:** The side controlled by the player.
   - **stats:** A dictionary containing the statistics the application maintains, such as games played, wins, losses, and draws.
   - **bot:** The move-selection strategy controlling a computer player, or `None` for a human player.

7. **Ability**

   Provides the shared behavior for generating possible moves, identifying attacked cells, or modifying move choices.

   - **No fixed instance variables are required in the base Ability class.** It defines the common functions that specific abilities implement.
   - **Ability-specific configuration:** Individual ability objects store the settings they need. Examples include `directions` for movement offsets, `max_steps` for a maximum sliding distance, or `steps` for an exact forward distance. Special abilities may need conditions, partner-piece references, or promotion choices.
   - **Game and piece information:** These are supplied when an ability is used. The ability can then inspect the current board and find the piece’s position, without permanently storing a board or position itself.

   This follows the agreed design of behavior-owning Ability objects. The existing description of Ability as an enum should be updated to match.

## Classes with their functions


1. **Piece**

   Initializes the information shared by all pieces. Movement behavior belongs to Ability, while Board stores each piece’s position.

   - **`__init__(color, abilities, value=0)` — written:** Stores the piece’s color, collection of abilities, and optional material value. Sets `has_moved` to `False` because the newly created piece has not moved yet.

   No additional functions are needed in Piece for the current design. Its variables can be accessed directly, such as `piece.color`. GameEngine updates its moved state when applying a move.

2. **Board**

   Creates the cells, provides access to their occupants, and finds where pieces are located. Drawing the board on screen belongs to the GUI.

   - **`__init__()` — written:** Creates eight rows containing eight separate Cell objects each. Stores these rows in `cells`, producing a board with 64 empty squares.
   - **`piece_at(row, col)` — written:** Returns the Piece object occupying the cell at the given row and column, or `None` if that cell is empty. The current implementation expects valid indices from 0 to 7.
   - **`position_of(piece)` — planned:** Searches the board for the given Piece object and returns the Cell containing it. Returns `None` if the piece is not on the board. This allows abilities to find a piece without storing its position inside Piece.
   - **`setup_pieces()` — planned:** Places the 32 starting pieces into their cells on an empty board. Each piece receives its color and abilities through its own initializer. We will add this after the six piece subclasses exist and choose how our row indices correspond to the white and black sides.

   Board provides the position information needed by the other classes. GameEngine decides which moves are legal and coordinates changes to the occupied cells.

3. **GameEngine**

   Coordinates players, turns, move legality, move application, and game results.

   - **`__init__(board, players)` — planned:** Stores the board and players in turn order. Sets `turn` to the first player, creates an empty move history, and sets `en_passant` to `None`.
   - **`legal_moves(piece=None)` — planned:** Collects candidate moves from the current player’s piece abilities, including any modifications such as promotion choices. Filters out moves that leave that player’s king in check. Returns legal moves for one piece when supplied, or for all of the current player’s pieces otherwise.
   - **`in_check(player)` — planned:** Finds the player’s king and checks whether an opposing piece attacks its cell. Uses the abilities’ attacked cells rather than opponents’ legal moves, so it does not need to calculate legal moves recursively.
   - **`play(move)` — planned:** Applies a move selected from the engine’s legal moves. Updates the affected cells, handles captures and additional changes, replaces a promoted pawn when necessary, and updates moved state. Records the move, updates or clears en passant permission, and advances the turn. This same move-application behavior will also be used when simulating candidate moves.
   - **`next_player()` — planned:** Returns the index of the next player, wrapping back to the first player after the last one. `play()` uses this value to update `turn`.
   - **`copy()` — planned:** Creates a separate game position for trying candidate moves without changing the real game. The copied board, cells, pieces, and mutable game state must remain independent. Moves used in a simulation must refer to the corresponding objects in that copy.
   - **`result()` — planned:** Determines whether the game is still running, has ended in checkmate, or has ended in stalemate. No legal moves while in check means checkmate; no legal moves without being in check means stalemate. Returns the result and winner when applicable, or `None` while play continues.
   - **`score(player)` — optional, planned:** Evaluates the position from the given player’s perspective using piece values and game results. Supports the optional material-counting bot.

   Abilities describe possible moves and attacks. GameEngine checks king safety and manages the resulting game state. Attack detection must still count attacks from pinned pieces, even when moving those pieces would expose their own king.

4. **Moves**

   Stores a description of one proposed or completed move. Creating this object does not change the board.

   - **`__init__(piece, startcell, endcell, captured_piece=None, promotion=None, additional_changes=None)` — planned:** Stores the moving piece, starting cell, destination cell, and any capture or promotion. Stores extra effects such as the rook’s movement during castling. When additional changes are not supplied, creates a fresh empty collection for this move.

   No separate execution function is needed in Moves because GameEngine applies moves. A captured piece is recorded in `captured_piece` and should not be repeated in `additional_changes`.

5. **Cell**

   Initializes one board square and can provide a readable representation of its coordinates.

   - **`__init__(rowNumber, colNumber, piece=None)` — written:** Stores the cell’s row and column indices and its occupying piece. Defaults to `None` so the cell starts empty unless a piece is supplied.
   - **`getColAlphabet()` — planned:** Converts the column index from 0–7 into its corresponding letter from `a`–`h`. For example, column 0 gives `a` and column 4 gives `e`.
   - **`get_label()` — optional, planned:** Combines the column letter with the chess rank to return a label such as `e4`. The rank conversion will follow the board orientation chosen during setup. The label is calculated when needed rather than stored as another variable.

   The occupying piece can be read or assigned directly through `cell.piece`; separate getter and setter functions are unnecessary.

6. **Player**

   Initializes a participant’s identity, side, statistics, and optional computer control.

   - **`__init__(name, color, bot=None)` — planned:** Stores the player’s name, color, and optional bot strategy. Creates a fresh statistics dictionary for this player, with the tracked counts starting at zero. A `bot` value of `None` identifies a human player.

   Human move choices come from the input interface. A computer player’s bot will provide its own `choose_move(game)` function. Move validation remains in GameEngine, and statistics can be updated once a game result is known.

7. **Ability**

   Defines the common functions used by reusable movement and special-move behaviors. These functions receive the current game and acting piece instead of storing a permanent position or board reference.

   - **`moves(game, piece)` — planned:** Produces candidate Moves objects for this ability by inspecting the board and applying its movement and capture rules. These candidates still need GameEngine’s king-safety checks before they can be treated as legal moves.
   - **`attacked_cells(game, piece)` — planned:** Returns the cells threatened by this ability, independently of whether moving the attacking piece would expose its own king. This is used to detect check and prevent a king from moving onto an attacked square. Pawn forward movement and castling do not contribute attacks.
   - **`modify_moves(game, piece, moves)` — planned:** Receives the combined candidate moves from a piece’s abilities and returns an adjusted collection. For example, promotion behavior can replace a move reaching the last rank with separate choices for the replacement piece. An ability that does not modify moves returns the collection unchanged.

   The base Ability class does not need an initializer until it has shared configuration to store. Specific abilities will initialize their own settings, such as directions, sliding limits, or promotion choices. These functions generate descriptions and must not change the current game position.

8. **Pawn, Rook, Knight, Bishop, Queen, and King**

   Each subclass inherits Piece’s variables and chooses its own abilities. Its initializer calls the Piece initializer to store the shared information. Movement rules remain in the abilities rather than being duplicated in these subclasses.

   - **`Pawn.__init__(color)` — planned:** Configures forward movement and diagonal captures for the pawn’s color. Its complete ability collection will also cover the initial double move, en passant, and promotion. Sets its material value through the Piece initializer.
   - **`Rook.__init__(color)` — planned:** Configures sliding movement along rows and columns and initializes the rook’s shared Piece information.
   - **`Knight.__init__(color)` — planned:** Configures L-shaped jumps that ignore intervening pieces and initializes the knight’s shared Piece information.
   - **`Bishop.__init__(color)` — planned:** Configures diagonal sliding movement and initializes the bishop’s shared Piece information.
   - **`Queen.__init__(color)` — planned:** Configures both straight and diagonal sliding movement and initializes the queen’s shared Piece information.
   - **`King.__init__(color)` — planned:** Configures one-square movement in every direction and initializes the king’s shared Piece information. Castling behavior can be attached during setup once the partner rooks are known. GameEngine rejects moves that leave the king on an attacked square.

   These six subclasses do not need their own `move()` functions. Their abilities generate moves, and GameEngine applies accepted moves.
