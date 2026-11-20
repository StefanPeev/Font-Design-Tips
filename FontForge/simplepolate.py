import fontforge

font = fontforge.activeFont()
selected = [g for g in font.selection.byGlyphs]

if len(selected) != 2:
    fontforge.postError("Simplepolator", "Please select exactly 2 compatible glyphs.")
else:
    g1, g2 = selected[0], selected[1]
    steps = 5  # Number of intermediate instances to generate

    for i in range(1, steps + 1):
        factor = i / (steps + 1)
        new_name = f"{g1.glyphname}.interp_{int(factor * 100)}"
        
        # Create a new glyph slot to hold the interpolation
        new_glyph = font.createChar(-1, new_name)
        new_glyph.foreground = g1.foreground.interpolateNewLayer(g2.foreground, factor)
        new_glyph.width = int(g1.width + (g2.width - g1.width) * factor)

    fontforge.postNotice("Simplepolator", f"Generated {steps} interpolated glyphs.")
