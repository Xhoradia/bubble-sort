"""Sorting Visualizer

Dieses Modul stellt eine tkinter-Anwendung zur Verfügung, die mehrere
Sortierverfahren Schritt für Schritt animiert. Die Anwendung richtet sich
an Lernende und legt Wert auf gut nachvollziehbare Visualisierungen,
kommentierten Code sowie konsistente Farbcodes für Vergleiche, Swaps und
sortierte Werte.
"""

from __future__ import annotations

import time
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Dict, Generator, Iterable, List, Optional, Set, Tuple

Step = Tuple[str, int, Optional[int]]
StepGenerator = Generator[Step, None, None]


class SortingVisualizer:
    """GUI-Anwendung zur Visualisierung verschiedener Sortieralgorithmen."""

    DEFAULT_COLOR = "#4a90e2"  # Ausgangszustand
    COMPARE_COLOR = "#f5d76e"  # Vergleiche (gelb)
    SWAP_COLOR = "#f85f5f"  # Vertauschung/Schreiben (rot)
    SORTED_COLOR = "#2ecc71"  # Sortiert (grün)

    DEFAULT_ANIMATION_DELAY_MS = 800
    TIMER_UPDATE_INTERVAL_MS = 20

    BAR_PADDING = 40  # Abstand links und rechts im Canvas

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Sorting Visualizer")

        self.content_frame = tk.Frame(self.root)
        self.left_frame = tk.Frame(self.content_frame)
        self.right_frame = tk.Frame(self.content_frame)

        # Der Canvas stellt die Balkendiagramm-Darstellung zur Verfügung.
        self.canvas_width = 600
        self.canvas_height = 320
        self.canvas = tk.Canvas(
            self.left_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="white",
            highlightthickness=0,
        )

        # GUI-Elemente für die Benutzereingabe
        self.input_label = tk.Label(
            self.left_frame,
            text="Bitte geben Sie fünf Zahlen ein (z. B. 8, 12, 88, 75, 106):",
        )
        self.input_frame = tk.Frame(self.left_frame)
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
        self.algorithm_labels: Dict[str, str] = {
            key: label for key, label, _ in self.algorithm_options
        }
        self.algorithm_information: Dict[str, Dict[str, object]] = {
            "bubble": {
                "description": (
                    "Vergleicht benachbarte Werte und vertauscht sie bei Bedarf; "
                    "größere Elemente \"blubbern\" nach oben."
                ),
                "advantages": [
                    "Sehr leicht zu verstehen und zu implementieren",
                    "Erkennt bereits sortierte Listen schnell dank Abbruchbedingung",
                ],
                "disadvantages": [
                    "Sehr ineffizient bei größeren Datensätzen (O(n²))",
                    "Viele unnötige Vergleiche und Vertauschungen",
                ],
            },
            "selection": {
                "description": (
                    "Sucht in jedem Durchlauf das kleinste verbleibende Element und setzt es an "
                    "die richtige Position."
                ),
                "advantages": [
                    "Wenig Speicherbedarf und deterministische Anzahl an Vertauschungen",
                    "Einfache Schritt-für-Schritt-Nachvollziehbarkeit",
                ],
                "disadvantages": [
                    "Benötigt viele Vergleiche (O(n²))",
                    "Reagiert nicht auf bereits teilweise sortierte Listen",
                ],
            },
            "insertion": {
                "description": (
                    "Fügt jedes neue Element an der passenden Stelle in den bereits sortierten "
                    "linken Teil ein."
                ),
                "advantages": [
                    "Sehr effizient für kleine oder fast sortierte Listen",
                    "Stabile Sortierung ohne zusätzliche Datenstrukturen",
                ],
                "disadvantages": [
                    "Quadratische Laufzeit im schlechtesten Fall",
                    "Viele Verschiebungen bei stark unsortierten Listen",
                ],
            },
            "merge": {
                "description": (
                    "Teilt die Liste rekursiv, sortiert die Hälften und fügt sie geordnet "
                    "wieder zusammen."
                ),
                "advantages": [
                    "Sehr gute Laufzeit O(n log n) auch im schlechtesten Fall",
                    "Stabile Sortierung mit klarer Divide-and-Conquer-Struktur",
                ],
                "disadvantages": [
                    "Benötigt zusätzlichen Speicher für Hilfsarrays",
                    "Komplexer zu implementieren als einfache Quadratalgorithmen",
                ],
            },
            "quick": {
                "description": (
                    "Wählt ein Pivot, partitioniert die Liste in kleinere und größere Werte und "
                    "sortiert die Teilbereiche rekursiv."
                ),
                "advantages": [
                    "Sehr schnell in der Praxis dank In-Place-Partitionierung",
                    "Gute Cache-Lokalität und geringe Hilfsspeichernutzung",
                ],
                "disadvantages": [
                    "Schlechtester Fall O(n²) bei ungünstiger Pivot-Wahl",
                    "Nicht stabil ohne zusätzliche Maßnahmen",
                ],
            },
            "heap": {
                "description": (
                    "Organisiert die Werte als Heap und entnimmt wiederholt das größte Element an "
                    "das Ende der Liste."
                ),
                "advantages": [
                    "Robuste Laufzeit O(n log n) unabhängig von der Eingabe",
                    "Sortiert In-Place mit konstantem zusätzlichen Speicher",
                ],
                "disadvantages": [
                    "Komplexere Datenstruktur als Ausgangspunkt",
                    "Nicht stabil und schwerer anschaulich zu verfolgen",
                ],
            },
        }
        self.algorithm_var = tk.StringVar(value=self.algorithm_options[0][0])
        self.algorithm_buttons: List[tk.Radiobutton] = []
        self.algorithm_info_title_var = tk.StringVar(value="")
        self.algorithm_info_title_label: Optional[tk.Label] = None
        self.algorithm_info_label: Optional[tk.Label] = None

        # Statistik-Elemente
        self.results_tree: Optional[ttk.Treeview] = None
        self.run_history: List[Tuple[int, str, float]] = []
        self.total_runs = 0
        self.active_algorithm_key: Optional[str] = None

        # Steuerungs-Buttons für die Animation
        self.button_frame = tk.Frame(self.left_frame)
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
        self.animation_speed_ms = self.DEFAULT_ANIMATION_DELAY_MS
        self.step_generator: Optional[StepGenerator] = None
        self.after_id: Optional[str] = None
        self.is_running = False
        self.is_paused = False
        self.elapsed_time_ms = 0.0
        self.timer_base_time: Optional[float] = None
        self.timer_after_id: Optional[str] = None
        self.timer_value_var = tk.StringVar(value="0 ms (0,00 s)")

        # Datenstrukturen für die Visualisierung
        self.current_data: List[int] = []
        self.sorted_indices: Set[int] = set()
        self.bar_rects: List[int] = []
        self.bar_texts: List[int] = []
        self._is_finalizing_run = False
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

        self.content_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))

        self.input_label.pack(pady=(15, 5))

        self.input_frame.pack(pady=(0, 10))
        for column in range(5):
            entry = tk.Entry(self.input_frame, width=6, justify="center")
            entry.grid(row=0, column=column, padx=5)
            self.input_entries.append(entry)

        self.canvas.pack(pady=20)

        self._build_legend()
        self._build_algorithm_selector()
        self._build_info_panel()

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

        legend_frame = tk.Frame(self.left_frame)
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

        options_frame = tk.LabelFrame(self.left_frame, text="Sortierverfahren")
        options_frame.pack(pady=(0, 10), padx=20, fill=tk.X)

        for index, (key, label, _) in enumerate(self.algorithm_options):
            button = tk.Radiobutton(
                options_frame,
                text=label,
                variable=self.algorithm_var,
                value=key,
                anchor="w",
                command=self._update_algorithm_info,
            )
            row = index // 2
            column = index % 2
            button.grid(row=row, column=column, sticky="w", padx=10, pady=2)
            self.algorithm_buttons.append(button)

    def _build_info_panel(self) -> None:
        """Erzeugt die rechte Seitenleiste mit Zeit- und Infobox."""

        timer_frame = tk.LabelFrame(self.right_frame, text="Zeitmessung")
        timer_frame.pack(fill=tk.X, pady=(0, 10))

        timer_label = tk.Label(timer_frame, text="Aktuelle Dauer:")
        timer_label.pack(anchor="w", padx=10, pady=(8, 0))

        timer_value = tk.Label(
            timer_frame,
            textvariable=self.timer_value_var,
            font=("Helvetica", 14, "bold"),
            anchor="w",
            justify=tk.LEFT,
        )
        timer_value.pack(anchor="w", padx=10, pady=(2, 8))

        info_frame = tk.LabelFrame(self.right_frame, text="Algorithmus-Info")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.algorithm_info_title_label = tk.Label(
            info_frame,
            textvariable=self.algorithm_info_title_var,
            font=("Helvetica", 13, "bold"),
            anchor="w",
            justify=tk.LEFT,
        )
        self.algorithm_info_title_label.pack(
            anchor="w", padx=10, pady=(8, 0)
        )

        self.algorithm_info_label = tk.Label(
            info_frame,
            justify=tk.LEFT,
            anchor="nw",
            wraplength=260,
        )
        self.algorithm_info_label.pack(
            fill=tk.BOTH, expand=True, padx=10, pady=(4, 8)
        )

        results_frame = tk.LabelFrame(self.right_frame, text="Rundenzeiten")
        results_frame.pack(fill=tk.BOTH, expand=False)

        columns = ("round", "algorithm", "time")
        self.results_tree = ttk.Treeview(
            results_frame,
            columns=columns,
            show="headings",
            height=8,
        )
        self.results_tree.heading("round", text="Runde")
        self.results_tree.heading("algorithm", text="Verfahren")
        self.results_tree.heading("time", text="Zeit")
        self.results_tree.column("round", width=90, anchor="w")
        self.results_tree.column("algorithm", width=130, anchor="w")
        self.results_tree.column("time", width=120, anchor="w")

        scrollbar = ttk.Scrollbar(
            results_frame,
            orient=tk.VERTICAL,
            command=self.results_tree.yview,
        )
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=8)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=8)

        self._update_algorithm_info()
        self._update_results_table()

    def _update_algorithm_info(self) -> None:
        """Aktualisiert den Informationstext zum gewählten Algorithmus."""

        if self.algorithm_info_label is None:
            return

        key = self.algorithm_var.get()
        title = self.algorithm_labels.get(key, key)
        if self.algorithm_info_title_var is not None:
            self.algorithm_info_title_var.set(title)

        info = self.algorithm_information.get(key)
        if not info:
            self.algorithm_info_label.config(
                text="Für dieses Verfahren liegt keine Beschreibung vor."
            )
            return

        advantages = "\n".join(f"- {item}" for item in info.get("advantages", []))
        disadvantages = "\n".join(f"- {item}" for item in info.get("disadvantages", []))
        text = (
            f"{info.get('description', '')}\n\n"
            f"Vorteile:\n{advantages}\n\n"
            f"Nachteile:\n{disadvantages}"
        )
        self.algorithm_info_label.config(text=text)

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

        self.active_algorithm_key = algorithm_key
        self.step_generator = generator_func(self.current_data)
        self.is_running = True
        self.is_paused = False
        self.animation_speed_ms = self.DEFAULT_ANIMATION_DELAY_MS
        self.pause_button.config(state=tk.NORMAL, text="Pause")
        self.start_button.config(state=tk.DISABLED)
        self._set_algorithm_buttons_state(tk.DISABLED)

        self._start_timer()
        self.perform_next_step()

    def pause_or_resume(self) -> None:
        """Pausiert oder setzt die Animation fort."""

        if not self.is_running:
            return

        if self.is_paused:
            self.is_paused = False
            self.pause_button.config(text="Pause")
            self._resume_timer()
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
            self._pause_timer()

    def reset(self) -> None:
        """Setzt die Anwendung in den Ausgangszustand zurück."""

        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None

        self._reset_timer()
        self.is_running = False
        self.is_paused = False
        self.step_generator = None
        self.active_algorithm_key = None
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

        self.run_history.clear()
        self.total_runs = 0
        self._update_results_table()

        for entry in self.input_entries:
            entry.delete(0, tk.END)

        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="Pause")
        self._set_algorithm_buttons_state(tk.NORMAL)

    def _set_algorithm_buttons_state(self, state: str) -> None:
        """Aktiviert oder deaktiviert alle Radiobuttons."""

        for button in self.algorithm_buttons:
            button.config(state=state)

    # ------------------------------------------------------------------
    # Zeitmessung und Auswertung
    # ------------------------------------------------------------------
    def _start_timer(self) -> None:
        """Initialisiert die Stoppuhr für einen neuen Durchlauf."""

        self.elapsed_time_ms = 0.0
        self.timer_base_time = time.perf_counter()
        self._cancel_timer_callback()
        self._update_timer_label(0.0)
        self._schedule_timer_update()

    def _pause_timer(self) -> None:
        """Hält die Stoppuhr an, behält aber den bisherigen Wert."""

        if self.timer_base_time is not None:
            self.elapsed_time_ms = self._current_elapsed_ms()
            self.timer_base_time = None
        self._cancel_timer_callback()
        self._update_timer_label(self.elapsed_time_ms)

    def _resume_timer(self) -> None:
        """Setzt die Stoppuhr nach einer Pause fort."""

        if not self.is_running:
            return
        if self.timer_base_time is None:
            self.timer_base_time = time.perf_counter()
        self._cancel_timer_callback()
        self._schedule_timer_update()

    def _stop_timer(self) -> float:
        """Beendet die Stoppuhr und gibt die gemessene Zeit in Millisekunden zurück."""

        if self.timer_base_time is not None:
            self.elapsed_time_ms = self._current_elapsed_ms()
            self.timer_base_time = None
        self._cancel_timer_callback()
        self._update_timer_label(self.elapsed_time_ms)
        return self.elapsed_time_ms

    def _reset_timer(self) -> None:
        """Setzt die Zeitmessung auf den Ausgangswert zurück."""

        self.timer_base_time = None
        self.elapsed_time_ms = 0.0
        self._cancel_timer_callback()
        self._update_timer_label(0.0)

    def _schedule_timer_update(self) -> None:
        """Aktualisiert die Zeitanzeige während der Animation."""

        if not self.is_running or self.is_paused or self.timer_base_time is None:
            self.timer_after_id = None
            return

        self._update_timer_label(self._current_elapsed_ms())
        self.timer_after_id = self.root.after(
            self.TIMER_UPDATE_INTERVAL_MS, self._schedule_timer_update
        )

    def _cancel_timer_callback(self) -> None:
        """Bricht einen geplanten Timer-Callback sicher ab."""

        if self.timer_after_id is not None:
            try:
                self.root.after_cancel(self.timer_after_id)
            except tk.TclError:
                pass
            self.timer_after_id = None

    def _current_elapsed_ms(self) -> float:
        """Berechnet die aktuelle Zeitspanne in Millisekunden."""

        if self.timer_base_time is None:
            return self.elapsed_time_ms
        delta = (time.perf_counter() - self.timer_base_time) * 1000.0
        return self.elapsed_time_ms + delta

    def _update_timer_label(self, elapsed_ms: float) -> None:
        """Aktualisiert die Textanzeige des Timers."""

        milliseconds = max(0.0, elapsed_ms)
        seconds = milliseconds / 1000.0
        seconds_text = f"{seconds:0.2f}".replace(".", ",")
        display_text = f"{int(round(milliseconds))} ms ({seconds_text} s)"
        self.timer_value_var.set(display_text)

    def _record_run_result(self, elapsed_ms: float) -> None:
        """Speichert das Ergebnis eines Durchlaufs für die Übersicht."""

        if self.active_algorithm_key is None:
            return

        algorithm_label = self.algorithm_labels.get(
            self.active_algorithm_key, self.active_algorithm_key
        )
        self.total_runs += 1
        self.run_history.append((self.total_runs, algorithm_label, elapsed_ms))
        if len(self.run_history) > 10:
            self.run_history = self.run_history[-10:]

        self._update_results_table()

    def _update_results_table(self) -> None:
        """Aktualisiert die Tabelle mit den gespeicherten Laufzeiten."""

        if self.results_tree is None:
            return

        for entry in self.results_tree.get_children():
            self.results_tree.delete(entry)

        for run_number, label, elapsed_ms in self.run_history:
            self.results_tree.insert(
                "",
                tk.END,
                values=(
                    f"Runde {run_number}",
                    label,
                    self._format_seconds(elapsed_ms),
                ),
            )

    def _format_seconds(self, elapsed_ms: float) -> str:
        """Formatiert Millisekunden als Sekunden mit deutschem Dezimaltrennzeichen."""

        seconds = elapsed_ms / 1000.0
        formatted = f"{seconds:0.2f}".replace(".", ",")
        return f"{formatted} Sekunden"

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

        if not self.is_running or self.is_paused or self.step_generator is None:
            return

        delay = max(10, int(self.animation_speed_ms))
        self.after_id = self.root.after(delay, self.perform_next_step)

    def _finish_sorting(self) -> None:
        """Wird aufgerufen, wenn alle Schritte abgearbeitet wurden."""

        if self._is_finalizing_run:
            return
        if not self.is_running and self.step_generator is None:
            return

        self._is_finalizing_run = True

        try:
            if self.after_id is not None:
                try:
                    self.root.after_cancel(self.after_id)
                except tk.TclError:
                    pass
                self.after_id = None

            elapsed_ms = self._stop_timer()
            self._record_run_result(elapsed_ms)
            self.active_algorithm_key = None
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
        finally:
            self._is_finalizing_run = False

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
            was_new = index not in self.sorted_indices
            self.sorted_indices.add(index)
            self._set_bar_color(index, self.SORTED_COLOR)

            if (
                was_new
                and not self._is_finalizing_run
                and self.is_running
                and len(self.sorted_indices) == len(self.current_data)
            ):
                self._finish_sorting()

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
