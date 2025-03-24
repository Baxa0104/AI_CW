import tkinter as tk # GUI framework
from tkinter import messagebox # For Tkinter Popup message/notification
import random # For shuffling
import math # For algorithm calculations
from typing import Optional, Tuple # Typing utils

# Game environment class. Defines and controls game states
class GameState:
    def __init__(self):

        # Sets Grid size. In this case it is 3x3
        self.grid_size = 3

        # Set habitat types.
        self.habitats = [
            'Wetland', 'Meadow', 'Woodland',
            'Grassland', 'Marsh', 'Scrubland',
            'Forest', 'Riverbank', 'Savanna'
        ]

        # Default Difficulty of the game
        self.difficulty = 'easy'
        self.reset_game()

    # Resets game
    def reset_game(self):
        self.board = []
        self.current_player = 'human'
        self.game_over = False
        self.winner = None
        
        habitats = self.habitats.copy()
        random.shuffle(habitats)
        
        for row in range(self.grid_size):
            board_row = []
            for col in range(self.grid_size):
                habitat = habitats.pop()
                board_row.append({
                    'habitat': habitat,
                    'state': 'damaged',
                    'protected': False
                })

            self.board.append(board_row)
    # Check if board is full
    def is_board_full(self) -> bool:
        return all(cell['state'] != 'damaged' for row in self.board for cell in row)

    # Checks winner. We have 3 states. Win, Lose and Tie as player perspective. Also 3 states of Habitat
    # Healthy - Green - after human move
    # Critical - RED - after AI move
    # Damaged - Yellow - Initial State
    def check_winner(self) -> Optional[str]:
        for i in range(self.grid_size):
            if all(cell['state'] == 'healthy' for cell in self.board[i]):
                return 'human'
            if all(cell['state'] == 'critical' for cell in self.board[i]):
                return 'ai'
            if all(self.board[j][i]['state'] == 'healthy' for j in range(self.grid_size)):
                return 'human'
            if all(self.board[j][i]['state'] == 'critical' for j in range(self.grid_size)):
                return 'ai'
        
        if all(self.board[i][i]['state'] == 'healthy' for i in range(self.grid_size)):
            return 'human'
        if all(self.board[i][i]['state'] == 'critical' for i in range(self.grid_size)):
            return 'ai'
        if all(self.board[i][self.grid_size-1-i]['state'] == 'healthy' for i in range(self.grid_size)):
            return 'human'
        if all(self.board[i][self.grid_size-1-i]['state'] == 'critical' for i in range(self.grid_size)):
            return 'ai'
        
        return None

