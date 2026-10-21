class Move:
    def __init__(self, piece, startcell, endcell, captured_piece=None,
                 promotion=None, additional_changes=None):
        self.piece = piece
        self.startcell = startcell
        self.endcell = endcell
        self.captured_piece = captured_piece
        self.promotion = promotion
        self.additional_changes = (
            [] if additional_changes is None else additional_changes
        )