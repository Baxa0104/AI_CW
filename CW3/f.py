import tkinter as tk
from tkinter import messagebox
import random
import math
from typing import Optional, Tuple

# GUI constants
COLORS = {
    'healthy': '#2ecc71',
    'damaged': '#f1c40f',
    'critical': '#e74c3c',
    'protected': '#3498db',
    'bg': '#ecf0f1',
    'text': '#2c3e50'
}
GRID_SIZE = 3
CELL_CONFIG = {
    'width': 10,
    'height': 5,
    'font': ('Arial', 10),
    'relief': 'flat'
}

class GameState:
    def __init__(self):
        self.habitats = [
            'Wetland', 'Meadow', 'Woodland',
            'Grassland', 'Marsh', 'Scrubland',
            'Forest', 'Riverbank', 'Savanna'
        ]
        self.difficulty = 'easy'
        self.reset_game()

    def reset_game(self):
        """Resets game state with random habitat distribution"""
        self.board = []
        self.current_player = 'human'
        self.game_over = False
        self.winner = None
        
        habitats = self.habitats.copy()
        random.shuffle(habitats)
        
        for row in range(GRID_SIZE):
            self.board.append([{
                'habitat': habitats.pop(),
                'state': 'damaged',
                'protected': False
            } for _ in range(GRID_SIZE)])

    def is_board_full(self) -> bool:
        return all(cell['state'] != 'damaged' for row in self.board for cell in row)

    def check_winner(self) -> Optional[str]:
        """Checks for winning conditions in rows, columns, and diagonals"""
        # Check rows and columns
        for i in range(GRID_SIZE):
            if all(cell['state'] == 'healthy' for cell in self.board[i]):
                return 'human'
            if all(cell['state'] == 'critical' for cell in self.board[i]):
                return 'ai'
            if all(self.board[j][i]['state'] == 'healthy' for j in range(GRID_SIZE)):
                return 'human'
            if all(self.board[j][i]['state'] == 'critical' for j in range(GRID_SIZE)):
                return 'ai'
        
        # Check diagonals
        diag1 = all(self.board[i][i]['state'] == 'healthy' for i in range(GRID_SIZE))
        diag2 = all(self.board[i][GRID_SIZE-1-i]['state'] == 'healthy' for i in range(GRID_SIZE))
        if diag1 or diag2:
            return 'human'
        
        diag1 = all(self.board[i][i]['state'] == 'critical' for i in range(GRID_SIZE))
        diag2 = all(self.board[i][GRID_SIZE-1-i]['state'] == 'critical' for i in range(GRID_SIZE))
        if diag1 or diag2:
            return 'ai'
        
        return None

class GameActions:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def human_move(self, row: int, col: int) -> bool:
        """Process human player move"""
        if (self.game_state.game_over or
            not (0 <= row < GRID_SIZE) or
            not (0 <= col < GRID_SIZE) or
            self.game_state.board[row][col]['state'] != 'damaged'):
            return False

        self.game_state.board[row][col].update({'state': 'healthy', 'protected': True})
        self.game_state.current_player = 'ai'
        
        if winner := self.game_state.check_winner():
            self.game_state.game_over = True
            self.game_state.winner = winner
        elif self.game_state.is_board_full():
            self.game_state.game_over = True
            
        return True

    def ai_move(self) -> Tuple[int, int]:
        return (self._random_ai_move() if self.game_state.difficulty == 'easy'
                else self._minimax_ai_move())

    def _random_ai_move(self) -> Tuple[int, int]:
        possible_moves = [
            (r, c) for r in range(GRID_SIZE)
            for c in range(GRID_SIZE)
            if self.game_state.board[r][c]['state'] == 'damaged'
        ]
        if not possible_moves:
            return (0, 0)
            
        row, col = random.choice(possible_moves)
        self._process_ai_move(row, col)
        return (row, col)

    def _minimax_ai_move(self) -> Tuple[int, int]:
        best_score = -math.inf
        best_move = None
        alpha = -math.inf
        beta = math.inf
        
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.game_state.board[row][col]['state'] == 'damaged':
                    self.game_state.board[row][col]['state'] = 'critical'
                    score = self._minimax(False, alpha, beta)
                    self.game_state.board[row][col]['state'] = 'damaged'
                    
                    if score > best_score:
                        best_score, best_move = score, (row, col)
                    
                    alpha = max(alpha, best_score)
                    if beta <= alpha:
                        break
        
        if best_move:
            self._process_ai_move(*best_move)
        return best_move or (0, 0)

    def _process_ai_move(self, row: int, col: int):
        self.game_state.board[row][col]['state'] = 'critical'
        self.game_state.current_player = 'human'
        if winner := self.game_state.check_winner():
            self.game_state.game_over = True
            self.game_state.winner = winner
        elif self.game_state.is_board_full():
            self.game_state.game_over = True

    def _minimax(self, is_maximizing: bool, alpha: float, beta: float, depth: int = 0) -> float:
        if winner := self.game_state.check_winner():
            return 10 - depth if winner == 'ai' else -10 + depth
        if self.game_state.is_board_full():
            return 0

        best_val = -math.inf if is_maximizing else math.inf
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.game_state.board[row][col]['state'] == 'damaged':
                    new_state = 'critical' if is_maximizing else 'healthy'
                    self.game_state.board[row][col]['state'] = new_state
                    
                    val = self._minimax(not is_maximizing, alpha, beta, depth + 1)
                    best_val = max(best_val, val) if is_maximizing else min(best_val, val)
                    
                    self.game_state.board[row][col]['state'] = 'damaged'
                    if is_maximizing:
                        alpha = max(alpha, val)
                    else:
                        beta = min(beta, val)
                        
                    if beta <= alpha:
                        return best_val
        return best_val

class WildlifeGameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wildlife Preservation Simulator")
        self.root.geometry("300x400")
        
        self.state = GameState()
        self.actions = GameActions(self.state)
        
        self._create_widgets()
        self.show_difficulty_menu()

    def _create_widgets(self):
        """Initialize all UI components"""
        # Configure grid layout
        for i in range(6):  # 3 rows + message + restart + padding
            self.root.grid_rowconfigure(i, weight=1)
        for i in range(3):
            self.root.grid_columnconfigure(i, weight=1)

        # Game board buttons
        self.buttons = [
            [self._create_cell_button(row, col) 
             for col in range(GRID_SIZE)]
            for row in range(GRID_SIZE)
        ]
        
        # Status components
        self.title_label = tk.Label(
            self.root, text="Wildlife Preservation", 
            font=('Arial', 16, 'bold'), fg=COLORS['text']
        )
        self.message_var = tk.StringVar()
        self.message_label = tk.Label(
            self.root, textvariable=self.message_var,
            font=('Arial', 12), wraplength=300,
            bg=COLORS['bg'], fg=COLORS['text']
        )
        self.restart_btn = tk.Button(
            self.root, text="Change Difficulty", 
            command=self.show_difficulty_menu,
            font=('Arial', 10), state='normal'
        )

    def _create_cell_button(self, row: int, col: int) -> tk.Button:
        """Create a grid cell button with consistent styling"""
        btn = tk.Button(
            self.root, text="", 
            command=lambda r=row, c=col: self.on_cell_click(r, c),
            **CELL_CONFIG
        )
        # Set initial appearance
        btn.config(
            bg=COLORS['damaged'],
            fg='black',
            highlightbackground=COLORS['bg'],
            highlightthickness=0
        )
        return btn

    def show_difficulty_menu(self):
        """Show difficulty selection screen"""
        self._hide_game_ui()
        
        self.difficulty_frame = tk.Frame(self.root, bg=COLORS['bg'])
        self.difficulty_frame.grid(row=1, column=0, rowspan=4, columnspan=3, sticky='nsew')
        
        tk.Label(
            self.difficulty_frame, text="Select Difficulty", 
            font=('Arial', 16, 'bold'), bg=COLORS['bg'], fg=COLORS['text']
        ).pack(pady=20)
        
        for text, difficulty in [("Easy (Random AI)", 'easy'), ("Hard (Minimax AI)", 'hard')]:
            tk.Button(
                self.difficulty_frame, text=text, 
                command=lambda d=difficulty: self.start_game(d),
                font=('Arial', 12), width=20, pady=10,
                bg=COLORS['healthy' if difficulty == 'easy' else 'critical'], 
                fg='white', relief='flat'
            ).pack(pady=10)
        
        tk.Label(
            self.difficulty_frame, 
            text="Easy: Random AI moves\nHard: Smart AI moves",
            font=('Arial', 10), bg=COLORS['bg'], fg=COLORS['text']
        ).pack(pady=10)

    def start_game(self, difficulty: str):
        """Start new game with selected difficulty"""
        self.state.difficulty = difficulty
        self.state.reset_game()
        self.difficulty_frame.destroy()
        self._show_game_ui()
        self.message_var.set("Your turn - protect a habitat!")
        self.update_board()  # Explicitly update the board after difficulty change

    def _show_game_ui(self):
        """Display game UI components"""
        self.title_label.grid(row=0, column=0, columnspan=3, pady=5)
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self.buttons[row][col].grid(row=row+1, column=col, padx=2, pady=2)
        self.message_label.grid(row=4, column=0, columnspan=3, pady=5, sticky='ew')
        self.restart_btn.grid(row=5, column=0, columnspan=3, pady=5)

    def _hide_game_ui(self):
        """Hide game UI components"""
        self.title_label.grid_remove()
        for row in self.buttons:
            for btn in row:
                btn.grid_remove()
        self.message_label.grid_remove()
        self.restart_btn.grid_remove()

    def update_board(self):
        """Update button appearances based on game state"""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                cell = self.state.board[row][col]
                btn = self.buttons[row][col]
                btn.config(
                    text=cell['habitat'],
                    bg=COLORS[cell['state']],
                    fg='white' if cell['state'] != 'damaged' else 'black',
                    highlightbackground=COLORS['protected'] if cell['protected'] else COLORS['bg'],
                    highlightthickness=3 if cell['protected'] else 0
                )

    def on_cell_click(self, row: int, col: int):
        """Handle player cell selection"""
        if self.state.game_over or self.state.current_player != 'human':
            return
            
        if self.actions.human_move(row, col):
            self.update_board()
            if self.state.game_over:
                self.game_over()
            else:
                self.root.after(500, self.ai_turn)

    def ai_turn(self):
        """Process AI move with visual feedback"""
        row, col = self.actions.ai_move()
        self.update_board()
        self.message_var.set(f"AI damaged {self.state.board[row][col]['habitat']}!")
        if self.state.game_over:
            self.game_over()

    def game_over(self):
        """Handle game conclusion"""
        if self.state.winner == 'human':
            message = "You win! Habitats preserved!"
        elif self.state.winner == 'ai':
            message = "You lost! Habitats degraded!"
        else:
            message = "Game ended in a tie!"
        messagebox.showinfo("Game Over", message)
        self.restart_btn.config(state='normal')

if __name__ == "__main__":
    root = tk.Tk()
    WildlifeGameUI(root)
    root.mainloop()