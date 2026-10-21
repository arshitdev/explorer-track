class Player:
    def __init__(self, name, color, bot=None):
        self.name = name
        self.color = color
        self.bot = bot
        self.stats = {"games_played":0, "wins":0, "losses":0, "draws":0}