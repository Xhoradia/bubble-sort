README - Sorting Visualizer

🔄 Sorting Visualizer (Bubble, Selection, Insertion, Merge, Quick, Heap)
Ein Lernprojekt, das mehrere Sortierverfahren grafisch animiert:
Bubble Sort, Selection Sort, Insertion Sort, Merge Sort, Quick Sort und Heap Sort.
Perfekt für Einsteiger, die Sortieralgorithmen Schritt für Schritt verstehen möchten.

✨ Features
- Eingabe: 5 Zahlen frei wählbar (ein- oder mehrstellig, z. B. 8, 12, 88, 75, 106)
- Algorithmus-Auswahl: Über Option-Buttons (Radio-Buttons) wählbar:
  Bubble, Selection, Insertion, Merge, Quick, Heap
- Visualisierung: Darstellung der Werte als Balkendiagramm mit farblicher Hervorhebung jeder Aktion
- Farbcodierung:
  - Grau = Ausgangszustand
  - Gelb = Vergleich
  - Rot = Tausch bzw. aktiver Schritt
  - Grün = endgültig sortierter Bereich/Elemente
- Steuerung:
  - Start – startet die Animation
  - Pause/Fortsetzen – stoppt und setzt fort
  - Reset – Eingabe neu beginnen (inkl. geleertem Log)
- Algorithmus-Info: Rechte Seitenleiste mit Beschreibung, Vorteilen/Nachteilen und Tabelle der letzten Rundenzeiten
- Zeitmessung: Stoppuhr startet automatisch mit dem Lauf und hält exakt in dem Moment an, in dem der letzte Balken grün wird
- Schrittlogik: Alle Algorithmen liefern fein granular Schritte, sodass die Visualisierung konsistent bleibt

🛠️ Voraussetzungen
- Python 3.8 oder neuer
- Keine externen Bibliotheken notwendig (nur tkinter aus der Python-Standardbibliothek)

🚀 Nutzung
1. Repository klonen oder Dateien herunterladen
2. Programm starten:
   python bubble_sort_visualizer.py
3. Fünf Zahlen in die Eingabefelder eintragen
4. Über Option-Buttons das Sortierverfahren auswählen
5. Start klicken und die Animation beobachten

🧠 Didaktik
- Konsistente Farbcodes und Schritt-Events über alle Algorithmen
- Sprechende UI-Beschriftungen und eindeutige Status-Anzeigen
- Optionale Schritt-für-Schritt-Ausführung (Pause/Fortsetzen) zum genauen Nachvollziehen
