#FLM: Build Combining Diacritical Marks (FontLab 9)
# -----------------------------------------------------------------------------
# SCRIPT NAME: Build Combining Diacritical Marks
# DESCRIPTION: Finds spacing diacritic glyphs in the active font that have a
#              Unicode equivalent in the Combining Diacritical Marks block
#              (U+0300–U+036F), creates or updates each combining mark glyph
#              across all master layers, places the source glyph as a linked
#              Element Reference optically centered along the master's Italic
#              Angle, and sets the advance width to zero.
# COPYRIGHT:   (c) 2026 Stefan Peev (https://github.com). All rights reserved.
#
# DISCLAIMER:
# This script is provided "as is", without warranty of any kind, express or
# implied, including but not limited to the warranties of merchantability,
# fitness for a particular purpose, and noninfringement. In no event shall the
# author or copyright holder be liable for any claim, damages, or other
# liability arising from the use of this script. Use at your own risk.
#
# LICENSE:     MIT License
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----------------------------------------------------------------------------

import math
import fontlab as fl6
import PythonQt as pqt

# Mapping: (Source Names, Target Unicode, Target Names)
COMBINING_MAP = [
    (["grave"],                 0x0300, ["gravecomb", "uni0300"]),
    (["acute"],                 0x0301, ["acutecomb", "uni0301"]),
    (["circumflex"],            0x0302, ["circumflexcomb", "uni0302"]),
    (["tilde"],                 0x0303, ["tildecomb", "uni0303"]),
    (["macron"],                0x0304, ["macroncomb", "uni0304"]),
    (["overline"],              0x0305, ["overlinecomb", "uni0305"]),
    (["breve"],                 0x0306, ["brevecomb", "uni0306"]),
    (["dotaccent"],             0x0307, ["dotaccentcomb", "uni0307"]),
    (["dieresis"],              0x0308, ["dieresiscomb", "uni0308"]),
    (["hookabove"],             0x0309, ["hookabovecomb", "uni0309"]),
    (["ring"],                  0x030A, ["ringcomb", "uni030A"]),
    (["hungarumlaut"],          0x030B, ["hungarumlautcomb", "uni030B"]),
    (["caron"],                 0x030C, ["caroncomb", "uni030C"]),
    (["verticallineabove"],     0x030D, ["verticallineabovecomb", "uni030D"]),
    (["dblverticallineabove"],  0x030E, ["dblverticallineabovecomb", "uni030E"]),
    (["commaaccentturned"],     0x0312, ["commaaccentturnedcomb", "uni0312"]),
    (["gravebelow"],            0x0316, ["gravebelowcomb", "uni0316"]),
    (["acutebelow"],            0x0317, ["acutebelowcomb", "uni0317"]),
    (["horn"],                  0x031B, ["horncomb", "uni031B"]),
    (["dotbelow"],              0x0323, ["dotbelowcomb", "uni0323"]),
    (["dieresisbelow"],         0x0324, ["dieresisbelowcomb", "uni0324"]),
    (["ringbelow"],             0x0325, ["ringbelowcomb", "uni0325"]),
    (["commaaccent"],           0x0326, ["commaaccentcomb", "uni0326"]),
    (["cedilla"],               0x0327, ["cedillacomb", "uni0327"]),
    (["ogonek"],                0x0328, ["ogonekcomb", "uni0328"]),
    (["verticallinebelow"],     0x0329, ["verticallinebelowcomb", "uni0329"]),
    (["brevebelow"],            0x032E, ["brevebelowcomb", "uni032E"]),
    (["macronbelow"],           0x0331, ["macronbelowcomb", "uni0331"]),
    (["lowline"],               0x0332, ["lowlinecomb", "uni0332"]),
    (["dbloverline"],           0x033F, ["dbloverlinecomb", "uni033F"]),
]

SOURCE_UNICODES = {
    0x0300: 0x0060,
    0x0301: 0x00B4,
    0x0302: 0x02C6,
    0x0303: 0x02DC,
    0x0304: 0x00AF,
    0x0305: 0x203E,
    0x0306: 0x02D8,
    0x0307: 0x02D9,
    0x0308: 0x00A8,
    0x030A: 0x02DA,
    0x030B: 0x02DD,
    0x030C: 0x02C7,
    0x0327: 0x00B8,
    0x0328: 0x02DB,
}


