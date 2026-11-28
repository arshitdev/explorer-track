"""The graphical user interface (GUI), made with pygame.

This is the ONLY file that knows about the window, the mouse and drawing.
The rules of chess stay in game.py, board.py and pieces.py - they did not
change at all when we replaced the text interface with this GUI.

How to play: click one of your pieces (its legal moves are marked with dots),
then click the square you want to move to.
"""

import os

import pygame

from chess.board import position_to_square
from chess.game import Game
from chess.pieces import WHITE, BLACK
from chess.player import Player, ComputerPlayer
from chess.storage import save_game
from chess.analysis import review_game
from chess.stockfish import is_installed

# ---- sizes (in pixels) ----
SQUARE_SIZE = 80
BOARD_SIZE = 8 * SQUARE_SIZE          # 640
PANEL_WIDTH = 260                     # the area to the right of the board
WINDOW_WIDTH = BOARD_SIZE + PANEL_WIDTH
WINDOW_HEIGHT = BOARD_SIZE

# ---- colours as (red, green, blue) ----
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
SELECTED = (246, 246, 105)
CHECK_RED = (235, 97, 80)
MOVE_DOT = (90, 90, 90)
PANEL_BACKGROUND = (45, 45, 48)
TEXT_COLOR = (235, 235, 235)
BUTTON_COLOR = (80, 80, 90)
WHITE_PIECE = (250, 250, 250)
BLACK_PIECE = (30, 30, 30)

# Folder with the piece images, named like white_K.png or black_N.png
PIECE_SIZE = SQUARE_SIZE - 8   # a small gap so the a-h / 1-8 labels stay visible
ASSETS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

COMPUTER_DELAY = 400   # milliseconds the computer "thinks", so you can see your own move


# ---------------------------------------------------------------- helpers
def pixel_to_square(x, y):
    """Turn a mouse position into a board square (row, col).
    Returns None if the click was outside the board."""
    if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
        return (y // SQUARE_SIZE, x // SQUARE_SIZE)
    return None


def square_to_pixel(row, col):
    """The top-left corner (x, y) of a square on the screen."""
    return (col * SQUARE_SIZE, row * SQUARE_SIZE)


def wrap_text(text, max_chars):
    """Split a long message into lines of at most max_chars characters."""
    lines = []
    current = ""
    for word in text.split():
        if current and len(current) + 1 + len(word) > max_chars:
            lines.append(current)
            current = word
        elif current:
            current = current + " " + word
        else:
            current = word
    if current:
        lines.append(current)
    return lines


def history_lines(history):
    """Pair up the moves: ["e2-e4", "e7-e5", "g1-f3"] -> ["1. e2-e4  e7-e5", "2. g1-f3"]."""
    lines = []
    for i in range(0, len(history), 2):
        line = f"{i // 2 + 1}. {history[i]}"
        if i + 1 < len(history):
            line = line + "  " + history[i + 1]
        lines.append(line)
    return lines


# ---------------------------------------------------------------- classes
class Button:
    """A rectangle with a label that can be clicked."""

    def __init__(self, text, x, y, width, height):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)

    def is_clicked(self, x, y):
        return self.rect.collidepoint(x, y)

    def draw(self, screen, font):
        pygame.draw.rect(screen, BUTTON_COLOR, self.rect, border_radius=6)
        label = font.render(self.text, True, TEXT_COLOR)
        screen.blit(label, label.get_rect(center=self.rect.center))


