"""
SCRIPT NAME: Compare Two Open Fonts
DESCRIPTION: Compares the first two open fonts in FontLab 9 by glyph names and generates a text report listing the missing glyphs in each font.
COPYRIGHT: (c) 2026 Stefan Peev (https://github.com/StefanPeev). All rights reserved.
DISCLAIMER: This script is provided "as is", without warranty of any kind, express or implied. In no event shall the author be liable for any claim, damages, or other liability arising from the use of this script.
LICENSE: MIT
"""

import os
import fontlab as fl

def compare_open_fonts():
    # Get all currently open fonts in FontLab 9
    fonts = fl.AllFonts()
    
    if len(fonts) < 2:
        print("Error: Please open at least two fonts in FontLab 9 to compare them.")
        return

    # Select the first two open fonts
    font1 = fonts[0]
    font2 = fonts[1]

    # Extract font names (or file names if metadata is missing)
    name1 = getattr(font1.info, "familyName", None) or os.path.basename(font1.path) or "Font_1"
    style1 = getattr(font1.info, "styleName", "")
    full_name1 = f"{name1} {style1}".strip()

    name2 = getattr(font2.info, "familyName", None) or os.path.basename(font2.path) or "Font_2"
    style2 = getattr(font2.info, "styleName", "")
    full_name2 = f"{name2} {style2}".strip()

    # Collect glyph names from both fonts
    glyphs1 = {g.name for g in font1.glyphs if g.name}
    glyphs2 = {g.name for g in font2.glyphs if g.name}

    # Calculate missing glyphs
    missing_in_1 = sorted(list(glyphs2 - glyphs1))
    missing_in_2 = sorted(list(glyphs1 - glyphs2))

    # Format the text report
    lines = [
        "GLYPH COMPARISON REPORT",
        "=" * 50,
        f"Font 1: {full_name1} (Total glyphs: {len(glyphs1)})",
        f"Font 2: {full_name2} (Total glyphs: {len(glyphs2)})",
        "=" * 50,
        "",
        f"Missing in '{full_name1}' ({len(missing_in_1)} glyphs):",
        "-" * 50,
    ]

    if missing_in_1:
        lines.extend(missing_in_1)
    else:
        lines.append("(No missing glyphs)")

    lines.extend([
        "",
        f"Missing in '{full_name2}' ({len(missing_in_2)} glyphs):",
        "-" * 50,
    ])

    if missing_in_2:
        lines.extend(missing_in_2)
    else:
        lines.append("(No missing glyphs)")

    report_text = "\n".join(lines)

    # Print the report in FontLab's Output panel
    print(report_text)

    # Prompt the user to save the text file
    save_path = fl.GetFileName(0, "txt", "glyph_comparison.txt", "Text Files (*.txt)")
    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"\nReport successfully saved to: {save_path}")

if __name__ == "__main__":
    compare_open_fonts()
