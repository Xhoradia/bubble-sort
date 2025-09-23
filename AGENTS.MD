Projektüberblick
=================
Dieses Repository enthält eine vollständig implementierte tkinter-Anwendung,
die sechs Sortieralgorithmen (Bubble, Selection, Insertion, Merge, Quick und
Heap) visuell darstellt. Nutzerinnen und Nutzer geben exakt fünf Zahlen ein;
das Programm animiert die Sortierschritte als Balkendiagramm mit einem
konsistenten Farbschema (Grau für unsortiert, Gelb für Vergleiche, Rot für
Schreiboperationen und Grün für endgültig sortierte Werte).

Aktueller Funktionsumfang
-------------------------
* Radiobuttons zur Auswahl des Sortierverfahrens und Schaltflächen für Start,
  Pause/Fortsetzen sowie Reset.
* Eine Infobox, die Vorteile und Nachteile des gewählten Algorithmus
  beschreibt, sowie eine Tabelle mit den Zeiten der letzten Durchläufe.
* Eine Stoppuhr, die beim Start automatisch losläuft und exakt in dem Moment
  stoppt, in dem alle Balken grün markiert sind.
* Schrittgeneratoren für alle unterstützten Algorithmen; jeder Schritt ist als
  Tupel `(aktion, index, optionaler_index_oder_wert)` aufgebaut.

Arbeitsrichtlinien
------------------
* Bewahre die klare Trennung zwischen Schrittgeneratoren und Rendererlogik.
* Verwende sprechende Namen, Typannotationen und aussagekräftige Kommentare,
  um den didaktischen Charakter des Projekts zu erhalten.
* Halte die Farb- und Ereignis-Semantik bei (`compare`, `swap`, `overwrite`,
  `revert`, `mark_sorted`). Neue Ereignistypen sollten nur mit gutem Grund
  eingeführt werden.
* Animationen müssen über `after`-Callbacks laufen, damit die Oberfläche nicht
  blockiert. Achte darauf, dass Timer und Animationen sauber beendet werden,
  sobald ein Lauf fertig ist.

Tests und Validierung
---------------------
* Es existieren keine automatisierten Tests. Prüfe Änderungen manuell, indem
  du `python bubble_sort_visualizer.py` startest und mehrere Algorithmen mit
  unterschiedlichen Eingaben durchspielst.
* Kontrolliere dabei insbesondere, dass die Stoppuhr unmittelbar anhält,
  sobald der letzte Balken grün eingefärbt wird, und dass Pause/Reset weiterhin
  zuverlässig funktionieren.
