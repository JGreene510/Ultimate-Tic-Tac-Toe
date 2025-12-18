"""
Ultimate Tic Tac Toe - Fully Self-Contained Version
Single Python File (All code + sounds embedded)
Dependencies: tkinter, pygame, base64
Build: pyinstaller --onefile --windowed UltimateTicTacToe.py
"""

import tkinter as tk
from tkinter import messagebox
import json
import os
import random
import io
import base64
import pygame

# -------------------- BASE64 SOUNDS --------------------
# Replace these strings with your actual WAV files encoded in base64
MOVE_WAV_B64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YRAAAA=="  # placeholder
AI_MOVE_WAV_B64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YRAAAA=="  # placeholder
WIN_WAV_B64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YRAAAA=="  # placeholder
DRAW_WAV_B64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YRAAAA=="  # placeholder

# -------------------- INITIALIZE PYGAME --------------------
pygame.mixer.init()

def load_sound(b64_string):
    try:
        sound_bytes = base64.b64decode(b64_string)
        return pygame.mixer.Sound(file=io.BytesIO(sound_bytes))
    except Exception as e:
        print(f"Sound load error: {e}")
        return None

MOVE_SOUND = load_sound(MOVE_WAV_B64)
AI_MOVE_SOUND = load_sound(AI_MOVE_WAV_B64)
WIN_SOUND = load_sound(WIN_WAV_B64)
DRAW_SOUND = load_sound(DRAW_WAV_B64)

# -------------------- GAME LOGIC --------------------
class Game:
    def __init__(self, size=3):
        self.size = size
        self.board = [["" for _ in range(size)] for _ in range(size)]
        self.current_player = "X"

    def make_move(self, row, col):
        if self.board[row][col] == "":
            self.board[row][col] = self.current_player
            self.current_player = "O" if self.current_player == "X" else "X"
            return True
        return False

    def check_winner(self):
        # Rows, cols, diagonals
        lines = []
        lines.extend(self.board)
        lines.extend([[self.board[r][c] for r in range(self.size)] for c in range(self.size)])
        lines.append([self.board[i][i] for i in range(self.size)])
        lines.append([self.board[i][self.size-1-i] for i in range(self.size)])
        for line in lines:
            if line[0] != "" and all(x == line[0] for x in line):
                return line[0]
        return None

    def reset(self):
        self.board = [["" for _ in range(self.size)] for _ in range(self.size)]
        self.current_player = "X"

# -------------------- AI --------------------
class AI:
    def __init__(self, enabled=True, level="medium"):
        self.enabled = enabled
        self.level = level

    def set_level(self, level):
        self.level = level

    def get_move(self, game):
        if self.level == "easy":
            return self.easy_move(game)
        elif self.level == "medium":
            return self.medium_move(game)
        else:
            return self.hard_move(game)

    def easy_move(self, game):
        for r in range(game.size):
            for c in range(game.size):
                if game.board[r][c] == "":
                    return r, c

    def medium_move(self, game):
        empty = [(r,c) for r in range(game.size) for c in range(game.size) if game.board[r][c] == ""]
        return random.choice(empty)

    def hard_move(self, game):
        best_score = -float('inf')
        best_move = None
        for r in range(game.size):
            for c in range(game.size):
                if game.board[r][c] == "":
                    game.board[r][c] = "O"
                    score = self.minimax(game, False)
                    game.board[r][c] = ""
                    if score > best_score:
                        best_score = score
                        best_move = (r,c)
        return best_move

    def minimax(self, game, is_maximizing):
        winner = game.check_winner()
        if winner == "O": return 1
        elif winner == "X": return -1
        elif all(game.board[r][c] != "" for r in range(game.size) for c in range(game.size)):
            return 0

        if is_maximizing:
            best_score = -float('inf')
            for r in range(game.size):
                for c in range(game.size):
                    if game.board[r][c] == "":
                        game.board[r][c] = "O"
                        score = self.minimax(game, False)
                        game.board[r][c] = ""
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for r in range(game.size):
                for c in range(game.size):
                    if game.board[r][c] == "":
                        game.board[r][c] = "X"
                        score = self.minimax(game, True)
                        game.board[r][c] = ""
                        best_score = min(score, best_score)
            return best_score

