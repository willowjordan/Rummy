"""

"""

import random
import tkinter as tk

from player import Player
from card import Card, Suit

# UI CONSTANTS
BG_COLOR = "darkgreen"
BUTTON_WIDTH = 40
BUTTON_HEIGHT = 7
PAD = 10
UI_FONT = ('Arial', 18)
GAME_FONT = ('Helvetica', 16)

class TitleScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(background = BG_COLOR)
        self.master = master

        self.label = tk.Label(self, text="Rummy", font=UI_FONT, background=BG_COLOR)
        self.startbutton = tk.Button(self, command=self.start_game, text="Play", width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        self.exitbutton = tk.Button(self, command=self.master.destroy, text="Quit", width=BUTTON_WIDTH, height=BUTTON_HEIGHT)

        self.label.pack(pady=PAD)
        self.startbutton.pack(pady=PAD)
        self.exitbutton.pack(pady=PAD)
    
    def start_game(self):
        self.master.display(SettingsScreen(self.master))

class SettingsScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(background=BG_COLOR)
        self.master = master

        self.player_frame = tk.Frame(self, width=600, height=400)
        
        self.startbutton = tk.Button(self, command=self.start, text="Start Game", width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        self.backbutton = tk.Button(self, command=self.back, text="Back", width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
    
        self.player_frame.pack(pady=PAD)
        self.startbutton.pack(pady=PAD)
        self.backbutton.pack(pady=PAD)

    def start(self):
        #TODO: handle settings

        self.master.display(GameScreen(self.master))

    def back(self):
        self.master.display(TitleScreen(self.master))

class GameScreen(tk.Canvas):
    def __init__(self, master, players=[]):
        super().__init__(master, width=800, height=800, bd=0, highlightthickness=0, relief='ridge')
        self.master = master
        self.players = players
        #self.turn = random.randint(0, len(players)-1)

        self.drawBackground()

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
        self.drawHand(0)
    
    def drawHand(self, player_id):
        x = 0
        for card in self.players[player_id].hand:
            self.create_image(x, 600, image=card.image, anchor=tk.NW)
            x += 100

# main game object
class Game(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("800x800")
        self.title("Rummy")
        self.configure(background="lightgray")

        self.current_screen = None # current frame being displayed
        self.display(TitleScreen(self))

    def display(self, screen):
        """Destroy current screen and display provided screen."""
        if self.current_screen is not None:
            self.current_screen.destroy()
        self.current_screen = screen
        self.current_screen.pack()

if __name__ == "__main__":
    game = Game()
    game.display(GameScreen(game, [Player(False), Player(True)]))
    game.mainloop()