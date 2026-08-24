from pathlib import Path

p = Path("app.py")
src = p.read_text(encoding="utf-8")

CSS_OLD = "  </style>"
CSS_NEW = """    mark {
      background: var(--accent);
      color: var(--on-accent);
      border-radius: 6px;
      padding: 0 3px;
    }

    .ptr {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 30;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      padding: 12px 0;
      color: var(--muted);
      font-size: calc(var(--base-size) * 0.8px);
      transform: translateY(-100%);
      transition: transform 0.18s ease;
      pointer-events: none;
    }

    .ptr-spinner {
      width: 18px;
      height: 18px;
      border: 2px solid var(--line);
      border-top-color: var(--accent);
      border-radius: 50%;
      opacity: 0;
    }

    .ptr.refreshing .ptr-spinner {
      opacity: 1;
      animation: ptrSpin 0.8s linear infinite;
    }

    @keyframes ptrSpin {
      to {
        transform: rotate(360deg);
      }
    }
  </style>"""

FA_OLD = """        refresh: "به‌روزرسانی",
        reset: "بازنشانی\""""
FA_NEW = """        refresh: "به‌روزرسانی",
        reset: "بازنشانی",
        pullHint: "برای به‌روزرسانی بکشید",
        releaseHint: "رها کنید تا به‌روزرسانی شود",
        refreshingHint: "در حال به‌روزرسانی...\""""

EN_OLD = """        refresh: "Refresh",
        reset: "Reset\""""
EN_NEW = """        refresh: "Refresh",
        reset: "Reset",
        pullHint: "Pull to refresh",
        releaseHint: "Release to refresh",
        refreshingHint: "Refreshing...\""""

QUERY_OLD = """      const query = document.getElementById("search").value.trim().toLowerCase();
      const feed = document.getElementById("feed");"""
QUERY_NEW = """      const queryRaw = document.getElementById("search").value.trim();
      const query = queryRaw.toLowerCase();
      const feed = document.getElementById("feed");"""

TEXT_OLD = "          .map(item => `<div class=\"text\">${escapeHtml(item.text)}</div>`)"
TEXT_NEW = "          .map(item => `<div class=\"text\">${highlightText(item.text, queryRaw)}</div>`)"

HIGHLIGHT_FN = """    function highlightText(text, query) {
      const value = String(text ?? "");

      if (!query) {
        return escapeHtml(value);
      }

      const lower = value.toLowerCase();
      const q = query.toLowerCase();

      let result = "";
      let cursor = 0;
      let index = lower.indexOf(q, cursor);

      if (index === -1) {
        return escapeHtml(value);
      }

      while (index !== -1) {
        result += escapeHtml(value.slice(cursor, index));
        result += "<mark>" + escapeHtml(value.slice(index, index + q.length)) + "</mark>";
        cursor = index + q.length;
        index = lower.indexOf(q, cursor);
      }

      result += escapeHtml(value.slice(cursor));

      return result;
    }

    function render() {"""

RENDER_OLD = "    function render() {"

PTR_HTML_OLD = """<body data-theme="dark">
  <div class="app">"""
PTR_HTML_NEW = """<body data-theme="dark">
  <div class="ptr" id="ptr">
    <div class="ptr-spinner"></div>
    <div id="ptrText"></div>
  </div>

  <div class="app">"""

PTR_JS_OLD = """    applyAll();
    loadNews();"""
PTR_JS_NEW = """    const ptrEl = document.getElementById("ptr");
    const ptrTextEl = document.getElementById("ptrText");

    let ptrState = "idle";
    let ptrStartY = null;

    function ptrUpdateText() {
      if (ptrState === "ready") {
        ptrTextEl.textContent = t("releaseHint");
      } else if (ptrState === "refreshing") {
        ptrTextEl.textContent = t("refreshingHint");
      } else {
        ptrTextEl.textContent = t("pullHint");
      }
    }

    function ptrSetOffset(offset) {
      ptrEl.style.transform = "translateY(calc(-100% + " + offset + "px))";
    }

    document.addEventListener("touchstart", (e) => {
      const sheetOpen = document.getElementById("sheet").classList.contains("open");

      if (!sheetOpen && window.scrollY <= 0) {
        ptrStartY = e.touches[0].clientY;
      } else {
        ptrStartY = null;
      }
    }, { passive: true });

    document.addEventListener("touchmove", (e) => {
      if (ptrStartY === null || ptrState === "refreshing") {
        return;
      }

      if (window.scrollY > 0) {
        ptrStartY = null;
        ptrSetOffset(0);
        return;
      }

      const delta = e.touches[0].clientY - ptrStartY;

      if (delta <= 0) {
        ptrState = "idle";
        ptrSetOffset(0);
        return;
      }

      e.preventDefault();

      ptrEl.style.transition = "none";

      const offset = Math.min(90, delta * 0.45);

      ptrSetOffset(offset);
      ptrState = offset >= 60 ? "ready" : "pulling";
      ptrUpdateText();
    }, { passive: false });

    document.addEventListener("touchend", () => {
      ptrEl.style.transition = "";

      if (ptrState === "ready") {
        ptrState = "refreshing";
        ptrEl.classList.add("refreshing");
        ptrSetOffset(64);
        ptrUpdateText();

        loadNews().finally(() => {
          ptrEl.classList.remove("refreshing");
          ptrState = "idle";
          ptrSetOffset(0);
        });
      } else {
        ptrState = "idle";
        ptrSetOffset(0);
      }

      ptrStartY = null;
    });

    applyAll();
    loadNews();"""

replacements = [
    (CSS_OLD, CSS_NEW),
    (FA_OLD, FA_NEW),
    (EN_OLD, EN_NEW),
    (QUERY_OLD, QUERY_NEW),
    (TEXT_OLD, TEXT_NEW),
    (RENDER_OLD, HIGHLIGHT_FN),
    (PTR_HTML_OLD, PTR_HTML_NEW),
    (PTR_JS_OLD, PTR_JS_NEW),
]

for old, new in replacements:
    if old not in src:
        print("NOT FOUND:", old[:70])
        raise SystemExit(1)
    src = src.replace(old, new, 1)

Path("app.py.bak").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
p.write_text(src, encoding="utf-8")
print("UI patch applied")
