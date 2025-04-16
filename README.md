# 🧩 Sudoku Solver using Backtracking in Python

This Python program solves a standard **9x9 Sudoku puzzle** using the **backtracking algorithm**. It includes input validation, a custom exception for error handling, and a user-friendly board display.

---

## 🔑 Key Components

### 1. Custom Exception
- **`InvalidSudokuBoard`**: A user-defined exception that is raised when the input Sudoku board is invalid (not 9x9 or contains values outside the range 0-9).

### 2. `Board` Class

- **`__init__`**  
  Initializes the board and validates it using the `is_valid_grid` method.

- **`is_valid_grid(grid)`**  
  Checks whether the grid is 9x9 and all cells contain integers from 0 to 9.

- **`is_valid(num, row, col)`**  
  Checks if placing a number in the given cell follows Sudoku rules:
  - Not repeated in the row
  - Not repeated in the column
  - Not repeated in the corresponding 3x3 box

- **`solve()`**  
  Uses **recursive backtracking** to find a valid solution.

- **`find_empty()`**  
  Finds the next empty cell (represented by 0).

- **`display()`**  
  Displays the board in a readable format, with `.` representing empty cells and lines separating 3x3 grids.

---

## 🧪 Main Functionality

- A sample Sudoku board (`sample_board`) is defined.
- The board is validated and displayed in its initial state.
- The `solve()` method attempts to solve the puzzle.
- If successful, the completed board is displayed.
- If no solution exists, an appropriate message is shown.

---

## 🎯 Purpose

This program demonstrates solving a Sudoku puzzle using Python and a classic algorithmic technique: **backtracking**. It’s an ideal example for:

- Practicing recursion
- Learning constraint satisfaction problems
- Exploring algorithmic thinking
