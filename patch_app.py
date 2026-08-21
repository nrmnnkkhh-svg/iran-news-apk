from pathlib import Path

p = Path("app.py")
src = p.read_text(encoding="utf-8")

if "threaded=True" not in src:
    src = src.replace("debug=True", "threaded=True")

old = 'const res = await fetch("/api/news");'
new = (
    'const controller = new AbortController();\n'
    '        const timer = setTimeout(() => controller.abort(), 10000);\n'
    '        const res = await fetch("/api/news", { signal: controller.signal });\n'
    '        clearTimeout(timer);'
)

if old in src:
    src = src.replace(old, new)

p.write_text(src, encoding="utf-8")
print("app.py patched")
