import fontlab as fl

def check_anchors_across_masters():
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

    print(f"Checking {len(font)} glyphs across {len(master_names)} masters: {', '.join(master_names)}")
    print("-" * 60)

    mismatched_glyphs = []
    
    # Safely extract the first master's name and the list of remaining masters
    first_master, *other_masters = master_names

    for glyph in font.glyphs:
        fl_glyph = fl.flGlyph(glyph, font)
        layers_dict = {lyr.name: lyr for lyr in fl_glyph.layers}
        anchors_by_master = {}
        
        for m_name in master_names:
            layer = layers_dict.get(m_name)
            if layer:
                raw_anchors = layer.anchors() if callable(layer.anchors) else layer.anchors
                names = sorted([a.name for a in raw_anchors])
                anchors_by_master[m_name] = names
            else:
                anchors_by_master[m_name] = None

        # Compare all other masters against the first master
        reference_anchors = anchors_by_master.get(first_master)
        
        is_identical = True
        for m_name in other_masters:
            if anchors_by_master.get(m_name) != reference_anchors:
                is_identical = False
                break

        if not is_identical:
            mismatched_glyphs.append(glyph.name)
            print(f"Mismatch in glyph: /{glyph.name}")
            for m_name in master_names:
                anc_list = anchors_by_master.get(m_name)
                if anc_list is None:
                    print(f"   • [{m_name}]: missing layer")
                elif len(anc_list) == 0:
                    print(f"   • [{m_name}]: no anchors")
                else:
                    print(f"   • [{m_name}]: {', '.join(anc_list)}")

    print("-" * 60)
    if not mismatched_glyphs:
        print("Success! All glyphs have identical anchor names across all masters.")
    else:
        print(f"Mismatches found in a total of {len(mismatched_glyphs)} glyphs.")
        font.unselectAll()
        for g_name in mismatched_glyphs:
            font[g_name].selected = True
        pkg.update()
        print("All mismatched glyphs have been selected in the Font Window.")

check_anchors_across_masters()
