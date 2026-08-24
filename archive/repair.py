import re
from pathlib import Path

p = Path("app.py")
src = p.read_text(encoding="utf-8")

GARBAGE = """}
;
      });
    }"""

if GARBAGE in src:
    src = src.replace(GARBAGE, "}", 1)
    print("garbage removed (literal)")
else:
    src2, n = re.subn(r"\}\n;\n\s*\}\);\n\s*\}", "}", src, count=1)
    if n:
        src = src2
        print("garbage removed (regex)")
    else:
        print("WARNING: garbage pattern not found")

assert src.count("function setupSwipe(card)") == 1
assert "\n;\n      });" not in src

p.write_text(src, encoding="utf-8")
print("app.py repaired")
