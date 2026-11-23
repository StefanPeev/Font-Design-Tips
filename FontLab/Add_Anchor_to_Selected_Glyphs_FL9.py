#FLM: Add Anchor to Selected Glyphs (FontLab 9)
#
# SCRIPT NAME: Add Anchor to Selected Glyphs
# DESCRIPTION: Adds or updates a named anchor on selected glyphs across the
#              current master or all masters, with fixed or relative X/Y
#              alignment (Advance Width / 2, Bounding Box Center, vertical font
#              metrics), italic angle compensation, skip-existing control, and
#              persistent settings.
# COPYRIGHT:   (c) 2026 Stefan Peev (https://github.com/StefanPeev). All rights reserved.
#
# DISCLAIMER:
# This script is provided "as is", without warranty of any kind, express or
# implied, including but not limited to the warranties of merchantability,
# fitness for a particular purpose, and noninfringement. In no event shall the
# author or copyright holder be liable for any claim, damages, or other
# liability arising from the use of this script. Use at your own risk.

import json, math, os, tempfile, traceback
import fontlab as fl
import FL
from PythonQt import QtCore, QtGui

PREFS = os.path.join(tempfile.gettempdir(), "fl9_add_anchor.json")


def load_prefs():
    d = {"name": "top", "xm": 1, "xv": 0.0, "it": True, "ym": 2, "yv": 0.0, "all": False, "skip": False}
    try:
        if os.path.exists(PREFS):
            with open(PREFS, "r", encoding="utf-8") as f:
                d.update(json.load(f))
    except Exception:
        pass
    return d


def save_prefs(d):
    try:
        with open(PREFS, "w", encoding="utf-8") as f:
            json.dump(d, f)
    except Exception:
        pass


