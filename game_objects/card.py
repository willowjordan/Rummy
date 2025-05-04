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
    VALUE_STRINGS = {
        1: ("A", "Ace"),
        2: ("02", "Two"),
        3: ("03", "Three"),
        4: ("04", "Four"),
        5: ("05", "Five"),
        6: ("06", "Six"),
        7: ("07", "Seven"),
        8: ("08", "Eight"),
        9: ("09", "Nine"),
        10: ("10", "Ten"),
        11: ("J", "Jack"),
        12: ("Q", "Queen"),
        13: ("K", "King"),
    } # first string is for getting photo image, second is for printing
    def __init__(self, suit:Suit, value:int):
        """
        :param suit: Suit of the card.
        :param value: Value of the card, from 1-13 (1=Ace, 11=Jack, 12=Queen, 13=King)
        """
        if (value < 1) | (value > 13): raise ValueError(f"Cannot create a card with value {value}")
        self.suit = suit
        self.value = value

        # get photoimage object
        value_path, self.value_str = Card.VALUE_STRINGS[value]
        self.suit_str = suit.name.lower()
        path = Card.PLAYING_CARD_PATH.format(suit=self.suit_str, value=value_path)
        self.image = PhotoImage(file=path)

    def __str__(self):
        return f"Card object: {self.value_str} of {self.suit_str}"