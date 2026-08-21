from pathlib import Path

p = Path("app.py")
src = p.read_text(encoding="utf-8")

PTR_TOP_OLD = "      top: var(--sb-pad, 0px);"
PTR_TOP_NEW = "      top: 0;"

PTR_FN_OLD = """    function ptrSetOffset(offset) {
      ptrEl.style.transform = "translateY(calc(-100% + " + offset + "px))";
    }"""
PTR_FN_NEW = """    function sbPad() {
      const v = parseFloat(
        getComputedStyle(document.documentElement).getPropertyValue("--sb-pad") || "0"
      );
      return isNaN(v) ? 0 : v;
    }

    function ptrSetOffset(offset) {
      const y = offset <= 0 ? 0 : sbPad() + offset;
      ptrEl.style.transform = "translateY(calc(-100% + " + y + "px))";
    }"""

SCROLL_OLD = """      if (y <= 40) {
        setBarsHidden(false);
      } else if (y > lastY + 8) {
        setBarsHidden(true);
      } else if (y < lastY - 8) {
        setBarsHidden(false);
      }"""
SCROLL_NEW = """      if (y <= 24) {
        setBarsHidden(false);
      } else if (y > lastY + 3) {
        setBarsHidden(true);
      } else if (y < lastY - 3) {
        setBarsHidden(false);
      }"""

BARS_OLD = """    function setBarsHidden(hidden) {
      toolbarEl.classList.toggle("hidden", hidden);
      fabEl.classList.toggle("hidden", hidden);
      syncStatusBar(hidden);
    }"""
BARS_NEW = """    function setBarsHidden(hidden) {
      toolbarEl.classList.toggle("hidden", hidden);
      fabEl.classList.toggle("hidden", hidden);
    }"""

for old, new in [
    (PTR_TOP_OLD, PTR_TOP_NEW),
    (PTR_FN_OLD, PTR_FN_NEW),
    (SCROLL_OLD, SCROLL_NEW),
    (BARS_OLD, BARS_NEW),
]:
    if old not in src:
        print("NOT FOUND:", old[:70])
        raise SystemExit(1)
    src = src.replace(old, new, 1)

Path("app.py.bak").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
p.write_text(src, encoding="utf-8")
print("fix3 patch applied")
