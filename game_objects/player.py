"""This script defines the Player class, which represents one human player and
the cards they hold."""

from game_objects.card import Card

class Player():
    def __init__(self, id:int, starting_hand:list = []):
        self.score = 0
        self.id = id
        self.hand = starting_hand # list of cards
    
    def addToHand(self, card:Card):
        self.hand.append(card)
        card.card_id = len(self.hand) - 1
    
    def removeFromHand(self, id:int):
        """Remove card with given id from hand."""
        if id >= len(self.hand): raise ValueError("Provided ID does not exist")
        del self.hand[id]
        # update all subsequent card's internal IDs
        for i in range(id, len(self.hand)):
            self.hand[i].card_id = i