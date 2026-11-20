#FLM: Anchor Names (FontLab 9)
"""
Description:
    Checks all base glyphs across all masters in the current FontLab 9 font,
    automatically skipping composite glyphs (glyphs containing components or
    referenced elements). If an anchor exists in at least one master, this
    script copies any missing anchors into the remaining masters using the first
    available coordinates, and selects the modified base glyphs in the Font
    Window for manual adjustment.

Copyright:
    Copyright (c) 2026 Stefan Peev (https://github.com/StefanPeev). All rights reserved.

Disclaimer:
    This script is provided "as is", without warranty of any kind, express or
    implied. Always save a backup of your font file before running batch
    modification scripts. The author is not liable for any data loss or
    unintended changes to your font files.
"""

import fontlab as fl

def is_composite_layer(layer):
    """Returns True if the flLayer contains component/element references."""
    # Check modern FontLab flShape list for component shapes
    shapes = layer.shapes() if callable(layer.shapes) else getattr(layer, "shapes", [])
    if shapes:
        for shape in shapes:
            # Check if shape is a component (has componentGlyph / isComponent / shapeData)
            if getattr(shape, "isComponent", False):
                return True
            s_data = shape.shapeData if hasattr(shape, "shapeData") else None
            if s_data and getattr(s_data, "componentGlyph", None):
                return True
            if hasattr(shape, "componentGlyph") and shape.componentGlyph:
                return True

    # Fallback check for older elements / components properties
    for attr in ("components", "elements"):
        if hasattr(layer, attr):
            val = getattr(layer, attr)
            items = val() if callable(val) else val
            if items and len(items) > 0:
                # For elements, check if any element references another glyph
                if attr == "elements":
                    for el in items:
                        if getattr(el, "componentGlyph", None) or getattr(el, "isComponent", False):
                            return True
                else:
                    return True
    return False


def sync_base_glyph_anchors():
    font = fl.CurrentFont()
    if not font:
        print("Error: No open font in FontLab 9.")
        return

    pkg = fl.flPackage(font)
    
    # Get the list of master names in the font
    raw_masters = pkg.masters if hasattr(pkg, "masters") else pkg.layers
    master_names = [m if isinstance(m, str) else m.name for m in raw_masters]
    
    if len(master_names) < 2:
        print(f"The font has only {len(master_names)} master. Nothing to compare.")
        return

    print(f"Checking base glyphs across {len(master_names)} masters: {', '.join(master_names)}")
    print("-" * 60)

    fixed_glyphs = []
    skipped_composites = 0

    for glyph in font.glyphs:
        fl_glyph = fl.flGlyph(glyph, font)
        layers_dict = {lyr.name: lyr for lyr in fl_glyph.layers}
        
        # 1. Skip if the glyph is a composite in any master
        is_composite = any(
            is_composite_layer(layers_dict[m_name])
            for m_name in master_names
            if m_name in layers_dict
        )
        
        if is_composite:
            skipped_composites += 1
            continue

        # 2. Collect all anchors per master and build a master union of anchor names
        anchors_by_master = {}
        all_expected_anchors = {}  # {anchor_name: source_anchor_object}
        
        for m_name in master_names:
            layer = layers_dict.get(m_name)
            if layer:
                raw_anchors = layer.anchors() if callable(layer.anchors) else layer.anchors
                anc_map = {a.name: a for a in raw_anchors}
                anchors_by_master[m_name] = anc_map
                
                for a_name, a_obj in anc_map.items():
                    if a_name not in all_expected_anchors:
                        all_expected_anchors[a_name] = a_obj
            else:
                anchors_by_master[m_name] = None

        if not all_expected_anchors:
            continue

        # 3. Copy any missing anchors into masters that lack them
        glyph_modified = False
        log_lines = []

        for m_name in master_names:
            layer = layers_dict.get(m_name)
            anc_map = anchors_by_master.get(m_name)
            
            if layer is None or anc_map is None:
                continue

            missing_names = [name for name in sorted(all_expected_anchors.keys()) if name not in anc_map]
            
            if missing_names:
                glyph_modified = True
                for missing_name in missing_names:
                    src_anchor = all_expected_anchors[missing_name]
                    new_anchor = src_anchor.clone() if hasattr(src_anchor, "clone") else fl.flAnchor(src_anchor.name, src_anchor.point)
                    
                    if hasattr(layer, "addAnchor"):
                        layer.addAnchor(new_anchor)
                    else:
                        layer.anchors.append(new_anchor)
                
                log_lines.append(f"   • [{m_name}]: added {', '.join(missing_names)}")

        if glyph_modified:
            fixed_glyphs.append(glyph.name)
            fl_glyph.update()
            print(f"Fixed base glyph: /{glyph.name}")
            for line in log_lines:
                print(line)

    print("-" * 60)
    print(f"Skipped {skipped_composites} composite glyphs.")
    
    if not fixed_glyphs:
        print("Success! All base glyphs already have identical anchors across all masters.")
    else:
        print(f"Added missing anchors in {len(fixed_glyphs)} base glyph(s).")
        
        # Safely update selection in Font Window
        fixed_set = set(fixed_glyphs)
        for g in font.glyphs:
            g.selected = (g.name in fixed_set)
        pkg.update()
        
        print("Modified base glyphs have been selected in the Font Window so you can adjust anchor positions.")

sync_base_glyph_anchors()
