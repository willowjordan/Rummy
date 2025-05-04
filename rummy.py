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

# main game object
class Game(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("800x800")
        self.title("Rummy")
        self.configure(background="lightgray")

        self.current_screen = None # current frame being displayed
        self.display_title()

    def display_title(self):
        """Destroy current screen and display the title screen."""
        if self.current_screen is not None:
            self.current_screen.destroy()
        self.current_screen = TitleScreen(self)
    
    def display_settings(self):
        """Destroy current screen and display the settings screen."""
        if self.current_screen is not None:
            self.current_screen.destroy()
        self.current_screen = SettingsScreen(self)

    def display_game(self, players = None):
        """Destroy current screen and display the game screen using the provided list of players."""
        if self.current_screen is not None:
            self.current_screen.destroy()
        if players is None:
            self.current_screen = GameScreen(self)
        else:
            self.current_screen = GameScreen(self, players)

    def display(self, screen):
        """Destroy current screen and display provided screen."""
        if self.current_screen is not None:
            self.current_screen.destroy()
        self.current_screen = screen
        self.current_screen.pack()

if __name__ == "__main__":
    game = Game()
    game.display(GameScreen(game, [Player(False, [Card(Suit.CLUBS, 1), Card(Suit.DIAMONDS, 13), Card(Suit.HEARTS, 11), Card(Suit.SPADES, 12)])]))
    game.mainloop()