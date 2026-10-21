from chess.core.cell import Cell
class Board:
    def __init__(self):
        self.cells = []

        for row in range(8):
            current_row = []
            for col in range(8):
                current_row.append(Cell(row, col))

            self.cells.append(current_row)

    def piece_at(self, row, col):
        return self.cells[row][col].piece

    def position_of(self, piece):
        for row in range(8):
            for col in range(8):
                current_piece = self.cells[row][col].piece
                if current_piece is piece:
                    return self.cells[row][col]

        return None

    def setup_pieces(self):
        ...