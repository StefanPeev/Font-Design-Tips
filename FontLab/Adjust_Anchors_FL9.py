#FLM: Adjust Anchors (FontLab 9)
"""
SCRIPT NAME:
Adjust Anchors (FontLab 9)

DESCRIPTION:
Interactive dialog for precision adjustment of anchor coordinates in FontLab 9.
- Displays all glyphs containing anchors with an anchor-name filter dropdown.
- Allows switching between font masters and individual anchors within each glyph.
- Provides directional nudge buttons (±1, ±5, ±20 units) and keyboard arrow shortcuts (Arrows = ±1, Shift+Arrows = ±5, Ctrl+Left/Right = ±20).
- Tracks Original, Shift, and Final X/Y coordinates in real time and syncs updates live with both the Glyph canvas and FontLab's Anchors panel.
- Commits all modified glyphs on OK or restores original positions on Cancel.

COPYRIGHT:
(c) 2026 Stefan Peev (https://github.com/StefanPeev). All rights reserved.
    
DISCLAIMER:
THIS SCRIPT IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR OR COPYRIGHT HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY ARISING FROM THE USE OF THIS SCRIPT. USE AT YOUR OWN RISK.
"""

import fontlab as fl6
from PythonQt import QtCore, QtGui

_dlg = None

def fmt(v):
    return int(v) if v == int(v) else round(v, 2)

def find_fg_glyph(f, gn):
    if f is None or not gn:
        return None
    if hasattr(f, "findGlyph"):
        g = f.findGlyph(gn)
        if g is not None:
            return g
    for g in f.glyphs:
        if str(g.name) == gn:
            return g
    return None

def scan_font():
    f = fl6.CurrentFont()
    if f is None:
        return None, None, [], "", []
    cur_g = fl6.CurrentGlyph()
    init_g = str(cur_g.name) if cur_g is not None else None
    act_lyr = getattr(cur_g, "activeLayer", None) if cur_g is not None else None
    act_m = str(act_lyr.name) if act_lyr is not None else ""
    masters = []
    backup = {}
    all_anchors = set()

    for g in f.glyphs:
        gn = str(g.name)
        g_bak = {}
        for l in list(g.layers):
            if getattr(l, "isMasterLayer", True):
                ln = str(l.name)
                if ln not in masters:
                    masters.append(ln)
                ancs = list(l.anchors)
                if ancs:
                    g_bak[ln] = {}
                    for a in ancs:
                        an = str(a.name)
                        all_anchors.add(an)
                        g_bak[ln][an] = (float(a.x.coordinate), float(a.y.coordinate))
        if g_bak:
            backup[gn] = g_bak

    if not act_m and masters:
        act_m = next(iter(masters))
    return backup, init_g, masters, act_m, sorted(all_anchors)

backup, init_g, masters, act_m, all_anchors = scan_font()
if backup is None:
    QtGui.QMessageBox.warning(None, "Adjust Anchors", "Please open a font first.")
