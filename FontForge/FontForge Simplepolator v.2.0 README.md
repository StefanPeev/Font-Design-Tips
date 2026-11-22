# FontForge Simplepolator v.2.0

A FontForge plug-in to generate interpolated glyph instances ("children") between two compatible master characters directly from the **Tools** menu.

Inspired by the Simplepolator FontLab/RoboFont script by Pablo Impallari ([Simplepolation](http://www.impallari.com/projects/overview/simplepolation)) to apply Gunnlaugur SE Briem's interpolation method ([Briem's Method](http://66.147.242.192/~operinan/2/2.3.3a/2.3.3.02.tests.htm)).

---

## Features

- **Tools Menu Integration:** Registers directly under **Tools > Simplepolator** in FontForge's Font view.
- **Smart Selection Guard:** Automatically enables the menu item only when **exactly 2 glyphs** are selected (otherwise grayed out).
- **Automatic Compatibility Check:** Verifies contour counts, point counts per contour, and component reference counts between both selected glyphs before interpolating, reporting exact mismatches if found.
- **Interactive Step Prompt:** Prompts for the desired number of intermediate interpolated glyphs (default: `5`) each time the tool is executed.
- **Automatic Advance Width Interpolation:** Linearly interpolates both foreground outlines and glyph advance widths, creating unencoded glyph slots named `<glyphname>.interp_<percentage>`.

---

## Installation

Place `simplepolator.py` in FontForge's Python startup directory so it loads automatically when FontForge starts.

### 1. Standard Installations
- **Linux / macOS:**
  Copy `simplepolator.py` to:
  ```text
  ~/.FontForge/python/
  ```
  *(or `~/.config/fontforge/python/` depending on your FontForge build)*

- **Windows (Installed):**
  Copy `simplepolator.py` to:
  ```text
  %APPDATA%\FontForge\python\
  ```

### 2. Portable Installations (Windows)
1. Locate your portable FontForge directory and open the Python startup folder:
   ```text
   <FontForgePortable>\share\fontforge\python\
   ```
   *(Create the `python` folder if it does not already exist. You can verify the exact startup paths inside FontForge via **File > Execute Script...** by running `import fontforge; fontforge.postNotice("Paths", str(fontforge.scriptPath()))`.)*
2. Copy `simplepolator.py` into that folder.

### 3. Activate
Completely restart **FontForge** after copying the file.

---

## Usage

1. Open your font in **FontForge** (Font view).
2. Select **exactly 2 compatible glyphs** (e.g., a Light master glyph and a Bold master glyph).
3. In the top menu bar, click **Tools > Simplepolator**.
   - *If fewer or more than 2 glyphs are selected, **Simplepolator** will appear grayed out.*
   - *If the two glyphs have different contour, point, or reference counts, a warning dialog will display the exact mismatch.*
4. Enter the number of intermediate children you want to generate (e.g., `5`) and click **OK**.
5. FontForge will generate the new interpolated glyphs at the end of the font table named `<first_glyph>.interp_16`, `<first_glyph>.interp_33`, etc.

---

## License & Credits

- **Copyright (c) 2012**, Dave Crossland (`dave@understandingfonts.com`)
- **Copyright (c) 2012**, Michal Nowakowski (`miszka@limes.com.pl`)
- **Copyright (c) 2026**, Stefan Peev (`localfonts.eu@gmail.com`)

Licensed under the **BSD 3-Clause License**. See the header inside `simplepolator.py` for full license terms.
