from pathlib import Path

p = Path("app.py")
src = p.read_text(encoding="utf-8")

IMPORT_OLD = "from flask import Flask, jsonify"
IMPORT_NEW = "from flask import Flask, jsonify, send_from_directory"

ROUTES_OLD = """@app.route("/")
def home():
    return PAGE"""
ROUTES_NEW = """BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route("/manifest.json")
def manifest():
    return send_from_directory(BASE_DIR, "manifest.json", mimetype="application/manifest+json")


@app.route("/sw.js")
def service_worker():
    resp = send_from_directory(BASE_DIR, "sw.js", mimetype="application/javascript")
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.route("/icon-192.png")
def icon192():
    return send_from_directory(BASE_DIR, "icon-192.png", mimetype="image/png")


@app.route("/icon-512.png")
def icon512():
    return send_from_directory(BASE_DIR, "icon-512.png", mimetype="image/png")


@app.route("/")
def home():
    return PAGE"""

HEAD_OLD = "  <title>خبر ایران</title>"
HEAD_NEW = """  <title>خبر ایران</title>

  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#070b12">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <link rel="icon" type="image/png" href="/icon-192.png">"""

THEME_OLD = """    function applyTheme() {
      document.body.dataset.theme = settings.theme;"""
THEME_NEW = """    function applyTheme() {
      document.body.dataset.theme = settings.theme;

      const themeColors = {
        light: "#f5f6fa",
        dark: "#070b12",
        comfort: "#171310"
      };

      const themeMeta = document.querySelector('meta[name="theme-color"]');

      if (themeMeta) {
        themeMeta.setAttribute("content", themeColors[settings.theme] || "#070b12");
      }"""

SW_OLD = "    setInterval(loadNews, 30000);"
SW_NEW = """    setInterval(loadNews, 30000);

    if ("serviceWorker" in navigator) {
      window.addEventListener("load", () => {
        navigator.serviceWorker.register("/sw.js").catch(() => {});
      });
    }"""

replacements = [
    (IMPORT_OLD, IMPORT_NEW),
    (ROUTES_OLD, ROUTES_NEW),
    (HEAD_OLD, HEAD_NEW),
    (THEME_OLD, THEME_NEW),
    (SW_OLD, SW_NEW),
]

for old, new in replacements:
    if old not in src:
        print("NOT FOUND:", old[:70])
        raise SystemExit(1)
    src = src.replace(old, new, 1)

Path("app.py.bak").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
p.write_text(src, encoding="utf-8")
print("PWA patch applied")
