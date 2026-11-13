"""The Board class: an 8x8 grid that holds the pieces."""

from chess.pieces import WHITE, BLACK, Rook, Knight, Bishop, Queen, King, Pawn, other_color

FILES = "abcdefgh"


def square_to_position(square):
    """Convert text like "e2" into a (row, col) pair like (6, 4).

    Raises ValueError if the text is not a real square.
    """
    square = square.strip().lower()
    if len(square) != 2 or square[0] not in FILES or square[1] not in "12345678":
        raise ValueError(f"'{square}' is not a square. Use a letter a-h and a number 1-8, like e2.")
    col = FILES.index(square[0])
    row = 8 - int(square[1])
    return (row, col)


def position_to_square(row, col):
    """Convert (6, 4) back into "e2"."""
    return FILES[col] + str(8 - row)


class Board:
    """Stores which piece is on which square."""

    def __init__(self):
        # grid[row][col] holds a Piece object, or None for an empty square
        self.grid = []
        for row in range(8):
            self.grid.append([None] * 8)

    def setup(self):
        """Put all 32 pieces on their starting squares."""
        back_row = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col in range(8):
            self.grid[0][col] = back_row[col](BLACK)
            self.grid[1][col] = Pawn(BLACK)
            self.grid[6][col] = Pawn(WHITE)
            self.grid[7][col] = back_row[col](WHITE)

    def is_inside(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def get_piece(self, row, col):
        return self.grid[row][col]

    def place_piece(self, piece, row, col):
        self.grid[row][col] = piece

    def move_piece(self, start, end):
        """Move a piece from start to end (both are (row, col) pairs).

        This does NOT check whether the move is legal - the Game does that.
        It returns the captured piece, or None.
        """
        start_row, start_col = start
        end_row, end_col = end
        piece = self.grid[start_row][start_col]
        captured = self.grid[end_row][end_col]

        self.grid[end_row][end_col] = piece
        self.grid[start_row][start_col] = None
        piece.has_moved = True

        # Castling: the king moves two squares, so the rook jumps over it
        if isinstance(piece, King) and abs(end_col - start_col) == 2:
            if end_col == 6:      # king side: rook h -> f
                rook = self.grid[end_row][7]
                self.grid[end_row][7] = None
                self.grid[end_row][5] = rook
            else:                 # queen side: rook a -> d
                rook = self.grid[end_row][0]
                self.grid[end_row][0] = None
                self.grid[end_row][3] = rook
            rook.has_moved = True

        # Promotion: a pawn reaching the last row becomes a queen
        if isinstance(piece, Pawn) and (end_row == 0 or end_row == 7):
            self.grid[end_row][end_col] = Queen(piece.color)

        return captured

    def find_king(self, color):
        """Return the (row, col) of the king of this colour."""
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if isinstance(piece, King) and piece.color == color:
                    return (row, col)
        return None

    def is_square_attacked(self, row, col, by_color):
        """True if any piece of by_color attacks the square (row, col)."""
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece is not None and piece.color == by_color:
                    if (row, col) in piece.get_attacks(self, r, c):
                        return True
        return False

    def is_in_check(self, color):
        """True if the king of this colour is attacked."""
        king_position = self.find_king(color)
        if king_position is None:
            return False
        row, col = king_position
        return self.is_square_attacked(row, col, other_color(color))

    def display(self):
        """Return the board as text, ready to print."""
        lines = ["    a b c d e f g h", "  +-----------------+"]
        for row in range(8):
            rank = 8 - row
            cells = []
            for col in range(8):
                piece = self.grid[row][col]
                if piece is None:
                    cells.append(".")
                else:
                    cells.append(piece.symbol())
            lines.append(f"{rank} | {' '.join(cells)} | {rank}")
        lines.append("  +-----------------+")
        lines.append("    a b c d e f g h")
        return "\n".join(lines)
