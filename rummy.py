"""

"""

import random
import tkinter as tk

from game_objects.player import Player
from game_objects.card import Card, Suit
from game_objects.board import CardGroup, Board

from screens.TitleScreen import TitleScreen
from screens.SettingsScreen import SettingsScreen
from screens.GameScreen import GameScreen

from ui_constants import BG_COLOR

# main game object
class Game(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("800x800")
        self.title("Rummy")
        self.configure(background=BG_COLOR)

        self.current_screen = None # current frame being displayed
        self.display_title()

    def display_title(self):
        """Destroy current screen and display the title screen."""
        if self.current_screen is not None:
            self.current_screen.destroy()
        self.current_screen = TitleScreen(self)
        self.current_screen.pack()
    
    def display_settings(self):
        """Destroy current screen and display the settings screen."""
        if self.current_screen is not None:
            self.current_screen.destroy()
        self.current_screen = SettingsScreen(self)
        self.current_screen.pack()

    def display_game(self, numHumanPlayers, numComputerPlayers):
        """Destroy current screen and display the game screen using the provided list of players."""
        if self.current_screen is not None:
            self.current_screen.destroy()
        self.current_screen = GameScreen(self, numHumanPlayers, numComputerPlayers)
        self.current_screen.pack()

    def display(self, screen):
        """Destroy current screen and display provided screen."""
        if self.current_screen is not None:
            self.current_screen.destroy()
        self.current_screen = screen
        self.current_screen.pack()

if __name__ == "__main__":
    game = Game()
    game.display_game(1, 0)
    game.mainloop()