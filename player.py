"""This script defines the Player class, which represents one human player and the cards they hold."""

class Player():
    def __init__(self, is_cpu:bool):
        self.score = 0
        self.hand = [] # list of cards
        self.is_cpu = is_cpu