# FontLab 9 Python Scripts

A collection of Python 3.11 + PythonQt automation scripts for **FontLab 9**, designed to streamline anchor management, diacritic construction, guideline placement, and stem inspection across single- and multi-master fonts.

**Author:** Stefan Peev ([https://github.com](https://github.com))


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
   - [5. Build Combining Diacritical Marks](#5-build-combining-diacritical-marks)
   - [6. Select Glyphs by Anchor (FontLab 9)](#6-select-glyphs-by-anchor-fontlab-9)
   - [7. Stem Finder Pro (Vertical & Horizontal)](#7-stem-finder-pro-vertical--horizontal)

---

## Overview & Script Index

| Script Name | File | Purpose | Scope |
| :--- | :--- | :--- | :--- |
| [**Add Anchor to Selected Glyphs**](#1-add-anchor-to-selected-glyphs) | `Add_Anchor_to_Selected_Glyphs_FL9.py` | Adds or updates named anchors with fixed/relative alignment, metric snapping, and italic angle compensation. | Current or All Masters |
| [**Add Center Vertical Guideline (`width/2`)**](#2-add-center-vertical-guideline-width2) | `Add_Center_Vertical_Guideline_FL9.py` | Places a dynamic `width/2` local vertical guideline on selected glyphs, skipping duplicates. | Active Layer |
| [**Adjust Anchors (FontLab 9)**](#3-adjust-anchors-fontlab-9) | `Adjust_Anchors_FL9.py` | Interactive dialog with nudge buttons and keyboard shortcuts (`±1`, `±5`, `±20`) for real-time anchor tuning. | All Masters |
| [**Anchor Names (FontLab 9)**](#4-anchor-names-fontlab-9) | `Anchor_Names_FL9.py` | Audits base glyphs across masters (skipping composites) and copies missing anchors into remaining masters. | All Masters |
| [**Build Combining Diacritical Marks**](#5-build-combining-diacritical-marks) | `Build_Combining_Diacritical_Marks_FL9.py` | Generates or updates zero-width combining marks (`U+0300`–`U+036F`) from spacing marks as italic-centered Element References. | All Masters |
| [**Select Glyphs by Anchor (FontLab 9)**](#6-select-glyphs-by-anchor-fontlab-9) | `Select_Glyphs_by_Anchor_FL9.py` | Filters and previews glyphs by anchor presence/absence and selects or opens them in a Glyph Window. | Active or All Masters |
| [**Stem Finder Pro (Vertical & Horizontal)**](#7-stem-finder-pro-vertical--horizontal) | `Stem_Finder_Pro_FL9.py` | Locates straight and curved stems matching a target width `± tolerance`, highlights nodes, and opens matched glyphs. | Active or All Masters |

---

## Requirements

* **FontLab 9** (with built-in Python 3.11 and `PythonQt` enabled)
* **macOS** or **Windows**
* No external third-party Python libraries required.

---

## Installation

1. Download the desired `.py` script(s) from this repository.
2. Locate your FontLab 9 `Scripts` directory:
   * Via FontLab menu: **Help > Open User Data Folder** (or **Scripts > Open Scripts Folder**), then open the **`Scripts`** subfolder.
   * **macOS default:** `~/Library/Application Support/FontLab/FontLab 9/Scripts/`
   * **Windows default:** `%APPDATA%\FontLab\FontLab 9\Scripts\`
3. Copy the `.py` file(s) into the **`Scripts`** folder (or a custom subfolder inside it).
4. In FontLab 9, choose **Scripts > Update / Rescan Scripts** (or restart FontLab).
5. Launch any installed tool from the **Scripts** menu.

*(Alternatively, paste any script's code into **Window > Panels > Scripting** and click **Run**.)*

> **Note:** Always save a backup copy of your font project before running batch modification scripts.

---

## Scripts Documentation

---

### 1. Add Anchor to Selected Glyphs

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

#### Copyright & Disclaimer
* **Copyright:** © 2026 Stefan Peev ([https://github.com](https://github.com)). All rights reserved.
* **Disclaimer:** This script is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the author or copyright holder be liable for any claim, damages, or other liability arising from the use of this script. Use at your own risk.

---

### 2. Add Center Vertical Guideline (`width/2`)

Adds a dynamic local vertical guideline with the expression `"width/2"` to the active layer of all selected glyphs, automatically skipping glyphs that already contain one.

#### Features
* **Dynamic Expression Binding:** Sets `guide.expression = "width/2"` and binds layer dependencies so the guideline automatically moves whenever the glyph's advance width changes.
* **Duplicate Prevention:** Checks existing layer guidelines and skips any glyph that already has a `"width/2"` guideline.
* **Smart Selection Fallback:** Operates on glyphs selected in the **Font Window**, or falls back to the currently active glyph in an open **Glyph Window**.

#### Usage
1. Select glyphs in the **Font Window** or open a glyph in the **Glyph Window**.
2. Run **Scripts > Add Center Vertical Guideline (width/2)**.
3. The script adds the local guideline, refreshes the canvas, and reports the count of updated glyphs in the **Output** panel.

#### Copyright & Disclaimer
* **Copyright:** © 2026 Stefan Peev ([https://github.com](https://github.com)). All rights reserved.
* **Disclaimer:** This script is provided "as is", without warranty of any kind, express or implied. Always save a backup of your font file before running batch modification scripts. The author is not liable for any data loss or unintended changes to your font files.

---

### 3. Adjust Anchors (FontLab 9)

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

#### Copyright & Disclaimer
* **Copyright:** © 2026 Stefan Peev ([https://github.com](https://github.com)). All rights reserved.
* **Disclaimer:** THIS SCRIPT IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR OR COPYRIGHT HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY ARISING FROM THE USE OF THIS SCRIPT. USE AT YOUR OWN RISK.

---

### 4. Anchor Names (FontLab 9)

Audits all base glyphs across all masters in the active font, automatically skips composite glyphs, copies any missing anchors into masters that lack them, and selects the modified base glyphs in the Font Window for manual positioning.

#### Features
