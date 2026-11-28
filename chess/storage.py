"""Saving finished games to files and loading them again.

A saved game is a small JSON file in the saved_games/ folder:

    {
      "date": "2026-11-27 12:30",
      "white": "White", "white_is_computer": false,
      "black": "Computer", "black_is_computer": true,
      "result": "Checkmate! White wins.",
      "moves": ["e2-e4", "e7-e5", "g1-f3"]
    }

Only the moves are stored, not the board. Loading a game replays the moves
with Game.make_move, so the position is rebuilt by the normal rules.
"""

import json
import os
from datetime import datetime

from chess.game import Game
from chess.pieces import WHITE, BLACK
from chess.player import Player, ComputerPlayer

# saved_games/ sits next to the chess/ folder
SAVE_FOLDER = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "saved_games"))


def save_game(game, folder=SAVE_FOLDER):
    """Write the game to a new JSON file and return the file's path."""
    os.makedirs(folder, exist_ok=True)
    now = datetime.now()
    white = game.players[WHITE]
    black = game.players[BLACK]
    data = {
        "date": now.strftime("%Y-%m-%d %H:%M"),
        "white": white.name,
        "white_is_computer": white.is_computer(),
        "black": black.name,
        "black_is_computer": black.is_computer(),
        "result": game.result,
        "moves": game.history,
    }
    path = os.path.join(folder, now.strftime("game_%Y-%m-%d_%H-%M-%S.json"))
    with open(path, "w") as file:
        json.dump(data, file, indent=2)
    return path


def load_game(path):
    """Read a saved game and replay its moves. Returns a Game object."""
    with open(path) as file:
        data = json.load(file)

    players = {}
    for color in (WHITE, BLACK):
        if data[f"{color}_is_computer"]:
            players[color] = ComputerPlayer(data[color], color)
        else:
            players[color] = Player(data[color], color)

    game = Game(players[WHITE], players[BLACK])
    for move in data["moves"]:
        start, end = move[:2], move[3:5]      # "e2-e4" or "d4xe5" -> "e2", "e4"
        game.make_move(start, end)

    # A resignation doesn't show up in the moves, so copy the result across
    if data["result"] and not game.game_over:
        game.game_over = True
        game.resigned = "resigned" in data["result"]
        game.result = data["result"]
    return game


def list_saved_games(folder=SAVE_FOLDER):
    """The paths of all saved games, oldest first."""
    if not os.path.isdir(folder):
        return []
    names = sorted(name for name in os.listdir(folder) if name.endswith(".json"))
    return [os.path.join(folder, name) for name in names]
