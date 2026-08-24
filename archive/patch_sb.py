from pathlib import Path

p = Path("app.py")
src = p.read_text(encoding="utf-8")

CSS_OLD = """      padding: 14px 0 8px;"""
CSS_NEW = """      padding: calc(14px + var(--sb-pad, 0px)) 0 8px;
      transition: padding-top 0.2s ease;"""

PTR_OLD = """    .ptr {
      position: fixed;
      top: 0;"""
PTR_NEW = """    .ptr {
      position: fixed;
      top: var(--sb-pad, 0px);"""

JS_OLD = "    let news = [];"
JS_NEW = """    window.setStatusBarPad = function (px) {
      document.documentElement.style.setProperty("--sb-pad", px + "px");
    };

    let news = [];"""

for old, new in [(CSS_OLD, CSS_NEW), (PTR_OLD, PTR_NEW), (JS_OLD, JS_NEW)]:
    if old not in src:
        print("NOT FOUND:", old[:70])
        raise SystemExit(1)
    src = src.replace(old, new, 1)

Path("app.py.bak").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
p.write_text(src, encoding="utf-8")
print("status bar patch applied")
