"""Sorting Visualizer

Dieses Modul stellt eine tkinter-Anwendung zur Verfügung, die mehrere
Sortierverfahren Schritt für Schritt animiert. Die Anwendung richtet sich
an Lernende und legt Wert auf gut nachvollziehbare Visualisierungen,
kommentierten Code sowie konsistente Farbcodes für Vergleiche, Swaps und
sortierte Werte.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Dict, Generator, Iterable, List, Optional, Set, Tuple

Step = Tuple[str, int, Optional[int]]
StepGenerator = Generator[Step, None, None]


class SortingVisualizer:
    """GUI-Anwendung zur Visualisierung verschiedener Sortieralgorithmen."""

    DEFAULT_COLOR = "#4a90e2"  # Ausgangszustand
    COMPARE_COLOR = "#f5d76e"  # Vergleiche (gelb)
    SWAP_COLOR = "#f85f5f"  # Vertauschung/Schreiben (rot)
    SORTED_COLOR = "#2ecc71"  # Sortiert (grün)

    BAR_PADDING = 40  # Abstand links und rechts im Canvas

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Sorting Visualizer")

        # Der Canvas stellt die Balkendiagramm-Darstellung zur Verfügung.
        self.canvas_width = 600
        self.canvas_height = 320
        self.canvas = tk.Canvas(
            self.root,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="white",
            highlightthickness=0,
        )

        # GUI-Elemente für die Benutzereingabe
        self.input_label = tk.Label(
            self.root,
            text="Bitte geben Sie fünf Zahlen ein (z. B. 8, 12, 88, 75, 106):",
        )
        self.input_frame = tk.Frame(self.root)
        self.input_entries: List[tk.Entry] = []

        # Algorithmus-Auswahl
        self.algorithm_options: List[
            Tuple[str, str, Callable[[Iterable[int]], StepGenerator]]
        ] = [
            ("bubble", "Bubble Sort", self._bubble_sort_steps),
            ("selection", "Selection Sort", self._selection_sort_steps),
            ("insertion", "Insertion Sort", self._insertion_sort_steps),
            ("merge", "Merge Sort", self._merge_sort_steps),
            ("quick", "Quick Sort", self._quick_sort_steps),
            ("heap", "Heap Sort", self._heap_sort_steps),
        ]
        self.algorithm_generators: Dict[str, Callable[[Iterable[int]], StepGenerator]] = {
            key: generator for key, _, generator in self.algorithm_options
        }
        self.algorithm_var = tk.StringVar(value=self.algorithm_options[0][0])
        self.algorithm_buttons: List[tk.Radiobutton] = []

        # Steuerungs-Buttons für die Animation
        self.button_frame = tk.Frame(self.root)
        self.start_button = tk.Button(
            self.button_frame,
            text="Start",
            command=self.start_sort,
        )
        self.pause_button = tk.Button(
            self.button_frame,
            text="Pause",
            state=tk.DISABLED,
            command=self.pause_or_resume,
        )
        self.reset_button = tk.Button(
            self.button_frame,
            text="Reset",
            command=self.reset,
        )

        # Variablen zur Steuerung der Animation
        self.animation_speed_ms = 800  # Zeitabstand zwischen den Schritten
        self.speed_var = tk.IntVar(value=self.animation_speed_ms)
        self.step_generator: Optional[StepGenerator] = None
        self.after_id: Optional[str] = None
        self.is_running = False
        self.is_paused = False

        # Datenstrukturen für die Visualisierung
        self.current_data: List[int] = []
        self.sorted_indices: Set[int] = set()
        self.bar_rects: List[int] = []
        self.bar_texts: List[int] = []
        self.value_min = 0
        self.value_max = 0
        self.value_range = 1
        self.slot_width = 0.0
        self.bar_width = 0.0
        self.base_line_y = self.canvas_height - 40

        self._build_layout()

    # ------------------------------------------------------------------
    # GUI-Aufbau
    # ------------------------------------------------------------------
    def _build_layout(self) -> None:
        """Platziert alle Widgets im Fenster."""

        self.input_label.pack(pady=(15, 5))

        self.input_frame.pack(pady=(0, 10))
        for column in range(5):
            entry = tk.Entry(self.input_frame, width=6, justify="center")
            entry.grid(row=0, column=column, padx=5)
            self.input_entries.append(entry)

        self.canvas.pack(pady=20)

        self._build_legend()
        self._build_algorithm_selector()
        self._build_speed_controls()

        self.start_button.pack(side=tk.LEFT, padx=5)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        self.button_frame.pack(pady=10)

        if self.input_entries:
            self.input_entries[0].focus_set()

    def _build_legend(self) -> None:
        """Erzeugt eine Legende für die verwendeten Balkenfarben."""

        legend_items = [
            (self.DEFAULT_COLOR, "Unsortiert"),
            (self.COMPARE_COLOR, "Vergleich"),
            (self.SWAP_COLOR, "Tausch / Schreiben"),
            (self.SORTED_COLOR, "Sortiert"),
        ]

        legend_frame = tk.Frame(self.root)
        legend_frame.pack(pady=(0, 10))

        for color, description in legend_items:
            item_frame = tk.Frame(legend_frame)
            item_frame.pack(side=tk.LEFT, padx=10)

            color_box = tk.Label(
                item_frame,
                bg=color,
                width=2,
                height=1,
                relief=tk.SOLID,
                bd=1,
            )
            color_box.pack(side=tk.LEFT, padx=(0, 4))

            text_label = tk.Label(item_frame, text=description)
            text_label.pack(side=tk.LEFT)

    def _build_algorithm_selector(self) -> None:
        """Legt die Radiobuttons für die Algorithmuswahl an."""

        options_frame = tk.LabelFrame(self.root, text="Sortierverfahren")
        options_frame.pack(pady=(0, 10), padx=20, fill=tk.X)

        for index, (key, label, _) in enumerate(self.algorithm_options):
            button = tk.Radiobutton(
                options_frame,
                text=label,
                variable=self.algorithm_var,
                value=key,
                anchor="w",
            )
            row = index // 2
            column = index % 2
            button.grid(row=row, column=column, sticky="w", padx=10, pady=2)
            self.algorithm_buttons.append(button)

    def _build_speed_controls(self) -> None:
        """Erzeugt den Geschwindigkeitsregler."""

        speed_frame = tk.Frame(self.root)
        speed_frame.pack(pady=(0, 10))

        speed_label = tk.Label(speed_frame, text="Geschwindigkeit (ms pro Schritt)")
        speed_label.pack()

        speed_scale = tk.Scale(
            speed_frame,
            from_=100,
            to=1500,
            resolution=50,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            command=self._update_speed,
            length=260,
        )
        speed_scale.pack()

    # ------------------------------------------------------------------
    # Bedienlogik
    # ------------------------------------------------------------------
    def start_sort(self) -> None:
        """Startet die Animation für das gewählte Sortierverfahren."""

        if self.is_running:
            return  # Mehrfachstarts vermeiden

        numbers = self._parse_numbers()
        if numbers is None:
            return

        self.current_data = list(numbers)
        self.sorted_indices.clear()
        self._create_bars(self.current_data)

        algorithm_key = self.algorithm_var.get()
        generator_func = self.algorithm_generators.get(algorithm_key)
        if generator_func is None:
            messagebox.showerror(
                "Algorithmusfehler",
                "Das gewählte Sortierverfahren ist nicht verfügbar.",
            )
            return

        self.step_generator = generator_func(self.current_data)
        self.is_running = True
        self.is_paused = False
        self.animation_speed_ms = max(10, int(self.speed_var.get()))
        self.pause_button.config(state=tk.NORMAL, text="Pause")
        self.start_button.config(state=tk.DISABLED)
        self._set_algorithm_buttons_state(tk.DISABLED)

        self.perform_next_step()

    def pause_or_resume(self) -> None:
        """Pausiert oder setzt die Animation fort."""

        if not self.is_running:
            return

        if self.is_paused:
            self.is_paused = False
            self.pause_button.config(text="Pause")
            self.perform_next_step()
        else:
            self.is_paused = True
            self.pause_button.config(text="Fortsetzen")
            if self.after_id is not None:
                try:
                    self.root.after_cancel(self.after_id)
                except tk.TclError:
                    pass
                self.after_id = None

    def reset(self) -> None:
        """Setzt die Anwendung in den Ausgangszustand zurück."""

        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None

        self.is_running = False
        self.is_paused = False
        self.step_generator = None
        self.current_data = []
        self.sorted_indices.clear()
        self.value_min = 0
        self.value_max = 0
        self.value_range = 1
        self.slot_width = 0.0
        self.bar_width = 0.0

        self.canvas.delete("all")
        self.bar_rects.clear()
        self.bar_texts.clear()

        for entry in self.input_entries:
            entry.delete(0, tk.END)

        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="Pause")
        self._set_algorithm_buttons_state(tk.NORMAL)

    def _set_algorithm_buttons_state(self, state: str) -> None:
        """Aktiviert oder deaktiviert alle Radiobuttons."""

        for button in self.algorithm_buttons:
            button.config(state=state)

    def _update_speed(self, value: str) -> None:
        """Aktualisiert die Animationsgeschwindigkeit anhand des Sliders."""

        try:
            self.animation_speed_ms = max(10, int(float(value)))
        except (TypeError, ValueError):
            # Ungültige Eingaben werden ignoriert.
            pass

    # ------------------------------------------------------------------
    # Datenverarbeitung
    # ------------------------------------------------------------------
    def _parse_numbers(self) -> Optional[List[int]]:
        """Liest fünf einzelne Eingabefelder aus und wandelt sie in ganze Zahlen um."""

        raw_values = []
        for index, entry in enumerate(self.input_entries, start=1):
            value = entry.get().strip()
            if not value:
                messagebox.showerror(
                    "Eingabefehler",
                    "Bitte füllen Sie alle fünf Zahlenfelder aus.",
                )
                entry.focus_set()
                return None
            raw_values.append((index, value))

        numbers: List[int] = []
        for index, value in raw_values:
            try:
                numbers.append(int(value))
            except ValueError:
                messagebox.showerror(
                    "Eingabefehler",
                    f"Feld {index}: '{value}' ist keine gültige ganze Zahl.",
                )
                self.input_entries[index - 1].focus_set()
                return None

        return numbers

    def _bubble_sort_steps(self, numbers: Iterable[int]) -> StepGenerator:
        """Erzeugt Schritt-für-Schritt-Anweisungen für den Bubble Sort."""

        data = list(numbers)
        n = len(data)

        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                yield ("compare", j, j + 1)
                if data[j] > data[j + 1]:
                    data[j], data[j + 1] = data[j + 1], data[j]
                    swapped = True
                    yield ("swap", j, j + 1)
                yield ("revert", j, j + 1)
            yield ("mark_sorted", n - i - 1, None)
            if not swapped:
                for remaining in range(n - i - 1):
                    yield ("mark_sorted", remaining, None)
                break

    def _selection_sort_steps(self, numbers: Iterable[int]) -> StepGenerator:
        """Erzeugt Schrittanweisungen für Selection Sort."""

        data = list(numbers)
        n = len(data)

        for i in range(n):
            min_index = i
            for j in range(i + 1, n):
                previous_min = min_index
                yield ("compare", min_index, j)
                if data[j] < data[min_index]:
                    min_index = j
                yield ("revert", previous_min, j)
            if min_index != i:
                data[i], data[min_index] = data[min_index], data[i]
                yield ("swap", i, min_index)
                yield ("revert", i, min_index)
            yield ("mark_sorted", i, None)

    def _insertion_sort_steps(self, numbers: Iterable[int]) -> StepGenerator:
        """Erzeugt Schrittanweisungen für Insertion Sort."""

        data = list(numbers)
        n = len(data)

        for i in range(1, n):
            j = i
            while j > 0:
                yield ("compare", j - 1, j)
                if data[j - 1] > data[j]:
                    data[j - 1], data[j] = data[j], data[j - 1]
                    yield ("swap", j - 1, j)
                    yield ("revert", j - 1, j)
                    j -= 1
                else:
                    yield ("revert", j - 1, j)
                    break
            for sorted_index in range(i + 1):
                yield ("mark_sorted", sorted_index, None)
        if n:
            yield ("mark_sorted", n - 1, None)

    def _merge_sort_steps(self, numbers: Iterable[int]) -> StepGenerator:
        """Erzeugt Schrittanweisungen für Merge Sort."""

        data = list(numbers)
        n = len(data)

        def merge_sort(left: int, right: int) -> StepGenerator:
            if left >= right:
                return
            mid = (left + right) // 2
            yield from merge_sort(left, mid)
            yield from merge_sort(mid + 1, right)
            yield from merge(left, mid, right)

        def merge(left: int, mid: int, right: int) -> StepGenerator:
            left_part = data[left : mid + 1]
            right_part = data[mid + 1 : right + 1]
            i = 0
            j = 0
            k = left

            while i < len(left_part) and j < len(right_part):
                left_index = left + i
                right_index = mid + 1 + j
                yield ("compare", left_index, right_index)
                if left_part[i] <= right_part[j]:
                    yield ("revert", left_index, right_index)
                    value = left_part[i]
                    data[k] = value
                    yield ("overwrite", k, value)
                    yield ("revert", k, k)
                    i += 1
                else:
                    yield ("revert", left_index, right_index)
                    value = right_part[j]
                    data[k] = value
                    yield ("overwrite", k, value)
                    yield ("revert", k, k)
                    j += 1
                k += 1

            while i < len(left_part):
                value = left_part[i]
                data[k] = value
                yield ("overwrite", k, value)
                yield ("revert", k, k)
                i += 1
                k += 1

            while j < len(right_part):
                value = right_part[j]
                data[k] = value
                yield ("overwrite", k, value)
                yield ("revert", k, k)
                j += 1
                k += 1

        if n > 0:
            yield from merge_sort(0, n - 1)
            for index in range(n):
                yield ("mark_sorted", index, None)

    def _quick_sort_steps(self, numbers: Iterable[int]) -> StepGenerator:
        """Erzeugt Schrittanweisungen für Quick Sort (Lomuto-Partition)."""

        data = list(numbers)
        n = len(data)

        def quick_sort(low: int, high: int) -> StepGenerator:
            if low >= high:
                if low == high:
                    yield ("mark_sorted", low, None)
                return

            pivot_pos = high
            pivot_value = data[pivot_pos]
            i = low
            for j in range(low, high):
                yield ("compare", j, pivot_pos)
                if data[j] <= pivot_value:
                    if i != j:
                        data[i], data[j] = data[j], data[i]
                        yield ("swap", i, j)
                        yield ("revert", i, j)
                    i += 1
                yield ("revert", j, pivot_pos)

            data[i], data[pivot_pos] = data[pivot_pos], data[i]
            yield ("swap", i, pivot_pos)
            yield ("revert", i, pivot_pos)
            yield ("mark_sorted", i, None)

            yield from quick_sort(low, i - 1)
            yield from quick_sort(i + 1, high)

        if n > 0:
            yield from quick_sort(0, n - 1)
            for index in range(n):
                yield ("mark_sorted", index, None)

    def _heap_sort_steps(self, numbers: Iterable[int]) -> StepGenerator:
        """Erzeugt Schrittanweisungen für Heap Sort."""

        data = list(numbers)
        n = len(data)

        def heapify(size: int, root: int) -> StepGenerator:
            largest = root
            left = 2 * root + 1
            right = 2 * root + 2

            if left < size:
                yield ("compare", root, left)
                if data[left] > data[largest]:
                    largest = left
                yield ("revert", root, left)

            if right < size:
                compare_index = largest
                yield ("compare", compare_index, right)
                if data[right] > data[largest]:
                    largest = right
                yield ("revert", compare_index, right)

            if largest != root:
                data[root], data[largest] = data[largest], data[root]
                yield ("swap", root, largest)
                yield ("revert", root, largest)
                yield from heapify(size, largest)

        for index in range(n // 2 - 1, -1, -1):
            yield from heapify(n, index)

        for end in range(n - 1, 0, -1):
            data[0], data[end] = data[end], data[0]
            yield ("swap", 0, end)
            yield ("mark_sorted", end, None)
            yield ("revert", 0, end)
            yield from heapify(end, 0)

        if n > 0:
            yield ("mark_sorted", 0, None)

    # ------------------------------------------------------------------
    # Animationslogik
    # ------------------------------------------------------------------
    def perform_next_step(self) -> None:
        """Führt den nächsten Animationsschritt aus."""

        if self.after_id is not None:
            self.after_id = None

        if not self.is_running or self.is_paused or self.step_generator is None:
            return

        try:
            action, first_index, second_value = next(self.step_generator)
        except StopIteration:
            self._finish_sorting()
            return

        if action == "compare" and second_value is not None:
            self._highlight_compare(first_index, second_value)
        elif action == "swap" and second_value is not None:
            self._highlight_swap(first_index, second_value)
        elif action == "overwrite" and second_value is not None:
            self._apply_overwrite(first_index, second_value)
        elif action == "revert" and second_value is not None:
            self._reset_colors(first_index, second_value)
        elif action == "mark_sorted":
            self._mark_sorted(first_index)

        delay = max(10, int(self.animation_speed_ms))
        self.after_id = self.root.after(delay, self.perform_next_step)

    def _finish_sorting(self) -> None:
        """Wird aufgerufen, wenn alle Schritte abgearbeitet wurden."""

        self.is_running = False
        self.is_paused = False
        self.after_id = None
        self.step_generator = None
        self.pause_button.config(state=tk.DISABLED, text="Pause")
        self.start_button.config(state=tk.NORMAL)
        for index in range(len(self.current_data)):
            if index not in self.sorted_indices:
                self._mark_sorted(index)
        self._set_algorithm_buttons_state(tk.NORMAL)

    def _highlight_compare(self, i: int, j: int) -> None:
        """Setzt die Farben der verglichenen Balken auf gelb."""

        self._set_bar_color(i, self.COMPARE_COLOR)
        self._set_bar_color(j, self.COMPARE_COLOR)

    def _highlight_swap(self, i: int, j: int) -> None:
        """Zeigt einen Swap (rot) an und aktualisiert die Balkenhöhen."""

        self.current_data[i], self.current_data[j] = (
            self.current_data[j],
            self.current_data[i],
        )
        self._update_bar_height(i)
        self._update_bar_height(j)

        self._set_bar_color(i, self.SWAP_COLOR)
        self._set_bar_color(j, self.SWAP_COLOR)

    def _apply_overwrite(self, index: int, value: int) -> None:
        """Schreibt einen neuen Wert an eine Position und hebt ihn hervor."""

        self.current_data[index] = value
        self._update_bar_height(index)
        self._set_bar_color(index, self.SWAP_COLOR)

    def _reset_colors(self, i: int, j: int) -> None:
        """Setzt die Balkenfarben nach einem Vergleich/Tausch zurück."""

        if i not in self.sorted_indices:
            self._set_bar_color(i, self.DEFAULT_COLOR)
        if j not in self.sorted_indices:
            self._set_bar_color(j, self.DEFAULT_COLOR)

    def _mark_sorted(self, index: int) -> None:
        """Hebt einen Balken als endgültig sortiert hervor."""

        if 0 <= index < len(self.current_data):
            self.sorted_indices.add(index)
            self._set_bar_color(index, self.SORTED_COLOR)

    # ------------------------------------------------------------------
    # Zeichenhilfsfunktionen
    # ------------------------------------------------------------------
    def _create_bars(self, values: List[int]) -> None:
        """Erzeugt die Balken entsprechend der aktuellen Daten."""

        self.canvas.delete("all")
        self.bar_rects.clear()
        self.bar_texts.clear()

        if not values:
            return

        self.value_min = min(values)
        self.value_max = max(values)
        self.value_range = max(self.value_max - self.value_min, 1)

        self.slot_width = (self.canvas_width - 2 * self.BAR_PADDING) / len(values)
        self.bar_width = self.slot_width * 0.7

        self.canvas.create_line(
            self.BAR_PADDING / 2,
            self.base_line_y,
            self.canvas_width - self.BAR_PADDING / 2,
            self.base_line_y,
            fill="#d0d0d0",
        )

        for index, value in enumerate(values):
            x_center = self.BAR_PADDING + index * self.slot_width + self.slot_width / 2
            x0 = x_center - self.bar_width / 2
            x1 = x_center + self.bar_width / 2
            bar_height = self._calculate_bar_height(value)
            y0 = self.base_line_y - bar_height
            y1 = self.base_line_y

            rect = self.canvas.create_rectangle(
                x0,
                y0,
                x1,
                y1,
                fill=self.DEFAULT_COLOR,
                outline="",
            )
            self.bar_rects.append(rect)

            label_y = max(y0 - 12, 15)
            text = self.canvas.create_text(
                x_center,
                label_y,
                text=str(value),
                font=("Helvetica", 12, "bold"),
            )
            self.bar_texts.append(text)

    def _update_bar_height(self, index: int) -> None:
        """Passt die Höhe eines Balkens an die geänderten Daten an."""

        if not self.current_data:
            return

        value = self.current_data[index]

        x_center = self.BAR_PADDING + index * self.slot_width + self.slot_width / 2
        x0 = x_center - self.bar_width / 2
        x1 = x_center + self.bar_width / 2

        bar_height = self._calculate_bar_height(value)
        y0 = self.base_line_y - bar_height
        y1 = self.base_line_y

        self.canvas.coords(self.bar_rects[index], x0, y0, x1, y1)
        self.canvas.itemconfig(self.bar_texts[index], text=str(value))
        label_y = max(y0 - 12, 15)
        self.canvas.coords(self.bar_texts[index], x_center, label_y)

    def _set_bar_color(self, index: int, color: str) -> None:
        """Aktualisiert die Farbe eines Balkens."""

        if 0 <= index < len(self.bar_rects):
            self.canvas.itemconfig(self.bar_rects[index], fill=color)

    def _calculate_bar_height(self, value: int) -> float:
        """Berechnet die visuelle Höhe eines Balkens für einen gegebenen Wert."""

        max_height = self.canvas_height - 120
        max_height = max(max_height, 40)
        base_height = 20
        dynamic_height = max_height - base_height
        value_range = max(self.value_range, 1)
        normalized = (value - self.value_min) / value_range
        normalized = min(max(normalized, 0.0), 1.0)
        return base_height + normalized * dynamic_height

    # ------------------------------------------------------------------
    # Startpunkt der Anwendung
    # ------------------------------------------------------------------
    def run(self) -> None:
        """Startet die tkinter-Ereignisschleife."""

        self.root.mainloop()


if __name__ == "__main__":
    SortingVisualizer().run()
