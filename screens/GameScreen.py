import random
import tkinter as tk
from enum import Enum

from game_objects.player import Player
from game_objects.card import Card, Suit, Parent, DEFAULT_CARD_HEIGHT, DEFAULT_CARD_WIDTH
from game_objects.board import CardGroup, Board

from ui_constants import BG_COLOR, UI_FONT, PAD, BUTTON_WIDTH, BUTTON_HEIGHT

SELECTION_COLOR = "lightblue"
SELECTION_WIDTH = 2

HAND_MENU_Y = 550
TURN_MENU_Y = 700
TURN_MENU_PLAYER_WIDTH = 100

class TurnPhase(Enum):
    READY = 0
    DRAW = 1
    PLAY = 2
    DISCARD = 3

class GameScreen(tk.Canvas):
    def __init__(self, master, numPlayers = 2):
        super().__init__(master, width=800, height=800, bd=0, highlightthickness=0, relief='ridge')
        self.master = master
        self.board = Board(self)
        
        # create photo images to be used later
        self.card_back = tk.PhotoImage(file="./sprites/card_back.png")
        self.card_back_small = tk.PhotoImage(file="./sprites/card_back_small.png")

        # create and populate deck
        self.deck = []
        for suit in list(Suit):
            # 1 (ace) thru 13 (king)
            for value in range(1, 14):
                self.deck.append(Card(suit, value))
        random.shuffle(self.deck)
        self.discard = [] # discard pile

        # create players and generate starting hands
        if numPlayers == 2:
            startingHandSize = 10
        elif (numPlayers == 3) | (numPlayers == 4):
            startingHandSize = 7
        elif (numPlayers == 5) | (numPlayers == 6):
            startingHandSize = 6
        else: raise ValueError("Number of players must be between 2 and 6")
        self.players = []
        for i in range(0, numPlayers):
            # draw first n cards
            startingHand = self.deck[0:startingHandSize]
            self.deck = self.deck[startingHandSize:]
            self.players.append(Player(len(self.players), startingHand))

        # player whose turn it is
        self.curr_player:Player = self.players[0]
        #self.curr_player:Player = self.players[random.randint(0, len(self.players)-1)]
        # the card that's currently selected
        self.selected_card:Card = None
        self.turn_phase = TurnPhase.READY

        # canvas object ID containers (for easy deletion)
        self.selection_lines = [] # lines making up the selection
        self.hand_items = []
        self.turnmenu_items = [] # background squares/lines in turn menu
        self.player_turnmenu_items = [] # player specific items in turn menu
        for player in self.players:
            self.player_turnmenu_items.append([])

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
        self.create_rectangle(0, 100, 800, HAND_MENU_Y, fill=BG_COLOR, width=0) # board
        self.create_rectangle(0, HAND_MENU_Y, 800, TURN_MENU_Y, fill="darkred", width=0) # hand

        # lines separating components
        self.create_line(0, 100, 800, 100, width=2)
        self.create_line(0, HAND_MENU_Y, 800, HAND_MENU_Y, width=2)
        self.create_line(0, HAND_MENU_Y, 800, HAND_MENU_Y, width=2)
        self.create_line(0, TURN_MENU_Y, 800, TURN_MENU_Y, width=2)

        # border lines
        self.create_line(0, 0, 0, 800, width=2)
        self.create_line(0, 800, 800, 800, width=2)
        self.create_line(800, 800, 800, 0, width=2)
        self.create_line(800, 0, 0, 0, width=2)

    def drawHand(self):
        """Draw current player's hand."""
        x = 8
        y = HAND_MENU_Y
        for card in self.curr_player.hand:
            if x >= 800:
                x -= 800
                y += 30
            card.draw(self, x, y, 2)
            x += 100
    
    def drawTurnMenu(self):
        """Draw the list of players, and their facedown cards."""
        # player background squares in turn menu
        for i in range(0, len(self.players)):
            playerbg = self.create_rectangle(i * TURN_MENU_PLAYER_WIDTH, TURN_MENU_Y, 800, 800, fill="silver", width=0)
            self.turnmenu_items.append(playerbg)
            self.drawPlayer(self.players[i])
        for i in range(0, len(self.players)):
            line_x = TURN_MENU_PLAYER_WIDTH * (i+1)
            line = self.create_line(line_x, TURN_MENU_Y, line_x, 800, width=2)
            self.turnmenu_items.append(line)
        # buttons for drawing/advancing turn/resetting board
        drawmenu_x = TURN_MENU_PLAYER_WIDTH * 6
        deck = self.create_image(drawmenu_x + 40, TURN_MENU_Y+50, image=self.card_back, anchor=tk.CENTER)
        decklabel = self.create_text(drawmenu_x + 40, TURN_MENU_Y+10, text="Deck", anchor=tk.CENTER)
        discard = self.create_image(drawmenu_x + 100, TURN_MENU_Y+50, image=self.card_back, anchor=tk.CENTER)
        discardlabel = self.create_text(drawmenu_x + 100, TURN_MENU_Y+10, text="Discard", anchor=tk.CENTER)
        nextturnbutton = self.create_rectangle(drawmenu_x + 130, TURN_MENU_Y+20, drawmenu_x + 190, TURN_MENU_Y+40, fill="green")
        nextturnlabel = self.create_text(drawmenu_x+160, TURN_MENU_Y+30, text="End Turn", anchor=tk.CENTER)
        resetbutton = self.create_rectangle(drawmenu_x + 130, TURN_MENU_Y+60, drawmenu_x + 190, TURN_MENU_Y+80, fill="green")
        resetlabel = self.create_text(drawmenu_x+160, TURN_MENU_Y+70, text="Reset Board", anchor=tk.CENTER)
        self.turnmenu_items += [deck, decklabel, discard, discardlabel, nextturnbutton, nextturnlabel, resetbutton, resetlabel]

    def drawPlayer(self, player:Player):
        """Draw a single player's name and cards in the turn menu."""
        # erase current items in player's turn menu
        for item_id in self.player_turnmenu_items[player.id]:
            self.delete(item_id)
        start_x = player.id * TURN_MENU_PLAYER_WIDTH
        text_x = start_x + (TURN_MENU_PLAYER_WIDTH/2)
        text_y = TURN_MENU_Y + 10
        textbox = self.create_text(text_x, text_y, text=f"Player {player.id+1}", anchor=tk.CENTER)
        self.player_turnmenu_items[player.id].append(textbox)
        hand_x = start_x + 10
        hand_y = TURN_MENU_Y + 40
        # print a blank card for every card in player's hand
        for i in range(0, len(player.hand), 7):
            for j in range(0, 7):
                if i+j >= len(player.hand): break
                card_x = hand_x + j*10
                card_y = hand_y + i
                cardImg = self.create_image(card_x, card_y, image=self.card_back_small, anchor=tk.NW)
                self.player_turnmenu_items[player.id].append(cardImg)

    def drawReadyScreen(self):
        """Draw a screen asking the current player if they're ready to start their turn.
        This screen will prevent players from seeing each other's hands."""
        # erase player hand
        # erase turn menu
        for item_id in self.turnmenu_items:
            self.delete(item_id)
        for item_list in self.player_turnmenu_items:
            for item_id in item_list:
                self.delete(item_id)

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
        self.drawTurnMenu()
    
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
        # if all checks pass, advance turn
        next_id = self.curr_player.id + 1
        if next_id >= len(self.players):
            next_id = 0
        self.curr_player = self.players[next_id]
        self.drawReadyScreen()

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
        if self.turn_phase == TurnPhase.READY:
            pass
        elif self.turn_phase == TurnPhase.DRAW:
            pass
        elif self.turn_phase == TurnPhase.PLAY:
            pass
        elif self.turn_phase == TurnPhase.DISCARD:
            pass
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