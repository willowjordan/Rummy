"""This script defines the Card class, which represents a single playing card."""

import tkinter as tk
from enum import Enum

DEFAULT_CARD_WIDTH = 42
DEFAULT_CARD_HEIGHT = 60

class Suit(Enum):
    HEARTS = 0
    DIAMONDS = 1
    CLUBS = 2
    SPADES = 3

class Parent(Enum):
    HAND = 0
    CARDGROUP = 1

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

    def __init__(self, suit:Suit, value:int, parent_type:Parent = None, parent_id:int = None, card_id:int = None):
        """
        :param suit: Suit of the card.
        :param value: Value of the card, from 1-13 (1=Ace, 11=Jack, 12=Queen, 13=King)
        :param parent_type: The type of container holding the card.
            Either a player's hand or a card group on the board
        :param parent_id: The ID of the parent container.
            For HAND, the hand's player's ID.
            For CARDGROUP, the card group's group ID.
        :param card_id: The ID of the card within the parent container.
        """
        if (value < 1) | (value > 13): raise ValueError(f"Cannot create a card with value {value}")
        self.suit = suit
        self.value = value
        self.parent_type = parent_type
        self.parent_id = parent_id
        self.card_id = card_id

        # get photoimage object
        value_path, self.value_str = Card.VALUE_STRINGS[value]
        self.suit_str = suit.name.lower()
        path = Card.PLAYING_CARD_PATH.format(suit=self.suit_str, value=value_path)
        self.image = tk.PhotoImage(file=path)

        # variables to be set by draw()
        self.zoomed_image = None # PhotoImage that will actually be drawn on board
        self.image_id = None # id of PhotoImage on canvas
        self.click_region = None # region in which a click will register
    
    def draw(self, canvas:tk.Canvas, x, y, zoom_factor:int):
        """Draw the card at x, y with specified zoom factor on specified canvas.
        Set click_region variable accordingly.
        Return the image ID.
        Cards are 42x60 px by default."""
        if self.image_id is not None: self.erase(canvas)
        self.zoomed_image = self.image.zoom(zoom_factor, zoom_factor)
        self.image_id = canvas.create_image(x, y, image=self.zoomed_image, anchor=tk.NW)
        self.click_region = (x, y, x+zoom_factor*DEFAULT_CARD_WIDTH, y+zoom_factor*DEFAULT_CARD_HEIGHT)
        return self.image_id

    def erase(self, canvas:tk.Canvas):
        """Erase drawing and unset associated variables."""
        canvas.delete(self.image_id)
        self.zoomed_image = None
        self.image_id = None
        self.click_region = None

    def __str__(self):
        return f"Card object: {self.value_str} of {self.suit_str}"