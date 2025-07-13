"""
File: GameScreen.py
Author: Willow Jordan
Purpose: This script defines the GameScreen object (overriding tk.Canvas). It handles user input and a good portion of the game logic.
"""

import copy
import random
import tkinter as tk
from enum import Enum

from game_objects.player import Player
from game_objects.card import Card, Suit, Parent
from game_objects.board import Board

from ui_constants import BG_COLOR, UI_FONT

SELECTION_COLOR = "lightblue"
SELECTION_WIDTH = 2

HAND_MENU_Y = 450
TURN_MENU_Y = 700
TURN_MENU_PLAYER_WIDTH = 100

DECK_X = 640
DECK_Y = 750
DISCARD_X = 700
DISCARD_Y = 750

class TurnPhase(Enum):
    READY = 0
    DRAW = 1
    PLAY = 2
    DISCARD = 3

"""class GameButton():
    def __init__(self, canvas:tk.Canvas, x, y, width, height, color, on_click:function):
        self.canvas = canvas
        self.bounds = (x, y, x+width, y+height)
        self.function = function
        self.bg = canvas.create_rectangle(*self.bounds, fill=color)
        self.on_click = on_click
    
    def addLabel(self, text:str, textColor="black", font=UI_FONT):
        x = (self.bounds[0] + self.bounds[2]) / 2
        y = (self.bounds[1] + self.bounds[3]) / 2
        self.label = self.canvas.create_text(x, y, text=text, fill=textColor, font=font, anchor=tk.CENTER)"""

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
            if suit == Suit.NONE: continue
            # 1 (ace) thru 13 (king)
            for value in range(1, 14):
                self.deck.append(Card(suit, value))
        random.shuffle(self.deck)

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
            for j in range(0, startingHandSize):
                startingHand[j].setInternals(Parent.HAND, i, j)
            self.players.append(Player(len(self.players), startingHand))
        # draw top card from deck for discard pile
        self.discard_pile:list[Card] = [self.deck[0]]
        self.deck = self.deck[1:]

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
        self.readyscreen_items = []

        # button regions
        self.deck_bounds = (619, 720, 661, 780)
        self.discard_bounds = (679, 720, 721, 780)
        self.next_turn_bounds = (725, 720, 795, 740)
        self.reset_bounds = (725, 760, 795, 780)

        # bind mouse1 to onClick function
        self.bind("<Button-1>", self.onClick)
        self.master.bind("<Key>", self.onKeyPress)

        # start the game
        self.drawBackground()
        self.board.draw()
        self.startReadyPhase()

    ### DRAWING FUNCTIONS ###
    def drawBackground(self):
        """Draw things that won't change."""
        # component backgrounds
        self.create_rectangle(0, 0, 800, 100, fill="darkred", width=0) # info
        self.create_rectangle(0, 100, 800, HAND_MENU_Y, fill=BG_COLOR, width=0) # board
        self.create_rectangle(0, HAND_MENU_Y, 800, 800, fill="darkred", width=0) # hand

        # lines separating components
        self.create_line(0, 100, 800, 100, width=2)
        self.create_line(0, HAND_MENU_Y, 800, HAND_MENU_Y, width=2)
        self.create_line(0, HAND_MENU_Y, 800, HAND_MENU_Y, width=2)

        # border lines
        self.create_line(0, 0, 0, 800, width=2)
        self.create_line(0, 800, 800, 800, width=2)
        self.create_line(800, 800, 800, 0, width=2)
        self.create_line(800, 0, 0, 0, width=2)

    def printInfo(self, info:str):
        """Print a message to the info bar at the top of the screen"""
        # delete current info text if it exists
        try:
            if self.info_text is not None:
                self.delete(self.info_text)
        except AttributeError: pass
        self.info_text = self.create_text(10, 10, text=info, anchor=tk.NW, fill="white")

    def drawHand(self):
        """Draw current player's hand."""
        x = 8
        y = HAND_MENU_Y
        for card in self.curr_player.hand:
            if x >= 800:
                x -= 800
                y += 120
            card.draw(self, x, y, 2)
            x += 100
    
    def drawTurnMenu(self):
        """Draw the list of players, and their facedown cards."""
        # erase the previous turn menu
        for item_id in self.turnmenu_items:
            self.delete(item_id)
        for item_list in self.player_turnmenu_items:
            for item_id in item_list:
                self.delete(item_id)
        self.turnmenu_items.append(self.create_rectangle(0, TURN_MENU_Y, 800, 800, fill="silver"))
        # player background squares in turn menu
        for i in range(0, len(self.players)):
            # draw background rectangle for player, highlighting if it's their turn
            bg_fill = "silver"
            if self.players[i] == self.curr_player: bg_fill = "gold"
            playerbg = self.create_rectangle(i * TURN_MENU_PLAYER_WIDTH, TURN_MENU_Y, (i+1) * TURN_MENU_PLAYER_WIDTH, 800, fill=bg_fill, width=0)
            self.turnmenu_items.append(playerbg)
            self.drawPlayer(self.players[i])
        for i in range(0, len(self.players)):
            # draw line between this player and next player
            line_x = TURN_MENU_PLAYER_WIDTH * (i+1)
            line = self.create_line(line_x, TURN_MENU_Y, line_x, 800, width=2)
            self.turnmenu_items.append(line)
        # line separating turn menu from hand
        line = self.create_line(0, TURN_MENU_Y, 800, TURN_MENU_Y, width=2)
        self.turnmenu_items.append(line)
        # buttons for drawing/advancing turn/resetting board
        drawmenu_x = TURN_MENU_PLAYER_WIDTH * 6
        self.drawDeck()
        decklabel = self.create_text(drawmenu_x + 40, TURN_MENU_Y+10, text="Deck", anchor=tk.CENTER)
        self.drawDiscard()
        discardlabel = self.create_text(drawmenu_x + 100, TURN_MENU_Y+10, text="Discard", anchor=tk.CENTER)
        self.turnmenu_items += [decklabel, discardlabel]

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

    def drawDeck(self):
        """Draw the deck centered at DECK_X, DECK_Y"""
        deck = self.create_image(DECK_X, DECK_Y, image=self.card_back, anchor=tk.CENTER)
        cards_left = self.create_text(DECK_X, DECK_Y, text=str(len(self.deck)), anchor=tk.CENTER)
        self.turnmenu_items += [deck, cards_left]

    def drawDiscard(self):
        """Draw the discard pile centered at DISCARD_X, DISCARD_Y"""
        if len(self.discard_pile) == 0:
            dpile = self.create_image(DISCARD_X, DISCARD_Y, image=self.card_back, anchor=tk.CENTER)
        else:
            dpile = self.discard_pile[len(self.discard_pile)-1].draw(self, DISCARD_X, DISCARD_Y, 1, tk_anchor=tk.CENTER)
        self.turnmenu_items += [dpile]

    def drawBlankCard(self, x, y, zoom_factor, tk_anchor = tk.NW):
        card = Card(Suit.NONE, 0)
        return card.draw(self, x, y, zoom_factor, tk_anchor)
    
    def drawPlayButtons(self):
        """Draw buttons to be used during play phase."""
        nextturnbutton = self.create_rectangle(725, 720, 795, 740, fill="green")
        nextturnlabel = self.create_text(760, 730, text="End Turn", anchor=tk.CENTER)
        resetbutton = self.create_rectangle(725, 760, 795, 780, fill="green")
        resetlabel = self.create_text(760, 770, text="Reset Board", anchor=tk.CENTER)
        self.play_buttons = [nextturnbutton, nextturnlabel, resetbutton, resetlabel]

    def erasePlayButtons(self):
        """Erase buttons from play phase."""
        for item_id in self.play_buttons:
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

    ### PHASE CHANGE FUNCTIONS ###
    def startReadyPhase(self):
        self.turn_phase = TurnPhase.READY
        self.drawTurnMenu()
        self.printInfo(f"Player {self.curr_player.id+1}, press ENTER to begin your turn")

    def startTurn(self):
        """Run start-of-turn routines for the current player. Move to draw phase."""
        self.turn_phase = TurnPhase.DRAW
        # erase ready phase visual items
        for item_id in self.readyscreen_items:
            self.delete(item_id)
        self.drawHand()
        self.printInfo(f"Player {self.curr_player.id+1}: Draw a card by clicking the deck or discard pile")

    def moveToPlayPhase(self):
        """Move to the play phase."""
        self.turn_phase = TurnPhase.PLAY
        # redraw hand (since a card was drawn)
        self.drawHand()
        # redraw player's entry in menu (since a card was drawn)
        self.drawPlayer(self.curr_player)
        self.drawPlayButtons()
        # create save state of board and player's hand that can be reverted to
        self.createSaveState()
        self.printInfo(f"""Player {self.curr_player.id+1}: Play cards from your hand to form sets and runs. You may also move cards around on the board.
Set: A group of cards of the same value, but different suits. Run: A group of cards of the same suit increasing in value.
Both sets and runs must contain at least 3 cards.
Click "Reset Board" to reset the board to its state at the start of this turn.
Click "End Turn" when you are done playing/moving cards.""")

    def moveToDiscardPhase(self):
        """Run checks to make sure board is valid. If it is, move to discard phase."""
        if len(self.curr_player.hand) < 1:
            self.printInfo("You must keep at least one card in your hand to discard.\nClick \"Reset Board\" to get your cards back and play differently.")
            return
        if not self.board.validateGroups():
            self.printInfo("Not every group on the board is a valid run or set. Try again.")
            return
        
        # checks passed, move on to discard phase
        self.turn_phase = TurnPhase.DISCARD
        self.erasePlayButtons()
        self.clearSelection()
        self.printInfo(f"Player {self.curr_player.id+1}: Click a card in your hand to discard it.")

    def changeTurns(self):
        """Check if the current player won. If they did, move to the victory screen. Otherwise, change to the next player."""
        # check if current player won
        if len(self.curr_player.hand) == 0:
            # calculate scores based on cards left in players' hands
            scores = {}
            for player in self.players:
                score = 0
                for card in player.hand:
                    if card.value == 1: score += 14
                    elif card.value > 10: score += 10
                    else: score += card.value
                scores[player.id] = score
            self.master.display_victory(scores)
        # erase current player's hand
        for card in self.curr_player.hand:
            card.erase(self)
        # if all checks pass, advance turn
        next_id = self.curr_player.id + 1
        if next_id >= len(self.players):
            next_id = 0
        self.curr_player = self.players[next_id]
        self.startReadyPhase()

    ### PLAY PHASE FUNCTIONS ###
    def createSaveState(self):
        """Create a save state of the board and current player's hand."""
        # shallow copy so that we don't copy the cards as well
        self.saved_cgroups = copy.copy(self.board.card_groups)
        self.saved_hand = copy.copy(self.curr_player.hand)

    def loadSaveState(self):
        """Reset the board and current player's hand to the last save state."""
        self.clearSelection()
        self.board.card_groups = self.saved_cgroups
        self.curr_player.hand = self.saved_hand
        # reset cards' internal data (this may have been overwritten in the copy)
        for cgroup_id in self.board.card_groups:
            for i in range(0, len(self.board.card_groups[cgroup_id])):
                card:Card = self.board.card_groups[cgroup_id][i]
                card.setInternals(Parent.CARDGROUP, cgroup_id, i)
        for i in range(0, len(self.curr_player.hand)):
            card:Card = self.curr_player.hand[i]
            card.setInternals(Parent.HAND, self.curr_player.id, i)
        # redraw everything
        print("Save state loaded")
        print(self.board.card_groups)
        self.board.draw()
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
        self.clearSelection()
    
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
            return
        elif self.turn_phase == TurnPhase.DRAW:
            self.handleClick_Draw(event)
        elif self.turn_phase == TurnPhase.PLAY:
            self.handleClick_Play(event)
        elif self.turn_phase == TurnPhase.DISCARD:
            self.handleClick_Discard(event)
    
    def handleClick_Draw(self, event:tk.Event):
        """Handle a click in the draw phase"""
        if self.posInBounds(self.deck_bounds, (event.x, event.y)):
            # draw a card from the deck
            card = self.deck.pop()
            # if deck is empty, shuffle discard into deck
            if len(self.deck) == 0:
                self.deck = copy.copy(self.discard_pile)
                random.shuffle(self.deck)
                self.discard_pile = [self.deck.pop()]
            self.drawDeck()
        elif self.posInBounds(self.discard_bounds, (event.x, event.y)):
            # draw a card from the discard pile
            card = self.discard_pile.pop()
            self.drawDiscard()
        else: return
        self.curr_player.addToHand(card)
        self.moveToPlayPhase()

    def handleClick_Play(self, event:tk.Event):
        """Handle a click in the play phase"""
        if event.y < HAND_MENU_Y: # on board
            """board_card = self.getBoardCardIDs(event.x, event.y)
            if board_card is not None:
                cgroup_id, card_id = board_card
                if self.selected_card is not None:
                    if self.selected_card.parent_id == cgroup_id:
                        if self.selected_card.card_id == card_id:
                            # if selected card is clicked, deselect
                            self.clearSelection()
                            return
                        # if another card in the group is clicked, select that card
                        self.selectCard(cgroup[i])
                        return
                    # otherwise, move the selected card to the clicked group
                    self.moveSelectedCard(cgroup_id)
                else: # if no selection, select clicked card
                    self.selectCard(cgroup[i])"""
            # check only the nearest card stacks
            groups_to_check = self.board.getClosestCardGroups(event.x, event.y)
            groups_to_check.sort() # check lowest group first
            for group_id in groups_to_check:
                if group_id in self.board.card_groups:
                    cgroup = self.board.card_groups[group_id]
                    for i in range(len(cgroup)-1, -1, -1):
                        if not self.wasAreaClicked(cgroup[i].click_region, event):
                            continue
                        if self.selected_card is not None:
                            # if selected card is clicked, deselect
                            if cgroup[i] == self.selected_card:
                                self.clearSelection()
                                return
                            # if another card in the group is clicked, select that card
                            if cgroup == self.getParent(self.selected_card):
                                self.selectCard(cgroup[i])
                                return
                            self.moveSelectedCard(group_id)
                        else: # if no selection, select clicked card
                            self.selectCard(cgroup[i])
                        return
                else: # no card group here
                    if not self.wasAreaClicked(self.board.empty_rectangle_hitboxes[group_id], event):
                        continue
                    if self.selected_card is not None:
                        self.moveSelectedCard(group_id)
                    return
        elif event.y < TURN_MENU_Y: # in hand
            hand = self.curr_player.hand
            # loop backwards through cards in hand
            for i in range(len(hand)-1, -1, -1):
                if not self.wasAreaClicked(hand[i].click_region, event):
                    continue
                # if card was clicked:
                if hand[i] == self.selected_card:
                    # if selected card is clicked, deselect
                    self.clearSelection()
                else:
                    self.selectCard(hand[i])
                return
        else: # in turn menu
            if self.wasAreaClicked(self.next_turn_bounds, event):
                self.moveToDiscardPhase()
            elif self.wasAreaClicked(self.reset_bounds, event):
                self.loadSaveState()
    
    def handleClick_Discard(self, event:tk.Event):
        """Handle a click in the discard phase"""
        if (event.y < TURN_MENU_Y) & (event.y > HAND_MENU_Y): # in hand
            hand = self.curr_player.hand
            # loop backwards through cards in hand
            for i in range(len(hand)-1, -1, -1):
                if not self.wasAreaClicked(hand[i].click_region, event):
                    continue
                # if card was clicked, discard it
                hand[i].erase(self)
                self.discard_pile.append(hand[i])
                self.curr_player.removeFromHand(i)
                self.changeTurns()
                return

    def onKeyPress(self, event:tk.Event):
        if self.turn_phase != TurnPhase.READY: return
        if event.keysym == "Return": # ENTER was pressed
            self.startTurn()
    
    def getBoardCardIDs(self, x, y):
        """Return the IDs of card on the board at (x, y).
        Return None if no card on board exists at (x, y), or (x, y) is outside board.\n
        :param x: X position to check\n
        :param y: Y position to check\n
        :return: Tuple containing (card group ID, card ID (in group))
        """
        if y > HAND_MENU_Y: # not on board
            return None
        # check only the nearest card stacks
        groups_to_check = self.board.getClosestCardGroups(x, y)
        groups_to_check.sort() # check lowest group first
        for group_id in groups_to_check:
            if group_id in self.board.card_groups:
                cgroup = self.board.card_groups[group_id]
                for i in range(len(cgroup)-1, -1, -1):
                    if self.posInBounds(cgroup[i].click_region, (x, y)):
                        return (cgroup[i].parent_id, cgroup[i].card_id)
            else: # no card group here
                if self.posInBounds(self.board.empty_rectangle_hitboxes[group_id], (x, y)):
                    return (group_id, 0)
        return None
        
    def getHandCardID(self, x, y):
        """Return the card ID of card in hand at (x, y).
        Return None if no card in hand exists at (x, y), or (x, y) is outside board."""
        if y < HAND_MENU_Y: # on board
            return None
        if y > TURN_MENU_Y: # in turn menu
            return None
        hand = self.curr_player.hand
        # loop backwards through cards in hand
        for i in range(len(hand)-1, -1, -1):
            if self.posInBounds(hand[i].click_region, (x, y)):
                return hand[i].card_id
        return None

    def posInBounds(self, bounds:tuple, pos:tuple=None):
        """Return true if (x, y) is in the given bounds.
        :param bounds: (x0, y0, x1, y1) of a rectangular area to check.
        :param pos: (x, y) of the position to check.
        """
        if pos[0] < bounds[0]: return False
        if pos[1] < bounds[1]: return False
        if pos[0] > bounds[2]: return False
        if pos[1] > bounds[3]: return False
        return True