import re
from pathlib import Path

p = Path("app.py")
src = p.read_text(encoding="utf-8")

# 1. CSS touch-action
if "touch-action: pan-y;" not in src:
    src = src.replace(
        "box-shadow: var(--shadow);\n    }",
        "box-shadow: var(--shadow);\n      touch-action: pan-y;\n      transition: transform 0.25s ease, opacity 0.25s ease;\n    }\n\n    .card.swiping {\n      transition: none;\n    }",
        1
    )

# 2. HTML View toggle
if 'id="viewLabel"' not in src:
    src = src.replace(
        '<div class="section">\n        <div class="section-label" id="themeLabel">',
        '<div class="section">\n        <div class="section-label" id="viewLabel">نمایش</div>\n        <div class="segmented" id="viewOptions">\n          <button data-view-choice="feed" id="viewFeedBtn">خبرها</button>\n          <button data-view-choice="archive" id="viewArchiveBtn">بایگانی</button>\n        </div>\n      </div>\n\n      <div class="section">\n        <div class="section-label" id="themeLabel">',
        1
    )

# 3 & 4. i18n
if 'viewArchive: "بایگانی"' not in src:
    src = src.replace(
        'reset: "بازنشانی"',
        'reset: "بازنشانی",\n        view: "نمایش",\n        viewFeed: "خبرها",\n        viewArchive: "بایگانی"'
    )
if 'viewArchive: "Archive"' not in src:
    src = src.replace(
        'reset: "Reset"',
        'reset: "Reset",\n        view: "View",\n        viewFeed: "News",\n        viewArchive: "Archive"'
    )

# 5. JS State
if "ARCHIVE_KEY" not in src:
    src = src.replace(
        'const SEEN_KEY = "seenTweetIds";',
        'const SEEN_KEY = "seenTweetIds";\n    const ARCHIVE_KEY = "archivedTweetIds";\n    let archivedIds = loadArchivedIds();\n    let viewMode = "feed";\n\n    function loadArchivedIds() {\n      try {\n        const raw = localStorage.getItem(ARCHIVE_KEY);\n        if (!raw) return new Set();\n        const arr = JSON.parse(raw);\n        return Array.isArray(arr) ? new Set(arr.map(String)) : new Set();\n      } catch (err) {\n        return new Set();\n      }\n    }\n\n    function saveArchivedIds() {\n      const arr = [...archivedIds].slice(-2000);\n      localStorage.setItem(ARCHIVE_KEY, JSON.stringify(arr));\n    }'
    )

# 6. Render filter
if "viewMode === \"feed\"" not in src:
    src = src.replace(
        'let groups = groupNews(news);',
        'let groups = groupNews(news);\n\n      if (viewMode === "feed") {\n        groups = groups\n          .map(group => group.filter(item => !archivedIds.has(String(item.tweet_id || "").trim())))\n          .filter(group => group.length > 0);\n      } else {\n        groups = groups\n          .map(group => group.filter(item => archivedIds.has(String(item.tweet_id || "").trim())))\n          .filter(group => group.length > 0);\n      }'
    )

# 7. Swipe logic
if "function setupSwipe(card)" not in src:
    render_end_pattern = re.compile(r'(if \(id\) renderedIds\.add\(id\);\s*\}\);\s*\}\);\s*\})')
    match = render_end_pattern.search(src)
    if match:
        old_end = match.group(1)
        new_end = old_end.replace('})', '})\n      document.querySelectorAll(\'.card\').forEach(setupSwipe);\n    }\n\n    function setupSwipe(card) {\n      let startX = 0, startY = 0, currentX = 0, isSwiping = false;\n      \n      card.addEventListener(\'touchstart\', (e) => {\n        startX = e.touches[0].clientX;\n        startY = e.touches[0].clientY;\n        isSwiping = false;\n      }, {passive: true});\n\n      card.addEventListener(\'touchmove\', (e) => {\n        const dx = e.touches[0].clientX - startX;\n        const dy = e.touches[0].clientY - startY;\n        \n        if (!isSwiping && Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 15) {\n          isSwiping = true;\n          card.classList.add(\'swiping\');\n        }\n        \n        if (isSwiping) {\n          currentX = dx;\n          const translateX = dx * 0.5; \n          card.style.transform = `translateX(${translateX}px) rotate(${translateX * 0.05}deg)`;\n          card.style.opacity = Math.max(0.2, 1 - Math.abs(dx) / 400);\n        }\n      }, {passive: true});\n\n      card.addEventListener(\'touchend\', () => {\n        if (isSwiping) {\n          card.classList.remove(\'swiping\');\n          if (Math.abs(currentX) > 120) {\n            const dir = currentX > 0 ? 100 : -100;\n            card.style.transform = `translateX(${dir}%) rotate(${dir * 0.1}deg)`;\n            card.style.opacity = \'0\';\n            \n            const ids = String(card.dataset.tweetIds || "").split(/\\s+/).filter(Boolean);\n            if (viewMode === "feed") {\n              ids.forEach(id => archivedIds.add(id));\n            } else {\n              ids.forEach(id => archivedIds.delete(id));\n            }\n            saveArchivedIds();\n            \n            setTimeout(() => {\n              card.remove();\n              if (document.querySelectorAll(\'#feed .card\').length === 0) {\n                 render(); \n              }\n            }, 250);\n          } else {\n            card.style.transform = \'\';\n            card.style.opacity = \'\';\n          }\n        }\n        isSwiping = false;\n        currentX = 0;\n      }, {passive: true});\n    }')
        src = src.replace(old_end, new_end, 1)
    else:
        print("Could not find render end")

# 8. Apply language
if 'document.getElementById("viewLabel")' not in src:
    src = src.replace(
        'document.getElementById("themeLabel").textContent = t("theme");',
        'document.getElementById("viewLabel").textContent = t("view");\n      document.getElementById("viewFeedBtn").textContent = t("viewFeed");\n      document.getElementById("viewArchiveBtn").textContent = t("viewArchive");\n\n      document.getElementById("themeLabel").textContent = t("theme");'
    )

# 9. Events
if 'data-view-choice' not in src:
    src = src.replace(
        'document.querySelectorAll("[data-theme-choice]").forEach(btn => {',
        'document.querySelectorAll("[data-view-choice]").forEach(btn => {\n      btn.addEventListener("click", () => {\n        viewMode = btn.dataset.viewChoice;\n        document.querySelectorAll("[data-view-choice]").forEach(b => {\n          b.classList.toggle("active", b.dataset.viewChoice === viewMode);\n        });\n        render();\n        closeSettings();\n      });\n    });\n\n    document.querySelectorAll("[data-theme-choice]").forEach(btn => {'
    )

# 10. Apply all
if "function applyView()" not in src:
    src = src.replace(
        'function applyAll() {\n      applyTheme();',
        'function applyView() {\n      document.querySelectorAll("[data-view-choice]").forEach(b => {\n        b.classList.toggle("active", b.dataset.viewChoice === viewMode);\n      });\n    }\n\n    function applyAll() {\n      applyView();\n      applyTheme();'
    )

p.write_text(src, encoding="utf-8")
print("Archive feature patched successfully")
