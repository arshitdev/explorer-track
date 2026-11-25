"""The six chess pieces.

Every piece is a class that inherits from the parent class Piece.
Each piece knows its colour, and how it moves (its get_moves method).

Squares are written as (row, col) pairs:
    row 0 is rank 8 (Black's side, top of the screen)
    row 7 is rank 1 (White's side, bottom of the screen)
    col 0 is file a, col 7 is file h
"""

WHITE = "white"
BLACK = "black"

# Directions as (row change, column change)
STRAIGHT = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIAGONAL = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
KNIGHT_JUMPS = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]


def other_color(color):
    """Return the opponent's colour."""
    if color == WHITE:
        return BLACK
    return WHITE


class Piece:
    """Parent class for all pieces. The child classes fill in the details."""

    letter = "?"   # each child class sets its own letter, e.g. "R" for rook
    name = "piece"

    def __init__(self, color):
        self.color = color
        self.has_moved = False   # needed for castling and the pawn's first move

    def symbol(self):
        """Upper case letter for White pieces, lower case for Black pieces."""
        if self.color == WHITE:
            return self.letter
        return self.letter.lower()

    def get_moves(self, board, row, col):
        """Return a list of (row, col) squares this piece can move to.

        Every child class MUST write its own version of this method.
        """
        raise NotImplementedError("Each piece must define get_moves")

    def get_attacks(self, board, row, col):
        """Squares this piece attacks. For most pieces it is the same as get_moves.
        (The pawn is different, so it overrides this method.)"""
        return self.get_moves(board, row, col)

    # ---- two helper methods shared by the child classes ----

    def slide(self, board, row, col, directions):
        """Move in straight lines until something blocks the way (rook, bishop, queen)."""
        moves = []
        for row_step, col_step in directions:
            r = row + row_step
            c = col + col_step
            while board.is_inside(r, c):
                target = board.get_piece(r, c)
                if target is None:
                    moves.append((r, c))          # empty square: keep going
                elif target.color != self.color:
                    moves.append((r, c))          # enemy piece: capture, then stop
                    break
                else:
                    break                         # own piece: stop before it
                r = r + row_step
                c = c + col_step
        return moves

    def jump(self, board, row, col, offsets):
        """Jump to fixed squares (king and knight)."""
        moves = []
        for row_step, col_step in offsets:
            r = row + row_step
            c = col + col_step
            if board.is_inside(r, c):
                target = board.get_piece(r, c)
                if target is None or target.color != self.color:
                    moves.append((r, c))
        return moves


class Rook(Piece):
    letter = "R"
    name = "rook"

    def get_moves(self, board, row, col):
        return self.slide(board, row, col, STRAIGHT)


class Bishop(Piece):
    letter = "B"
    name = "bishop"

    def get_moves(self, board, row, col):
        return self.slide(board, row, col, DIAGONAL)


class Queen(Piece):
    letter = "Q"
    name = "queen"

    def get_moves(self, board, row, col):
        return self.slide(board, row, col, STRAIGHT + DIAGONAL)


class Knight(Piece):
    letter = "N"   # "K" is already used by the king
    name = "knight"

    def get_moves(self, board, row, col):
        return self.jump(board, row, col, KNIGHT_JUMPS)


class King(Piece):
    letter = "K"
    name = "king"

    def get_moves(self, board, row, col):
        # Castling is handled by the Game class, because it needs to
        # know which squares are attacked.
        return self.jump(board, row, col, STRAIGHT + DIAGONAL)


class Pawn(Piece):
    letter = "P"
    name = "pawn"

    def direction(self):
        """White pawns move up the screen (row gets smaller), Black pawns move down."""
        if self.color == WHITE:
            return -1
        return 1

    def get_moves(self, board, row, col):
        moves = []
        step = self.direction()

        # 1. One square forward, only if empty
        r = row + step
        if board.is_inside(r, col) and board.get_piece(r, col) is None:
            moves.append((r, col))
            # 2. Two squares forward on the pawn's first move, if both are empty
            r2 = row + 2 * step
            if not self.has_moved and board.is_inside(r2, col) and board.get_piece(r2, col) is None:
                moves.append((r2, col))

        # 3. Capture diagonally forward, only if an enemy piece is there
        # 4. En passant: capture diagonally onto the empty square an enemy pawn
        #    just skipped over with its two-square move
        for r, c in self.get_attacks(board, row, col):
            target = board.get_piece(r, c)
            if target is not None and target.color != self.color:
                moves.append((r, c))
            elif target is None and (r, c) == board.en_passant:
                moves.append((r, c))
        return moves

    def get_attacks(self, board, row, col):
        """A pawn attacks the two squares diagonally in front of it."""
        attacks = []
        r = row + self.direction()
        for c in (col - 1, col + 1):
            if board.is_inside(r, c):
                attacks.append((r, c))
        return attacks
