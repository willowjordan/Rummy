import tkinter as tk

from ui_constants import BG_COLOR, UI_FONT, PAD, BUTTON_WIDTH, BUTTON_HEIGHT

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
        self.master.display_settings()