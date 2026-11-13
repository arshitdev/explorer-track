"""The Game class: turns, the rules, check, checkmate, history and undo."""

import copy

from chess.board import Board, square_to_position, position_to_square
from chess.pieces import WHITE, BLACK, King, Rook, other_color
from chess.player import Player


class Game:
    """One game of chess between two players."""

    def __init__(self, white_player=None, black_player=None):
        self.board = Board()
        self.board.setup()
        if white_player is None:
            white_player = Player("White", WHITE)
        if black_player is None:
            black_player = Player("Black", BLACK)
        self.players = {WHITE: white_player, BLACK: black_player}
        self.current_color = WHITE   # White always starts
        self.history = []            # moves played, e.g. ["e2-e4", "e7-e5"]
        self.saved_boards = []       # a copy of the board before each move (for undo)
        self.game_over = False
        self.result = ""             # e.g. "Checkmate! White wins."

    def current_player(self):
        return self.players[self.current_color]

    # ------------------------------------------------------------ the rules

    def get_legal_moves(self, row, col):
        """All squares the piece on (row, col) may legally move to.

        A move is legal if it follows the piece's movement rule AND does not
        leave your own king in check. To test the second part we simply try
        the move on a copy of the board and look.
        """
        piece = self.board.get_piece(row, col)
        if piece is None:
            return []
        candidates = piece.get_moves(self.board, row, col)
        if isinstance(piece, King):
            candidates = candidates + self.get_castling_moves(row, col)

        legal = []
        for end in candidates:
            test_board = copy.deepcopy(self.board)
            test_board.move_piece((row, col), end)
            if not test_board.is_in_check(piece.color):
                legal.append(end)
        return legal

    def get_castling_moves(self, row, col):
        """Castling squares for the king on (row, col), if castling is allowed."""
        king = self.board.get_piece(row, col)
        if king.has_moved or self.board.is_in_check(king.color):
            return []
        enemy = other_color(king.color)
        moves = []
        # (column of the rook, columns that must be empty, columns the king walks over)
        options = [(7, [5, 6], [5, 6]),       # king side
                   (0, [1, 2, 3], [3, 2])]    # queen side
        for rook_col, must_be_empty, king_path in options:
            rook = self.board.get_piece(row, rook_col)
            if not isinstance(rook, Rook) or rook.color != king.color or rook.has_moved:
                continue
            if any(self.board.get_piece(row, c) is not None for c in must_be_empty):
                continue
            if any(self.board.is_square_attacked(row, c, enemy) for c in king_path):
                continue
            moves.append((row, king_path[-1]))
        return moves

    def all_legal_moves(self, color):
        """Every legal move for one colour, as a list of (start, end) pairs."""
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece is not None and piece.color == color:
                    for end in self.get_legal_moves(row, col):
                        moves.append(((row, col), end))
        return moves

    def is_in_check(self):
        return self.board.is_in_check(self.current_color)

    def is_checkmate(self, color):
        return self.board.is_in_check(color) and len(self.all_legal_moves(color)) == 0

    def is_stalemate(self, color):
        return not self.board.is_in_check(color) and len(self.all_legal_moves(color)) == 0

    # ------------------------------------------------------------ playing

    def make_move(self, start_text, end_text):
        """Play a move such as make_move("e2", "e4").

        Raises ValueError with a helpful message if the move is not allowed.
        """
        if self.game_over:
            raise ValueError("The game is over.")
        start = square_to_position(start_text)
        end = square_to_position(end_text)
        piece = self.board.get_piece(*start)

        if piece is None:
            raise ValueError(f"There is no piece on {start_text}.")
        if piece.color != self.current_color:
            raise ValueError(f"That {piece.name} is {piece.color}. It is {self.current_color}'s turn.")
        if end not in self.get_legal_moves(*start):
            # Give the player a reason, not just "illegal"
            follows_rule = end in piece.get_moves(self.board, *start)
            if follows_rule:
                raise ValueError("That move would leave your king in check.")
            raise ValueError(f"A {piece.name} cannot move from {start_text} to {end_text}.")

        self.saved_boards.append(copy.deepcopy(self.board))   # remember, for undo
        captured = self.board.move_piece(start, end)

        separator = "x" if captured else "-"
        self.history.append(f"{start_text}{separator}{end_text}")
        self.current_color = other_color(self.current_color)
        self.check_game_over()
        return captured

    def check_game_over(self):
        """After every move: has the player to move been checkmated or stalemated?"""
        color = self.current_color
        if self.is_checkmate(color):
            self.game_over = True
            self.result = f"Checkmate! {other_color(color).capitalize()} wins."
        elif self.is_stalemate(color):
            self.game_over = True
            self.result = "Stalemate! The game is a draw."

    def undo(self):
        """Take back the last move."""
        if len(self.saved_boards) == 0:
            raise ValueError("There are no moves to undo.")
        self.board = self.saved_boards.pop()
        self.history.pop()
        self.current_color = other_color(self.current_color)
        self.game_over = False
        self.result = ""

    def resign(self):
        """The player whose turn it is gives up."""
        loser = self.current_color
        self.game_over = True
        self.result = f"{loser.capitalize()} resigned. {other_color(loser).capitalize()} wins."
