# Stem Finder Pro for FontLab 9

A Python 3.11 + PythonQt script for **FontLab 9** that locates vertical and horizontal stems (both straight and curved) matching a target width and tolerance, highlights the matching stem nodes, and opens all matched glyphs in a separate Glyph window for rapid quality assurance and optical consistency checks.

---

## Features

* **Vertical & Horizontal Stem Detection:** Scans glyph contours for opposing vertical or horizontal stem walls separated by your target width (`± tolerance`).
* **Curved Stem Support (`Include curved stems`):** Evaluates vertical and horizontal curve extrema (bowls, arches, and spines such as `O`, `C`, `S`, `e`, `oe`, `zecyr`) in addition to straight segments.
* **Serif & Bracket Filtering (`Min. Stem Length`):** Filters out short serif tips, brackets, or tiny notches by requiring a minimum segment length.
* **Single or Multi-Master Scanning (`Scan all masters`):** Inspects either the currently active master layer or every master in the font simultaneously, highlighting nodes across all matching layers.
* **Scoped Search:** Search across the entire font or limit the scan to glyphs currently selected in the Font Window.
* **Instant Highlighting & Inspection:**
  * Selects the exact boundary nodes/handles forming each matched stem inside the glyph layer.
  * Selects all matched glyphs in the Font Window and triggers a separate Glyph window/tab.
  * Copies the slash-separated glyph string (e.g. `/Ylongcyr/becyr/icyr/DZ/dz`) directly to the clipboard and displays it in the dialog.
  * Logs a detailed per-glyph, per-master coordinate breakdown in FontLab's **Output** panel.

---

## Requirements

* **FontLab 9** (with Python 3.11 and PythonQt enabled)
* macOS or Windows

---

## Installation

1. Download `StemFinderPro.py` from this repository.
2. Open FontLab 9 and go to **Help > Open User Data Folder** (or locate your FontLab 9 `Scripts` directory).
3. Copy `StemFinderPro.py` into the **`Scripts`** folder.
4. In FontLab 9, choose **Scripts > Update/Rescan Scripts**.
5. Launch the tool anytime from **Scripts > Stem Finder Pro**.

*(Alternatively, paste the contents of `StemFinderPro.py` into **Window > Panels > Scripting** and click **Run**.)*

---

## Usage

1. Open your font in **FontLab 9**.
2. Launch **Scripts > Stem Finder Pro**.
3. Configure your search parameters:
   * **Target Stem Width:** The stem thickness in font units you want to find (e.g. `22.0` or `85.0`).
   * **Tolerance (+/-):** Allowed deviation in font units (e.g. `1.0`).
   * **Min. Stem Length (serif filter):** Minimum length in font units for straight segments; increase this (e.g. `60`–`100`) to ignore thin serifs and short crossbars.
   * **Include curved stems (O, C, S):** Check to include opposing curve extrema alongside straight segments.
   * **Scan all masters:** Check to scan every master layer in the font at once.
   * **Search selected glyphs only:** Check to restrict the scan to glyphs selected in the Font Window.
4. Click **1. Find Vertical Stems** or **2. Find Horizontal Stems**.
5. Inspect the matched glyphs in the newly opened Glyph window—the detected stem nodes are already highlighted for editing, and full coordinates are printed in **Window > Panels > Output**.

---

## Output Example

```text
--- Vertical Stems: 22.0 +/- 1.0 ---
  /Ylongcyr -> {'Active': [(21.0, 120.0, 141.0, 'straight')]}
  /becyr -> {'Active': [(22.0, 49.0, 71.0, 'straight'), (22.0, 49.0, 71.0, 'curve')]}
  /gecyr.loclBGR -> {'Active': [(21.0, 396.0, 417.0, 'curve')]}
  /DZ -> {'Active': [(22.0, 88.0, 110.0, 'straight')]}
```

Each tuple reports `(measured_width, start_coordinate, end_coordinate, stem_type)`.

---

## Copyright & Disclaimer

**Copyright:** © 2026 Stefan Peev (https://github.com/StefanPeev). All rights reserved.

**Disclaimer:**
This script is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the author or copyright holder be liable for any claim, damages, or other liability arising from the use of this script. Use at your own risk.
