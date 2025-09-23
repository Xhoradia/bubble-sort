AGENTS.md

Goal
This agent should develop and maintain a Python program that graphically visualizes and animates multiple sorting algorithms: Bubble Sort, Selection Sort, Insertion Sort, Merge Sort, Quick Sort, and Heap Sort. The project is designed for learning and demonstration purposes, helping beginners understand sorting algorithms step by step.

Context
- Language & Environment: Python 3.8+, standard library only (tkinter for GUI/animation)
- Input: 5 freely chosen numbers (also multi-digit, e.g., 8, 12, 88, 75, 106)
- Visualization: Bar chart in a Canvas, consistent color codes (Gray / Yellow / Red / Green)
- UI Controls: Start, Pause/Resume, Reset, Speed slider
- Algorithm Selection: Option buttons (radio buttons) for Bubble, Selection, Insertion, Merge, Quick, Heap
- Architecture: GUI separated from algorithm logic; each algorithm produces a step sequence (comparisons, swaps, markings) consumed by the visualizer

Agent Behavior
- Clear, well-structured, and commented code; use meaningful variable names
- Didactics: Explicitly model the steps of algorithms (events with type, indices, optional values/colors)
- Robustness: Validate input (exactly 5 integers), report errors via dialogs
- Consistency: Unified event and color semantics across all algorithms
- Performance: Animation using tkinter's after-callbacks with adjustable delay, no UI blocking
- Extensibility: New algorithms can be added as step generators without changing the renderer

Tasks
- Implement the six sorting algorithms as step generators (yielding comparison/swap/mark events)
- Build a GUI with input fields, option buttons for algorithm selection, control buttons, and a speed slider
- Create a renderer that translates events into Canvas updates (set colors, swap bar positions, mark as final)
- Ensure that pause/resume and reset correctly manage the animation state
- Perform manual tests for typical and edge cases
