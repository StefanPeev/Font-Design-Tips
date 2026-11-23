#FLM: Stem Finder Pro (FontLab 9)
# SCRIPT NAME: Stem Finder Pro (Vertical & Horizontal)
# DESCRIPTION: Finds vertical and horizontal stems (straight and curved) by a
#              specified target width and tolerance in FontLab 9, filters short
#              serifs by minimum length, scans active or all masters, highlights
#              stem nodes, and opens matched glyphs in a separate window.
# COPYRIGHT:   (c) 2026 Stefan Peev (https://github.com). All rights reserved.
# DISCLAIMER:
# This script is provided "as is", without warranty of any kind, express or
# implied, including but not limited to the warranties of merchantability,
# fitness for a particular purpose, and noninfringement. In no event shall the
# author or copyright holder be liable for any claim, damages, or other
# liability arising from the use of this script. Use at your own risk.

import traceback
import fontlab as fl
import fontgate as fg
from PythonQt import QtCore, QtGui

def _b(obj, attr, default=True):
    if not hasattr(obj, attr):
        return default
    v = getattr(obj, attr)
    return bool(v()) if callable(v) else bool(v)

def _items(obj, attr):
    if not hasattr(obj, attr):
        return []
    v = getattr(obj, attr)
    res = v() if callable(v) else v
    return list(res) if res is not None else []

def get_pkg():
    ws = fl.flWorkspace.instance()
    pkg = ws.currentPackage
    if pkg is not None and not _b(pkg, "isNull", False):
        return pkg
    font = fl.CurrentFont()
    return fl.flPackage(font) if font else None

def get_sel_names():
    names = []
    try:
        import FL
        f = FL.fl.font
        if f:
            for i in range(len(f)):
                if FL.fl.Selected(i):
                    names.append(f[i].name)
    except Exception:
        pass
    return names

def get_masters(pkg, font):
    names = []
    for src in (pkg, font):
        if src and hasattr(src, "masters"):
            for m in _items(src, "masters"):
                mn = getattr(m, "name", None)
                if callable(mn):
                    mn = mn()
                if mn and str(mn) not in names:
                    names.append(str(mn))
            if names:
                return names
    am = getattr(pkg, "activeMasterName", None)
    return [am] if am else [None]

def scan_layer(layer, mode, target_w, tol, min_len, curves):
    if not layer or not _b(layer, "isValid", True):
        return []
    v_items, h_items = [], []
    for sh in _items(layer, "shapes"):
        for ct in _items(sh, "contours"):
            nodes = _items(ct, "nodes")
            n = len(nodes)
            if n < 2:
                continue
            for nd in nodes:
                nd.selected = False
            for i in range(n):
                n1, n2 = nodes[i], nodes[(i + 1) % n]
                if not (_b(n1, "isOn") and _b(n2, "isOn")):
                    continue
                x1, y1, x2, y2 = float(n1.x), float(n1.y), float(n2.x), float(n2.y)
                if abs(x1 - x2) <= 0.5 and abs(y1 - y2) >= min_len:
                    v_items.append(((x1 + x2) / 2.0, min(y1, y2), max(y1, y2), False, [n1, n2]))
                elif abs(y1 - y2) <= 0.5 and abs(x1 - x2) >= min_len:
                    h_items.append(((y1 + y2) / 2.0, min(x1, x2), max(x1, x2), False, [n1, n2]))
            if curves and n >= 3:
                for i in range(n):
                    cn = nodes[i]
                    if not _b(cn, "isOn"):
                        continue
                    pn, nn = nodes[(i - 1) % n], nodes[(i + 1) % n]
                    if _b(pn, "isOn") and _b(nn, "isOn"):
                        continue
                    cx, cy, px, py, nx, ny = float(cn.x), float(cn.y), float(pn.x), float(pn.y), float(nn.x), float(nn.y)
                    pv = (not _b(pn, "isOn")) and abs(px - cx) <= 1.0 and abs(py - cy) > 2.0
                    nv = (not _b(nn, "isOn")) and abs(nx - cx) <= 1.0 and abs(ny - cy) > 2.0
                    if pv or nv:
                        ys = [cy] + ([py] if pv else []) + ([ny] if nv else [])
                        ns = [cn] + ([pn] if pv else []) + ([nn] if nv else [])
                        v_items.append((cx, min(ys), max(ys), True, ns))
                    ph = (not _b(pn, "isOn")) and abs(py - cy) <= 1.0 and abs(px - cx) > 2.0
                    nh = (not _b(nn, "isOn")) and abs(ny - cy) <= 1.0 and abs(nx - cx) > 2.0
                    if ph or nh:
                        xs = [cx] + ([px] if ph else []) + ([nx] if nh else [])
                        ns = [cn] + ([pn] if ph else []) + ([nn] if nh else [])
                        h_items.append((cy, min(xs), max(xs), True, ns))

    items = v_items if mode == "V" else h_items
    matches, seen = [], set()
    for i in range(len(items)):
        p1, a1, b1, c1, ns1 = items[i]
        for j in range(i + 1, len(items)):
            p2, a2, b2, c2, ns2 = items[j]
            dist = abs(p2 - p1)
            if abs(dist - target_w) <= tol:
                ov = min(b1, b2) - max(a1, a2)
                if ov >= (2.0 if (c1 or c2) else min(min_len, 2.0)):
                    for nd in ns1 + ns2:
                        nd.selected = True
                    key = (round(dist, 1), round(min(p1, p2), 1), round(max(p1, p2), 1), "curve" if (c1 or c2) else "straight")
                    if key not in seen:
                        seen.add(key)
                        matches.append(key)
    return matches