# Defines AI and Game actions
class GameActions:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

    # Defines Player Move and its result.
    def human_move(self, row: int, col: int) -> bool:
        if (self.game_state.game_over or 
            self.game_state.current_player != 'human' or
            not (0 <= row < self.game_state.grid_size) or
            not (0 <= col < self.game_state.grid_size) or
            self.game_state.board[row][col]['state'] != 'damaged'):
            return False

        # Changes board state to healthy
        self.game_state.board[row][col]['state'] = 'healthy'
        # Changes to Protected to protect from modification
        self.game_state.board[row][col]['protected'] = True
        # Calls AI to perform its move.
        self.game_state.current_player = 'ai'
        
        if winner := self.game_state.check_winner():
            self.game_state.game_over = True
            self.game_state.winner = winner
        elif self.game_state.is_board_full():
            self.game_state.game_over = True
            
        return True

    # AI move definition. Decides ai move based on Chosen difficulty
    def ai_move(self) -> Tuple[int, int]:
        if self.game_state.difficulty == 'easy':
            return self._random_ai_move()
        else:
            return self._minimax_ai_move()

    # Reduced Difficulty of AI move. We do not need to check if cell is protected.
    # Checking Cell condition is enough for AI to perform the move.
    def _random_ai_move(self) -> Tuple[int, int]:
        possible_moves = [
            (row, col) for row in range(self.game_state.grid_size)
            for col in range(self.game_state.grid_size)
            if self.game_state.board[row][col]['state'] == 'damaged'
        ]
        
        if not possible_moves:
            return (0, 0)
        
        # Random Choice to move.     
        row, col = random.choice(possible_moves)
        # Changes state to critical
        self.game_state.board[row][col]['state'] = 'critical'
        # Calls Human to perform the move
        self.game_state.current_player = 'human'
        
        # We will define if game finished here as ai will perform checking programmatically
        # Checking will be needed on both moves if the game is multiplayer.
        if winner := self.game_state.check_winner():
            self.game_state.game_over = True
            self.game_state.winner = winner
        elif self.game_state.is_board_full():
            self.game_state.game_over = True
            
        return (row, col)

    # Defines Minimax algorithm with alpha-beta pruning for optimization. hard mode of the game.
    def _minimax_ai_move(self) -> Tuple[int, int]:
        best_score = -math.inf
        best_move = None
        alpha = -math.inf
        beta = math.inf
        
        for row in range(self.game_state.grid_size):
            for col in range(self.game_state.grid_size):
                if self.game_state.board[row][col]['state'] == 'damaged':
                    self.game_state.board[row][col]['state'] = 'critical'
                    score = self._minimax(False, alpha, beta)
                    self.game_state.board[row][col]['state'] = 'damaged'
                    
                    if score > best_score:
                        best_score = score
                        best_move = (row, col)
                    
                    alpha = max(alpha, best_score)
                    if beta <= alpha:
                        break
        
        if best_move:
            row, col = best_move
            self.game_state.board[row][col]['state'] = 'critical'
            self.game_state.current_player = 'human'
            
            if winner := self.game_state.check_winner():
                self.game_state.game_over = True
                self.game_state.winner = winner
            elif self.game_state.is_board_full():
                self.game_state.game_over = True
        
        return best_move or (0, 0)
    

    # Definition of Minimax algorithm itself.
    def _minimax(self, is_maximizing: bool, alpha: float, beta: float, depth: int = 0) -> float:
        if winner := self.game_state.check_winner():
            return 10 - depth if winner == 'ai' else -10 + depth
        if self.game_state.is_board_full():
            return 0

        if is_maximizing:
            max_eval = -math.inf
            for row in range(self.game_state.grid_size):
                for col in range(self.game_state.grid_size):
                    if self.game_state.board[row][col]['state'] == 'damaged':
                        self.game_state.board[row][col]['state'] = 'critical'
                        eval = self._minimax(False, alpha, beta, depth + 1)
                        self.game_state.board[row][col]['state'] = 'damaged'
                        max_eval = max(max_eval, eval)
                        alpha = max(alpha, eval)
                        if beta <= alpha:
                            break
            return max_eval
        else:
            min_eval = math.inf
            for row in range(self.game_state.grid_size):
                for col in range(self.game_state.grid_size):
                    if self.game_state.board[row][col]['state'] == 'damaged':
                        self.game_state.board[row][col]['state'] = 'healthy'
                        eval = self._minimax(True, alpha, beta, depth + 1)
                        self.game_state.board[row][col]['state'] = 'damaged'
                        min_eval = min(min_eval, eval)
                        beta = min(beta, eval)
                        if beta <= alpha:
                            break
            return min_eval

