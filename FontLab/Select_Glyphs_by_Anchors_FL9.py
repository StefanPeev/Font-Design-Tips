#FLM: Select Glyphs by Anchor (FontLab 9)
"""
Script Name:   Select Glyphs by Anchor (FontLab 9)
Description:   Scans master layers for anchor names and previews, selects in the
               Font Window, or opens in a Glyph Window tab matching glyphs.
Copyright:     (c) 2026 Stefan Peev (https://github.com/StefanPeev). All rights reserved.
Disclaimer:    THIS SCRIPT IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
               EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
               OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
               NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR OR COPYRIGHT
               HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY
               ARISING FROM THE USE OF THIS SCRIPT. USE AT YOUR OWN RISK.
"""

import traceback
import fontlab as fl6
from PythonQt import QtCore, QtGui

_sel_anc_dlg = None
MAX_GW_OPEN = 150


def scan_anchors():
    f = fl6.CurrentFont()
    if f is None:
        return None, [], {}, "", set()
    cur_g = fl6.CurrentGlyph()
    act_lyr = getattr(cur_g, "activeLayer", None) if cur_g is not None else None
    act_m = str(act_lyr.name) if act_lyr is not None else ""
    all_anc, all_m, g_anc, g_ord = set(), set(), {}, []
    for g in f.glyphs:
        gn = str(g.name)
        g_ord.append(gn)
        m_map = {}
        for l in list(g.layers):
            if getattr(l, "isMasterLayer", True):
                ln = str(l.name)
                all_m.add(ln)
                if not act_m:
                    act_m = ln
                names = {str(a.name) for a in list(l.anchors)}
                if names:
                    m_map[ln] = names
                    all_anc.update(names)
        if m_map:
            g_anc[gn] = m_map
    return sorted(all_anc), g_ord, g_anc, act_m, all_m


def select_in_fw(font_obj, names, add=False):
    try:
        from FL import fl
        if not add:
            fl.Unselect()
        for gn in names:
            fl.Select(gn)
        fl6.Update(font_obj)
    except Exception as e:
        print("Select warning:", e)


def open_in_gw(font_obj, names):
    """Opens the selected glyphs in a new Glyph Window tab via FontLab's Edit Glyphs action."""
    if not names:
        return

    # 1. Try fontlabapp controller if available in FontLab 9
    try:
        from fontlabapp import Application
        app = Application(with_ui=True, with_preflib=False)
        with app.control as flc:
            flc.action("Edit Glyphs").trigger()
            return
    except Exception:
        pass

    # 2. Trigger FontLab's native "Edit Glyphs" QAction from the main window
    try:
        ws = fl6.flWorkspace.instance()
        mw = ws.mainWindow
        mw.activateWindow()
        QtGui.QApplication.processEvents()
        for act in mw.findChildren(QtGui.QAction):
            txt = str(act.text).replace("&", "").strip()
            if txt == "Edit Glyphs" and act.enabled:
                act.trigger()
                return
    except Exception as e:
        print("Edit Glyphs action warning:", e)


all_anchors, glyph_order, glyph_anchors, act_m, all_masters = scan_anchors()

if all_anchors is None:
    QtGui.QMessageBox.warning(None, "Select Glyphs by Anchor", "Please open a font first.")
elif not all_anchors:
    QtGui.QMessageBox.information(None, "Select Glyphs by Anchor", "No anchors were found in this font.")
