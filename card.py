"""This script defines the Card class, which represents a single playing card."""

from tkinter import PhotoImage
from enum import Enum

class Suit(Enum):
    HEARTS = 0
    DIAMONDS = 1
    CLUBS = 2
    SPADES = 3

class Card():
    PLAYING_CARD_PATH = "./sprites/card_{suit}_{value}.png"
    def __init__(self, suit:Suit, value:int):
        """
        :param suit: Suit of the card.
        :param value: Value of the card, from 1-13 (1=Ace, 11=Jack, 12=Queen, 13=King)
        """
        if (value < 1) | (value > 13): raise ValueError(f"Cannot create a card with value {value}")
        self.suit = suit
        self.value = value

        # get photoimage object
        if value == 1:
            value_str = "A"
        elif value < 10:
            value_str = f"0{value}"
        elif value == 11:
            value_str = "J"
        elif value == 12:
            value_str = "Q"
        elif value == 13:
            value_str = "K"
        suit_str = suit.name.lower()
        path = Card.PLAYING_CARD_PATH.format(suit=suit_str, value=value_str)
        self.image = PhotoImage(file=path)