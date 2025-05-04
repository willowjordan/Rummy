import random
import tkinter as tk

from game_objects.player import Player
from game_objects.card import Card, Suit
from game_objects.board import CardGroup, Board

from ui_constants import BG_COLOR, UI_FONT, PAD, BUTTON_WIDTH, BUTTON_HEIGHT
DEFAULT_CARD_IMAGE_WIDTH = 42
CARD_STACK_SPACING = 20

class GameScreen(tk.Canvas):
    def __init__(self, master, players:list=[Player()]):
        super().__init__(master, width=800, height=800, bd=0, highlightthickness=0, relief='ridge')
        self.master = master
        self.players = players
        self.board = Board()
        self.curr_player = random.randint(0, len(players)-1) # id of player in self.players whose turn it is
        # the card that's currently selected
        self.selected_card_info = {
            "parent": None, # the object holding the card (hand or cardgroup on board)
            "card_id": -1, # the card's position in the parent object
        }
        # regions on the screen where a click should register as clicking a specific card
        self.card_click_regions = []
        self.card_images = []

        # start the game
        self.drawBackground()
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

        self.players[0].hand = [Card(Suit.CLUBS, 1), Card(Suit.DIAMONDS, 13), Card(Suit.HEARTS, 11), Card(Suit.SPADES, 12)]
    
    def drawCard(self, card:Card, x, y, zoom_factor):
        """Draw the specified card at x, y with the specified zoom factor.
        Cards are 42x60 px by default."""
        print(f"Called drawCard on {card}")
        img = card.image.zoom(zoom_factor, zoom_factor)
        self.card_images.append(img)
        self.create_image(x, y, image=img, anchor=tk.NW)

    def drawHand(self):
        """Draw current player's hand."""
        # TODO: draw player hands to the left
        x = 0
        for card in self.players[self.curr_player].hand:
            self.drawCard(card, x, 600, 2)
            x += 100
        # TODO: draw player hands to the right
    
    def drawBoard(self):
        """Draw all of the cards on the board."""
        # TODO: determine board size/drawing variables
        # will initially be 8 card groups but will expand to accommodate as many as possible
        for cgroup in self.board.card_groups:
            x = 0 # TODO: determine starting x and y
            y = 0
            for card in cgroup:
                self.drawCard(card, x, y, 2)
                x += CARD_STACK_SPACING
                y += CARD_STACK_SPACING

    def drawReadyScreen(self):
        """Draw a screen asking the current player if they're ready to start their turn.
        This screen will prevent players from seeing each other's hands."""

    ### MAIN GAME FUNCTIONS ###
    def startTurn(self):
        """Run start-of-turn routines for the current player."""
        self.drawHand()
        self.drawBoard()

    def playCard(self, card_id, card_group_id):
        """Move specified card from current player's hand to board."""
        card = self.players[self.curr_player].hand.pop(card_id)
        self.board.add_to_card_group(card_group_id, card)
    
    def moveCard(self, card_id, from_group, to_group):
        """Move specified card on board from from_group to to_group."""
        card = self.board.card_groups[from_group].pop(card_id)
        self.board.add_to_card_group(to_group, card)
    
    def changeTurns(self):
        """Attempt to change turns. If changing turns fails, change info message to say why."""

    ### INPUT HANDLING FUNCTIONS ###
    def onClick(self, event:tk.Event):
        pass