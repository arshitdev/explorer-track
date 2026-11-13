"""Players: a person, or a (very simple) computer."""

import random

from chess.board import position_to_square


class Player:
    """A person playing the game."""

    def __init__(self, name, color):
        self.name = name
        self.color = color

    def is_computer(self):
        return False


class ComputerPlayer(Player):
    """A computer player that chooses a random legal move.

    It inherits name and color from Player, and changes (overrides)
    is_computer. It also adds a new method, choose_move.
    """

    def is_computer(self):
        return True

    def choose_move(self, game):
        """Pick a random legal move and return it as text, e.g. ("g8", "f6")."""
        moves = game.all_legal_moves(self.color)
        start, end = random.choice(moves)
        return position_to_square(*start), position_to_square(*end)
