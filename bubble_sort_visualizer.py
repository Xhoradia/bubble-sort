"""Bubble Sort Visualizer

Dieses Modul stellt eine kleine tkinter-Anwendung zur Verfügung, die den Bubble
Sort Algorithmus Schritt für Schritt animiert. Die Implementierung ist
absichtlich ausführlich kommentiert und verwendet sprechende Variablennamen, um
den Lerncharakter der Anwendung zu unterstreichen.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Generator, Iterable, List, Optional, Set, Tuple


class BubbleSortVisualizer:
    """GUI-Anwendung zur Visualisierung des Bubble Sort Algorithmus."""

    # Farbdefinitionen für die unterschiedlichen Zustände eines Balkens
    DEFAULT_COLOR = "#4a90e2"  # Ausgangszustand
    COMPARE_COLOR = "#f5d76e"  # Vergleiche (gelb)
    SWAP_COLOR = "#f85f5f"  # Vertauschung (rot)
    SORTED_COLOR = "#2ecc71"  # Sortiert (grün)

    BAR_PADDING = 40  # Abstand links und rechts im Canvas

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Bubble Sort Visualizer")

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
        self.input_entry = tk.Entry(self.root, width=50)

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
        self.step_generator: Optional[
            Generator[Tuple[str, int, Optional[int]], None, None]
        ] = None
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
        self.input_entry.pack()
        self.canvas.pack(pady=20)

        self.start_button.pack(side=tk.LEFT, padx=5)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        self.button_frame.pack(pady=10)

    # ------------------------------------------------------------------
    # Bedienlogik
    # ------------------------------------------------------------------
    def start_sort(self) -> None:
        """Startet die Bubble-Sort-Animation nach Eingabeprüfung."""

        if self.is_running:
            return  # Mehrfachstarts vermeiden

        numbers = self._parse_numbers(self.input_entry.get())
        if numbers is None:
            return

        self.current_data = list(numbers)
        self.sorted_indices.clear()
        self._create_bars(self.current_data)

        self.step_generator = self._bubble_sort_steps(self.current_data)
        self.is_running = True
        self.is_paused = False
        self.pause_button.config(state=tk.NORMAL, text="Pause")
        self.start_button.config(state=tk.DISABLED)

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
                # Falls der geplante Aufruf bereits ausgeführt wurde, ignorieren wir den Fehler.
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

        self.input_entry.delete(0, tk.END)

        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="Pause")

    # ------------------------------------------------------------------
    # Datenverarbeitung
    # ------------------------------------------------------------------
    def _parse_numbers(self, text: str) -> Optional[List[int]]:
        """Überführt die Benutzereingabe in eine Liste von fünf ganzen Zahlen."""

        raw_values = [part.strip() for part in text.replace(";", ",").split(",") if part.strip()]

        if len(raw_values) != 5:
            messagebox.showerror(
                "Eingabefehler",
                "Bitte geben Sie genau fünf Zahlen ein, getrennt durch Kommas.",
            )
            return None

        numbers: List[int] = []
        for value in raw_values:
            try:
                numbers.append(int(value))
            except ValueError:
                messagebox.showerror(
                    "Eingabefehler",
                    f"'{value}' ist keine gültige ganze Zahl.",
                )
                return None

        return numbers

    def _bubble_sort_steps(
        self, numbers: Iterable[int]
    ) -> Generator[Tuple[str, int, Optional[int]], None, None]:
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
                # Das Feld ist bereits sortiert: restliche Elemente markieren.
                for remaining in range(n - i - 1):
                    yield ("mark_sorted", remaining, None)
                break

    # ------------------------------------------------------------------
    # Animationslogik
    # ------------------------------------------------------------------
    def perform_next_step(self) -> None:
        """Führt den nächsten Animationsschritt aus."""

        if self.after_id is not None:
            # Die zuvor geplante "after"-ID ist mit diesem Aufruf abgearbeitet.
            self.after_id = None

        if not self.is_running or self.is_paused or self.step_generator is None:
            return

        try:
            action, first_index, second_index = next(self.step_generator)
        except StopIteration:
            self._finish_sorting()
            return

        if action == "compare" and second_index is not None:
            self._highlight_compare(first_index, second_index)
        elif action == "swap" and second_index is not None:
            self._highlight_swap(first_index, second_index)
        elif action == "revert" and second_index is not None:
            self._reset_colors(first_index, second_index)
        elif action == "mark_sorted":
            self._mark_sorted(first_index)

        self.after_id = self.root.after(self.animation_speed_ms, self.perform_next_step)

    def _finish_sorting(self) -> None:
        """Wird aufgerufen, wenn alle Schritte abgearbeitet wurden."""

        self.is_running = False
        self.is_paused = False
        self.after_id = None
        self.step_generator = None
        self.pause_button.config(state=tk.DISABLED, text="Pause")
        self.start_button.config(state=tk.NORMAL)

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

    def _reset_colors(self, i: int, j: int) -> None:
        """Setzt die Balkenfarben nach einem Vergleich/Tausch zurück."""

        if i not in self.sorted_indices:
            self._set_bar_color(i, self.DEFAULT_COLOR)
        if j not in self.sorted_indices:
            self._set_bar_color(j, self.DEFAULT_COLOR)

    def _mark_sorted(self, index: int) -> None:
        """Hebt einen Balken als endgültig sortiert hervor."""

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

        # Eine dünne Linie markiert die Basis aller Balken.
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
    BubbleSortVisualizer().run()
