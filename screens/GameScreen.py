import random
import tkinter as tk

from game_objects.player import Player
from game_objects.card import Card, Suit, Parent, DEFAULT_CARD_HEIGHT, DEFAULT_CARD_WIDTH
from game_objects.board import CardGroup, Board

from ui_constants import BG_COLOR, UI_FONT, PAD, BUTTON_WIDTH, BUTTON_HEIGHT

SELECTION_COLOR = "lightblue"
SELECTION_WIDTH = 2

class CardSelector():
    def __init__(self):
        pass

class GameScreen(tk.Canvas):
    def __init__(self, master, numHumanPlayers = 2, numComputerPlayers = 0):
        super().__init__(master, width=800, height=800, bd=0, highlightthickness=0, relief='ridge')
        self.master = master
        self.players = []
        DEBUG_STARTING_HAND = [
            Card(Suit.CLUBS, 1, Parent.HAND, 0, 0), 
            Card(Suit.DIAMONDS, 13, Parent.HAND, 0, 1), 
            Card(Suit.HEARTS, 11, Parent.HAND, 0, 2), 
            Card(Suit.SPADES, 12, Parent.HAND, 0, 3)]
        for i in range(0, numHumanPlayers):
            self.players.append(Player(len(self.players), False, DEBUG_STARTING_HAND))
        for i in range(0, numHumanPlayers):
            self.players.append(Player(len(self.players), True, DEBUG_STARTING_HAND))
        self.board = Board(self) # create and draw board
        self.curr_player:Player = self.players[0]
        #self.curr_player:Player = self.players[random.randint(0, len(self.players)-1)]
        # the card that's currently selected
        self.selected_card:Card = None

        # canvas object ID containers (for easy deletion)
        self.selection_lines = [] # lines making up the selection

        # bind mouse1 to onClick function
        self.bind("<Button-1>", self.onClick)

        # start the game
        self.drawBackground()
        self.board.draw()
        self.startTurn()

    ### DRAWING FUNCTIONS ###
    def drawBackground(self):
        """Draw things that won't change."""
        # component backgrounds
        self.create_rectangle(0, 0, 800, 100, fill="darkred", width=0) # info
        self.create_rectangle(0, 100, 800, 600, fill=BG_COLOR, width=0) # board
        self.create_rectangle(0, 600, 800, 800, fill="darkred", width=0) # hand

        # lines separating components
        self.create_line(0, 100, 800, 100, width=2)
        self.create_line(0, 600, 800, 600, width=2)

        # border lines
        self.create_line(0, 0, 0, 800, width=2)
        self.create_line(0, 800, 800, 800, width=2)
        self.create_line(800, 800, 800, 0, width=2)
        self.create_line(800, 0, 0, 0, width=2)

    def drawHand(self):
        """Draw current player's hand."""
        # TODO: draw player hands to the left
        x = 0
        for card in self.curr_player.hand:
            card.draw(self, x, 600, 2)
            x += 100
        # TODO: draw player hands to the right

    def drawReadyScreen(self):
        """Draw a screen asking the current player if they're ready to start their turn.
        This screen will prevent players from seeing each other's hands."""

    def drawCardSelection(self):
        """Draw an outline around the selected card and any cards above it on the stack."""
        if self.selection_lines != []: # existing selection
            self.eraseCardSelection()
        self.drawOutline(self.selected_card)
        if self.selected_card.parent_type == Parent.CARDGROUP:
            # iterate through card group starting at card above selected one
            card_group = self.getParent(self.selected_card)
            for i in range(self.selected_card.card_id+1, len(card_group)):
                self.drawOutline(card_group[i])
    
    def drawOutline(self, card:Card):
        """Draw an outline around the given card"""
        bounds = card.click_region
        self.selection_lines.append(self.create_line(bounds[0], bounds[1], bounds[2], bounds[1], fill=SELECTION_COLOR, width=SELECTION_WIDTH))
        self.selection_lines.append(self.create_line(bounds[2], bounds[1], bounds[2], bounds[3], fill=SELECTION_COLOR, width=SELECTION_WIDTH))
        self.selection_lines.append(self.create_line(bounds[2], bounds[3], bounds[0], bounds[3], fill=SELECTION_COLOR, width=SELECTION_WIDTH))
        self.selection_lines.append(self.create_line(bounds[0], bounds[3], bounds[0], bounds[1], fill=SELECTION_COLOR, width=SELECTION_WIDTH))

    def eraseCardSelection(self):
        """Erase outline around selected card."""
        for line_id in self.selection_lines:
            self.delete(line_id)
        self.selection_lines = []

    ### HELPER FUNCTIONS ###
    def getParent(self, card:Card):
        """Return the parent container of the given card."""
        if card.parent_type == Parent.HAND:
            return self.players[card.parent_id].hand
        else: # CARDGROUP
            return self.board.card_groups[card.parent_id]

    ### MAIN GAME FUNCTIONS ###
    def startTurn(self):
        """Run start-of-turn routines for the current player."""
        self.drawHand()
    
    def moveSelectedCard(self, to_group_id:int):
        """Move selected card to specified card group on board.
        If card is in a group, split that group on that card.
        :param to_group_id: ID of card group to move ID to
        """
        card = self.selected_card
        if card.parent_type == Parent.HAND:
            if card.parent_id != self.curr_player.id:
                raise RuntimeError("This card is in another player's hand!")
            # remove card from hand
            self.curr_player.removeFromHand(card.card_id)
            # add to specified card group
            self.board.addToGroup(to_group_id, card)
            self.drawHand() # redraw hand
        else: # CARDGROUP
            self.board.splitGroup(card.parent_id, card.card_id, to_group_id)
    
    def changeTurns(self):
        """Attempt to change turns. If changing turns fails, change info message to say why."""

    def selectCard(self, card:Card):
        """Select specified card and draw an outline around it."""
        self.selected_card = card
        self.drawCardSelection()

    def clearSelection(self):
        """Clear internal selection info and erase selection outline."""
        self.selected_card = None
        self.eraseCardSelection()

    ### INPUT HANDLING FUNCTIONS ###
    def onClick(self, event:tk.Event):
        #print(f"Click! Event: {event}")
        # TODO: check buttons
        if event.y < 600: # on board
            for cg_id in self.board.card_groups:
                cgroup = self.board.card_groups[cg_id]
                click = False
                # iterate backwards to prioritize top of stack
                for i in range(len(cgroup)-1, -1, -1):
                    if not self.wasAreaClicked(cgroup[i].click_region, event):
                        continue
                    # if card was clicked:
                    if self.selected_card is not None:
                        # if selected card is clicked, deselect
                        if cgroup[i] == self.selected_card:
                            self.clearSelection()
                            return
                        # if another card in the group is clicked, select that card
                        if cgroup == self.getParent(self.selected_card):
                            self.selectCard(cgroup[i])
                            return
                        
                        self.moveSelectedCard(cg_id)
                        self.clearSelection()
                    else:
                        # if no selection, select clicked card
                        self.selectCard(cgroup[i])
                    return
            for group_id in self.board.empty_rectangle_hitboxes:
                if not self.wasAreaClicked(self.board.empty_rectangle_hitboxes[group_id], event):
                    continue
                # if empty stack was clicked
                if self.selected_card is not None:
                    self.moveSelectedCard(group_id)
                    self.clearSelection()
                return
        else: # in hand
            hand = self.curr_player.hand
            for i in range(0, len(hand)):
                if not self.wasAreaClicked(hand[i].click_region, event):
                    continue
                # if card was clicked:
                if hand[i] == self.selected_card:
                    # if selected card is clicked, deselect
                    self.clearSelection()
                else:
                    self.selectCard(hand[i])
                return

    def wasAreaClicked(self, bounds, event:tk.Event):
        """Return true if a specific card was clicked on, false otherwise.
        :param bounds: (x0, y0, x1, y1) of a rectangular area to check
        :param event: The click event
        """
        if event.x < bounds[0]: return False
        if event.y < bounds[1]: return False
        if event.x > bounds[2]: return False
        if event.y > bounds[3]: return False
        return True