class AnchorDlg(QtGui.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Anchor to Selected Glyphs")
        self.setMinimumWidth(350)
        p = load_prefs()
        lay = QtGui.QVBoxLayout(self)

        r1 = QtGui.QHBoxLayout()
        r1.addWidget(QtGui.QLabel("Anchor Name:"))
        self.name_in = QtGui.QLineEdit(str(p["name"]))
        r1.addWidget(self.name_in)
        lay.addLayout(r1)

        xg = QtGui.QGroupBox("Horizontal Position (X)")
        xl = QtGui.QVBoxLayout(xg)
        xr1 = QtGui.QHBoxLayout()
        xr1.addWidget(QtGui.QLabel("Alignment:"))
        self.xm = QtGui.QComboBox()
        self.xm.addItems(["Fixed X", "Advance Width / 2", "Bounding Box Center"])
        self.xm.setCurrentIndex(int(p["xm"]))
        xr1.addWidget(self.xm)
        xl.addLayout(xr1)

        xr2 = QtGui.QHBoxLayout()
        self.xlbl = QtGui.QLabel("X Value:")
        xr2.addWidget(self.xlbl)
        self.xv = QtGui.QDoubleSpinBox()
        self.xv.setRange(-10000, 10000)
        self.xv.setDecimals(1)
        self.xv.setValue(float(p["xv"]))
        xr2.addWidget(self.xv)
        xl.addLayout(xr2)

        self.it = QtGui.QCheckBox("Compensate for Master Italic Angle")
        self.it.setChecked(bool(p["it"]))
        xl.addWidget(self.it)
        lay.addWidget(xg)

        yg = QtGui.QGroupBox("Vertical Position (Y)")
        yl = QtGui.QVBoxLayout(yg)
        yr1 = QtGui.QHBoxLayout()
        yr1.addWidget(QtGui.QLabel("Reference:"))
        self.ym = QtGui.QComboBox()
        self.ym.addItems(["Fixed Y", "Baseline (0)", "x-Height", "Cap Height", "Ascender", "Descender"])
        self.ym.setCurrentIndex(int(p["ym"]))
        yr1.addWidget(self.ym)
        yl.addLayout(yr1)

        yr2 = QtGui.QHBoxLayout()
        self.ylbl = QtGui.QLabel("Y Value:")
        yr2.addWidget(self.ylbl)
        self.yv = QtGui.QDoubleSpinBox()
        self.yv.setRange(-10000, 10000)
        self.yv.setDecimals(1)
        self.yv.setValue(float(p["yv"]))
        yr2.addWidget(self.yv)
        yl.addLayout(yr2)
        lay.addWidget(yg)

        sg = QtGui.QGroupBox("Options")
        sl = QtGui.QVBoxLayout(sg)
        self.rcur = QtGui.QRadioButton("Current Master")
        self.rall = QtGui.QRadioButton("All Masters")
        (self.rall if p["all"] else self.rcur).setChecked(True)
        sl.addWidget(self.rcur)
        sl.addWidget(self.rall)

        self.skip_chk = QtGui.QCheckBox("Skip if anchor already exists")
        self.skip_chk.setChecked(bool(p["skip"]))
        sl.addWidget(self.skip_chk)
        lay.addWidget(sg)

        bl = QtGui.QHBoxLayout()
        bl.addStretch()
        cb = QtGui.QPushButton("Cancel")
        cb.clicked.connect(lambda: self.reject())
        ok = QtGui.QPushButton("OK")
        ok.setDefault(True)
        ok.clicked.connect(lambda: self._ok())
        bl.addWidget(cb)
        bl.addWidget(ok)
        lay.addLayout(bl)

        self._lbls()
        self.xm.currentIndexChanged.connect(lambda i: (self._lbls(), self.xv.setValue(250.0 if i == 0 else 0.0)))
        self.ym.currentIndexChanged.connect(lambda i: (self._lbls(), self.yv.setValue(500.0 if i == 0 else 0.0)))

    def _lbls(self):
        self.xlbl.setText("X Value:" if self.xm.currentIndex == 0 else "X Offset:")
        self.ylbl.setText("Y Value:" if self.ym.currentIndex == 0 else "Y Offset:")

    def _ok(self):
        save_prefs({
            "name": self.name_in.text.strip(), "xm": self.xm.currentIndex, "xv": self.xv.value,
            "it": self.it.isChecked(), "ym": self.ym.currentIndex, "yv": self.yv.value,
            "all": self.rall.isChecked(), "skip": self.skip_chk.isChecked()
        })
        self.accept()


def get_selected(font, pkg):
    sel, seen = [], set()
    def add_name(n):
        if n and n not in seen:
            fg = pkg.findName(n)
            if fg:
                seen.add(n)
                sel.append(fg)

    items = fl.flItems()
    if hasattr(items, "selectedGlyphs"):
        for g in items.selectedGlyphs():
            add_name(getattr(g, "name", None))

    if not sel and FL.fl.count > 0 and FL.fl.font is not None:
        lf = FL.fl.font
        for i in range(len(lf)):
            if FL.fl.Selected(i):
                add_name(lf[i].name)

    if not sel and fl.CurrentGlyph():
        add_name(getattr(fl.CurrentGlyph(), "name", None))

    return sel


def get_target_layers(glyph, all_masters, master_names):
    if not all_masters:
        return [glyph.activeLayer] if glyph.activeLayer else []

    layers = []
    if hasattr(glyph, "findLayer"):
        for m in master_names:
            lyr = glyph.findLayer(m)
            if lyr:
                layers.append(lyr)
    elif hasattr(glyph, "layers"):
        m_set = set(master_names)
        for lyr in glyph.layers:
            if getattr(lyr, "name", None) in m_set:
                layers.append(lyr)
    return layers


def metric(pkg, layer, names, default):
    sources = []
    if hasattr(pkg, "masterInfo") and callable(pkg.masterInfo) and isinstance(layer.name, str):
        try:
            mi = pkg.masterInfo(layer.name)
            if mi is not None:
                sources.append(mi)
        except Exception:
            pass
    if hasattr(pkg, "info") and pkg.info is not None:
        sources.append(pkg.info)

    for src in sources:
        for k in names:
            if hasattr(src, k):
                v = getattr(src, k)
                if callable(v):
                    v = v()
                if v is not None:
                    return float(v)
    return default


def apply_anchor(pkg, layer, name, xm, xv, it, ym, yv, skip_existing):
    if not layer or layer.autoLayer:
        return "ignored"
    ex = layer.findAnchor(name)
    if ex and skip_existing:
        return "skipped"

    base_y = 0.0
    if ym == 2: base_y = metric(pkg, layer, ["xHeight"], 500.0)
    elif ym == 3: base_y = metric(pkg, layer, ["capsHeight", "capHeight"], 700.0)
    elif ym == 4: base_y = metric(pkg, layer, ["ascender"], 750.0)
    elif ym == 5: base_y = metric(pkg, layer, ["descender"], -250.0)
    y = round(yv if ym == 0 else base_y + yv, 1)

    if xm == 1:
        x = (layer.advanceWidth / 2.0) + xv
    elif xm == 2:
        bb = layer.boundingBox
        x = (bb.center().x() if (bb and not bb.isEmpty()) else layer.advanceWidth / 2.0) + xv
    else:
        x = xv

    if it:
        ang = metric(pkg, layer, ["italicAngle"], 0.0)
        if ang != 0.0:
            x += y * math.tan(math.radians(-ang))
    x = round(x, 1)

    if ex:
        ex.point = QtCore.QPointF(x, y)
        return "updated"
    else:
        a = fl.flPinPoint(QtCore.QPointF(x, y))
        a.name = name
        layer.addAnchor(a)
        return "added"


def main():
    font = fl.CurrentFont()
    if not font:
        QtGui.QMessageBox.warning(None, "Error", "No font open.")
        return
    pkg = fl.flPackage(font)
    glyphs = get_selected(font, pkg)
    if not glyphs:
        QtGui.QMessageBox.warning(None, "Error", "No glyphs selected.")
        return

    dlg = AnchorDlg()
    if not dlg.exec_():
        return
    name = dlg.name_in.text.strip()
    if not name:
        return

    xm, xv, it = dlg.xm.currentIndex, dlg.xv.value, dlg.it.isChecked()
    ym, yv, all_m = dlg.ym.currentIndex, dlg.yv.value, dlg.rall.isChecked()
    skip = dlg.skip_chk.isChecked()
    m_names = [m if isinstance(m, str) else m.name for m in pkg.masters] if all_m else []

    added = updated = skipped = 0
    for g in glyphs:
        layers = get_target_layers(g, all_m, m_names)
        changed = False
        for lyr in layers:
            res = apply_anchor(pkg, lyr, name, xm, xv, it, ym, yv, skip)
            if res == "added":
                added += 1
                changed = True
            elif res == "updated":
                updated += 1
                changed = True
            elif res == "skipped":
                skipped += 1
        if changed:
            g.update()

    fl.Update(font)
    print(f"Done '{name}': {added} added, {updated} updated, {skipped} skipped across {len(glyphs)} glyph(s).")


try:
    main()
except Exception:
    err = traceback.format_exc()
    print(err)
    QtGui.QMessageBox.critical(None, "Script Error", err)