def find_fl_glyph(pkg, fg_font, names, unicode_int=None):
    """Find an flGlyph in the active flPackage by name or Unicode."""
    for name in names:
        g = pkg.findName(name)
        if g is not None and not g.isNull:
            return g

    if unicode_int is not None:
        for fg_g in fg_font.glyphs:
            if unicode_int in (fg_g.unicodes or []):
                g = pkg.findName(fg_g.name)
                if g is not None and not g.isNull:
                    return g
    return None


def get_fl_layer(fl_glyph, layer_name):
    """Retrieve a specific flLayer by name from an flGlyph."""
    if hasattr(fl_glyph, "findLayer"):
        lyr = fl_glyph.findLayer(layer_name)
        if lyr is not None and not getattr(lyr, "isNull", False):
            return lyr
    for lyr in (fl_glyph.layers or []):
        if lyr.name == layer_name:
            return lyr
    return None


def get_master_italic_angle(pkg, fg_font, layer_name):
    """Return italic_angle_deg for the given master layer."""
    try:
        master = pkg.findMaster(layer_name)
        if master is not None and hasattr(master, "italicAngle") and master.italicAngle is not None:
            return float(master.italicAngle)
    except Exception:
        pass

    try:
        if fg_font.info.italicAngle is not None:
            return float(fg_font.info.italicAngle)
    except Exception:
        pass

    return 0.0


def main():
    fg_font = fl6.CurrentFont()
    if fg_font is None:
        print("No active font open in FontLab.")
        return

    pkg = fl6.flPackage(fg_font)

    master_names = [m if isinstance(m, str) else m.name for m in (pkg.masters or [])]
    if not master_names:
        am = pkg.activeMaster
        master_names = [am if isinstance(am, str) else am.name]

    processed = []

    for src_names, target_uni, target_names in COMBINING_MAP:
        src_glyph = find_fl_glyph(pkg, fg_font, src_names, SOURCE_UNICODES.get(target_uni))
        if src_glyph is None:
            continue

        # 1. Find or create target combining glyph
        dst_glyph = find_fl_glyph(pkg, fg_font, target_names, target_uni)
        if dst_glyph is None:
            new_name = f"uni{target_uni:04X}"
            dst_glyph = fl6.flGlyph()
            dst_glyph.name = new_name
            pkg.addGlyph(dst_glyph)
            dst_glyph = pkg.findName(new_name)

        # Assign Unicode codepoint
        fg_dst = fg_font[dst_glyph.name]
        if fg_dst is not None:
            fg_dst.unicode = target_uni

        # 2. Process every master layer
        for layer_name in master_names:
            src_layer = get_fl_layer(src_glyph, layer_name)
            dst_layer = get_fl_layer(dst_glyph, layer_name)
            if src_layer is None or dst_layer is None:
                continue

            # Clear existing outlines/components and any previously added _top/_bottom anchors
            dst_layer.removeAllShapes()
            for anc in list(dst_layer.anchors):
                if anc.name in ("_top", "_bottom"):
                    dst_layer.removeAnchor(anc)

            # Read master italic angle
            italic_deg = get_master_italic_angle(pkg, fg_font, layer_name)
            tan_slant = math.tan(math.radians(-italic_deg))

            # Compute optical horizontal shift along the italic slant axis
            src_bbox = src_layer.boundingBox
            if src_bbox.width() > 0:
                src_center_x = src_bbox.x() + (src_bbox.width() / 2.0)
                src_center_y = src_bbox.y() + (src_bbox.height() / 2.0)
                optical_axis_x = src_center_y * tan_slant
                shift_x = optical_axis_x - src_center_x
            else:
                shift_x = 0.0

            # Build QTransform for horizontal optical centering
            tx = pqt.QtGui.QTransform()
            tx.translate(shift_x, 0.0)

            # Place linked Element Reference (GlyphComponent)
            comp = fl6.GlyphComponent(src_glyph.name)
            comp.transform = tx
            dst_layer.setGlyphComponents([comp], 0.0, pkg, False, 0)

            # 3. Ensure advance width is 0
            dst_layer.advanceWidth = 0.0

            dst_layer.update()

        dst_glyph.update()
        processed.append(f"{src_glyph.name} -> {dst_glyph.name} (U+{target_uni:04X})")

    pkg.update()
    print(f"Done. Processed {len(processed)} combining marks:")
    for item in processed:
        print("  ", item)


if __name__ == "__main__":
    main()
