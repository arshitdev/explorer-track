"""Game review: how well did each player play the opening, middlegame and endgame?

How it works:
1. Replay the game move by move. Before each move, note the game phase.
2. Ask Stockfish to score every position (from White's point of view).
3. The "loss" of a move is how much the score dropped for the player who moved.
   A perfect move loses about 0; giving away a knight loses about 300 (3 pawns).
4. Average the losses for each phase and turn them into advice.

You can also review a saved game from the terminal:
    python -m chess.analysis saved_games/game_2026-11-27_12-30-00.json
"""

import sys

from chess.board import square_to_position
from chess.game import Game
from chess.pieces import WHITE, BLACK, Pawn, Knight, Bishop, Rook, Queen, King

# How big a loss (in centipawns, 100 = one pawn) counts as each kind of mistake
INACCURACY = 50
MISTAKE = 100
BLUNDER = 300
MAX_LOSS = 1000     # cap, so one missed checkmate doesn't swamp the averages

OPENING_MOVES = 10  # the first 10 moves by each side count as the opening
PHASES = ["opening", "middlegame", "endgame"]
PIECE_VALUES = {Knight: 3, Bishop: 3, Rook: 5, Queen: 9}

TIPS = {
    "opening": "In the opening, bring out your knights and bishops, fight for the centre "
               "and castle early. Avoid moving the same piece twice.",
    "middlegame": "In the middlegame, before every move check which of your pieces are "
                  "attacked and whether they are protected.",
    "endgame": "In the endgame, use your king actively and push your passed pawns. "
               "Trade pieces when you are ahead.",
}


def game_phase(board, half_moves_played):
    """Which phase is the game in? half_moves_played counts both players' moves."""
    queens = 0
    material = 0    # knights, bishops, rooks and queens of both sides (pawns and kings don't count)
    for row in range(8):
        for col in range(8):
            piece = board.get_piece(row, col)
            if piece is None:
                continue
            if isinstance(piece, Queen):
                queens += 1
            material += PIECE_VALUES.get(type(piece), 0)
    # At the start material is 62. Endgame: queens traded, or few pieces left.
    if queens == 0 or material <= 26:
        return "endgame"
    if half_moves_played < 2 * OPENING_MOVES:
        return "opening"
    return "middlegame"


def to_uci(start, end, piece):
    """Our move "e2", "e4" -> Stockfish's "e2e4". A pawn reaching the last row
    always becomes a queen in our engine, so we add "q"."""
    move = start + end
    if isinstance(piece, Pawn) and end[1] in "18":
        move += "q"
    return move


def plural(count, word):
    """plural(1, "mistake") -> "1 mistake", plural(3, "mistake") -> "3 mistakes" """
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def label_for(loss):
    if loss >= BLUNDER:
        return "blunder"
    if loss >= MISTAKE:
        return "mistake"
    if loss >= INACCURACY:
        return "inaccuracy"
    return "good"


class MoveReview:
    """What we found out about one move."""

    def __init__(self, number, color, move, phase, loss, best_move):
        self.number = number          # the move number, as in "12. e2-e4"
        self.color = color
        self.move = move              # e.g. "e2-e4"
        self.phase = phase
        self.loss = loss              # centipawns this move gave away
        self.label = label_for(loss)
        self.best_move = best_move    # what Stockfish would have played, e.g. "g1-f3"


