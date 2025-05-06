"""This script defines the Board class, which represents a board upon which cards can be placed."""

from game_objects.card import Card, Suit, Parent, DEFAULT_CARD_WIDTH, DEFAULT_CARD_HEIGHT
import tkinter as tk

class CardGroup(list):
    def __init__(self, cards:list[Card] = []):
        super().__init__(cards)

    def sortCards(self):
        pass

    def isValidRun(self):
        """Return true if this card group is a valid run, false otherwise.
        THIS FUNCTION ASSUMES THE LIST IS SORTED.
        """
        suit = self[0].suit
        for i in range(1, len(self)):
            if self[i].suit != suit: return False
            if self[i-1].value == 13:
                expected = 1
            else: expected = self[i-1].value + 1
            if self[i].value != expected: return False
        return True

    def isValidSet(self):
        """Return true if this card group is a valid set, false otherwise.
        THIS FUNCTION ASSUMES THE LIST IS SORTED.
        """
        value = self[0].value
        suits = [self[0].suit]
        for i in range(1, len(self)):
            if self[i].value != value: return False
            if self[i].suit in suits: return False
            suits.append(self[i].suit)
        return True
    
    def __str__(self):
        rv = "CardGroup Object || Cards:\n"
        for card in self:
            rv += f"\t{card}\n"
        return rv

