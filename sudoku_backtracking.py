import tkinter as tk
from tkinter import messagebox
import numpy as np # type: ignore
import random
from PIL import Image, ImageTk # type: ignore
import math

class SudokuGame:
    def __init__(self, parent_window, main_menu, game_data):
        try:
            print("Initializing SudokuGame...")
            if not parent_window or not main_menu:
                raise ValueError("Parent window and main menu must be provided")
                
            self.parent_window = parent_window
            self.main_menu = main_menu
            self.game_data = game_data or {}
            
            print("Creating game window...")
            # Initialize window with simpler approach
            self.window = tk.Toplevel(parent_window)
            self.window.title("Sudoku Game")
            self.window.geometry("700x800")
            self.window.configure(bg='#1a2a3a')
            self.window.resizable(False, False)
            
            # Basic window setup
            self.window.transient(parent_window)
            self.window.grab_set()
            self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Initialize game state
            self.board = np.zeros((9, 9), dtype=int)
            self.solution = np.zeros((9, 9), dtype=int)
            self.original_numbers = set()
            self.selected_cell = None
            self.mistakes = 0
            self.max_mistakes = 3
            
            # Initialize UI components
            self.cells = {}
            self.cell_frames = {}
            self.mistakes_label = None
            
            # Initialize animation tracking
            self.animation_ids = {}
            self.active_animations = set()
            
            # Create basic widgets first
            self.create_basic_widgets()
            
            # Generate puzzle
            self.generate_puzzle()
            self.update_board()
            
            # Bind keyboard events
            self.window.bind('<Key>', self.handle_key_press)
            
            # Center window
            self.center_window()
            
            # Make sure window is visible
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
            
            # Force window update
            self.window.update()
            self.window.update_idletasks()
            
            print("Game window initialization complete!")
            
        except Exception as e:
            print(f"Error initializing game: {str(e)}")
            import traceback
            traceback.print_exc()
            if hasattr(self, 'window'):
                self.window.destroy()
            raise

    def create_basic_widgets(self):
        try:
            # Main frame
            self.main_frame = tk.Frame(self.window, bg='#1a2a3a')
            self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
            
            # Title
            title_label = tk.Label(
                self.main_frame,
                text="SUDOKU",
                font=('Helvetica', 24, 'bold'),
                bg='#1a2a3a',
                fg='white',
                pady=10
            )
            title_label.pack()
            
            # Difficulty label
            difficulty_label = tk.Label(
                self.main_frame,
                text=f"Difficulty: {self.game_data.get('difficulty', 'Medium')}",
                font=('Helvetica', 12),
                bg='#1a2a3a',
                fg='white',
                pady=5
            )
            difficulty_label.pack()
            
            # Game board
            self.board_frame = tk.Frame(
                self.main_frame,
                bg='#0d47a1',
                padx=2,
                pady=2
            )
            self.board_frame.pack(pady=20)
            
            # Create cells
            self.cells = {}
            self.cell_frames = {}
            
            for i in range(9):
                for j in range(9):
                    cell_frame = tk.Frame(
                        self.board_frame,
                        width=55,
                        height=55,
                        bg='white',
                        highlightthickness=1,
                        highlightbackground='#0d47a1'
                    )
                    cell_frame.grid(row=i, column=j, padx=1, pady=1)
                    cell_frame.grid_propagate(False)
                    
                    cell_label = tk.Label(
                        cell_frame,
                        text='',
                        font=('Helvetica', 22),
                        bg='white',
                        cursor='hand2',
                        width=2,
                        height=1
                    )
                    cell_label.place(relx=0.5, rely=0.5, anchor='center')
                    
                    cell_frame.bind('<Button-1>', lambda e, i=i, j=j: self.select_cell(i, j))
                    cell_label.bind('<Button-1>', lambda e, i=i, j=j: self.select_cell(i, j))
                    
                    self.cells[(i, j)] = cell_label
                    self.cell_frames[(i, j)] = cell_frame
            
            # Control buttons
            self.control_frame = tk.Frame(self.main_frame, bg='#1a2a3a')
            self.control_frame.pack(pady=20)
            
            buttons = [
                ("Check Solution", self.check_solution),
                ("Solve", self.solve_puzzle),
                ("Save Game", self.save_game),
                ("Back to Menu", self.on_closing)
            ]
            
            for text, command in buttons:
                btn = tk.Button(
                    self.control_frame,
                    text=text,
                    font=('Helvetica', 14),
                    command=command,
                    bg='#2196F3',
                    fg='white',
                    relief=tk.FLAT,
                    padx=10,
                    pady=5
                )
                btn.pack(side=tk.LEFT, padx=10)
            
            # Mistakes label
            self.mistakes_label = tk.Label(
                self.main_frame,
                text=f"Mistakes: {self.mistakes}/{self.max_mistakes}",
                font=('Helvetica', 14),
                bg='#1a2a3a',
                fg='white',
                pady=10
            )
            self.mistakes_label.pack()
            
        except Exception as e:
            print(f"Error creating basic widgets: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def on_closing(self):
        try:
            # Ask for confirmation before closing
            if messagebox.askyesno("Quit Game", "Are you sure you want to quit the current game?"):
                # Cancel all pending animations
                self.cancel_all_animations()
                
                # Clean up canvas items
                if hasattr(self, 'bg_canvas'):
                    self.bg_canvas.delete('all')
                
                # Reset game state
                self.board = None
                self.solution = None
                self.original_numbers = None
                self.selected_cell = None
                
                # Release grab and destroy window
                self.window.grab_release()
                
                # Make sure parent window is shown before destroying
                if self.parent_window:
                    self.parent_window.deiconify()
                    self.parent_window.lift()
                    self.parent_window.focus_force()
                
                # Destroy the window
                self.window.destroy()
            
        except Exception as e:
            print(f"Error during window closing: {str(e)}")
            if self.parent_window:
                self.parent_window.deiconify()
                self.parent_window.lift()
                self.parent_window.focus_force()
            self.window.destroy()

    def schedule_animation(self, name, callback, delay):
        try:
            # Cancel previous animation with same name if exists
            self.cancel_animation(name)
            
            # Validate parameters
            if not callable(callback):
                raise ValueError("Callback must be callable")
            if not isinstance(delay, (int, float)) or delay < 0:
                raise ValueError("Delay must be a non-negative number")
                
            # Schedule new animation
            self.animation_ids[name] = self.window.after(delay, callback)
            self.active_animations.add(name)
        except Exception as e:
            print(f"Error scheduling animation {name}: {str(e)}")
            self.cancel_animation(name)

    def cancel_animation(self, name):
        try:
            if name in self.animation_ids and self.animation_ids[name]:
                self.window.after_cancel(self.animation_ids[name])
                self.animation_ids[name] = None
            if name in self.active_animations:
                self.active_animations.remove(name)
        except Exception as e:
            print(f"Error canceling animation {name}: {str(e)}")

    def cancel_all_animations(self):
        try:
            # Create a copy of active animations to avoid modification during iteration
            for name in list(self.active_animations):
                self.cancel_animation(name)
        except Exception as e:
            print(f"Error canceling all animations: {str(e)}")

    def animate_bg_gradient(self):
        # Animate a vertical gradient by cycling colors
        self.bg_canvas.delete("gradient")
        h = 800
        steps = 30
        
        # Calculate gradient colors
        phase = self.bg_gradient_phase
        base_colors = [(26, 42, 58), (33, 150, 243), (21, 101, 192), (26, 42, 58)]
        
        # Create smooth gradient
        for i in range(steps):
            y1 = i * h / steps
            y2 = (i + 1) * h / steps
            t = i / (steps - 1)
            
            # Interpolate between base colors based on phase
            idx = int(t * (len(base_colors) - 1))
            next_idx = min(idx + 1, len(base_colors) - 1)
            
            c1 = base_colors[idx]
            c2 = base_colors[next_idx]
            
            # Add phase offset for animation
            t_with_phase = (t + phase) % 1.0
            
            # Smooth interpolation between colors
            r = int(c1[0] + (c2[0] - c1[0]) * t_with_phase)
            g = int(c1[1] + (c2[1] - c1[1]) * t_with_phase)
            b = int(c1[2] + (c2[2] - c1[2]) * t_with_phase)
            
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.bg_canvas.create_rectangle(0, y1, 700, y2, fill=color, outline="", tags="gradient")
        
        # Update phase for next frame
        self.bg_gradient_phase = (self.bg_gradient_phase + 0.01) % 1.0
        self.schedule_animation('bg_gradient', self.animate_bg_gradient, 50)

    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        try:
            print("Creating main frame...")
            # Main frame (transparent for fade-in)
            self.main_frame = tk.Frame(self.window, bg='', highlightthickness=0)
            self.main_frame.place(relx=0.5, rely=0.5, anchor='center')
            
            print("Creating title frame...")
            # Title frame
            title_frame = tk.Frame(self.main_frame, bg='#0d47a1')
            title_frame.pack(fill="x", pady=(0, 20))
            
            title_label = tk.Label(
                title_frame,
                text="SUDOKU",
                font=('Helvetica', 24, 'bold'),
                bg='#0d47a1',
                fg='white',
                pady=10
            )
            title_label.pack()
            
            # Difficulty label
            difficulty_label = tk.Label(
                title_frame,
                text=f"Difficulty: {self.game_data['difficulty']}",
                font=('Helvetica', 12),
                bg='#0d47a1',
                fg='white',
                pady=5
            )
            difficulty_label.pack()
            
            print("Creating game board...")
            # Game board
            self.board_frame = tk.Frame(
                self.main_frame,
                bg='#0d47a1',
                padx=2,
                pady=2
            )
            self.board_frame.pack(pady=20)
            
            # Create cells with improved Sudoku styling
            self.cells = {}
            self.cell_frames = {}
            
            print("Creating cells...")
            # Create 3x3 subgrids first
            for box_i in range(3):
                for box_j in range(3):
                    subgrid = tk.Frame(
                        self.board_frame,
                        bg='#0d47a1',
                        padx=1,
                        pady=1
                    )
                    subgrid.grid(row=box_i, column=box_j, padx=1, pady=1)
                    
                    # Create cells within each subgrid
                    for i in range(3):
                        for j in range(3):
                            global_i = box_i * 3 + i
                            global_j = box_j * 3 + j
                            
                            cell_frame = tk.Frame(
                                subgrid,
                                width=55,
                                height=55,
                                bg='white',
                                highlightthickness=1,
                                highlightbackground='#0d47a1'
                            )
                            cell_frame.grid(row=i, column=j)
                            cell_frame.grid_propagate(False)
                            
                            cell_label = tk.Label(
                                cell_frame,
                                text='',
                                font=('Helvetica', 22),
                                bg='white',
                                cursor='hand2',
                                width=2,
                                height=1
                            )
                            cell_label.place(relx=0.5, rely=0.5, anchor='center')
                            
                            cell_frame.bind('<Button-1>', 
                                lambda e, i=global_i, j=global_j: self.select_cell(i, j))
                            cell_label.bind('<Button-1>', 
                                lambda e, i=global_i, j=global_j: self.select_cell(i, j))
                            
                            self.cells[(global_i, global_j)] = cell_label
                            self.cell_frames[(global_i, global_j)] = cell_frame
            
            print("Creating control buttons...")
            # Control buttons with modern styling
            self.control_frame = tk.Frame(self.main_frame, bg='')
            self.control_frame.pack(pady=20)
            buttons = [
                ("Check Solution", self.check_solution, '#4CAF50', '#388E3C'),
                ("Solve", self.solve_puzzle, '#FF9800', '#F57C00'),
                ("Save Game", self.save_game, '#2196F3', '#1976D2'),
                ("Back to Menu", self.window.destroy, '#F44336', '#D32F2F')
            ]
            for text, command, bg, hover_bg in buttons:
                btn = tk.Button(
                    self.control_frame,
                    text=text,
                    font=('Helvetica', 14),
                    command=command,
                    bg=bg,
                    fg='white',
                    activebackground=hover_bg,
                    relief=tk.FLAT,
                    borderwidth=0,
                    cursor='hand2',
                    padx=10,
                    pady=5
                )
                btn.pack(side=tk.LEFT, padx=10)
                btn.bind('<Enter>', lambda e, b=btn, h=hover_bg: self.on_enter(e, b, h))
                btn.bind('<Leave>', lambda e, b=btn, bg=bg: self.on_leave(e, b, bg))
                btn.configure(highlightthickness=2, highlightbackground='#0d47a1')
            
            self.mistakes_label = tk.Label(
                self.main_frame,
                text=f"Mistakes: {self.mistakes}/{self.max_mistakes}",
                font=('Helvetica', 14),
                bg='#1a2a3a',
                fg='white',
                pady=10
            )
            self.mistakes_label.pack()
            
            print("Widget creation complete!")
            
        except Exception as e:
            print(f"Error creating widgets: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def on_enter(self, event, button, hover_bg=None):
        if hover_bg:
            button.configure(bg=hover_bg)
        else:
            button.configure(bg='#1976D2')

    def on_leave(self, event, button, original_bg=None):
        if original_bg:
            button.configure(bg=original_bg)
        else:
            button.configure(bg='#2196F3')

    def handle_key_press(self, event):
        try:
            if not self.selected_cell:
                return
                
            row, col = self.selected_cell
            if event.char.isdigit() and 1 <= int(event.char) <= 9:
                self.place_number(int(event.char))
            elif event.keysym == 'BackSpace' or event.keysym == 'Delete':
                self.place_number(0)
            elif event.keysym in ['Left', 'Right', 'Up', 'Down']:
                # Handle arrow key navigation
                if event.keysym == 'Left' and col > 0:
                    self.select_cell(row, col - 1)
                elif event.keysym == 'Right' and col < 8:
                    self.select_cell(row, col + 1)
                elif event.keysym == 'Up' and row > 0:
                    self.select_cell(row - 1, col)
                elif event.keysym == 'Down' and row < 8:
                    self.select_cell(row + 1, col)
                    
        except Exception as e:
            print(f"Error handling key press: {str(e)}")

    def generate_puzzle(self):
        try:
            # Generate a solved board
            self.solution = self.generate_solved_board()
            if not self.is_valid_board(self.solution):
                raise ValueError("Generated solution is invalid")
            
            # Create a copy for the puzzle
            self.board = self.solution.copy()
            self.original_numbers = set()
            
            # Remove numbers based on difficulty
            cells_to_remove = {
                'Easy': 30,
                'Medium': 40,
                'Hard': 50
            }.get(self.game_data.get('difficulty', 'Medium'), 40)
            
            # Create a list of all cell positions
            all_cells = [(i, j) for i in range(9) for j in range(9)]
            random.shuffle(all_cells)
            
            # Remove numbers while ensuring the puzzle has a unique solution
            removed = 0
            max_attempts = len(all_cells) * 2  # Safety check
            attempts = 0
            
            # Initially mark all cells as original
            for i in range(9):
                for j in range(9):
                    self.original_numbers.add((i, j))
            
            for row, col in all_cells:
                if removed >= cells_to_remove or attempts >= max_attempts:
                    break
                    
                temp = self.board[row, col]
                self.board[row, col] = 0
                
                # Check if the puzzle still has a unique solution
                if self.count_solutions(self.board.copy()) == 1:
                    removed += 1
                    self.original_numbers.remove((row, col))
                else:
                    self.board[row, col] = temp
                attempts += 1
                
            # Validate the generated puzzle
            if not self.is_valid_board(self.board):
                raise ValueError("Generated puzzle is invalid")
                
            # If we couldn't remove enough numbers, try generating a new puzzle
            if removed < cells_to_remove // 2:
                print("Regenerating puzzle due to insufficient removable numbers...")
                return self.generate_puzzle()
                
            # Update the board display
            self.update_board()
            
        except Exception as e:
            print(f"Error in generate_puzzle: {str(e)}")
            # If there's an error, try to generate a simpler puzzle
            self.board = np.zeros((9, 9), dtype=int)
            self.solution = np.zeros((9, 9), dtype=int)
            self.original_numbers = set()
            self.update_board()
            messagebox.showerror("Error", "Failed to generate puzzle. Please try again.")

    def is_valid_board(self, board):
        """Check if a board is a valid Sudoku board"""
        try:
            # Check rows
            for row in board:
                if len(set(row[row != 0])) != len(row[row != 0]):
                    return False
            
            # Check columns
            for col in range(9):
                column = board[:, col]
                if len(set(column[column != 0])) != len(column[column != 0]):
                    return False
            
            # Check 3x3 boxes
            for box_row in range(0, 9, 3):
                for box_col in range(0, 9, 3):
                    box = board[box_row:box_row+3, box_col:box_col+3]
                    box_flat = box.flatten()
                    if len(set(box_flat[box_flat != 0])) != len(box_flat[box_flat != 0]):
                        return False
            
            return True
        except Exception:
            return False

    def generate_solved_board(self):
        board = np.zeros((9, 9), dtype=int)
        self.solve(board)
        return board

    def solve(self, board):
        empty = self.find_empty(board)
        if not empty:
            return True
        
        row, col = empty
        numbers = list(range(1, 10))
        random.shuffle(numbers)
        
        for num in numbers:
            if self.is_valid(board, num, (row, col)):
                board[row, col] = num
                if self.solve(board):
                    return True
                board[row, col] = 0
        return False

    def find_empty(self, board):
        for i in range(9):
            for j in range(9):
                if board[i, j] == 0:
                    return (i, j)
        return None

    def is_valid(self, board, num, pos):
        # Check row
        if num in board[pos[0]]:
            return False
        
        # Check column
        if num in board[:, pos[1]]:
            return False
        
        # Check box
        box_x = pos[1] // 3
        box_y = pos[0] // 3
        if num in board[box_y*3:box_y*3+3, box_x*3:box_x*3+3]:
            return False
        
        return True

    def count_solutions(self, board):
        empty = self.find_empty(board)
        if not empty:
            return 1
        
        row, col = empty
        count = 0
        
        for num in range(1, 10):
            if self.is_valid(board, num, (row, col)):
                board[row, col] = num
                count += self.count_solutions(board.copy())
                board[row, col] = 0
                if count > 1:
                    return count
        return count

    def select_cell(self, row, col):
        try:
            # Validate coordinates
            if not (0 <= row < 9 and 0 <= col < 9):
                return
                
            if (row, col) in self.original_numbers:
                return
            
            # Clear previous selection
            if self.selected_cell:
                prev_row, prev_col = self.selected_cell
                if (prev_row, prev_col) in self.cells:
                    self.cells[(prev_row, prev_col)].configure(bg='white')
            
            # Cancel any existing selection animation
            self.cancel_animation('cell_selection')
            
            # Update selection
            self.selected_cell = (row, col)
            self.animate_cell_selection(row, col, 0)
            
            # Focus the window to receive keyboard input
            self.window.focus_force()
            
        except Exception as e:
            print(f"Error in select_cell: {str(e)}")

    def animate_cell_selection(self, row, col, phase):
        # Pulse glow effect for selected cell
        if self.selected_cell != (row, col):
            self.cells[(row, col)].configure(bg='white')
            self.cancel_animation('cell_selection')
            return
            
        glow = int(230 + 25 * abs(math.sin(phase)))
        color = f'#E3F2FD' if glow > 240 else f'#{glow:02x}{glow:02x}fd'
        self.cells[(row, col)].configure(bg=color)
        
        if phase < 10:  # Limit animation duration
            self.schedule_animation('cell_selection', 
                lambda: self.animate_cell_selection(row, col, phase+0.2), 40)
        else:
            self.cancel_animation('cell_selection')

    def place_number(self, num):
        try:
            if not self.selected_cell:
                return
                
            row, col = self.selected_cell
            if not (0 <= row < 9 and 0 <= col < 9):
                return
                
            if (row, col) in self.original_numbers:
                return
            
            if not isinstance(num, int) or not (0 <= num <= 9):
                return
                
            # Store previous value
            prev = self.board[row, col]
            
            # Update board
            self.board[row, col] = num
            self.update_board()
            
            # Handle game logic
            if num != 0:
                if num != self.solution[row, col]:
                    self.mistakes += 1
                    if self.mistakes_label:
                        self.mistakes_label.configure(text=f"Mistakes: {self.mistakes}/{self.max_mistakes}")
                    self.animate_mistake(row, col, 0)
                    if self.mistakes >= self.max_mistakes:
                        messagebox.showinfo("Game Over", "Too many mistakes! Game over.")
                        self.window.destroy()
                else:
                    self.animate_number_entry(row, col, 0)
                    
                # Check for victory
                if np.array_equal(self.board, self.solution):
                    self.animate_victory(0)
                    self.window.after(1200, lambda: (
                        messagebox.showinfo("Congratulations!", "You solved the puzzle!"),
                        self.window.destroy()
                    ))
        except Exception as e:
            print(f"Error in place_number: {str(e)}")
            messagebox.showerror("Error", "An error occurred while placing the number. Please try again.")

    def animate_number_entry(self, row, col, phase):
        # Pop/fade-in effect for number entry
        if phase > 1.0:
            self.cells[(row, col)].configure(font=('Helvetica', 22))
            self.cancel_animation('number_entry')
            return
            
        size = int(22 + 8 * math.sin(math.pi * phase))
        self.cells[(row, col)].configure(font=('Helvetica', size))
        self.schedule_animation('number_entry',
            lambda: self.animate_number_entry(row, col, phase+0.12), 20)

    def animate_mistake(self, row, col, phase):
        # Shake effect for mistake
        if phase > 1.0:
            self.cell_frames[(row, col)].place_configure(x=0)
            self.cancel_animation('mistake')
            return
            
        offset = int(6 * math.sin(phase * 8 * math.pi))
        self.cell_frames[(row, col)].place(x=offset, y=0)
        self.schedule_animation('mistake',
            lambda: self.animate_mistake(row, col, phase+0.08), 20)

    def animate_victory(self, phase):
        # Board glow/confetti effect
        if phase > 1.0:
            for cell in self.cells.values():
                cell.configure(bg='white')
            self.cancel_animation('victory')
            return
            
        glow = int(230 + 25 * abs(math.sin(phase * math.pi)))
        color = f'#{glow:02x}{glow:02x}fd'
        for cell in self.cells.values():
            cell.configure(bg=color)
            
        # Simple confetti: draw random colored dots on bg_canvas
        self.bg_canvas.delete('confetti')
        for _ in range(30):
            x = random.randint(50, 650)
            y = random.randint(100, 700)
            c = random.choice(['#FFEB3B', '#FF4081', '#69F0AE', '#40C4FF', '#FFD740'])
            self.bg_canvas.create_oval(x, y, x+8, y+8, fill=c, outline='', tags='confetti')
            
        self.schedule_animation('victory',
            lambda: self.animate_victory(phase+0.08), 60)

    def update_board(self):
        try:
            if not hasattr(self, 'cells') or not self.cells:
                return
                
            for i in range(9):
                for j in range(9):
                    cell = self.cells.get((i, j))
                    if not cell:
                        continue
                        
                    try:
                        value = self.board[i, j]
                        if value != 0:
                            cell.configure(text=str(value))
                            if (i, j) in self.original_numbers:
                                cell.configure(
                                    fg='black',
                                    font=('Helvetica', 22, 'bold'),
                                    bg='white'
                                )
                            else:
                                cell.configure(
                                    fg='#2196F3',
                                    font=('Helvetica', 22),
                                    bg='white'
                                )
                        else:
                            cell.configure(text='', bg='white')
                    except Exception as e:
                        print(f"Error updating cell ({i}, {j}): {str(e)}")
                        continue
        except Exception as e:
            print(f"Error in update_board: {str(e)}")
            messagebox.showerror("Error", "An error occurred while updating the board. Please restart the game.")

    def check_solution(self):
        try:
            if not hasattr(self, 'board') or not hasattr(self, 'solution'):
                messagebox.showerror("Error", "Game state is invalid. Please restart the game.")
                return
                
            if np.array_equal(self.board, self.solution):
                messagebox.showinfo("Correct!", "Your solution is correct!")
            else:
                messagebox.showinfo("Incorrect", "Your solution is incorrect. Keep trying!")
        except Exception as e:
            print(f"Error in check_solution: {str(e)}")
            messagebox.showerror("Error", "An error occurred while checking the solution.")

    def solve_puzzle(self):
        self.board = self.solution.copy()
        self.update_board()
        messagebox.showinfo("Solved", "The puzzle has been solved!")

    def save_game(self):
        save_data = {
            'board': self.board.tolist(),
            'solution': self.solution.tolist(),
            'original_numbers': list(self.original_numbers),
            'mistakes': self.mistakes,
            **self.game_data
        }
        self.main_menu.save_game(save_data)
        messagebox.showinfo("Saved", "Game saved successfully!") 