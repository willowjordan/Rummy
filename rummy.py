"""

"""

import random
import tkinter as tk

from player import Player

# UI CONSTANTS
BG_COLOR = "lightblue"
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
        errormsg = ""

        self.master.display(GameScreen(self.master, players=[Player(True)]))

    def back(self):
        self.master.display(TitleScreen(self.master))

class GameScreen(tk.Frame):
    def __init__(self, master, players):
        self.master = master
        self.players = players
        self.turn = random.randint(0, len(players)-1)

# main game object
class Game(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("800x800")
        self.title("Battleship")
        self.configure(background=BG_COLOR)

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
    #game.display(GameScreen(game, ComputerPlayer(IntermediateCPU(False))))
    game.mainloop()