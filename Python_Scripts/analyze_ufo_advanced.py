import os
import sys
import unicodedata
from fontTools.ufoLib import UFOReader
from fontTools.unicodedata import Blocks


class MinimalGlyph:
    """Lightweight helper object to capture glyph metadata without parsing outlines."""
    def __init__(self):
        self.unicodes = []
        self.unicode = None


def load_unicode_blocks():
    """Loads all official Unicode blocks from fontTools built-in database."""
    blocks = []
    ranges = Blocks.RANGES
    values = Blocks.VALUES

    for i in range(len(values)):
        start_cp = ranges[i]
        # End of current block is one before the start of the next block (or 0x10FFFF for the last)
        end_cp = (ranges[i + 1] - 1) if (i + 1 < len(ranges)) else 0x10FFFF
        name = values[i]

        if name != "No_Block":
            clean_name = name.replace("_", " ")
            blocks.append((start_cp, end_cp, clean_name))

    return blocks


def get_assigned_codepoints(start_cp, end_cp):
    """Returns a list of all officially assigned (non-reserved) Unicode codepoints in a block."""
    assigned = []
    for cp in range(start_cp, end_cp + 1):
        try:
            char = chr(cp)
            cat = unicodedata.category(char)
            if cat not in ("Cn", "Cs"):
                assigned.append(cp)
        except ValueError:
            continue
    return assigned


def find_block_for_cp(codepoint, blocks):
    """Finds the corresponding Unicode block for a given codepoint using binary search."""
    low, high = 0, len(blocks) - 1
    while low <= high:
        mid = (low + high) // 2
        start, end, name = blocks[mid]
        if start <= codepoint <= end:
            return blocks[mid]
        elif codepoint < start:
            high = mid - 1
        else:
            low = mid + 1
    return None


def analyze_single_ufo(ufo_path, output_dir, blocks):
    """Analyzes a single .ufo font and writes a tabular text report."""
    font_filename = os.path.basename(os.path.normpath(ufo_path))
    base_name, _ = os.path.splitext(font_filename)
    output_txt_path = os.path.join(output_dir, f"{base_name}_unicode_report.txt")

    try:
        reader = UFOReader(ufo_path)
        glyph_set = reader.getGlyphSet()
    except Exception as e:
        print(f"[ERROR] Failed to read {ufo_path}: {e}")
        return

    # Collect all unique Unicode codepoints by explicitly reading each .glif file
    font_codepoints = set()
    for glyph_name in glyph_set.keys():
        g = MinimalGlyph()
        try:
            glyph_set.readGlyph(glyph_name, g)
        except Exception:
            continue

        if g.unicodes:
            font_codepoints.update(g.unicodes)
        elif g.unicode is not None:
            font_codepoints.add(g.unicode)

    # Group found codepoints by Unicode block
    active_blocks = {}
    for cp in font_codepoints:
        block = find_block_for_cp(cp, blocks)
        if block is not None:
            if block not in active_blocks:
                active_blocks[block] = set()
            active_blocks[block].add(cp)

    # Sort blocks by starting codepoint (keys are tuples of (start_cp, end_cp, block_name))
    sorted_blocks = sorted(active_blocks.items(), key=lambda item: item[0][0])

    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(f"UNICODE FONT ANALYSIS: {font_filename}\n")
        f.write(f"Total unique Unicode codepoints in font: {len(font_codepoints)}\n")
        f.write(f"Total active Unicode blocks detected: {len(sorted_blocks)}\n")
        f.write("=" * 115 + "\n\n")

        header = (
            f"{'Unicode Block Name':<42}\t"
            f"{'Unicode Range':<22}\t"
            f"{'Found / Total':<15}\t"
            f"{'Coverage %'}\n"
        )
        f.write(header)
        f.write("-" * 115 + "\n")

        missing_details = []

        for (start_cp, end_cp, block_name), present_cps in sorted_blocks:
            assigned_cps = get_assigned_codepoints(start_cp, end_cp)
            total_assigned = len(assigned_cps)
            found_count = len(present_cps)

            if total_assigned > 0:
                coverage = (found_count / total_assigned) * 100
            else:
                total_assigned = (end_cp - start_cp) + 1
                coverage = (found_count / total_assigned) * 100

            range_str = f"U+{start_cp:04X}..U+{end_cp:04X}"
            ratio_str = f"{found_count} / {total_assigned}"
            cov_str = f"{coverage:.2f}%"

            f.write(f"{block_name:<42}\t{range_str:<22}\t{ratio_str:<15}\t{cov_str}\n")

            if found_count < total_assigned and "Private Use" not in block_name:
                missing_cps = sorted(set(assigned_cps) - present_cps)
                if missing_cps:
                    missing_details.append((block_name, range_str, missing_cps))

        f.write("\n" + "=" * 115 + "\n")
        f.write("DETAILED LIST OF MISSING CHARACTERS BY BLOCK\n")
        f.write("=" * 115 + "\n\n")

        if not missing_details:
            f.write("All detected Unicode blocks are 100% complete!\n")
        else:
            for block_name, range_str, missing_cps in missing_details:
                f.write(f"Block: {block_name} ({range_str}) - Missing {len(missing_cps)} characters:\n")
                formatted_missing = []
                for cp in missing_cps:
                    char_name = unicodedata.name(chr(cp), "UNKNOWN")
                    formatted_missing.append(f"  - U+{cp:04X} ({char_name})")
                f.write("\n".join(formatted_missing) + "\n\n")

    print(f"[OK] Report generated: {output_txt_path} ({len(font_codepoints)} codepoints across {len(sorted_blocks)} blocks)")


def process_target(target_path, output_dir="unicode_reports"):
    """Processes a single .ufo font or scans a directory for multiple .ufo fonts."""
    if not os.path.exists(target_path):
        print(f"Error: Path '{target_path}' does not exist.")
        return

    os.makedirs(output_dir, exist_ok=True)
    blocks = load_unicode_blocks()

    ufo_list = []

    if target_path.lower().endswith(".ufo") and os.path.isdir(target_path):
        ufo_list.append(target_path)
    elif os.path.isdir(target_path):
        for root, dirs, _ in os.walk(target_path):
            for d in dirs:
                if d.lower().endswith(".ufo"):
                    ufo_list.append(os.path.join(root, d))
            dirs[:] = [d for d in dirs if not d.lower().endswith(".ufo")]

    if not ufo_list:
        print(f"No .ufo fonts found in '{target_path}'.")
        return

    print(f"Found {len(ufo_list)} UFO font(s). Starting analysis...\n")
    for ufo in sorted(ufo_list):
        analyze_single_ufo(ufo, output_dir, blocks)

    print(f"\nAll reports saved to: '{os.path.abspath(output_dir)}'")


if __name__ == "__main__":
    TARGET_PATH = "./fonts_folder"
    OUTPUT_FOLDER = "./unicode_reports"

    if len(sys.argv) > 1:
        TARGET_PATH = sys.argv[1]
    if len(sys.argv) > 2:
        OUTPUT_FOLDER = sys.argv[2]

    process_target(TARGET_PATH, OUTPUT_FOLDER)