else:
    if _sel_anc_dlg is not None:
        try:
            _sel_anc_dlg.close()
        except Exception:
            pass

    dlg = QtGui.QDialog()
    _sel_anc_dlg = dlg
    dlg.setWindowTitle("Select Glyphs by Anchor")
    dlg.resize(450, 490)
    ml = QtGui.QVBoxLayout(dlg)

    # 1. Anchor Name
    top = QtGui.QHBoxLayout()
    top.addWidget(QtGui.QLabel("<b>Anchor name:</b>"))
    cb_anc = QtGui.QComboBox()
    cb_anc.setEditable(True)
    for an in all_anchors:
        cb_anc.addItem(an)
    top.addWidget(cb_anc, 1)
    ml.addLayout(top)

    # 2. Scope & Inversion Toggles
    grp = QtGui.QGroupBox("Search Scope & Filter")
    gl = QtGui.QVBoxLayout(grp)
    chk_act = QtGui.QCheckBox(f"Search in active master only ({act_m})")
    chk_all = QtGui.QCheckBox(f"Require anchor in ALL masters ({len(all_masters)} masters)")
    chk_inv = QtGui.QCheckBox("Invert match (select glyphs WITHOUT this anchor)")
    gl.addWidget(chk_act)
    gl.addWidget(chk_all)
    gl.addWidget(chk_inv)
    ml.addWidget(grp)

    # 3. Live Preview List
    lbl_cnt = QtGui.QLabel("<b>Matching glyphs:</b> 0")
    ml.addWidget(lbl_cnt)
    lst = QtGui.QListWidget()
    lst.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
    ml.addWidget(lst, 1)

    def get_matches():
        raw = cb_anc.currentText() if callable(cb_anc.currentText) else cb_anc.currentText
        target = str(raw).strip()
        only_a, req_all, inv = chk_act.isChecked(), chk_all.isChecked(), chk_inv.isChecked()
        mc = max(1, len(all_masters))
        res = []
        for gn in glyph_order:
            mm = glyph_anchors.get(gn, {})
            if only_a:
                has = target in mm.get(act_m, set())
            elif req_all:
                has = len(mm) >= mc and all(target in mm.get(m, set()) for m in all_masters)
            else:
                has = any(target in s for s in mm.values())
            if (has and not inv) or (not has and inv):
                res.append(gn)
        return res

    def update_preview(*args):
        chk_all.setEnabled(not chk_act.isChecked())
        m = get_matches()
        lbl_cnt.setText(f"<b>Matching glyphs:</b> {len(m)}")
        lst.clear()
        lst.addItems(m)

    def on_dbl_click(item):
        f = fl6.CurrentFont()
        if f and item:
            txt = item.text() if callable(item.text) else item.text
            gn = str(txt)
            select_in_fw(f, [gn], False)
            open_in_gw(f, [gn])

    # 4. Execution Controls
    chk_add = QtGui.QCheckBox("Add to current Font Window selection")
    ml.addWidget(chk_add)

    brow = QtGui.QHBoxLayout()
    btn_close = QtGui.QPushButton("Close")
    btn_gw = QtGui.QPushButton("Open in Glyph Window")
    btn_fw = QtGui.QPushButton("Select in Font Window")
    btn_fw.setDefault(True)
    brow.addWidget(btn_close)
    brow.addStretch(1)
    brow.addWidget(btn_gw)
    brow.addWidget(btn_fw)
    ml.addLayout(brow)

    def run_action(open_tab):
        try:
            f = fl6.CurrentFont()
            if f is None:
                return
            m = get_matches()
            if not m:
                QtGui.QMessageBox.information(dlg, "Select Glyphs by Anchor", "No matching glyphs.")
                return
            if open_tab and len(m) > MAX_GW_OPEN:
                q = QtGui.QMessageBox.question(
                    dlg, "Open Many Glyphs",
                    f"Matched {len(m)} glyphs. Open first {MAX_GW_OPEN}?",
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel,
                )
                if q == QtGui.QMessageBox.Cancel:
                    return
                if q == QtGui.QMessageBox.Yes:
                    m = m[:MAX_GW_OPEN]
            dlg.hide()
            select_in_fw(f, m, chk_add.isChecked())
            if open_tab:
                open_in_gw(f, m)
            dlg.close()
        except Exception:
            print(traceback.format_exc())

    def on_fw():
        run_action(False)

    def on_gw():
        run_action(True)

    cb_anc.editTextChanged.connect(update_preview)
    chk_act.toggled.connect(update_preview)
    chk_all.toggled.connect(update_preview)
    chk_inv.toggled.connect(update_preview)
    lst.itemDoubleClicked.connect(on_dbl_click)
    btn_close.clicked.connect(dlg.close)
    btn_fw.clicked.connect(on_fw)
    btn_gw.clicked.connect(on_gw)

    update_preview()
    dlg.show()
