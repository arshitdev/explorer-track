"""A small connection to the Stockfish chess engine installed on this computer.

Stockfish is a separate program. We start it and talk to it through text
commands, using the standard UCI protocol ("Universal Chess Interface"):

    we send:   position startpos moves e2e4 e7e5
    we send:   go depth 16
    it sends:  info depth 16 ... score cp 35 ... pv g1f3 ...
    it sends:  bestmove g1f3

"score cp 35" means the side to move is ahead by 35 centipawns (0.35 of a pawn).
"score mate 3" means the side to move can force checkmate in 3 moves.

Install Stockfish first, e.g. on Arch Linux:   yay -S stockfish
"""

import shutil
import subprocess

MATE_SCORE = 10000      # how we count "checkmate is coming", in centipawns


def is_installed():
    return shutil.which("stockfish") is not None


class Stockfish:
    """Ask Stockfish how good a position is and what the best move would be."""

    def __init__(self, depth=16, path=None):
        if path is None:
            path = shutil.which("stockfish")
        if path is None:
            raise FileNotFoundError(
                "Stockfish is not installed. Install it with: yay -S stockfish")
        self.depth = depth      # how many moves ahead Stockfish looks
        self.process = subprocess.Popen([path], stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, text=True, bufsize=1)
        self.send("uci")
        self.read_until("uciok")
        self.send("isready")
        self.read_until("readyok")

    def send(self, command):
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

    def read_until(self, word):
        """Read Stockfish's answer line by line until a line starts with word.
        Returns all the lines read."""
        lines = []
        while True:
            line = self.process.stdout.readline()
            if line == "":
                raise RuntimeError("Stockfish stopped unexpectedly.")
            line = line.strip()
            lines.append(line)
            if line.startswith(word):
                return lines

    def evaluate(self, moves):
        """Evaluate the position reached after the given moves.

        moves are in UCI form, e.g. ["e2e4", "e7e5"] (promotion: "e7e8q").
        Returns (score, best_move):
          score     - centipawns from WHITE's point of view (+100 = White is a pawn up)
          best_move - Stockfish's best move in UCI form, or None if the game is over
        """
        if moves:
            self.send("position startpos moves " + " ".join(moves))
        else:
            self.send("position startpos")
        self.send(f"go depth {self.depth}")
        lines = self.read_until("bestmove")

        score = 0
        for line in lines:                  # the last "score" line is the deepest one
            words = line.split()
            if "score" in words:
                i = words.index("score")
                kind, value = words[i + 1], int(words[i + 2])
                if kind == "cp":
                    score = value
                elif value > 0:             # "mate 3": side to move mates soon
                    score = MATE_SCORE
                else:                       # "mate -2" or "mate 0": side to move gets mated
                    score = -MATE_SCORE

        # Stockfish scores from the side to move. Black is to move after an odd number of moves.
        if len(moves) % 2 == 1:
            score = -score

        best_move = lines[-1].split()[1]    # "bestmove g1f3 ponder ..." -> "g1f3"
        if best_move == "(none)":
            best_move = None
        return score, best_move

    def close(self):
        self.send("quit")
        self.process.wait(timeout=5)

    # These two let you write:  with Stockfish() as engine: ...
    def __enter__(self):
        return self

    def __exit__(self, *details):
        self.close()