# -------------------- UI --------------------
class TicTacToeUI(tk.Tk):
    THEMES = {
        "Classic": {"X":"#FF6666","O":"#6666FF","":"#FFFFFF"},
        "Dark": {"X":"#FFAAAA","O":"#AAAAFF","":"#333333"},
        "Pastel": {"X":"#FFB3BA","O":"#BAE1FF","":"#FFFFBA"}
    }

    STATS_FILE = os.path.join(os.path.expanduser("~"), ".ultimate_ttt_stats.json")

    def __init__(self):
        super().__init__()
        self.title("Ultimate Tic Tac Toe")
        self.resizable(False, False)
        self.configure(bg="#333333")
        self.game = Game()
        self.ai = AI(enabled=True)
        self.buttons = []
        self.colors = TicTacToeUI.THEMES["Classic"]
        self.stats = self.load_stats()
        self.create_board()
        self.create_status_bar()
        self.create_menu()
        self.update_buttons(animated=False)
        self.ai_anim_running = False
        self.ai_dots = 0

    # ---------------- Board ----------------
    def create_board(self):
        frame = tk.Frame(self, bg="#333333")
        frame.pack(padx=10,pady=10)
        for r in range(self.game.size):
            row_buttons=[]
            for c in range(self.game.size):
                btn=tk.Button(frame,text="",width=6,height=3,font=("Helvetica",32,"bold"),
                              bg=self.colors[""],activebackground="#AAAAAA",
                              command=lambda r=r,c=c:self.on_click(r,c))
                btn.grid(row=r,column=c,padx=3,pady=3)
                btn.bind("<Enter>", lambda e,b=btn: b.config(bg="#DDDDDD"))
                btn.bind("<Leave>", lambda e,b=btn,r=r,c=c: b.config(bg=self.colors[self.game.board[r][c]]))
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

    # ---------------- Status ----------------
    def create_status_bar(self):
        self.status_var=tk.StringVar()
        self.status_var.set(f"{self.game.current_player}'s turn")
        self.status_label=tk.Label(self,textvariable=self.status_var,
                                   bg="#222222",fg="#FFFFFF",font=("Helvetica",14))
        self.status_label.pack(fill="x",padx=5,pady=5)

    # ---------------- Menu ----------------
    def create_menu(self):
        menubar = tk.Menu(self)
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Reset Game", command=self.reset_game)
        game_menu.add_command(label="Quit", command=self.quit)
        menubar.add_cascade(label="Game", menu=game_menu)

        theme_menu = tk.Menu(menubar, tearoff=0)
        for name in TicTacToeUI.THEMES.keys():
            theme_menu.add_command(label=name,command=lambda n=name:self.change_theme(n))
        menubar.add_cascade(label="Theme",menu=theme_menu)

        ai_menu = tk.Menu(menubar, tearoff=0)
        ai_menu.add_command(label="Easy",command=lambda:self.ai.set_level("easy"))
        ai_menu.add_command(label="Medium",command=lambda:self.ai.set_level("medium"))
        ai_menu.add_command(label="Hard",command=lambda:self.ai.set_level("hard"))
        menubar.add_cascade(label="AI Level",menu=ai_menu)
        self.config(menu=menubar)

    def change_theme(self, theme_name):
        self.colors = TicTacToeUI.THEMES[theme_name]
        self.update_buttons(animated=False)

    # ---------------- Click ----------------
    def on_click(self,r,c):
        if self.game.make_move(r,c):
            self.animate_tile(r,c,self.game.board[r][c])
            self.play_sound(MOVE_SOUND)
            self.check_game_status()
            if self.ai.enabled and not self.game.check_winner():
                self.start_ai_thinking()
                self.after(500,self.ai_move)

    def ai_move(self):
        r,c=self.ai.get_move(self.game)
        if self.game.make_move(r,c):
            self.animate_tile(r,c,self.game.board[r][c])
            self.play_sound(AI_MOVE_SOUND)
            self.check_game_status()
        self.stop_ai_thinking()

    # ---------------- Game Status ----------------
    def check_game_status(self):
        winner=self.game.check_winner()
        if winner:
            self.handle_win(winner)
        elif all(self.game.board[r][c] != "" for r in range(self.game.size) for c in range(self.game.size)):
            self.handle_draw()
        else:
            self.status_var.set(f"{self.game.current_player}'s turn")

    def handle_win(self, player):
        self.flash_winner(player)
        self.play_sound(WIN_SOUND)
        self.stats[player] = self.stats.get(player,0)+1
        self.save_stats()
        self.after(1000,self.reset_game)

    def handle_draw(self):
        self.flash_draw()
        self.play_sound(DRAW_SOUND)
        self.after(1000,self.reset_game)

    # ---------------- Animations ----------------
    def animate_tile(self,r,c,player):
        colors=["#FFFFFF",self.colors[player]]
        def step(i=0):
            if i<len(colors):
                self.buttons[r][c].configure(bg=colors[i],text=player,fg="#FFFFFF" if player else "#000000")
                self.after(100,lambda: step(i+1))
        step()

    def flash_winner(self,player):
        # Rows, cols, diagonals
        for i in range(self.game.size):
            if all(self.game.board[i][c]==player for c in range(self.game.size)):
                self.flash_line([(i,c) for c in range(self.game.size)])
                return
            if all(self.game.board[r][i]==player for r in range(self.game.size)):
                self.flash_line([(r,i) for r in range(self.game.size)])
                return
        if all(self.game.board[i][i]==player for i in range(self.game.size)):
            self.flash_line([(i,i) for i in range(self.game.size)])
            return
        if all(self.game.board[i][self.game.size-1-i]==player for i in range(self.game.size)):
            self.flash_line([(i,self.game.size-1-i) for i in range(self.game.size)])
            return

    def flash_line(self, coords, flashes=4):
        def step(f=0):
            color="#FFFF00" if f%2==0 else self.colors[""]
            for r,c in coords:
                self.buttons[r][c].configure(bg=color)
            if f<flashes*2:
                self.after(200,lambda: step(f+1))
        step()

    def flash_draw(self, flashes=4):
        def step(f=0):
            color="#AAAAAA" if f%2==0 else "#FFFFFF"
            for r in range(self.game.size):
                for c in range(self.game.size):
                    self.buttons[r][c].configure(bg=color)
            if f<flashes*2:
                self.after(200,lambda: step(f+1))
        step()

    # ---------------- Update / Reset ----------------
    def update_buttons(self,animated=True):
        for r in range(self.game.size):
            for c in range(self.game.size):
                player=self.game.board[r][c]
                self.buttons[r][c].configure(text=player,bg=self.colors[player],fg="#FFFFFF" if player else "#000000")

    def reset_game(self):
        for r in range(self.game.size):
            for c in range(self.game.size):
                self.buttons[r][c].configure(bg=self.colors[""],text="")
        self.game.reset()
        self.update_buttons(animated=False)
        self.status_var.set(f"{self.game.current_player}'s turn")

    # ---------------- AI Thinking ----------------
    def start_ai_thinking(self):
        self.ai_anim_running=True
        self.ai_dots=0
        self.animate_ai_status()

    def stop_ai_thinking(self):
        self.ai_anim_running=False
        self.status_var.set(f"{self.game.current_player}'s turn")

    def animate_ai_status(self):
        if self.ai_anim_running:
            dots="."*(self.ai_dots%4)
            self.status_var.set(f"AI is thinking{dots}")
            self.ai_dots+=1
            self.after(500,self.animate_ai_status)

    # ---------------- Sound ----------------
    def play_sound(self,sound):
        try:
            if sound:
                sound.play()
        except Exception as e:
            print(f"Sound error: {e}")

    # ---------------- Stats ----------------
    def load_stats(self):
        if os.path.exists(TicTacToeUI.STATS_FILE):
            try:
                with open(TicTacToeUI.STATS_FILE) as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_stats(self):
        try:
            with open(TicTacToeUI.STATS_FILE,"w") as f:
                json.dump(self.stats,f)
        except Exception as e:
            print(f"Stats save error: {e}")

# -------------------- RUN --------------------
if __name__=="__main__":
    app=TicTacToeUI()
    app.mainloop()