# Controls UI elements.
class WildlifeGameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wildlife Preservation Simulator")
        
        # Initialize game components.
        self.state = GameState()
        self.actions = GameActions(self.state)
        
        # UI Configuration
        self.cell_size = 100
        self.colors = {
            'healthy': '#2ecc71',  # Green
            'damaged': '#f1c40f',   # Yellow
            'critical': '#e74c3c',  # Red
            'protected': '#3498db', # Blue
            'bg': '#ecf0f1',        # Light gray
            'text': '#2c3e50'       # Dark blue-gray
        }
        
        self.setup_ui()
        self.show_difficulty_menu()

    # Sets up The UI
    def setup_ui(self):

        # Configure grid
        for i in range(4):  # 3x3 grid + message area
            self.root.grid_rowconfigure(i, weight=1)
            if i < 3:
                self.root.grid_columnconfigure(i, weight=1)
        
        # Title label
        self.title_label = tk.Label(
            self.root, text="Wildlife Preservation", 
            font=('Arial', 16, 'bold'), fg=self.colors['text']
        )
        self.title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Actual In game Habitat buttons
        self.buttons = []
        for row in range(3):
            button_row = []
            for col in range(3):
                btn = tk.Button(
                    self.root, text="", width=10, height=5,
                    font=('Arial', 10), relief='flat',
                    command=lambda r=row, c=col: self.on_cell_click(r, c)
                )
                btn.grid(row=row+1, column=col, padx=2, pady=2)
                button_row.append(btn)
            self.buttons.append(button_row)
        
        # Message area. Shows in game status messages
        self.message_var = tk.StringVar()
        self.message_label = tk.Label(
            self.root, textvariable=self.message_var,
            font=('Arial', 12), wraplength=300,
            bg=self.colors['bg'], fg=self.colors['text']
        )
        self.message_label.grid(row=4, column=0, columnspan=3, pady=10, sticky='ew')
        
        # Restart button
        self.restart_btn = tk.Button(
            self.root, text="Change Difficulty", 
            command=self.show_difficulty_menu,
            font=('Arial', 10), state='disabled'
        )
        self.restart_btn.grid(row=5, column=0, columnspan=3, pady=10)

    def show_difficulty_menu(self):
        # Hide game board
        for row in self.buttons:
            for btn in row:
                btn.grid_remove()
        self.message_label.grid_remove()
        self.restart_btn.grid_remove()
        
        # Create difficulty selection frame
        self.difficulty_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.difficulty_frame.grid(row=1, column=0, rowspan=4, columnspan=3, sticky='nsew')
        
        tk.Label(
            self.difficulty_frame, text="Select Difficulty", 
            font=('Arial', 16, 'bold'), bg=self.colors['bg'], fg=self.colors['text']
        ).pack(pady=20)
        
        # Menu Buttons

        tk.Button(
            self.difficulty_frame, text="Easy (Random AI)", 
            command=lambda: self.start_game('easy'),
            font=('Arial', 12), width=20, pady=10,
            bg='#2ecc71', fg='white', relief='flat'
        ).pack(pady=10)
        
        tk.Button(
            self.difficulty_frame, text="Hard (Minimax AI)", 
            command=lambda: self.start_game('hard'),
            font=('Arial', 12), width=20, pady=10,
            bg='#e74c3c', fg='white', relief='flat'
        ).pack(pady=10)
        
        tk.Label(
            self.difficulty_frame, 
            text="Easy: AI makes random moves\nHard: AI uses Minimax algorithm",
            font=('Arial', 10), bg=self.colors['bg'], fg=self.colors['text']
        ).pack(pady=10)

    # Starts game 
    def start_game(self, difficulty):
        self.state.difficulty = difficulty
        self.state.reset_game()
        self.difficulty_frame.destroy()
        
        # Show game board
        for row in self.buttons:
            for btn in row:
                btn.grid()
        self.message_label.grid()
        self.restart_btn.config(state='normal')
        
        self.update_board()
        self.message_var.set("Your turn - protect a habitat!")

    def update_board(self):
        for row in range(3):
            for col in range(3):
                cell = self.state.board[row][col]
                btn = self.buttons[row][col]
                
                # Update button text and color
                btn.config(text=cell['habitat'])
                
                if cell['state'] == 'healthy':
                    btn.config(bg=self.colors['healthy'], fg='white')
                elif cell['state'] == 'critical':
                    btn.config(bg=self.colors['critical'], fg='white')
                else:  # damaged
                    btn.config(bg=self.colors['damaged'], fg='black')
                
                # Add border for protected cells
                if cell['protected']:
                    btn.config(highlightbackground=self.colors['protected'], highlightthickness=3)
                else:
                    btn.config(highlightbackground=self.colors['bg'], highlightthickness=0)

    # Calls human to move
    def on_cell_click(self, row, col):
        if self.state.game_over:
            return
            
        if self.state.current_player == 'human':
            if self.actions.human_move(row, col):
                self.update_board()
                self.message_var.set(f"Protected {self.state.board[row][col]['habitat']}!")
                
                if not self.state.game_over:
                    self.root.after(500, self.ai_turn)
                else:
                    self.game_over()

    # Calls ai to move 
    def ai_turn(self):
        row, col = self.actions.ai_move()
        self.update_board()
        self.message_var.set(f"AI damaged {self.state.board[row][col]['habitat']}!")
        
        if self.state.game_over:
            self.game_over()

    def game_over(self):
        if self.state.winner == 'human':
            messagebox.showinfo("Game Over", "You win! Habitats preserved!")
        elif self.state.winner == 'ai':
            messagebox.showinfo("Game Over", "You lost! Habitats degraded!")
        else:
            messagebox.showinfo("Game Over", "Game ended in a tie!")
        
        self.restart_btn.config(state='active')

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("300x400")
    game = WildlifeGameUI(root)
    root.mainloop()