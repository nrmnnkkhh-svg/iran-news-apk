from pathlib import Path

p = Path("app.py")
src = p.read_text(encoding="utf-8")

TOOLBAR_OLD = """      padding: calc(14px + var(--sb-pad, 0px)) 0 8px;
      transition: padding-top 0.2s ease;"""
TOOLBAR_NEW = """      padding: calc(14px + var(--sb-pad, 0px)) 0 8px;
      transition: transform 0.25s ease;"""

TOOLBAR_HIDDEN_OLD = """    .ptr {"""
TOOLBAR_HIDDEN_NEW = """    .toolbar.hidden {
      transform: translateY(-110%);
    }

    .ptr {"""

FAB_TRANS_OLD = "      transition: transform 0.15s ease;"
FAB_TRANS_NEW = "      transition: transform 0.25s ease, opacity 0.25s ease;"

FAB_HIDDEN_OLD = """    .fab:active {
      transform: scale(0.94);
    }"""
FAB_HIDDEN_NEW = """    .fab:active {
      transform: scale(0.94);
    }

    .fab.hidden {
      transform: translateY(120px);
      opacity: 0;
      pointer-events: none;
    }"""

JS_OLD = """    applyAll();
    loadNews();"""
JS_NEW = """    const toolbarEl = document.querySelector(".toolbar");
    const fabEl = document.getElementById("fabBtn");
    const searchEl = document.getElementById("search");

    let lastY = window.scrollY;
    let searchLocked = false;

    function setBarsHidden(hidden) {
      toolbarEl.classList.toggle("hidden", hidden);
      fabEl.classList.toggle("hidden", hidden);
    }

    searchEl.addEventListener("focus", () => {
      searchLocked = true;
      setBarsHidden(false);
    });

    searchEl.addEventListener("blur", () => {
      searchLocked = false;
    });

    window.addEventListener("scroll", () => {
      const y = window.scrollY;

      if (searchLocked || document.getElementById("sheet").classList.contains("open")) {
        lastY = y;
        return;
      }

      if (y <= 40) {
        setBarsHidden(false);
      } else if (y > lastY + 8) {
        setBarsHidden(true);
      } else if (y < lastY - 8) {
        setBarsHidden(false);
      }

      lastY = y;
    }, { passive: true });

    applyAll();
    loadNews();"""

for old, new in [
    (TOOLBAR_OLD, TOOLBAR_NEW),
    (TOOLBAR_HIDDEN_OLD, TOOLBAR_HIDDEN_NEW),
    (FAB_TRANS_OLD, FAB_TRANS_NEW),
    (FAB_HIDDEN_OLD, FAB_HIDDEN_NEW),
    (JS_OLD, JS_NEW),
]:
    if old not in src:
        print("NOT FOUND:", old[:70])
        raise SystemExit(1)
    src = src.replace(old, new, 1)

Path("app.py.bak").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
p.write_text(src, encoding="utf-8")
print("scroll UI patch applied")
