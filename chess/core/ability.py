from chess.core.move import Move

class Ability:
    def moves(self, game, piece):
        return []
    
    def attacked_cells(self, game, piece):
        return []

    def modify_moves(self, game, piece, moves):
        return moves

class SlideAbility(Ability):
    def __init__(self, directions, max_steps=7):
        self.directions = tuple(directions)
        self.max_steps = max_steps

        if not 1 <= max_steps <= 7:
            raise ValueError("Error, max_steps should be in b/w 1 and 7")

        for row_change, col_change in self.directions:
            if (
                row_change not in (-1, 0, 1)
                or col_change not in (-1, 0, 1)
                or (row_change == 0 and col_change == 0)
            ):
                raise ValueError(
                    "Each direction must be a non-zero step "
                    "using row and column changes from -1 to 1"
                )

    def moves(self, game, piece):
        board = game.board
        startcell = board.position_of(piece)

        if startcell is None:
            return []

        possible_moves = []

        for row_change, col_change in self.directions:
            for distance in range(1, self.max_steps + 1):
                row = startcell.rowNumber + row_change * distance
                col = startcell.colNumber + col_change * distance

                # Stop when this direction reaches the board's edge.
                if not (0 <= row < 8 and 0 <= col < 8):
                    break

                endcell = board.cells[row][col]
                occupant = endcell.piece

                # Empty squares are available destinations.
                if occupant is None:
                    possible_moves.append(
                        Move(
                            piece=piece,
                            startcell=startcell,
                            endcell=endcell,
                        )
                    )
                    continue

                # An opponent's piece can be captured.
                if occupant.color != piece.color:
                    possible_moves.append(
                        Move(
                            piece=piece,
                            startcell=startcell,
                            endcell=endcell,
                            captured_piece=occupant,
                        )
                    )

                # Any piece blocks further movement in this direction.
                break

        return possible_moves

    def attacked_cells(self, game, piece):
        board = game.board
        startcell = board.position_of(piece)

        if startcell is None:
            return []

        attacked = []

        for row_change, col_change in self.directions:
            for distance in range(1, self.max_steps + 1):
                row = startcell.rowNumber + row_change * distance
                col = startcell.colNumber + col_change * distance

                if not (0 <= row < 8 and 0 <= col < 8):
                    break

                cell = board.cells[row][col]
                attacked.append(cell)

                # Include a friendly occupied square as defended,
                # but do not attack through it.
                if cell.piece is not None:
                    break

        return attacked