class Board():
    START_X = 25
    START_Y = 125

    DRAWVARS = {
        1: {
            "NUM_ROWS": 2,
            "NUM_COLS": 4,
            "ROW_SPACING": 200,
            "COL_SPACING": 180,
            "ZOOM_FACTOR": 2,
            "STACK_SPACING": 20,
        },
        2: {
            "NUM_ROWS": 4,
            "NUM_COLS": 8,
            "ROW_SPACING": 100,
            "COL_SPACING": 90,
            "ZOOM_FACTOR": 1,
            "STACK_SPACING": 10,
        }
    }

    def __init__(self, canvas:tk.Canvas):
        # A card group is a set or a run on the board. These cards will be grouped together when drawn
        self.card_groups: dict[int, CardGroup] = {}
        self.canvas = canvas
        self.empty_rectangles = {} # card group id => canvas id for rectangle in that spot
        self.empty_rectangle_hitboxes = {} # card group id => (x0, y0, x1, y1) for clickable region or rectangle

        # drawing variables
        self.expand_level = 1
        self.loadDrawingVars()

    def loadDrawingVars(self):
        """Load the drawing variables based on the current expand level."""
        self.NUM_ROWS = Board.DRAWVARS[self.expand_level]["NUM_ROWS"]
        self.NUM_COLS = Board.DRAWVARS[self.expand_level]["NUM_COLS"]
        self.ROW_SPACING = Board.DRAWVARS[self.expand_level]["ROW_SPACING"]
        self.COL_SPACING = Board.DRAWVARS[self.expand_level]["COL_SPACING"]
        self.ZOOM_FACTOR = Board.DRAWVARS[self.expand_level]["ZOOM_FACTOR"]
        self.STACK_SPACING = Board.DRAWVARS[self.expand_level]["STACK_SPACING"]

    def draw(self):
        """Determine spacing variables, then draw every card group."""
        # clear empty rectangles if necessary
        for id in self.empty_rectangles.values():
            self.canvas.delete(id)
        self.empty_rectangles = {}
        self.empty_rectangle_hitboxes = {}

        # determine board size/drawing variables
        max_stacks = self.NUM_ROWS * self.NUM_COLS
        if len(self.card_groups) >= max_stacks:
            if (self.expand_level+1) in Board.DRAWVARS:
                # expand board
                self.expand_level += 1
                self.loadDrawingVars()
            else:
                print("You have reached the maximum expand level")
        elif len(self.card_groups) < (max_stacks / 4):
            if (self.expand_level-1) in Board.DRAWVARS:
                # collapse board
                self.expand_level -= 1
                self.loadDrawingVars()
                # move all card groups to be within board
                for i in range((max_stacks / 4), max_stacks):
                    if i not in self.card_groups: continue
                    self.splitGroup(i, 0, self.getNextGID(), draw=False)
        # will initially be 8 card groups but will expand to accommodate as many as possible
        for i in range(0, self.NUM_ROWS * self.NUM_COLS):
            self.drawCardGroup(i)

    def drawCardGroup(self, group_id):
        row = group_id // self.NUM_COLS
        col = group_id % self.NUM_COLS
        x = Board.START_X + col * self.COL_SPACING
        y = Board.START_Y + row * self.ROW_SPACING
        if group_id in self.card_groups:
            # draw card group
            for card in self.card_groups[group_id]:
                card.draw(self.canvas, x, y, self.ZOOM_FACTOR)
                x += self.STACK_SPACING
                y += self.STACK_SPACING
        else:
            # draw empty rectangle
            x1 = x + self.ZOOM_FACTOR * DEFAULT_CARD_WIDTH
            y1 = y + self.ZOOM_FACTOR * DEFAULT_CARD_HEIGHT
            self.empty_rectangles[group_id] = self.canvas.create_rectangle(x, y, x1, y1, fill = "darkgray", width=0)
            self.empty_rectangle_hitboxes[group_id] = (x, y, x1, y1)

    def getNextGID(self):
        # search for gaps in IDs
        for i in range(0, len(self.card_groups)):
            if i not in self.card_groups.keys():
                return i
        # if no gap found, add ID at end of range
        return len(self.card_groups)

    def makeGroup(self, cards:list, group_id:int = None, draw = True):
        """Create a new card group with the provided cards. If group_id is provided, use it."""
        if group_id is not None:
            if group_id in self.card_groups.keys(): raise ValueError("makeGroup: Provided ID already in card group IDs")
        else: # if none, determine id
            group_id = self.getNextGID()
        # delete empty rectangle for this group
        self.canvas.delete(self.empty_rectangles[group_id])
        del self.empty_rectangles[group_id]
        del self.empty_rectangle_hitboxes[group_id]
        # make group
        self.card_groups[group_id] = CardGroup(cards)
        # update all cards' internal info
        for card in self.card_groups[group_id]:
            card.parent_type = Parent.CARDGROUP
            card.parent_id = group_id
            card.card_id = len(self.card_groups[group_id]) - 1
        # redraw
        if draw:
            if len(self.card_groups) == 8:
                # board needs to be expanded, so redraw
                self.draw()
            else:
                # draw the new card group
                self.drawCardGroup(group_id)

    def addToGroup(self, group_id:int, card:Card, draw = True):
        """Add given card to card group with given ID."""
        if group_id not in self.card_groups.keys(): 
            # create new card group
            self.makeGroup([], group_id)
        self.card_groups[group_id].append(card) # add card
        # update card's internal info
        card.parent_type = Parent.CARDGROUP
        card.parent_id = group_id
        card.card_id = len(self.card_groups[group_id]) - 1
        if draw: self.drawCardGroup(group_id) # redraw
    
    def removeFromGroup(self, group_id:int, card_id:int, draw = True):
        """Remove card with card_id from group with group_id"""
        if group_id not in self.card_groups.keys():
            raise ValueError("Provided group ID does not exist")
        group = self.card_groups[group_id]
        del group[card_id] # remove card from group
        # update IDs for rest of group
        for i in range(card_id, len(group)):
            group[i].card_id = i
        if len(self.card_groups[group_id]) == 0:
            del self.card_groups[group_id]
        if draw: self.drawCardGroup(group_id) # redraw group

    def splitGroup(self, group_id:int, card_id:int, new_group_id:int, draw = True):
        """Split card group on given card. All cards before selected card will remain in group. All cards including and after selected card will be added to new group.
        :param group_id: ID of group to split
        :param card_id: In-group ID of card to split on
        :param new_group_id: ID of new group (must not be an existing group)
        """
        if group_id not in self.card_groups.keys():
            raise ValueError("Provided group ID to split doesn't exist")
        new_group_cards = self.card_groups[group_id][card_id:]
        self.card_groups[group_id] = self.card_groups[group_id][:card_id]
        if len(self.card_groups[group_id]) == 0:
            del self.card_groups[group_id]
            if draw: self.drawCardGroup(group_id)
        for card in new_group_cards:
            self.addToGroup(new_group_id, card, draw)

    def validateGroups(self):
        """Return true if every card group is a valid run or set.
        All card groups must have at least 3 cards.
        Valid runs have sequential cards of the same suit.
        Valid sets have cards of the same value but different suits.
        """
        for cgroup in self.card_groups.values():
            # length check
            if len(cgroup) < 3: return False
            # sort before running validity checks
            cgroup.sortCards()
            if (not cgroup.isValidRun()) & (not cgroup.isValidSet()):
                return False
        return True
