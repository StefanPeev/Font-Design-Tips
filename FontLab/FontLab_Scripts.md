# FontLab 9 Python Scripts

A collection of Python 3.11 + PythonQt automation scripts for **FontLab 9**, designed to streamline anchor management, diacritic construction, guideline placement, and stem inspection across single- and multi-master fonts.

**Author:** Stefan Peev ([https://github.com/StefanPeev](https://github.com/StefanPeev))

---

## Table of Contents

1. [Overview & Script Index](#overview--script-index)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Scripts Documentation](#scripts-documentation)
   - [1. Add Anchor to Selected Glyphs](#1-add-anchor-to-selected-glyphs)
   - [2. Add Center Vertical Guideline (`width/2`)](#2-add-center-vertical-guideline-width2)
   - [3. Adjust Anchors (FontLab 9)](#3-adjust-anchors-fontlab-9)
   - [4. Anchor Names (FontLab 9)](#4-anchor-names-fontlab-9)
   - [5. Build Combining Diacritical Marks (FontLab 9)](#5-build-combining-diacritical-marks-fontlab-9)
   - [6. Compare Two Open Fonts (FontLab 9)](#6-compare-two-open-fonts-fontlab-9)
   - [7. Select Glyphs by Anchor (FontLab 9)](#7-select-glyphs-by-anchor-fontlab-9)
   - [8. Stem Finder Pro (FontLab 9)](#8-stem-finder-pro-fontlab-9)
5. [License & Disclaimer](#license--disclaimer)

---

## Overview & Script Index

| Script Name | File | Purpose | Scope |
| :--- | :--- | :--- | :--- |
| [**Add Anchor to Selected Glyphs**](#1-add-anchor-to-selected-glyphs) | `Add_Anchor_to_Selected_Glyphs_FL9.py` | Adds or updates named anchors with fixed/relative alignment, metric snapping, and italic angle compensation. | Current or All Masters |
| [**Add Center Vertical Guideline (`width/2`)**](#2-add-center-vertical-guideline-width2) | `Add_Center_Vertical_Guideline_FL9.py` | Places a dynamic `width/2` local vertical guideline on selected glyphs, skipping duplicates. | Active Layer |
| [**Adjust Anchors (FontLab 9)**](#3-adjust-anchors-fontlab-9) | `Adjust_Anchors_FL9.py` | Interactive dialog with nudge buttons and keyboard shortcuts (`±1`, `±5`, `±20`) for real-time anchor tuning. | All Masters |
| [**Anchor Names (FontLab 9)**](#4-anchor-names-fontlab-9) | `Anchor_Names_FL9.py` | Audits base glyphs across masters (skipping composites) and copies missing anchors into remaining masters. | All Masters |
| [**Build Combining Diacritical Marks (FontLab 9)**](#5-build-combining-diacritical-marks-fontlab-9) | `Build_Combining_Diacritical_Marks_FL9.py` | Generates or updates zero-width combining marks (`U+0300`–`U+036F`) from spacing marks as italic-centered Element References. | All Masters |
| [**Compare Two Open Fonts (FontLab 9)**](#6-compare-two-open-fonts-fontlab-9) | `Compare_Two_Open_Fonts_FL9.py` | A Python script for **FontLab 9** that compares the glyph sets of two currently open fonts and generates a clean, structured text report of the missing glyphs in each font. |  |
| [**Select Glyphs by Anchor (FontLab 9)**](#7-select-glyphs-by-anchor-fontlab-9) | `Select_Glyphs_by_Anchor_FL9.py` | Filters and previews glyphs by anchor presence/absence and selects or opens them in a Glyph Window. | Active or All Masters |
| [**Stem Finder Pro (FontLab 9)**](#8-stem-finder-pro-fontlab-9) | `Stem_Finder_Pro_FL9.py` | Locates straight and curved stems matching a target width `± tolerance`, highlights nodes, and opens matched glyphs. | Active or All Masters |

---

## Requirements

* **FontLab 9** (with built-in Python 3.11 and `PythonQt` enabled)
* **macOS** or **Windows**
* No external third-party Python libraries required.

---

## Installation

1. Download the desired `.py` script(s) from this repository.
2. Locate your FontLab 9 `Scripts` directory:
   * Via FontLab menu: **Scripts > Open Scripts Folder** (or **Help > Open User Data Folder**, then open the **`Scripts`** subfolder).
   * **macOS default:** `~/Library/Application Support/FontLab/FontLab 9/Scripts/`
   * **Windows default:** `%APPDATA%\FontLab\FontLab 9\Scripts\`
3. Copy the `.py` file(s) into the **`Scripts`** folder (or a custom subfolder inside it).
4. In FontLab 9, choose **Scripts > Update / Rescan Scripts** (or restart FontLab).
5. Launch any installed tool from the **Scripts** menu.

*(Alternatively, paste any script's code into **Window > Panels > Scripting** and click **Run**.)*

> **Note:** Always save a backup copy of your font project (`File > Save Font As...`) before running batch modification scripts.

---

## Scripts Documentation

### 1. Add Anchor to Selected Glyphs

**File:** `Add_Anchor_to_Selected_Glyphs_FL9.py`

Adds or updates a named anchor on all selected glyphs across the current master or all masters, with fixed or relative X/Y alignment, vertical font metric snapping, italic angle compensation, and persistent dialog settings.

#### Features
* **Flexible Horizontal Alignment (X):**
  * **Fixed X:** Places the anchor at an exact horizontal coordinate.
  * **Advance Width / 2:** Centers the anchor horizontally within each glyph's advance width (plus optional offset).
  * **Bounding Box Center:** Centers the anchor on the glyph's outline bounding box (falling back to `Advance Width / 2` if empty).
* **Italic Angle Compensation:** Shifts the X coordinate along each master's `italicAngle` (`y * tan(-italicAngle)`).
* **Vertical Metric Snapping (Y):** Places the anchor at a **Fixed Y** coordinate or relative to **Baseline (0)**, **x-Height**, **Cap Height**, **Ascender**, or **Descender** with a custom offset.
* **Multi-Master & Overwrite Control:** Apply to **Current Master** or **All Masters**, and toggle **Skip if anchor already exists**.
* **Auto-Layer Protection:** Automatically ignores auto-layers so generated components are not disrupted.
* **Persistent Preferences:** Saves your last-used parameters to a temporary JSON file (`fl9_add_anchor.json`) between runs.

#### Usage
1. Select one or more glyphs in the **Font Window** (or open a glyph in the **Glyph Window**).
2. Run **Scripts > Add Anchor to Selected Glyphs**.
3. Enter the **Anchor Name** (e.g., `top`, `_top`, `bottom`, `_bottom`), choose horizontal and vertical alignment/offsets, and set master/skip options.
4. Click **OK**. A summary of added, updated, and skipped anchors is printed in **Window > Panels > Output**.

---

### 2. Add Center Vertical Guideline (`width/2`)

**File:** `Add_Center_Vertical_Guideline_FL9.py`

Adds a dynamic local vertical guideline with the expression `"width/2"` to the active layer of all selected glyphs, automatically skipping glyphs that already contain one.

#### Features
* **Dynamic Expression Binding:** Sets `guide.expression = "width/2"` and binds layer dependencies so the guideline automatically moves whenever the glyph's advance width changes.
* **Duplicate Prevention:** Checks existing layer guidelines and skips any glyph that already has a `"width/2"` guideline.
* **Smart Selection Fallback:** Operates on glyphs selected in the **Font Window**, or falls back to the currently active glyph in an open **Glyph Window**.

#### Usage
1. Select glyphs in the **Font Window** or open a glyph in the **Glyph Window**.
2. Run **Scripts > Add Center Vertical Guideline (width/2)**.
3. The script adds the local guideline, refreshes the canvas, and reports the count of updated glyphs in **Window > Panels > Output**.

---

### 3. Adjust Anchors (FontLab 9)

**File:** `Adjust_Anchors_FL9.py`

An interactive non-modal dialog for precision coordinate tuning of anchors in FontLab 9, featuring directional nudge buttons, keyboard shortcuts, live canvas updates, and full rollback on Cancel.

#### Features
* **Glyph & Anchor Filtering:** Lists all glyphs containing anchors with a dropdown filter to isolate specific anchor names across the font.
* **Multi-Master Switching:** Switch between font masters via radio buttons while inspecting or nudging anchors.
* **Directional Nudge Pad & Shortcuts:**
  * **Arrow keys / buttons:** `±1` unit
  * **Shift + Arrow keys / buttons:** `±5` units
  * **Ctrl + Left/Right / buttons:** `±20` units
* **Live Coordinate Tracking:** Displays **Original**, **Shift (delta)**, and **Final** X/Y coordinates while syncing live with the Glyph canvas and FontLab's **Anchors** panel.
* **Safe Commit / Cancel:** Clicking **OK** commits all pending changes; clicking **Cancel** restores every modified anchor to its original coordinates.

#### Usage
1. Open a font containing anchors and run **Scripts > Adjust Anchors (FontLab 9)**.
2. Filter by anchor name if desired, select a **Glyph**, **Master**, and **Anchor**.
3. Use the on-screen nudge buttons or keyboard shortcuts to adjust coordinates in real time.
4. Click **OK** to keep changes or **Cancel** to revert all edits.

---

### 4. Anchor Names (FontLab 9)

**File:** `Anchor_Names_FL9.py`

Ensures consistent anchor sets across all masters in a font by scanning all base glyphs, copying missing anchors from existing masters, and selecting every modified glyph for manual adjustment.

#### Features
* **Automatic Composite Skipping:** Detects and ignores composite glyphs (glyphs containing components or referenced elements) in any master so only base glyphs are modified.
* **Cross-Master Anchor Synchronization:** Builds a union of all anchor names present across every master and copies missing anchors into the remaining masters using the first available coordinates.
* **Smart Font Window Selection:** Automatically selects all modified base glyphs in the Font Window upon completion for quick visual inspection and manual positioning.
* **Detailed Console Logging:** Prints a clear summary of checked masters, added anchors per master, skipped composite count, and modified glyphs to **Window > Panels > Output**.

#### Usage
1. Open a multi-master font in **FontLab 9**.
2. Run **Scripts > Anchor Names (FontLab 9)**.
3. Review **Window > Panels > Output** to see which anchors were added to each base glyph and master.
4. Inspect the highlighted glyphs in the **Font Window** and adjust the newly added anchor positions as needed.

#### Example Output

```text
Checking base glyphs across 3 masters: Light, Regular, Bold
------------------------------------------------------------
Fixed base glyph: /A
   • [Bold]: added ogonek, top
Fixed base glyph: /e
   • [Light]: added bottom
------------------------------------------------------------
Skipped 142 composite glyphs.
Added missing anchors in 2 base glyph(s).
Modified base glyphs have been selected in the Font Window so you can adjust anchor positions.
```

---

### 5. Build Combining Diacritical Marks (FontLab 9)

**File:** `Build_Combining_Diacritical_Marks_FL9.py`

Finds spacing diacritic glyphs in the active font with Unicode equivalents in the Combining Diacritical Marks block (`U+0300`–`U+036F`), creates or updates each corresponding combining mark glyph across all masters, places the source glyph as a linked Element Reference optically centered along each master's italic angle, and sets the advance width to zero.

#### Features
* **Automatic Source Discovery:** Searches the active font by both glyph name (e.g., `acute`, `grave`, `dieresis`, `cedilla`) and spacing Unicode codepoint (e.g., `U+00B4`, `U+0060`, `U+00A8`, `U+00B8`) across 30 standard diacritic mappings.
* **Glyph Creation & Unicode Assignment:** Creates missing combining mark glyphs (`uni0300`–`uni033F`) or updates existing `*comb` / `uni03XX` glyphs and assigns the target combining Unicode codepoint.
* **Linked Element References:** Inserts the spacing diacritic as a linked `GlyphComponent` so outline edits to the spacing mark automatically propagate to the combining mark.
* **Italic-Aware Optical Centering:** Computes the horizontal center of each source glyph's bounding box relative to its vertical midpoint and aligns it along each master's `italicAngle` (`center_y * tan(-italicAngle)`).
* **Multi-Master Processing:** Processes every master layer in the font in a single run.
* **Clean Rebuild & Zero Advance Width:** Clears old shapes and `_top`/`_bottom` anchors on the target layer before placing the updated component and sets `advanceWidth = 0`.

#### Supported Diacritic Mappings

| Spacing Source | Spacing Unicode | Combining Target | Combining Unicode |
| :--- | :--- | :--- | :--- |
| `grave` | `U+0060` | `gravecomb` / `uni0300` | `U+0300` |
| `acute` | `U+00B4` | `acutecomb` / `uni0301` | `U+0301` |
| `circumflex` | `U+02C6` | `circumflexcomb` / `uni0302` | `U+0302` |
| `tilde` | `U+02DC` | `tildecomb` / `uni0303` | `U+0303` |
| `macron` | `U+00AF` | `macroncomb` / `uni0304` | `U+0304` |
| `overline` | `U+203E` | `overlinecomb` / `uni0305` | `U+0305` |
| `breve` | `U+02D8` | `brevecomb` / `uni0306` | `U+0306` |
| `dotaccent` | `U+02D9` | `dotaccentcomb` / `uni0307` | `U+0307` |
| `dieresis` | `U+00A8` | `dieresiscomb` / `uni0308` | `U+0308` |
| `hookabove` | — | `hookabovecomb` / `uni0309` | `U+0309` |
| `ring` | `U+02DA` | `ringcomb` / `uni030A` | `U+030A` |
| `hungarumlaut` | `U+02DD` | `hungarumlautcomb` / `uni030B` | `U+030B` |
| `caron` | `U+02C7` | `caroncomb` / `uni030C` | `U+030C` |
| `verticallineabove` | — | `verticallineabovecomb` / `uni030D` | `U+030D` |
| `dblverticallineabove` | — | `dblverticallineabovecomb` / `uni030E` | `U+030E` |
| `commaaccentturned` | — | `commaaccentturnedcomb` / `uni0312` | `U+0312` |
| `gravebelow` | — | `gravebelowcomb` / `uni0316` | `U+0316` |
| `acutebelow` | — | `acutebelowcomb` / `uni0317` | `U+0317` |
| `horn` | — | `horncomb` / `uni031B` | `U+031B` |
| `dotbelow` | — | `dotbelowcomb` / `uni0323` | `U+0323` |
| `dieresisbelow` | — | `dieresisbelowcomb` / `uni0324` | `U+0324` |
| `ringbelow` | — | `ringbelowcomb` / `uni0325` | `U+0325` |
| `commaaccent` | — | `commaaccentcomb` / `uni0326` | `U+0326` |
| `cedilla` | `U+00B8` | `cedillacomb` / `uni0327` | `U+0327` |
| `ogonek` | `U+02DB` | `ogonekcomb` / `uni0328` | `U+0328` |
| `verticallinebelow` | — | `verticallinebelowcomb` / `uni0329` | `U+0329` |
| `brevebelow` | — | `brevebelowcomb` / `uni032E` | `U+032E` |
| `macronbelow` | — | `macronbelowcomb` / `uni0331` | `U+0331` |
| `lowline` | — | `lowlinecomb` / `uni0332` | `U+0332` |
| `dbloverline` | — | `dbloverlinecomb` / `uni033F` | `U+033F` |

#### Usage
1. Open a font containing spacing diacritic glyphs in **FontLab 9**.
2. Run **Scripts > Build Combining Diacritical Marks (FontLab 9)**.
3. Open **Window > Panels > Output** to view the list of created or updated combining mark glyphs and their assigned Unicode codepoints.

---

### 6. Compare Two Open Fonts (FontLab 9)

**File:** `Compare_Two_Open_Fonts_FL9.py`

A Python script for **FontLab 9** that compares the glyph sets of two currently open fonts and generates a clean, structured text report of the missing glyphs in each font.

#### Features
* **Two-Way Comparison:** Identifies glyphs present in Font 2 that are missing in Font 1, and vice versa.
* **Smart Naming:** Automatically extracts the font family and style names from font metadata (falling back to the file name if metadata is unavailable).
* **Dual Output:** Prints the comparison report directly to FontLab's **Output** panel and prompts you to save the results as a UTF-8 encoded `.txt` file.
* **Zero Dependencies:** Uses only FontLab 9's built-in Python API and standard Python libraries (`os`).

#### Usage
1. Open the **two fonts** you want to compare in FontLab 9. *(Note: The script compares the first two open fonts in the workspace, so make sure only the target pair is open or that they are the first two tabs).*
2. Run the script via **Scripts > Compare Two Open Fonts** (or paste and run it inside **Window > Panels > Scripting**).
3. View the immediate summary in **Window > Panels > Output**.
4. Choose a destination folder and file name in the save dialog to export the `.txt` report.

#### Example Output

```text
GLYPH COMPARISON REPORT
==================================================
Font 1: Common Serif Regular (Total glyphs: 850)
Font 2: Common Serif Italic (Total glyphs: 842)
==================================================

Missing in 'Common Serif Regular' (2 glyphs):
--------------------------------------------------
f_f_i.alt
germandbls.calt

Missing in 'Common Serif Italic' (10 glyphs):
--------------------------------------------------
Aogonek
Eogonek
...
```

---

### 7. Select Glyphs by Anchor (FontLab 9)

**File:** `Select_Glyphs_by_Anchor_FL9.py`

Scans master layers for anchor names, provides a live preview of matching glyphs, and allows you to select them in the Font Window or open them directly in a Glyph Window tab.

#### Features
* **Automatic Anchor Discovery:** Scans all master layers in the active font and populates a searchable, editable dropdown list of existing anchor names.
* **Flexible Search Scopes & Filters:**
  * **Any Master (Default):** Matches glyphs containing the target anchor in at least one master layer.
  * **Active Master Only:** Restricts the search to the currently active master layer.
  * **Require in ALL Masters:** Ensures the target anchor is present across every master layer in the font (useful for checking variable font / multi-master consistency).
  * **Invert Match:** Finds glyphs *missing* the specified anchor across the selected scope.
* **Live Preview & Quick Inspection:** Displays a real-time count and scrollable list of matching glyph names. Double-clicking any glyph in the preview list immediately selects and opens it in a Glyph Window tab.
* **Batch Actions & Safety Guards:**
  * **Select in Font Window:** Highlights matching glyphs in the Font Window, with an option to append to your existing selection.
  * **Open in Glyph Window:** Opens matching glyphs in a new Glyph Window tab, featuring a built-in safety prompt when opening more than 150 glyphs at once.

#### Usage
1. Open a font in **FontLab 9**.
2. Run **Scripts > Select Glyphs by Anchor (FontLab 9)**.
3. Choose an existing anchor from the **Anchor name** dropdown or type a custom anchor name.
4. *(Optional)* Adjust the **Search Scope & Filter** checkboxes (`Search in active master only`, `Require anchor in ALL masters`, or `Invert match`).
5. Review the matching glyphs in the live preview list:
   * **Double-click** a single glyph name to jump straight to it in a Glyph Window.
   * Check **Add to current Font Window selection** if you want to preserve your existing selection.
   * Click **Select in Font Window** or **Open in Glyph Window** to apply the action to all matched glyphs.

---

### 8. Stem Finder Pro (FontLab 9)

**File:** `Stem_Finder_Pro_FL9.py`

Detects vertical and horizontal stems (both straight segments and curved extrema) matching a target width and tolerance, highlights the corresponding stem nodes, copies the matched glyph string to the clipboard, and opens matched glyphs in a new Glyph Window.

#### Features
* **Vertical & Horizontal Stem Detection:** Scans glyph contours for parallel vertical or horizontal stem edges within a configurable **Target Stem Width** and **Tolerance (+/-)**.
* **Curved Stem Support:** Optionally detects extrema on curved contours (such as `O`, `C`, and `S`) by analyzing on-curve nodes paired with vertical or horizontal off-curve handles.
* **Serif Filtering:** Uses a **Minimum Stem Length** threshold (`Min. Stem Length (serif filter)`) to exclude short serif edges and small contour details.
* **Multi-Master & Selection Scopes:**
  * Scan either the **active master** or **all masters** across the font.
  * Restrict the search to **selected glyphs only** or scan the entire font.
* **Visual Node Highlighting:** Automatically selects the matching stem nodes on the inspected layers and updates the glyphs for immediate visual inspection.
* **Batch Output & Glyph Window Integration:**
  * Prints detailed per-glyph and per-master measurements (`width`, `start`, `end`, `straight`/`curve`) to **Window > Panels > Output**.
  * Displays a slash-separated glyph string (e.g., `/H/I/O/n`) in the dialog and copies it directly to the system clipboard.
  * Selects matched glyphs in the Font Window and opens them in a new Glyph Window tab.

#### Usage
1. Open a font in **FontLab 9**.
2. Run **Scripts > Stem Finder Pro (FontLab 9)**.
3. Configure your search parameters in the dialog:
   * **Target Stem Width:** Desired stem thickness in font units (default: `22.0`).
   * **Tolerance (+/-):** Allowed deviation from the target width in font units (default: `1.0`).
   * **Min. Stem Length (serif filter):** Minimum segment length required to qualify as a straight stem (default: `5.0`).
   * **Include curved stems (O, C, S):** Include curved extrema alongside straight segments.
   * **Scan all masters:** Check every master in the font instead of only the active master.
   * **Search selected glyphs only:** Limit scanning to glyphs currently selected in the Font Window.
4. Click **1. Find Vertical Stems** or **2. Find Horizontal Stems**.
5. Review the results:
   * Matched glyphs are selected in the Font Window, opened in a Glyph Window tab, and copied to your clipboard as `/glyph1/glyph2/...`.
   * Matching stem nodes are highlighted directly on the contours.
   * Detailed stem coordinates and types are logged in **Window > Panels > Output**.

---

## License & Disclaimer

All scripts in this repository are offered under the **MIT License**.

```text
MIT License

Copyright (c) 2026 Stefan Peev (https://github.com/StefanPeev)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

> **Note:** Always save a backup copy of your font file before running batch modification scripts.
