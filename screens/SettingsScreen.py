"""
File: SettingsScreen.py
Author: Willow Jordan
Purpose: This script defines the SettingsScreen object (overriding tk.Frame), representing a screen where the user can enter the number of players and start the game.
"""

import tkinter as tk

from ui_constants import BG_COLOR, UI_FONT, PAD, BUTTON_WIDTH, BUTTON_HEIGHT, TEXT_COLOR

class SettingsScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(background=BG_COLOR)
        self.master = master

        self.settings_label = tk.Label(self, text="Settings", background = BG_COLOR, font=UI_FONT, foreground=TEXT_COLOR)

        self.player_options = [2, 3, 4, 5, 6]
        self.p_selection = tk.IntVar()

        self.player_label = tk.Label(self, text="Number of Players: ", background = BG_COLOR, foreground=TEXT_COLOR)
        self.player_selection = tk.OptionMenu(self, self.p_selection, *self.player_options)
        
        self.startbutton = tk.Button(self, command=self.start, text="Start Game", width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        self.backbutton = tk.Button(self, command=self.back, text="Back", width=BUTTON_WIDTH, height=BUTTON_HEIGHT)

        self.settings_label.grid(row=0, columnspan=2, pady=PAD)
        self.player_label.grid(row=1, column=0, pady=PAD)
        self.player_selection.grid(row=1, column=1, pady=PAD)
        self.startbutton.grid(row=2, columnspan=2, pady=PAD)
        self.backbutton.grid(row=3, columnspan=2, pady=PAD)

    def start(self):
        players = self.p_selection.get()
        if players == 0:
            self.errorlabel = tk.Label(self, text="Please select a player count.", font=UI_FONT, background = BG_COLOR, foreground="red")
            self.errorlabel.grid(row=4, columnspan=2)
        else:
            self.master.display_game(players)

    def back(self):
        self.master.display_title()