def open_win(pkg, matched):
    names = [g.name for g in matched]
    try:
        QtGui.QApplication.clipboard().setText("/" + "/".join(names))
    except Exception:
        pass
    try:
        import FL
        FL.fl.Unselect()
        for nm in names:
            FL.fl.Select(nm)
    except Exception:
        pass
    try:
        main = fl.flWorkspace.instance().mainWindow
        for kw in ["new glyph window", "new glyph tab", "open glyph", "edit glyph"]:
            for act in main.findChildren(QtGui.QAction):
                t = str(getattr(act, "text", "")).replace("&", "").strip().lower()
                if kw in t and _b(act, "enabled", True):
                    act.trigger()
                    return
    except Exception:
        pass

class StemDlg(QtGui.QDialog):
    def __init__(self):
        super().__init__(None)
        self.setWindowTitle("FontLab 9 - Stem Finder Pro")
        self.setMinimumWidth(380)
        lay = QtGui.QVBoxLayout(self)

        for lbl_txt, attr, rng, val in [
            ("Target Stem Width:", "w_sp", (1.0, 2000.0), 22.0),
            ("Tolerance (+/-):", "t_sp", (0.0, 100.0), 1.0),
            ("Min. Stem Length (serif filter):", "l_sp", (1.0, 2000.0), 5.0),
        ]:
            row = QtGui.QHBoxLayout()
            row.addWidget(QtGui.QLabel(lbl_txt))
            sp = QtGui.QDoubleSpinBox()
            sp.setRange(*rng)
            sp.setValue(val)
            setattr(self, attr, sp)
            row.addWidget(sp)
            lay.addLayout(row)

        self.c_cb = QtGui.QCheckBox("Include curved stems (O, C, S)")
        self.c_cb.setChecked(True)
        lay.addWidget(self.c_cb)
        self.m_cb = QtGui.QCheckBox("Scan all masters")
        lay.addWidget(self.m_cb)
        self.s_cb = QtGui.QCheckBox("Search selected glyphs only")
        lay.addWidget(self.s_cb)

        br = QtGui.QHBoxLayout()
        b1, b2 = QtGui.QPushButton("1. Find Vertical Stems"), QtGui.QPushButton("2. Find Horizontal Stems")
        br.addWidget(b1)
        br.addWidget(b2)
        lay.addLayout(br)

        self.st = QtGui.QLabel("Ready.")
        lay.addWidget(self.st)
        self.res = QtGui.QLineEdit()
        self.res.setReadOnly(True)
        lay.addWidget(self.res)
        b1.clicked.connect(lambda: self.go("V"))
        b2.clicked.connect(lambda: self.go("H"))

    def go(self, mode):
        pkg, font = get_pkg(), fl.CurrentFont()
        if not pkg or not font:
            self.st.setText("No open font.")
            return
        tw, tol, ml = float(self.w_sp.value), float(self.t_sp.value), float(self.l_sp.value)
        cv, am, so = bool(self.c_cb.checked), bool(self.m_cb.checked), bool(self.s_cb.checked)
        sel = set(get_sel_names()) if so else None
        fgs = [g for g in font.glyphs if g.name in sel] if so else list(font.glyphs)
        glyphs = [fl.flGlyph(g, font) for g in fgs]
        masters = get_masters(pkg, font) if am else [getattr(pkg, "activeMasterName", None)]
        matched = []
        lbl = "Vertical" if mode == "V" else "Horizontal"
        print("\n--- " + lbl + " Stems: " + str(tw) + " +/- " + str(tol) + " ---")

        for g in glyphs:
            if not _b(g, "isValid", True):
                continue
            gh = {}
            for m in masters:
                lyr = g.layer(m) if m else g.activeLayer
                h = scan_layer(lyr, mode, tw, tol, ml, cv)
                if h:
                    gh[m or "Active"] = h
            if gh:
                g.update()
                matched.append(g)
                print("  /" + g.name + " -> " + str(gh))

        if matched:
            self.res.setText("/" + "/".join(g.name for g in matched))
            open_win(pkg, matched)
            self.st.setText("Found " + str(len(matched)) + " glyph(s).")
        else:
            self.res.clear()
            self.st.setText("No matches.")

try:
    dlg = StemDlg()
    dlg.show()
    dlg.raise_()
except Exception:
    QtGui.QMessageBox.critical(None, "Error", traceback.format_exc())
