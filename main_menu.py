import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import math
from sudoku_backtracking import SudokuGame

class MainMenu:
    def __init__(self):
        print("Initializing MainMenu...")
        self.root = tk.Tk()
        self.root.title("Sudoku Master")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a2a3a')
        self.root.resizable(False, False)
        
        # Make sure window stays on top initially
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        
        print("Setting up theme...")
        # Animated gradient background using Canvas
        self.bg_canvas = tk.Canvas(self.root, width=900, height=700, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.gradient_colors = [(13, 71, 161), (33, 150, 243), (21, 101, 192), (2, 119, 189)]
        self.gradient_phase = 0
        self.animate_gradient()
        
        # Theme settings
        self.is_dark_mode = True
        self.theme_colors = {
            'dark': {
                'bg': '#1a2a3a',
                'fg': 'white',
                'button_bg': '#2196F3',
                'button_fg': 'white',
                'frame_bg': '#2a3a4a',
                'text_bg': '#1a2a3a',
                'hover_bg': '#1976D2',
                'title_bg': '#0d47a1',
                'title_fg': 'white',
                'border_color': '#0d47a1'
            },
            'light': {
                'bg': '#f0f0f0',
                'fg': 'black',
                'button_bg': '#1976D2',
                'button_fg': 'white',
                'frame_bg': '#e0e0e0',
                'text_bg': '#f0f0f0',
                'hover_bg': '#1565C0',
                'title_bg': '#0d47a1',
                'title_fg': 'white',
                'border_color': '#0d47a1'
            }
        }
        
        print("Loading game settings...")
        # Game settings
        self.difficulty = 'Medium'
        self.saved_games = []
        self.load_saved_games()
        
        print("Creating widgets...")
        self.create_widgets()
        self.apply_theme()
        
        print("Centering window...")
        # Center the window
        self.center_window()
        self.fade_in_widgets()
        print("MainMenu initialization complete!")

    def animate_gradient(self):
        # Animate a vertical gradient by cycling colors
        self.bg_canvas.delete("gradient")
        h = 700
        steps = 40
        for i in range(steps):
            phase = (self.gradient_phase + i/steps) % 1.0
            color = self.get_gradient_color(phase)
            self.bg_canvas.create_rectangle(0, i*h//steps, 900, (i+1)*h//steps, fill=color, outline="", tags="gradient")
        self.gradient_phase = (self.gradient_phase + 0.002) % 1.0
        self.root.after(30, self.animate_gradient)

    def get_gradient_color(self, phase):
        # Cycle through the gradient colors
        idx = int(phase * (len(self.gradient_colors)-1))
        c1 = self.gradient_colors[idx]
        c2 = self.gradient_colors[(idx+1)%len(self.gradient_colors)]
        t = (phase * (len(self.gradient_colors)-1)) % 1
        r = int(c1[0] + (c2[0]-c1[0])*t)
        g = int(c1[1] + (c2[1]-c1[1])*t)
        b = int(c1[2] + (c2[2]-c1[2])*t)
        return f'#{r:02x}{g:02x}{b:02x}'

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Main frame (transparent for fade-in)
        self.main_frame = tk.Frame(self.root, bg='#1a2a3a', highlightthickness=0)
        self.main_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Animated glowing title
        self.title_label = tk.Label(
            self.main_frame,
            text="SUDOKU MASTER",
            font=('Helvetica', 40, 'bold'),
            bg='#1a2a3a',
            fg='#ffffff',
            pady=20
        )
        self.title_label.pack()
        self.title_glow_phase = 0
        self.animate_title_glow()
        
        # Subtitle
        self.subtitle_label = tk.Label(
            self.main_frame,
            text="Challenge Your Mind",
            font=('Helvetica', 18),
            bg='#1a2a3a',
            fg='#e3f2fd',
            pady=5
        )
        self.subtitle_label.pack()
        
        # Buttons frame
        self.buttons_frame = tk.Frame(self.main_frame, bg='#1a2a3a')
        self.buttons_frame.pack(pady=40)
        
        # Create buttons with modern styling and animation
        self.menu_buttons = []
        buttons = [
            ("New Game", self.start_new_game),
            ("Load Game", self.show_load_game_menu),
            ("Options", self.show_options_menu),
            ("Exit", self.root.quit)
        ]
        
        for text, command in buttons:
            btn = tk.Label(
                self.buttons_frame,
                text=text,
                font=('Helvetica', 18, 'bold'),
                width=20,
                height=2,
                bg='#2196F3',
                fg='white',
                bd=0,
                relief=tk.FLAT,
                cursor='hand2',
                highlightthickness=0
            )
            btn.pack(pady=12)
            btn.bind('<Button-1>', lambda e, cmd=command: self.execute_command(cmd))
            btn.bind('<Enter>', lambda e, b=btn: self.animate_button_hover(b, True))
            btn.bind('<Leave>', lambda e, b=btn: self.animate_button_hover(b, False))
            self.menu_buttons.append(btn)

    def animate_title_glow(self):
        # Pulsing glow effect for the title
        phase = (math.sin(self.title_glow_phase) + 1) / 2
        color = f'#{int(255):02x}{int(255*phase):02x}{int(255*phase):02x}'
        self.title_label.configure(fg=color)
        self.title_glow_phase += 0.07
        self.root.after(40, self.animate_title_glow)

    def animate_button_hover(self, button, hover):
        # Animate button scaling and glow
        if hover:
            button.configure(bg='#1976D2', font=('Helvetica', 20, 'bold'))
        else:
            button.configure(bg='#2196F3', font=('Helvetica', 18, 'bold'))

    def fade_in_widgets(self):
        # Fade in the main frame and its children
        for i, widget in enumerate([self.title_label, self.subtitle_label] + self.menu_buttons):
            self.root.after(i*120, lambda w=widget: w.configure(fg=w.cget('fg')))

    def show_options_menu(self):
        options_window = tk.Toplevel(self.root)
        options_window.title("Options")
        options_window.geometry("400x300")
        options_window.configure(bg=self.theme_colors['dark']['bg'])
        options_window.resizable(False, False)
        
        # Center the options window
        options_window.update_idletasks()
        width = options_window.winfo_width()
        height = options_window.winfo_height()
        x = (options_window.winfo_screenwidth() // 2) - (width // 2)
        y = (options_window.winfo_screenheight() // 2) - (height // 2)
        options_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Theme selection
        theme_frame = tk.Frame(options_window, bg=self.theme_colors['dark']['bg'])
        theme_frame.pack(pady=20)
        
        theme_label = tk.Label(
            theme_frame,
            text="Theme:",
            font=('Arial', 14),
            bg=self.theme_colors['dark']['bg'],
            fg=self.theme_colors['dark']['fg']
        )
        theme_label.pack(side=tk.LEFT, padx=10)
        
        theme_var = tk.StringVar(value="Dark" if self.is_dark_mode else "Light")
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=theme_var,
            values=["Dark", "Light"],
            state="readonly",
            width=10
        )
        theme_combo.pack(side=tk.LEFT, padx=10)
        
        # Difficulty selection
        diff_frame = tk.Frame(options_window, bg=self.theme_colors['dark']['bg'])
        diff_frame.pack(pady=20)
        
        diff_label = tk.Label(
            diff_frame,
            text="Difficulty:",
            font=('Arial', 14),
            bg=self.theme_colors['dark']['bg'],
            fg=self.theme_colors['dark']['fg']
        )
        diff_label.pack(side=tk.LEFT, padx=10)
        
        diff_var = tk.StringVar(value=self.difficulty)
        diff_combo = ttk.Combobox(
            diff_frame,
            textvariable=diff_var,
            values=["Easy", "Medium", "Hard"],
            state="readonly",
            width=10
        )
        diff_combo.pack(side=tk.LEFT, padx=10)
        
        # Save button with hover effect
        def save_options():
            self.is_dark_mode = theme_var.get() == "Dark"
            self.difficulty = diff_var.get()
            self.apply_theme()
            options_window.destroy()
        
        save_btn = tk.Button(
            options_window,
            text="Save",
            font=('Arial', 14),
            command=save_options,
            bg=self.theme_colors['dark']['button_bg'],
            fg=self.theme_colors['dark']['button_fg'],
            activebackground=self.theme_colors['dark']['hover_bg'],
            relief=tk.RAISED,
            borderwidth=2
        )
        save_btn.pack(pady=20)
        
        # Add hover effect to save button
        save_btn.bind('<Enter>', lambda e: self.animate_button_hover(save_btn, True))
        save_btn.bind('<Leave>', lambda e: self.animate_button_hover(save_btn, False))

    def show_load_game_menu(self):
        if not self.saved_games:
            messagebox.showinfo("No Saved Games", "No saved games found!")
            return
            
        load_window = tk.Toplevel(self.root)
        load_window.title("Load Game")
        load_window.geometry("600x400")
        load_window.configure(bg=self.theme_colors['dark']['bg'])
        load_window.resizable(False, False)
        
        # Center the load window
        load_window.update_idletasks()
        width = load_window.winfo_width()
        height = load_window.winfo_height()
        x = (load_window.winfo_screenwidth() // 2) - (width // 2)
        y = (load_window.winfo_screenheight() // 2) - (height // 2)
        load_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Listbox for saved games
        listbox = tk.Listbox(
            load_window,
            font=('Arial', 12),
            bg=self.theme_colors['dark']['frame_bg'],
            fg=self.theme_colors['dark']['fg'],
            selectbackground=self.theme_colors['dark']['button_bg'],
            selectforeground='white',
            activestyle='none'
        )
        listbox.pack(expand=True, fill="both", padx=20, pady=20)
        
        for game in self.saved_games:
            listbox.insert(tk.END, f"{game['timestamp']} - {game['difficulty']}")
        
        # Load button with hover effect
        def load_selected():
            selection = listbox.curselection()
            if selection:
                game_data = self.saved_games[selection[0]]
                self.start_game(game_data)
                load_window.destroy()
        
        load_btn = tk.Button(
            load_window,
            text="Load Selected Game",
            font=('Arial', 14),
            command=load_selected,
            bg=self.theme_colors['dark']['button_bg'],
            fg=self.theme_colors['dark']['button_fg'],
            activebackground=self.theme_colors['dark']['hover_bg'],
            relief=tk.RAISED,
            borderwidth=2
        )
        load_btn.pack(pady=10)
        
        # Add hover effect to load button
        load_btn.bind('<Enter>', lambda e: self.animate_button_hover(load_btn, True))
        load_btn.bind('<Leave>', lambda e: self.animate_button_hover(load_btn, False))

    def start_new_game(self):
        game_data = {
            'difficulty': self.difficulty,
            'timestamp': self.get_current_timestamp()
        }
        self.start_game(game_data)

    def start_game(self, game_data):
        try:
            print("Starting new game...")
            # Create and start game
            print("Creating game window...")
            game = SudokuGame(self.root, self, game_data)
            print("Game window created")
            
            # Make sure the game window stays on top
            game.window.lift()
            game.window.focus_force()
            
            # Wait for game window to close
            print("Waiting for game window...")
            game.window.wait_window()
            print("Game window closed")
            
        except Exception as e:
            print(f"Error starting game: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", "Failed to start the game. Please try again.")

    def load_saved_games(self):
        try:
            if os.path.exists('saved_games.json'):
                with open('saved_games.json', 'r') as f:
                    self.saved_games = json.load(f)
        except Exception as e:
            print(f"Error loading saved games: {e}")
            self.saved_games = []

    def save_game(self, game_data):
        try:
            self.saved_games.append(game_data)
            with open('saved_games.json', 'w') as f:
                json.dump(self.saved_games, f)
        except Exception as e:
            print(f"Error saving game: {e}")

    def get_current_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def apply_theme(self):
        theme = 'dark' if self.is_dark_mode else 'light'
        colors = self.theme_colors[theme]
        
        self.root.configure(bg=colors['bg'])
        self.main_frame.configure(bg=colors['bg'])
        self.title_label.configure(bg=colors['bg'], fg=colors['fg'])
        self.buttons_frame.configure(bg=colors['bg'])
        
        for btn in self.buttons_frame.winfo_children():
            btn.configure(bg=colors['button_bg'], fg=colors['button_fg'])

    def execute_command(self, command):
        try:
            command()
        except Exception as e:
            print(f"Error executing command: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", "An error occurred while executing the command.")

    def run(self):
        print("Starting main loop...")
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.root.mainloop()
        print("Main loop ended")

if __name__ == "__main__":
    print("Starting Sudoku Master...")
    menu = MainMenu()
    menu.run()
    print("Sudoku Master closed") 