else:
    pending = {}
    st = dict(g=init_g, m=act_m, a=None, xo=0.0, yo=0.0, xf=0.0, yf=0.0, ready=False)

    dlg = QtGui.QDialog()
    _dlg = dlg
    dlg.setWindowTitle("Adjust Anchors")
    dlg.setMinimumWidth(640)
    ml = QtGui.QVBoxLayout(dlg)
    tl = QtGui.QHBoxLayout()

    gl = QtGui.QListWidget()
    gl.setMinimumWidth(155)
    flt = QtGui.QComboBox()
    flt.setFocusPolicy(QtCore.Qt.NoFocus)
    flt.addItem("All anchors")
    for an in all_anchors:
        flt.addItem(an)

    gbx = QtGui.QVBoxLayout()
    gbx.addWidget(QtGui.QLabel("<b>Glyphs</b>"))
    gbx.addWidget(flt)
    gbx.addWidget(gl)

    al = QtGui.QListWidget()
    al.setMinimumWidth(145)
    abx = QtGui.QVBoxLayout()
    abx.addWidget(QtGui.QLabel("<b>Anchors</b>"))
    abx.addWidget(al)

    pad = QtGui.QGridLayout()
    pad.setSpacing(5)
    lbl_s = QtGui.QLabel("x: 0\ny: 0")
    lbl_s.setAlignment(QtCore.Qt.AlignCenter)
    tl.addLayout(gbx)
    tl.addLayout(pad)
    tl.addLayout(abx)
    ml.addLayout(tl)

    bl = QtGui.QHBoxLayout()
    mg, cg = QtGui.QGroupBox("Masters"), QtGui.QGroupBox("Coordinates")
    mly, cly = QtGui.QVBoxLayout(mg), QtGui.QVBoxLayout(cg)
    lbl_o = QtGui.QLabel("Original: x: 0  y: 0")
    lbl_f = QtGui.QLabel("Final:    x: 0  y: 0")
    cly.addWidget(lbl_o)
    cly.addWidget(lbl_f)
    bl.addWidget(mg)
    bl.addWidget(cg)
    ml.addLayout(bl)

    hint = QtGui.QLabel("Shortcuts: Arrows = ±1   |   Shift + Arrows = ±5   |   Ctrl + Left/Right = ±20")
    hint.setStyleSheet("color: gray; font-size: 11px;")
    ml.addWidget(hint)

    br = QtGui.QHBoxLayout()
    br.addStretch()
    b_ok = QtGui.QPushButton("OK")
    b_cn = QtGui.QPushButton("Cancel")
    br.addWidget(b_ok)
    br.addWidget(b_cn)
    ml.addLayout(br)

    def refresh():
        lbl_s.setText(f"x: {fmt(round(st['xf'] - st['xo'], 2))}\ny: {fmt(round(st['yf'] - st['yo'], 2))}")
        lbl_o.setText(f"Original: x: {fmt(st['xo'])}  y: {fmt(st['yo'])}")
        lbl_f.setText(f"Final:    x: {fmt(st['xf'])}  y: {fmt(st['yf'])}")

    def load_c():
        gn, mn, an = st["g"], st["m"], st["a"]
        orig = backup.get(gn, {}).get(mn, {}).get(an)
        cur = pending.get(gn, {}).get(mn, {}).get(an, orig)
        if orig is None or cur is None:
            st.update(xo=0.0, yo=0.0, xf=0.0, yf=0.0)
        else:
            ox, oy = orig
            cx, cy = cur
            st.update(xo=round(ox, 2), yo=round(oy, 2), xf=round(cx, 2), yf=round(cy, 2))
        refresh()

    def apply_glyph(gn, m_map):
        f = fl6.CurrentFont()
        g = find_fg_glyph(f, gn)
        if g is None:
            return
        for l in list(g.layers):
            ln = str(l.name)
            if ln in m_map:
                a_dict = m_map[ln]
                for a in list(l.anchors):
                    an = str(a.name)
                    if an in a_dict:
                        nx, ny = a_dict[an]
                        cx, cy = float(a.x.coordinate), float(a.y.coordinate)
                        a.move(float(nx) - cx, float(ny) - cy)
        g.update()
        f.update()
        fl6.AcceptChanges(True)
        ws = fl6.flWorkspace.instance()
        if ws is not None:
            fp = getattr(ws, "currentFontPanel", None) or getattr(ws, "activeFontPanel", None)
            if fp is not None and hasattr(fp, "update"):
                fp.update()
        fl6.SetCurrentGlyph(g)

    def nudge(dx, dy):
        gn, mn, an = st["g"], st["m"], st["a"]
        orig = backup.get(gn, {}).get(mn, {}).get(an)
        cur = pending.get(gn, {}).get(mn, {}).get(an, orig)
        if cur is None:
            return
        cx, cy = cur
        nx, ny = round(cx + dx, 2), round(cy + dy, 2)
        st.update(xf=nx, yf=ny)
        pending.setdefault(gn, {}).setdefault(mn, {})[an] = (nx, ny)
        apply_glyph(gn, {mn: {an: (nx, ny)}})
        refresh()

    def sel_row(lw, name):
        for r in range(lw.count):
            if lw.item(r).text() == name:
                lw.setCurrentRow(r)
                return True
        return False

    def fill_a():
        f_anc = flt.currentText
        prev = f_anc if f_anc != "All anchors" else st["a"]
        al.blockSignals(True)
        al.clear()
        st["a"] = None
        for an in backup.get(st["g"], {}).get(st["m"], {}):
            al.addItem(an)
        al.blockSignals(False)
        if not (prev and sel_row(al, prev)):
            if al.count > 0:
                al.setCurrentRow(0)
            else:
                load_c()

    def fill_g(target_g=None):
        f_anc = flt.currentText
        prev_g = target_g if target_g is not None else st["g"]
        gl.blockSignals(True)
        gl.clear()
        for gn, m_map in backup.items():
            if f_anc == "All anchors":
                gl.addItem(gn)
            else:
                if f_anc in m_map.get(st["m"], {}) or any(f_anc in a_map for a_map in m_map.values()):
                    gl.addItem(gn)
        gl.blockSignals(False)
        if not (prev_g and sel_row(gl, prev_g)):
            if gl.count > 0:
                gl.setCurrentRow(0)
            else:
                st["g"] = None
                fill_a()

    def on_g(r):
        if r >= 0:
            gn = gl.item(r).text()
            st["g"] = gn
            if st["ready"]:
                g = find_fg_glyph(fl6.CurrentFont(), gn)
                if g is not None:
                    fl6.SetCurrentGlyph(g)
            fill_a()

    def on_ok():
        for gn, m_map in pending.items():
            apply_glyph(gn, m_map)
        dlg.close()

    def on_cn():
        for gn, m_map in pending.items():
            orig_m = {
                mn: {an: backup[gn][mn][an] for an in a_map if an in backup.get(gn, {}).get(mn, {})}
                for mn, a_map in m_map.items()
            }
            apply_glyph(gn, orig_m)
        dlg.close()

    for lbl, dx, dy, r, c in [("+5",0,5,0,3),("+1",0,1,1,3),("-20",-20,0,2,0),("-5",-5,0,2,1),("-1",-1,0,2,2),("+1",1,0,2,4),("+5",5,0,2,5),("+20",20,0,2,6),("-1",0,-1,3,3),("-5",0,-5,4,3)]:
        b = QtGui.QPushButton(lbl)
        b.setFixedSize(42, 34)
        b.setFocusPolicy(QtCore.Qt.NoFocus)
        b.clicked.connect(lambda chk=False, x=dx, y=dy: nudge(x, y))
        pad.addWidget(b, r, c)
    pad.addWidget(lbl_s, 2, 3)

    for mn in masters:
        rb = QtGui.QRadioButton(mn)
        rb.setChecked(mn == act_m)
        rb.setFocusPolicy(QtCore.Qt.NoFocus)
        rb.toggled.connect(lambda chk, n=mn: (st.update(m=n), fill_g()) if chk else None)
        mly.addWidget(rb)

    for seq, dx, dy in [
        ("Up", 0, 1), ("Down", 0, -1), ("Left", -1, 0), ("Right", 1, 0),
        ("Shift+Up", 0, 5), ("Shift+Down", 0, -5), ("Shift+Left", -5, 0), ("Shift+Right", 5, 0),
        ("Ctrl+Left", -20, 0), ("Ctrl+Right", 20, 0),
    ]:
        sc = QtGui.QShortcut(QtGui.QKeySequence(seq), dlg)
        sc.activated.connect(lambda x=dx, y=dy: nudge(x, y))

    flt.currentIndexChanged.connect(lambda idx: fill_g())
    gl.currentRowChanged.connect(on_g)
    al.currentRowChanged.connect(lambda r: (st.update(a=al.item(r).text() if r >= 0 else None), load_c()))
    b_ok.clicked.connect(lambda chk=False: on_ok())
    b_cn.clicked.connect(lambda chk=False: on_cn())

    fill_g(init_g)

    st["ready"] = True
    dlg.show()
    dlg.raise_()
    dlg.activateWindow()
