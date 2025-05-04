import tkinter as tk

from ui_constants import BG_COLOR, UI_FONT, PAD, BUTTON_WIDTH, BUTTON_HEIGHT

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

        self.master.display_game()

    def back(self):
        self.master.display_title()