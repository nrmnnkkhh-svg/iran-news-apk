from pathlib import Path

p = Path("app.py")
src = p.read_text(encoding="utf-8")

replacements = [
    # 1. CSS
    ("""    .card {
      position: relative;
      overflow: hidden;""",
     """    .card {
      position: relative;
      overflow: hidden;
      touch-action: pan-y;
      transition: transform 0.25s ease, opacity 0.25s ease;
    }

    .card.swiping {
      transition: none;
    }"""),

    # 2. Settings sheet HTML
    ("""      <div class="section">
        <div class="section-label" id="themeLabel">پوسته</div>""",
     """      <div class="section">
        <div class="section-label" id="viewLabel">نمایش</div>
        <div class="segmented" id="viewOptions">
          <button data-view-choice="feed" id="viewFeedBtn">خبرها</button>
          <button data-view-choice="archive" id="viewArchiveBtn">بایگانی</button>
        </div>
      </div>

      <div class="section">
        <div class="section-label" id="themeLabel">پوسته</div>"""),

    # 3. i18n FA
    ("""        refresh: "به‌روزرسانی",
        reset: "بازنشانی\"""",
     """        refresh: "به‌روزرسانی",
        reset: "بازنشانی",
        view: "نمایش",
        viewFeed: "خبرها",
        viewArchive: "بایگانی\""""),

    # 4. i18n EN
    ("""        refresh: "Refresh",
        reset: "Reset\"""",
     """        refresh: "Refresh",
        reset: "Reset",
        view: "View",
        viewFeed: "News",
        viewArchive: "Archive\""""),

    # 5. JS State
    ("""    const SEEN_KEY = "seenTweetIds";""",
     """    const SEEN_KEY = "seenTweetIds";
    const ARCHIVE_KEY = "archivedTweetIds";
    let archivedIds = loadArchivedIds();
    let viewMode = "feed";

    function loadArchivedIds() {
      try {
        const raw = localStorage.getItem(ARCHIVE_KEY);
        if (!raw) return new Set();
        const arr = JSON.parse(raw);
        return Array.isArray(arr) ? new Set(arr.map(String)) : new Set();
      } catch (err) {
        return new Set();
      }
    }

    function saveArchivedIds() {
      const arr = [...archivedIds].slice(-2000);
      localStorage.setItem(ARCHIVE_KEY, JSON.stringify(arr));
    }"""),

    # 6. Render filter
    ("""      let groups = groupNews(news);

      if (query) {""",
     """      let groups = groupNews(news);

      if (viewMode === "feed") {
        groups = groups
          .map(group => group.filter(item => !archivedIds.has(String(item.tweet_id || "").trim())))
          .filter(group => group.length > 0);
      } else {
        groups = groups
          .map(group => group.filter(item => archivedIds.has(String(item.tweet_id || "").trim())))
          .filter(group => group.length > 0);
      }

      if (query) {"""),

    # 7. Swipe logic
    ("""      observeUnseenCards();
    }""",
     """      observeUnseenCards();
      document.querySelectorAll('.card').forEach(setupSwipe);
    }

    function setupSwipe(card) {
      let startX = 0, startY = 0, currentX = 0, isSwiping = false;
      
      card.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
        isSwiping = false;
      }, {passive: true});

      card.addEventListener('touchmove', (e) => {
        const dx = e.touches[0].clientX - startX;
        const dy = e.touches[0].clientY - startY;
        
        if (!isSwiping && Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 15) {
          isSwiping = true;
          card.classList.add('swiping');
        }
        
        if (isSwiping) {
          currentX = dx;
          const translateX = dx * 0.5; 
          card.style.transform = `translateX(${translateX}px) rotate(${translateX * 0.05}deg)`;
          card.style.opacity = Math.max(0.2, 1 - Math.abs(dx) / 400);
        }
      }, {passive: true});

      card.addEventListener('touchend', () => {
        if (isSwiping) {
          card.classList.remove('swiping');
          if (Math.abs(currentX) > 120) {
            const dir = currentX > 0 ? 100 : -100;
            card.style.transform = `translateX(${dir}%) rotate(${dir * 0.1}deg)`;
            card.style.opacity = '0';
            
            const ids = String(card.dataset.tweetIds || "").split(/\\s+/).filter(Boolean);
            if (viewMode === "feed") {
              ids.forEach(id => archivedIds.add(id));
            } else {
              ids.forEach(id => archivedIds.delete(id));
            }
            saveArchivedIds();
            
            setTimeout(() => {
              card.remove();
              if (document.querySelectorAll('#feed .card').length === 0) {
                 render(); 
              }
            }, 250);
          } else {
            card.style.transform = '';
            card.style.opacity = '';
          }
        }
        isSwiping = false;
        currentX = 0;
      }, {passive: true});
    }"""),

    # 8. Apply language
    ("""      document.getElementById("themeLabel").textContent = t("theme");""",
     """      document.getElementById("viewLabel").textContent = t("view");
      document.getElementById("viewFeedBtn").textContent = t("viewFeed");
      document.getElementById("viewArchiveBtn").textContent = t("viewArchive");

      document.getElementById("themeLabel").textContent = t("theme");"""),

    # 9. Events
    ("""    document.querySelectorAll("[data-theme-choice]").forEach(btn => {""",
     """    document.querySelectorAll("[data-view-choice]").forEach(btn => {
      btn.addEventListener("click", () => {
        viewMode = btn.dataset.viewChoice;
        document.querySelectorAll("[data-view-choice]").forEach(b => {
          b.classList.toggle("active", b.dataset.viewChoice === viewMode);
        });
        render();
        closeSettings();
      });
    });

    document.querySelectorAll("[data-theme-choice]").forEach(btn => {"""),

    # 10. Apply all
    ("""    function applyAll() {
      applyTheme();""",
     """    function applyView() {
      document.querySelectorAll("[data-view-choice]").forEach(b => {
        b.classList.toggle("active", b.dataset.viewChoice === viewMode);
      });
    }

    function applyAll() {
      applyView();
      applyTheme();""")
]

for old, new in replacements:
    if old not in src:
        print("NOT FOUND:", old[:70])
        raise SystemExit(1)
    src = src.replace(old, new, 1)

p.write_text(src, encoding="utf-8")
print("Archive feature patched")
