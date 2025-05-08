"""
File: VictoryScreen.py
Author: Willow Jordan
Purpose: Define a victory screen (overriding tk.Frame) that can be created/displayed by the root.
"""

import tkinter as tk

from ui_constants import BG_COLOR, UI_FONT, PAD, BUTTON_WIDTH, BUTTON_HEIGHT, TEXT_COLOR

class VictoryScreen(tk.Frame):
    def __init__(self, master, player_scores:dict):
        super().__init__(background=BG_COLOR)
        self.master = master

        sorted_scores = sorted(player_scores.items(), key=lambda item: item[1])

        self.winner_label = tk.Label(self, text=f"Player {sorted_scores[0][0]+1} won!", font=UI_FONT, background=BG_COLOR, foreground=TEXT_COLOR)
        self.explanation = tk.Label(self, text="Scores are determined by cards left in hand.", background=BG_COLOR, foreground=TEXT_COLOR)
        self.player_header = tk.Label(self, text=f"Player", font=UI_FONT, background=BG_COLOR, foreground=TEXT_COLOR)
        self.score_header = tk.Label(self, text="Score", font=UI_FONT, background=BG_COLOR, foreground=TEXT_COLOR)
        self.winner_label.grid(row=0, columnspan=2, pady=PAD)
        self.explanation.grid(row=1, columnspan=2, pady=PAD)
        self.player_header.grid(row=2, column=0, pady=PAD)
        self.score_header.grid(row=2, column=1, pady=PAD)

        self.player_labels:list[tk.Label] = {}
        self.score_labels:list[tk.Label] = {}
        current_row = 3
        for id, score in sorted_scores:
            self.player_labels[id] = tk.Label(self, text=f"Player {id+1}", font=UI_FONT, background=BG_COLOR, foreground=TEXT_COLOR)
            self.score_labels[id] = tk.Label(self, text=str(score), font=UI_FONT, background=BG_COLOR, foreground=TEXT_COLOR)
            self.player_labels[id].grid(row=current_row, column=0, pady=PAD)
            self.score_labels[id].grid(row=current_row, column=1, pady=PAD)
            current_row += 1

        self.mainmenu_button = tk.Button(self, command=self.mainmenu, text="Main Menu", width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        self.mainmenu_button.grid(row=3+len(player_scores), columnspan=2)

    def mainmenu(self):
        self.master.display_title()