class GameAnalyzer:
    """Scores every move of a game with the help of an engine (e.g. Stockfish)."""

    def __init__(self, engine):
        self.engine = engine
        self.castled = {WHITE: False, BLACK: False}

    def analyse(self, moves):
        """moves: the game's history, e.g. ["e2-e4", "e7-e5"]. Returns a list of MoveReview."""
        game = Game()
        uci_moves = []
        phases = []
        evaluations = [self.engine.evaluate([])]     # (score, best move) of every position

        for i, move in enumerate(moves):
            start, end = move[:2], move[3:5]
            piece = game.board.get_piece(*square_to_position(start))
            phases.append(game_phase(game.board, i))
            if isinstance(piece, King) and abs(ord(end[0]) - ord(start[0])) == 2:
                self.castled[piece.color] = True
            uci_moves.append(to_uci(start, end, piece))
            game.make_move(start, end)
            evaluations.append(self.engine.evaluate(uci_moves))

        reviews = []
        for i, move in enumerate(moves):
            color = WHITE if i % 2 == 0 else BLACK
            before = evaluations[i][0]
            after = evaluations[i + 1][0]
            loss = before - after if color == WHITE else after - before
            loss = max(0, min(loss, MAX_LOSS))
            best = evaluations[i][1]
            if best == uci_moves[i]:
                loss = 0      # the engine's own top choice can't be a mistake
            best_text = f"{best[:2]}-{best[2:4]}" if best else None
            reviews.append(MoveReview(i // 2 + 1, color, move, phases[i], loss, best_text))
        return reviews


class Report:
    """Turns the move reviews of one player into advice."""

    def __init__(self, reviews, color, castled=True):
        self.color = color
        self.castled = castled
        self.moves = [review for review in reviews if review.color == color]

    def phase_moves(self, phase):
        return [review for review in self.moves if review.phase == phase]

    def average_loss(self, phase):
        moves = self.phase_moves(phase)
        if not moves:
            return None
        return sum(review.loss for review in moves) / len(moves)

    def count(self, phase, label):
        return sum(1 for review in self.phase_moves(phase) if review.label == label)

    def verdict(self, phase):
        """A one-word grade for a phase, from the average loss per move."""
        average = self.average_loss(phase)
        if average is None:
            return None
        if average < 30:
            return "strong"
        if average < 70:
            return "decent"
        if average < 150:
            return "shaky"
        return "weak"

    def lines(self):
        """The advice, as a list of sentences."""
        played = [phase for phase in PHASES if self.phase_moves(phase)]
        if not played:
            return [f"{self.color.capitalize()} made no moves to review."]

        lines = []
        for phase in played:
            blunders = plural(self.count(phase, "blunder"), "blunder")
            mistakes = plural(self.count(phase, "mistake"), "mistake")
            lines.append(f"{phase.capitalize()}: {self.verdict(phase)} "
                         f"({blunders}, {mistakes}, "
                         f"average loss {self.average_loss(phase) / 100:.1f} pawns per move).")

        # The headline: best phase vs worst phase
        best = min(played, key=self.average_loss)
        worst = max(played, key=self.average_loss)
        if len(played) == 1 or self.verdict(best) == self.verdict(worst):
            lines.append(f"Your play was {self.verdict(best)} throughout.")
        elif self.verdict(worst) in ("shaky", "weak"):
            lines.append(f"Your {best} is {self.verdict(best)}, however you struggle "
                         f"in the {worst}.")
        else:
            lines.append(f"Your {best} is {self.verdict(best)} and your {worst} "
                         f"is {self.verdict(worst)}.")
        if self.verdict(worst) in ("shaky", "weak"):
            lines.append(TIPS[worst])

        if not self.castled and len(self.moves) > OPENING_MOVES:
            lines.append("You never castled. Castling keeps your king safe and brings a rook into play.")

        worst_move = max(self.moves, key=lambda review: review.loss)
        if worst_move.label in ("mistake", "blunder"):
            if worst_move.loss >= MAX_LOSS:
                damage = "this let your opponent force checkmate or win a lot of material"
            else:
                damage = f"lost about {worst_move.loss / 100:.1f} pawns"
            line = f"Biggest mistake: move {worst_move.number}, {worst_move.move} ({damage})."
            if worst_move.best_move:
                line += f" Better was {worst_move.best_move}."
            lines.append(line)
        return lines


def review_game(moves, players_to_review=(WHITE, BLACK), engine=None):
    """Analyse a game and return {color: list of advice lines}."""
    from chess.stockfish import Stockfish
    if engine is None:
        with Stockfish() as engine:
            return review_game(moves, players_to_review, engine)
    analyzer = GameAnalyzer(engine)
    reviews = analyzer.analyse(moves)
    return {color: Report(reviews, color, analyzer.castled[color]).lines()
            for color in players_to_review}


if __name__ == "__main__":
    from chess.storage import load_game
    if len(sys.argv) != 2:
        print("Usage: python -m chess.analysis saved_games/<file>.json")
        sys.exit(1)
    saved = load_game(sys.argv[1])
    humans = [color for color in (WHITE, BLACK) if not saved.players[color].is_computer()]
    for color, lines in review_game(saved.history, humans).items():
        print(f"\n== {color.capitalize()} ({saved.players[color].name}) ==")
        for line in lines:
            print(" -", line)
