class Piece:
    def __init__(self, color, abilities, value=None):
        self.color = color
        self.abilities = abilities
        self.value = value
        # check for en passant, castling etc
        self.has_moved = False 