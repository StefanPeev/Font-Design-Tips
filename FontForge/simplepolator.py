# FontForge Simplepolator v.2.0
#
# Copyright (c) 2012, Dave Crossland (dave@understandingfonts.com)
# Copyright (c) 2012, Michal Nowakowski (miszka@limes.com.pl)
# Copyright (c) 2026, Stefan Peev (localfonts.eu@gmail.com)
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
#   The name of the author may not be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED
#   WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#   MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
#   EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#   OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
A FontForge plug-in to generate interpolated instances from 2 characters.

Inspired by the Simplepolator FontLab/RoboFont script by Pablo Impallari
found at http://impallari.com
to easily apply the Gunnlaugur SE Briem's method
http://66.147.242

Copy to ~/.FontForge/python/ and then find "Simplepolator" in the Tools menu,
active when 2 characters are selected.
"""

import fontforge

def check_glyph_compatibility(g1, g2):
    layer1 = g1.foreground
    layer2 = g2.foreground

    # 1. Check contour count
    if len(layer1) != len(layer2):
        return False, (
            f"Contour count mismatch:\n"
            f"• {g1.glyphname}: {len(layer1)} contour(s)\n"
            f"• {g2.glyphname}: {len(layer2)} contour(s)"
        )

    # 2. Check point count in each matching contour
    for idx, (c1, c2) in enumerate(zip(layer1, layer2)):
        if len(c1) != len(c2):
            return False, (
                f"Point count mismatch in contour #{idx + 1}:\n"
                f"• {g1.glyphname}: {len(c1)} point(s)\n"
                f"• {g2.glyphname}: {len(c2)} point(s)"
            )

    # 3. Check component reference count
    if len(g1.references) != len(g2.references):
        return False, (
            f"Reference count mismatch:\n"
            f"• {g1.glyphname}: {len(g1.references)} reference(s)\n"
            f"• {g2.glyphname}: {len(g2.references)} reference(s)"
        )

    return True, ""

def enable_simplepolator(data, font):
    # Enable the menu item only when exactly 2 glyphs are selected
    selected = [g for g in font.selection.byGlyphs]
    return len(selected) == 2

def run_simplepolator(data, font):
    selected = [g for g in font.selection.byGlyphs]

    if len(selected) != 2:
        fontforge.postError("Simplepolator", "Please select exactly 2 compatible glyphs.")
        return

    g1, g2 = selected[0], selected[1]

    # Run compatibility check before prompting or interpolating
    is_compatible, error_msg = check_glyph_compatibility(g1, g2)
    if not is_compatible:
        fontforge.postError(
            "Simplepolator - Incompatible Glyphs",
            f"Cannot interpolate '{g1.glyphname}' and '{g2.glyphname}'.\n\n{error_msg}"
        )
        return

    # Prompt the user for the number of intermediate instances (default: "5")
    answer = fontforge.askString(
        "Simplepolator",
        "Number of intermediate children to generate:",
        "5"
    )

    # Exit quietly if the user clicks Cancel or leaves it blank
    if not answer:
        return

    try:
        steps = int(answer.strip())
        if steps < 1:
            raise ValueError
    except ValueError:
        fontforge.postError("Simplepolator", "Please enter a valid positive whole number.")
        return

    for i in range(1, steps + 1):
        factor = i / (steps + 1)
        new_name = f"{g1.glyphname}.interp_{int(factor * 100)}"
        
        # Create a new glyph slot to hold the interpolation
        new_glyph = font.createChar(-1, new_name)
        new_glyph.foreground = g1.foreground.interpolateNewLayer(g2.foreground, factor)
        new_glyph.width = int(g1.width + (g2.width - g1.width) * factor)

    fontforge.postNotice("Simplepolator", f"Generated {steps} interpolated glyphs.")

fontforge.registerMenuItem(
    run_simplepolator,
    enable_simplepolator,
    None,
    "Font",
    None,
    "Simplepolator"
)
