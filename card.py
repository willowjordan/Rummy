"""This script defines the Card class, which represents a single playing card."""

from enum import Enum

class Suit(Enum):
    HEARTS = 0
    DIAMONDS = 1
    CLUBS = 2
    SPADES = 3

class Card():
    def __init__(self, suit:Suit, value:int):
        """
        :param suit: Suit of the card.
        :param value: Value of the card, from 1-13 (1=Ace, 11=Jack, 12=Queen, 13=King)
        """
        if (value < 1) | (value > 13): raise ValueError(f"Cannot create a card with value {value}")
        self.suit = suit
        self.value = value