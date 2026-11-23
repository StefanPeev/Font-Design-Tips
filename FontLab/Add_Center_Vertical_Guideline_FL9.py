#FLM: Add Center Vertical Guideline (width/2) (FontLab 9)
"""
Description:
    Adds a dynamic local vertical guideline with the expression "width/2" to the
    active layer of all selected glyphs in FontLab 9 (falling back to the active
    glyph in the Glyph Window if none are selected in the Font Window). Skips
    glyphs that already have a vertical guideline with the "width/2" expression.

Copyright:
    Copyright (c) 2026 Stefan Peev (https://github.com/StefanPeev). All rights reserved.

Disclaimer:
    This script is provided "as is", without warranty of any kind, express or
    implied. Always save a backup of your font file before running batch
    modification scripts. The author is not liable for any data loss or
    unintended changes to your font files.
"""

import fontlab as fl
import FL
from PythonQt.QtCore import QLineF

ws = fl.flWorkspace.instance()
package = ws.currentPackage

if package is not None:
    selected_names = []

    # 1. Check Font Window selection
    if hasattr(package, "selectedGlyphs") and package.selectedGlyphs:
        for item in package.selectedGlyphs:
            name = item.name if hasattr(item, "name") else str(item)
            if name:
                selected_names.append(name)
    elif FL.fl.font is not None:
        for i in range(len(FL.fl.font)):
            if FL.fl.Selected(i):
                selected_names.append(FL.fl.font[i].name)

    # 2. Fall back to the active glyph in an open Glyph Window
    if not selected_names:
        current = fl.CurrentGlyph()
        if current is not None and current.name:
            selected_names.append(current.name)

    glyph_guide_style = fl.SnapObjectsStyle["gsGlyphGuideline"]
    added = 0

    for name in selected_names:
        glyph = package.findName(name)
        if glyph is not None:
            fl_layer = glyph.activeLayer
            if fl_layer is not None:
                existing = fl_layer.guidelines or []
                already_exists = any(
                    (str(g.expression) if g.expression is not None else "").replace(" ", "") == "width/2"
                    for g in existing
                )

                if not already_exists:
                    center_x = float(fl_layer.advanceWidth) / 2.0

                    guide = fl.flGuideLine(QLineF(center_x, 0.0, center_x, 100.0))
                    guide.style = glyph_guide_style
                    guide.expression = "width/2"

                    fl_layer.appendGuidelines([guide])
                    fl_layer.bindDependencies()
                    fl_layer.update()
                    glyph.update()
                    added += 1

    package.update()
    fl.UpdateActiveCanvas()
    print(f"Added dynamic 'width/2' vertical guidelines to {added} glyph(s).")
else:
    print("No active font open.")
