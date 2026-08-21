from pathlib import Path

p = Path("app.py")
src = p.read_text(encoding="utf-8")

BARS_OLD = """    function setBarsHidden(hidden) {
      toolbarEl.classList.toggle("hidden", hidden);
      fabEl.classList.toggle("hidden", hidden);
    }"""
BARS_NEW = """    let barTimer = null;

    function syncStatusBar(hidden) {
      if (!window.AndroidBridge) return;

      clearTimeout(barTimer);

      if (hidden) {
        barTimer = setTimeout(() => {
          window.AndroidBridge.hideStatusBar();
        }, 150);
      } else {
        window.AndroidBridge.showStatusBar();
      }
    }

    function setBarsHidden(hidden) {
      toolbarEl.classList.toggle("hidden", hidden);
      fabEl.classList.toggle("hidden", hidden);
      syncStatusBar(hidden);
    }"""

THEME_OLD = """      if (themeMeta) {
        themeMeta.setAttribute("content", themeColors[settings.theme] || "#070b12");
      }"""
THEME_NEW = """      if (themeMeta) {
        themeMeta.setAttribute("content", themeColors[settings.theme] || "#070b12");
      }

      if (window.AndroidBridge) {
        window.AndroidBridge.setWindowBg(themeColors[settings.theme] || "#070b12");
      }"""

for old, new in [(BARS_OLD, BARS_NEW), (THEME_OLD, THEME_NEW)]:
    if old not in src:
        print("NOT FOUND:", old[:70])
        raise SystemExit(1)
    src = src.replace(old, new, 1)

Path("app.py.bak").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
p.write_text(src, encoding="utf-8")
print("bar sync patch applied")
