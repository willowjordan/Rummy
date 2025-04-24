"""This script defines the Board class, which represents a board upon which cards can be placed."""

from card import Card, Suit
from enum import Enum

class CardGroupType(Enum):
    NONE = 0
    SET = 1
    RUN = 2

class CardGroup(list):
    def __init__(self, grouptype:CardGroupType, cards:list = []):
        super.__init__(cards)
        self.grouptype = grouptype
    
    def sort_cards(self):
        pass

class Board():
    def __init__(self):
        # A card group is a set or a run on the board. These cards will be grouped together when drawn
        self.card_groups = {} # int => CardGroup

    def get_next_group_id(self):
        # search for gaps in IDs
        for i in range(0, len(self.card_groups)):
            if i not in self.card_groups.keys():
                return i
        # if no gap found, add ID at end of range
        return len(self.card_groups)

    def make_card_group(self, cards:list, group_id:int = None):
        """Create a new card group with the provided cards. If group_id is provided, use it."""
        if group_id is not None:
            if group_id in self.card_groups.keys(): raise ValueError("make_card_group: Provided ID already in card group IDs")
        else: # if none, determine id
            group_id = self.get_next_group_id()
        # TODO: determine group type
        self.card_groups[group_id] = CardGroup(CardGroupType.NONE, cards)

    def add_to_card_group(self, group_id:int, card:Card):
        """Attempt to add the given card to the group with the given ID. If addition fails due to group type, return False. Otherwise return True."""
        if group_id not in self.card_groups.keys(): 
            raise ValueError("add_to_card_group: Provided ID doesn't exist")
        group:CardGroup = self.card_groups[group_id]
        
        if group.grouptype == CardGroupType.RUN:
            # check if suit is correct
            if card.suit != group[0].suit: return False
            # check if card fits on one end or the other
            min = group[0].value - 1
            if min == 1: min = 13
            max = group[len(group)-1].value + 1
            if max == 13: max = 1
            if (card.value != min) & (card.value != max):
                return False
        elif group.grouptype == CardGroupType.SET:
            # check if value is correct
            if card.value != group[0].value: return False
            # check if suit isn't already present
            for groupcard in group:
                if groupcard.suit == card.suit:
                    return False
        # if no group type, can add no matter what
        group.append(card)
        group.sort_cards()
        return True

    def split_card_group(self, group_id:int):
        pass