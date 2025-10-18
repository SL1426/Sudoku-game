import tkinter as tk
from tkinter import messagebox

class TestWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Window")
        self.root.geometry("400x300")
        
        # Create a button to open a new window
        self.button = tk.Button(
            self.root,
            text="Open New Window",
            command=self.open_new_window
        )
        self.button.pack(pady=20)
        
        # Make sure window is visible
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        
    def open_new_window(self):
        # Create a new window
        new_window = tk.Toplevel(self.root)
        new_window.title("New Window")
        new_window.geometry("300x200")
        
        # Add some content
        label = tk.Label(new_window, text="This is a new window!")
        label.pack(pady=20)
        
        # Make sure new window is visible
        new_window.deiconify()
        new_window.lift()
        new_window.focus_force()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = TestWindow()
    app.run() 