class ChessGUI:
    """The game window: draws the board and turns mouse clicks into moves."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Chess in Python")
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.piece_font = pygame.font.Font(None, 46)
        self.piece_images = self.load_piece_images()

        x = BOARD_SIZE + 20
        width = PANEL_WIDTH - 40
        self.buttons = {
            "two_players": Button("New game: 2 players", x, 420, width, 40),
            "computer": Button("New game: vs computer", x, 470, width, 40),
            "undo": Button("Undo", x, 540, width // 2 - 5, 40),
            "resign": Button("Resign", x + width // 2 + 5, 540, width // 2 - 5, 40),
            "review": Button("Review game", x, 590, width, 40),
        }
        self.new_game(against_computer=False)

    def load_piece_images(self):
        """Load one picture per piece, e.g. assets/white_K.png, scaled to fit a square.

        Returns a dictionary {(color, letter): image}. If any picture is missing,
        it returns an empty dictionary and the pieces are drawn as lettered circles.
        """
        images = {}
        for color in (WHITE, BLACK):
            for letter in "KQRBNP":
                path = os.path.join(ASSETS_FOLDER, f"{color}_{letter}.png")
                try:
                    image = pygame.image.load(path).convert_alpha()
                except (FileNotFoundError, pygame.error):
                    print(f"Could not load {path}, drawing pieces as letters instead.")
                    return {}
                images[(color, letter)] = pygame.transform.smoothscale(image, (PIECE_SIZE, PIECE_SIZE))
        return images

    def new_game(self, against_computer):
        """Start a fresh game (with or without a computer opponent)."""
        if against_computer:
            black = ComputerPlayer("Computer", BLACK)
        else:
            black = Player("Black", BLACK)
        self.game = Game(Player("White", WHITE), black)
        self.selected = None      # the (row, col) of the piece the player clicked
        self.highlights = []      # the squares that piece can move to
        self.message = "White to move. Click a piece."
        self.saved_path = None    # where this game was saved once it ended
        self.review_lines = None  # the game review, shown over the board when not None

    # ------------------------------------------------------------ input
    def handle_click(self, x, y):
        """Decide what a mouse click means: a button, choosing a piece, or a move."""
        for name, button in self.buttons.items():
            if button.is_clicked(x, y):
                self.press_button(name)
                return

        square = pixel_to_square(x, y)
        if square is not None and self.review_lines is not None:
            self.review_lines = None              # a click on the board closes the review
            return
        if square is None or self.game.game_over:
            return
        if self.game.current_player().is_computer():
            return   # wait for the computer

        row, col = square
        piece = self.game.board.get_piece(row, col)
        if piece is not None and piece.color == self.game.current_color:
            self.select(row, col)                 # clicked one of your own pieces
        elif self.selected is not None:
            self.try_move(square)                 # clicked where to go
        else:
            self.message = f"Click one of the {self.game.current_color} pieces."

    def select(self, row, col):
        piece = self.game.board.get_piece(row, col)
        self.selected = (row, col)
        self.highlights = self.game.get_legal_moves(row, col)
        if self.highlights:
            self.message = f"{piece.name.capitalize()} on {position_to_square(row, col)} selected."
        else:
            self.message = f"That {piece.name} has no legal moves."

    def try_move(self, square):
        """Ask the Game to make the move. The Game explains if it is illegal."""
        start = position_to_square(*self.selected)
        end = position_to_square(*square)
        try:
            self.game.make_move(start, end)
            self.update_message()
            self.save_if_finished()
        except ValueError as error:
            self.message = str(error)
        self.selected = None
        self.highlights = []

    def press_button(self, name):
        if name == "two_players":
            self.new_game(against_computer=False)
        elif name == "computer":
            self.new_game(against_computer=True)
        elif name == "undo":
            self.undo()
        elif name == "resign" and not self.game.game_over:
            self.game.resign()
            self.message = self.game.result
            self.save_if_finished()
        elif name == "review":
            self.review()

    def undo(self):
        try:
            self.game.undo()
            # Against the computer, also take back the computer's move
            if self.game.current_player().is_computer() and len(self.game.saved_boards) > 0:
                self.game.undo()
            self.update_message()
            self.saved_path = None      # if the game ends again, save it again
        except ValueError as error:
            self.message = str(error)
        self.selected = None
        self.highlights = []

    def computer_turn(self):
        """If it is the computer's turn, let it move."""
        player = self.game.current_player()
        if not self.game.game_over and player.is_computer():
            start, end = player.choose_move(self.game)
            self.game.make_move(start, end)
            self.update_message()
            self.save_if_finished()
            if not self.game.game_over:
                self.message = f"Computer played {start}-{end}. " + self.message

    def save_if_finished(self):
        """Save the game to saved_games/ once it is over (only once per ending)."""
        if self.game.game_over and self.saved_path is None and self.game.history:
            self.saved_path = save_game(self.game)
            print(f"Game saved to {self.saved_path}")

    def review(self):
        """Ask Stockfish to review the moves so far and show advice for the human player(s)."""
        if not self.game.history:
            self.message = "Play some moves first, then review the game."
            return
        if not is_installed():
            self.message = "Stockfish is not installed. Run: yay -S stockfish"
            return
        self.message = "Reviewing the game..."
        self.draw()
        pygame.display.flip()       # show the message, because reviewing takes a few seconds
        humans = [color for color in (WHITE, BLACK)
                  if not self.game.players[color].is_computer()]
        try:
            advice = review_game(self.game.history, humans)
        except (OSError, RuntimeError) as error:
            self.message = f"Review failed: {error}"
            return
        self.review_lines = ["Game review (click the board to close)", ""]
        for color, lines in advice.items():
            self.review_lines.append(f"{color.capitalize()} ({self.game.players[color].name}):")
            for line in lines:
                self.review_lines.extend(wrap_text("- " + line, 62))
            self.review_lines.append("")
        self.update_message()

    def update_message(self):
        """Describe the new situation after a move."""
        color = self.game.current_color.capitalize()
        if self.game.game_over:
            self.message = self.game.result
        elif self.game.is_in_check():
            self.message = f"{color} is in CHECK!"
        else:
            self.message = f"{color} to move."

    # ------------------------------------------------------------ drawing
    def draw(self):
        self.draw_board()
        self.draw_pieces()
        self.draw_move_markers()
        self.draw_panel()
        if self.review_lines is not None:
            self.draw_review()

    def draw_board(self):
        king_in_check = None
        if self.game.is_in_check():
            king_in_check = self.game.board.find_king(self.game.current_color)
        for row in range(8):
            for col in range(8):
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                if (row, col) == self.selected:
                    color = SELECTED
                elif (row, col) == king_in_check:
                    color = CHECK_RED
                x, y = square_to_pixel(row, col)
                pygame.draw.rect(self.screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
        # file letters and rank numbers
        for i in range(8):
            letter = self.small_font.render("abcdefgh"[i], True, MOVE_DOT)
            self.screen.blit(letter, (i * SQUARE_SIZE + SQUARE_SIZE - 14, BOARD_SIZE - 18))
            number = self.small_font.render(str(8 - i), True, MOVE_DOT)
            self.screen.blit(number, (4, i * SQUARE_SIZE + 4))

    def draw_pieces(self):
        """Draw each piece's picture, or a circle with its letter if there are no pictures."""
        for row in range(8):
            for col in range(8):
                piece = self.game.board.get_piece(row, col)
                if piece is None:
                    continue
                x, y = square_to_pixel(row, col)
                image = self.piece_images.get((piece.color, piece.letter))
                if image is not None:
                    gap = (SQUARE_SIZE - PIECE_SIZE) // 2
                    self.screen.blit(image, (x + gap, y + gap))
                    continue
                center = (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)
                if piece.color == WHITE:
                    fill, text_color = WHITE_PIECE, BLACK_PIECE
                else:
                    fill, text_color = BLACK_PIECE, WHITE_PIECE
                pygame.draw.circle(self.screen, fill, center, 30)
                pygame.draw.circle(self.screen, MOVE_DOT, center, 30, 2)   # outline
                letter = self.piece_font.render(piece.letter, True, text_color)
                self.screen.blit(letter, letter.get_rect(center=center))

    def draw_move_markers(self):
        """Mark where the selected piece can go: a dot on an empty square,
        a ring around a piece that can be captured."""
        for row, col in self.highlights:
            x, y = square_to_pixel(row, col)
            center = (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2)
            if self.game.board.get_piece(row, col) is None:
                pygame.draw.circle(self.screen, MOVE_DOT, center, 10)
            else:
                pygame.draw.circle(self.screen, CHECK_RED, center, 36, 4)

    def draw_panel(self):
        left = BOARD_SIZE + 20
        pygame.draw.rect(self.screen, PANEL_BACKGROUND, (BOARD_SIZE, 0, PANEL_WIDTH, WINDOW_HEIGHT))
        self.write("Chess in Python", left, 20, self.font)
        y = 60
        for line in wrap_text(self.message, 20):   # 20 letters fit in the panel
            self.write(line, left, y, self.font)
            y += 26
        self.write("Moves:", left, 170, self.font)
        y = 200
        for line in history_lines(self.game.history)[-9:]:   # only the last 9 lines fit
            self.write(line, left, y, self.small_font)
            y += 22
        for button in self.buttons.values():
            button.draw(self.screen, self.small_font)

    def draw_review(self):
        """Show the game review in a dark box over the board."""
        pygame.draw.rect(self.screen, PANEL_BACKGROUND, (0, 0, BOARD_SIZE, BOARD_SIZE))
        y = 20
        for line in self.review_lines:
            if y > BOARD_SIZE - 30:
                break                        # no more room
            self.write(line, 20, y, self.small_font)
            y += 22

    def write(self, text, x, y, font):
        self.screen.blit(font.render(text, True, TEXT_COLOR), (x, y))

    # ------------------------------------------------------------ main loop
    def run(self):
        """Keep the window open: handle clicks, draw, let the computer move."""
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(*event.pos)
            self.draw()
            pygame.display.flip()
            if self.game.current_player().is_computer() and not self.game.game_over:
                pygame.time.wait(COMPUTER_DELAY)
                self.computer_turn()
            clock.tick(30)    # at most 30 frames per second
        pygame.quit()
