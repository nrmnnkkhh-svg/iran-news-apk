from pathlib import Path

code = r'''from flask import Flask, jsonify, send_from_directory
import json
import os

app = Flask(__name__)
NEWS_FILE = "news.json"
try:
    app.json.ensure_ascii = False
except Exception:
    pass

def load_news():
    if not os.path.exists(NEWS_FILE): return []
    try:
        with open(NEWS_FILE, encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception: return []

PAGE = """<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>خبر ایران</title>
  <link rel="manifest" href="/manifest.json">
  <meta name="theme-color" content="#070b12">
  <link rel="icon" type="image/png" href="/icon-192.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;700;800&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; }
    :root { --base-size: 16.5; --font-family: 'Vazirmatn', system-ui, sans-serif; --sb-pad: 0px; }
    body[data-theme="light"] { --bg: #f5f6fa; --card: #ffffff; --text: #16181d; --muted: #6b7280; --line: rgba(17,24,39,0.08); --accent: #e11d48; --chip: rgba(225,29,72,0.10); --glow: rgba(225,29,72,0.08); --shadow: 0 12px 30px rgba(15,23,42,0.08); --on-accent: #ffffff; }
    body[data-theme="dark"] { --bg: #070b12; --card: #0e1420; --text: #edf2f7; --muted: #94a3b8; --line: rgba(148,163,184,0.16); --accent: #fb7185; --chip: rgba(251,113,133,0.12); --glow: rgba(251,113,133,0.08); --shadow: 0 12px 30px rgba(0,0,0,0.30); --on-accent: #180a10; }
    body[data-theme="comfort"] { --bg: #171310; --card: #221c17; --text: #f4e9dc; --muted: #c4aa8e; --line: rgba(244,233,220,0.12); --accent: #e3a857; --chip: rgba(227,168,87,0.12); --glow: rgba(227,168,87,0.08); --shadow: 0 12px 30px rgba(0,0,0,0.25); --on-accent: #241a09; }
    html, body { margin: 0; padding: 0; }
    body { font-family: var(--font-family); background: radial-gradient(circle at top right, var(--glow), transparent 32%), var(--bg); color: var(--text); min-height: 100vh; font-size: calc(var(--base-size) * 1px); }
    .app { max-width: 820px; margin: 0 auto; padding: 0 16px 115px; }
    .toolbar { position: sticky; top: 0; z-index: 20; padding: calc(14px + var(--sb-pad)) 0 8px; background: linear-gradient(to bottom, var(--bg) 70%, transparent); transition: transform 0.25s ease; }
    .toolbar.hidden { transform: translateY(-110%); }
    .searchbar input { width: 100%; border: 1px solid var(--line); background: var(--card); color: var(--text); border-radius: 16px; padding: 13px 14px; font: inherit; box-shadow: var(--shadow); outline: none; }
    .searchbar input::placeholder { color: var(--muted); }
    .status { color: var(--muted); font-size: calc(var(--base-size) * 0.75px); margin-top: 8px; padding-inline-start: 4px; min-height: 18px; }
    .container { display: grid; gap: 14px; padding-top: 10px; }
    .card { position: relative; overflow: hidden; background: var(--card); border: 1px solid var(--line); border-radius: 22px; padding: 18px 18px 16px; box-shadow: var(--shadow); touch-action: pan-y; transition: transform 0.25s ease, opacity 0.25s ease; }
    .card.fresh { animation: fadeUp 0.28s ease; }
    .card.swiping { transition: none; }
    .card::before { content: ""; position: absolute; top: 18px; bottom: 18px; inset-inline-start: 0; width: 4px; border-radius: 999px; background: var(--accent); opacity: 0.85; }
    @keyframes fadeUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
    .chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
    .chip { padding: 5px 10px; border-radius: 999px; font-size: calc(var(--base-size) * 0.72px); font-weight: 700; background: var(--chip); color: var(--accent); }
    .chip.soft { background: rgba(148,163,184,0.14); color: var(--muted); }
    .chip.new { background: var(--accent); color: var(--on-accent); animation: newPulse 1.8s ease-in-out infinite; }
    @keyframes newPulse { 0%,100% { opacity: 1; } 50% { opacity: 0.72; } }
    .text { font-size: calc(var(--base-size) * 1.06px); line-height: 2.05; white-space: pre-wrap; unicode-bidi: plaintext; }
    .text + .text { margin-top: 12px; padding-top: 12px; border-top: 1px dashed var(--line); }
    mark { background: var(--accent); color: var(--on-accent); border-radius: 6px; padding: 0 3px; }
    .time { margin-top: 14px; color: var(--muted); font-size: calc(var(--base-size) * 0.78px); }
    .empty { text-align: center; color: var(--muted); padding: 46px 18px; background: var(--card); border: 1px dashed var(--line); border-radius: 22px; line-height: 2; font-size: calc(var(--base-size) * 0.95px); }
    .fab { position: fixed; bottom: 22px; inset-inline-end: 22px; width: 58px; height: 58px; border-radius: 50%; border: 1px solid var(--line); background: var(--card); color: var(--text); box-shadow: var(--shadow); cursor: pointer; z-index: 40; display: flex; align-items: center; justify-content: center; transition: transform 0.25s ease, opacity 0.25s ease; }
    .fab:active { transform: scale(0.94); }
    .fab.hidden { transform: translateY(120px); opacity: 0; pointer-events: none; }
    .fab svg, .close svg { display: block; margin: auto; }
    .ptr { position: fixed; top: 0; left: 0; right: 0; z-index: 30; display: flex; align-items: center; justify-content: center; gap: 10px; padding: 12px 0; color: var(--muted); font-size: calc(var(--base-size) * 0.8px); transform: translateY(-100%); transition: transform 0.18s ease; pointer-events: none; }
    .ptr-spinner { width: 18px; height: 18px; border: 2px solid var(--line); border-top-color: var(--accent); border-radius: 50%; opacity: 0; }
    .ptr.refreshing .ptr-spinner { opacity: 1; animation: ptrSpin 0.8s linear infinite; }
    @keyframes ptrSpin { to { transform: rotate(360deg); } }
    .overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.38); opacity: 0; pointer-events: none; transition: opacity 0.2s ease; z-index: 50; }
    .overlay.show { opacity: 1; pointer-events: auto; }
    .sheet { position: fixed; left: 0; right: 0; bottom: 0; z-index: 60; max-height: 82vh; overflow: auto; background: var(--card); border: 1px solid var(--line); border-bottom: none; border-radius: 26px 26px 0 0; box-shadow: var(--shadow); transform: translateY(112%); transition: transform 0.25s ease; }
    .sheet.open { transform: translateY(0); }
    .sheet-handle { width: 52px; height: 5px; border-radius: 999px; background: var(--line); margin: 12px auto 0; }
    .sheet-inner { padding: 16px 18px 24px; }
    .sheet-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
    .sheet-title { font-weight: 800; font-size: calc(var(--base-size) * 1.15px); }
    .close { min-width: 42px; height: 42px; border-radius: 14px; display: flex; align-items: center; justify-content: center; border: 1px solid var(--line); background: transparent; color: var(--text); cursor: pointer; }
    .section { margin-bottom: 18px; }
    .section-label { color: var(--muted); font-size: calc(var(--base-size) * 0.82px); margin-bottom: 9px; font-weight: 700; }
    .segmented { display: flex; flex-wrap: wrap; gap: 8px; }
    .segmented button { flex: 1 1 auto; min-height: 44px; border-radius: 14px; border: 1px solid var(--line); background: transparent; color: var(--text); font: inherit; cursor: pointer; }
    .segmented button.active { background: var(--chip); color: var(--accent); border-color: var(--accent); font-weight: 800; }
    input[type="range"] { width: 100%; accent-color: var(--accent); height: 34px; }
    .wide-btn { width: 100%; min-height: 46px; border-radius: 16px; margin-top: 8px; border: 1px solid var(--line); background: transparent; color: var(--text); font: inherit; cursor: pointer; }
  </style>
</head>
<body data-theme="dark">
  <div class="ptr" id="ptr"><div class="ptr-spinner"></div><div id="ptrText"></div></div>
  <div class="app">
    <div class="toolbar">
      <div class="searchbar"><input id="search" placeholder="جست‌وجوی خبرها..." oninput="render()"></div>
      <div id="updated" class="status"></div>
    </div>
    <main class="container" id="feed"></main>
  </div>
  <button class="fab" id="fabBtn" aria-label="settings">
    <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
  </button>
  <div class="overlay" id="overlay"></div>
  <aside class="sheet" id="sheet">
    <div class="sheet-handle"></div>
    <div class="sheet-inner">
      <div class="sheet-header">
        <div class="sheet-title" id="settingsTitle">تنظیمات</div>
        <button class="close" id="closeSettingsBtn" aria-label="close"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg></button>
      </div>
      <div class="section">
        <div class="section-label" id="viewLabel">نمایش</div>
        <div class="segmented">
          <button data-view-choice="feed" id="viewFeedBtn">خبرها</button>
          <button data-view-choice="archive" id="viewArchiveBtn">بایگانی</button>
        </div>
      </div>
      <div class="section">
        <div class="section-label" id="themeLabel">پوسته</div>
        <div class="segmented">
          <button data-theme-choice="light" id="themeLightBtn">سفید</button>
          <button data-theme-choice="dark" id="themeDarkBtn">تیره</button>
          <button data-theme-choice="comfort" id="themeComfortBtn">راحتی چشم</button>
        </div>
      </div>
      <div class="section">
        <div class="section-label" id="fontLabel">قلم</div>
        <div class="segmented">
          <button data-font-choice="vazirmatn" id="fontVazirmatnBtn">وزیرمتن</button>
          <button data-font-choice="system" id="fontSystemBtn">سیستم</button>
          <button data-font-choice="classic" id="fontClassicBtn">کلاسیک</button>
        </div>
      </div>
      <div class="section">
        <div class="section-label" id="textSizeLabel">اندازه متن</div>
        <input type="range" id="fontSizeRange" min="14" max="22" step="0.5" value="16.5">
      </div>
      <div class="section">
        <div class="section-label" id="languageLabel">زبان</div>
        <div class="segmented">
          <button data-lang-choice="fa" id="langFaBtn">فارسی</button>
          <button data-lang-choice="en" id="langEnBtn">English</button>
        </div>
      </div>
      <button class="wide-btn" id="refreshBtn">به‌روزرسانی</button>
      <button class="wide-btn" id="resetBtn">بازنشانی</button>
    </div>
  </aside>
  <script>
    window.onerror = function(msg, url, line) {
      try {
        var f = document.getElementById('feed');
        if (f) f.innerHTML = '<div class="empty" style="text-align:left;direction:ltr">JS error:<br>' + msg + '<br>line ' + line + '</div>';
      } catch(e) {}
    };
    window.addEventListener("error", function (ev) {
      try {
        var f = document.getElementById('feed');
        if (f) f.innerHTML = '<div class="empty" style="text-align:left;direction:ltr">PAGE error:<br>' + ev.message + '<br>line ' + ev.lineno + '</div>';
      } catch(e) {}
    }, true);
    setTimeout(function () {
      try {
        if (!window.__ok) {
          var u = document.getElementById('updated');
          if (u) u.textContent = 'main script did not finish';
        }
      } catch (e) {}
    }, 1500);
  </script>
  <script>
    window.setStatusBarPad = function (px) { document.documentElement.style.setProperty("--sb-pad", px + "px"); };
    var renderedIds = {};
    var news = [];
    var lastLoadDate = null;
    var loadFailed = false;
    var initialLoaded = false;
    var SEEN_KEY = "seenTweetIds";
    var ARCHIVE_KEY = "archivedTweetIds";
    var viewMode = "feed";
    var archivedIds = loadArchivedIds();
    var seenIds = loadSeenIds();
    var seenObserver = null;
    var dateFormatter = new Intl.DateTimeFormat("fa-IR-u-ca-persian", { dateStyle: "medium", timeStyle: "short" });
    var numberFormatter = new Intl.NumberFormat("fa-IR");
    var I18N = {
      fa: { dateLocale: "fa-IR-u-ca-persian", numberLocale: "fa-IR", dir: "rtl", appTitle: "خبر ایران", searchPlaceholder: "جست‌وجوی خبرها...", loading: "در حال دریافت خبرها...", updatedPrefix: "آخرین به‌روزرسانی:", loadFailed: "دریافت خبرها انجام نشد", noNews: "خبری یافت نشد.", now: "اکنون", thread: "رشته‌خبر", parts: "بخش", newLabel: "جدید", settings: "تنظیمات", theme: "پوسته", themeLight: "سفید", themeDark: "تیره", themeComfort: "راحتی چشم", font: "قلم", fontVazirmatn: "وزیرمتن", fontSystem: "سیستم", fontClassic: "کلاسیک", textSize: "اندازه متن", language: "زبان", refresh: "به‌روزرسانی", reset: "بازنشانی", pullHint: "برای به‌روزرسانی بکشید", releaseHint: "رها کنید تا به‌روزرسانی شود", refreshingHint: "در حال به‌روزرسانی...", view: "نمایش", viewFeed: "خبرها", viewArchive: "بایگانی" },
      en: { dateLocale: "en-US", numberLocale: "en-US", dir: "ltr", appTitle: "Iran News", searchPlaceholder: "Search news...", loading: "Loading news...", updatedPrefix: "Last updated:", loadFailed: "Failed to load news", noNews: "No news found.", now: "Now", thread: "Thread", parts: "parts", newLabel: "New", settings: "Settings", theme: "Theme", themeLight: "White", themeDark: "Dark", themeComfort: "Eye Comfort", font: "Font", fontVazirmatn: "Vazirmatn", fontSystem: "System", fontClassic: "Classic", textSize: "Text size", language: "Language", refresh: "Refresh", reset: "Reset", pullHint: "Pull to refresh", releaseHint: "Release to refresh", refreshingHint: "Refreshing...", view: "View", viewFeed: "News", viewArchive: "Archive" }
    };
    var DEFAULT_SETTINGS = { theme: "dark", font: "vazirmatn", fontSize: 16.5, lang: "fa" };
    var FONT_MAP = { vazirmatn: "'Vazirmatn', system-ui, sans-serif", system: "system-ui, sans-serif", classic: "Georgia, 'Times New Roman', serif" };
    function loadArchivedIds() { try { var raw = localStorage.getItem(ARCHIVE_KEY); if (!raw) return {}; var arr = JSON.parse(raw); var s = {}; for (var i = 0; i < arr.length; i++) s[String(arr[i])] = true; return s; } catch (e) { return {}; } }
    function saveArchivedIds() { try { var arr = Object.keys(archivedIds).slice(-2000); localStorage.setItem(ARCHIVE_KEY, JSON.stringify(arr)); } catch (e) {} }
    function loadSeenIds() { try { var raw = localStorage.getItem(SEEN_KEY); if (!raw) return {}; var arr = JSON.parse(raw); var s = {}; for (var i = 0; i < arr.length; i++) s[String(arr[i])] = true; return s; } catch (e) { return {}; } }
    function saveSeenIds() { try { var arr = Object.keys(seenIds).slice(-1000); localStorage.setItem(SEEN_KEY, JSON.stringify(arr)); } catch (e) {} }
    function maybeInitializeSeenIds(items) { if (localStorage.getItem(SEEN_KEY) !== null) return; for (var i = 0; i < items.length; i++) { var id = String(items[i].tweet_id || "").trim(); if (id) seenIds[id] = true; } saveSeenIds(); }
    function loadSettings() { try { var raw = localStorage.getItem("newsAppSettings"); if (!raw) return JSON.parse(JSON.stringify(DEFAULT_SETTINGS)); var o = JSON.parse(raw); var m = JSON.parse(JSON.stringify(DEFAULT_SETTINGS)); for (var k in o) m[k] = o[k]; return m; } catch (e) { return JSON.parse(JSON.stringify(DEFAULT_SETTINGS)); } }
    function saveSettings() { try { localStorage.setItem("newsAppSettings", JSON.stringify(settings)); } catch (e) {} }
    var settings = loadSettings();
    function currentI18n() { return I18N[settings.lang] || I18N.fa; }
    function t(key) { return currentI18n()[key] || key; }
    function escapeHtml(value) { var s = (value === null || value === undefined) ? "" : String(value); return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;"); }
    function highlightText(text, query) { var value = (text === null || text === undefined) ? "" : String(text); if (!query) return escapeHtml(value); var lower = value.toLowerCase(); var q = query.toLowerCase(); var result = ""; var cursor = 0; var index = lower.indexOf(q, cursor); if (index === -1) return escapeHtml(value); while (index !== -1) { result += escapeHtml(value.slice(cursor, index)); result += "<mark>" + escapeHtml(value.slice(index, index + q.length)) + "</mark>"; cursor = index + q.length; index = lower.indexOf(q, cursor); } result += escapeHtml(value.slice(cursor)); return result; }
    function compareIds(a, b) { try { var x = BigInt(a || "0"); var y = BigInt(b || "0"); if (x < y) return -1; if (x > y) return 1; return 0; } catch (e) { return String(a || "").localeCompare(String(b || "")); } }
    function groupNews(items) { var sorted = items.slice().sort(function (a, b) { var ta = a.created_at || ""; var tb = b.created_at || ""; if (ta && tb && ta !== tb) return ta.localeCompare(tb); return compareIds(a.tweet_id, b.tweet_id); }); var groups = {}; var order = []; for (var i = 0; i < sorted.length; i++) { var item = sorted[i]; var key = item.conversation_id || item.tweet_id || ("r" + i); if (!groups[key]) { groups[key] = []; order.push(key); } groups[key].push(item); } var result = []; for (var g = 0; g < order.length; g++) result.push(groups[order[g]]); result.sort(function (a, b) { var la = a[a.length - 1]; var lb = b[b.length - 1]; var ta = la.created_at || ""; var tb = lb.created_at || ""; if (ta && tb && ta !== tb) return tb.localeCompare(ta); return compareIds(lb.tweet_id, la.tweet_id); }); return result; }
    function formatTime(value) { if (!value) return t("now"); var d = new Date(value); if (isNaN(d.getTime())) return value; return dateFormatter.format(d); }
    function updateStatus() { var el = document.getElementById("updated"); if (loadFailed) { el.textContent = t("loadFailed"); return; } if (!lastLoadDate) { el.textContent = t("loading"); return; } var time = lastLoadDate.toLocaleTimeString(currentI18n().dateLocale, { hour: "2-digit", minute: "2-digit" }); el.textContent = t("updatedPrefix") + " " + time; }
    function isNearTop() { return window.scrollY <= 220; }
    function scrollToTop() { window.scrollTo(0, 0); }
    function setupSeenObserver() { if (!("IntersectionObserver" in window)) return; seenObserver = new IntersectionObserver(function (entries) { entries.forEach(function (entry) { if (!entry.isIntersecting) return; var el = entry.target; if (el.dataset.seenPending === "1") return; el.dataset.seenPending = "1"; setTimeout(function () { markSeen(el); if (seenObserver) seenObserver.unobserve(el); }, 1200); }); }, { threshold: 0.55 }); }
    function observeUnseenCards() { if (!seenObserver) setupSeenObserver(); if (!seenObserver) return; var cards = document.querySelectorAll('.card[data-unseen="true"]'); cards.forEach(function (card) { seenObserver.observe(card); }); }
    function markSeen(card) { var ids = String(card.dataset.tweetIds || "").split(/\s+/).filter(Boolean); var changed = false; ids.forEach(function (id) { if (!seenIds[id]) { seenIds[id] = true; changed = true; } }); if (changed) { card.removeAttribute("data-unseen"); card.querySelectorAll(".chip.new").forEach(function (chip) { chip.remove(); }); saveSeenIds(); } }
    function setupSwipe(card) { var startX = 0, startY = 0, currentX = 0, isSwiping = false; card.addEventListener('touchstart', function (e) { startX = e.touches[0].clientX; startY = e.touches[0].clientY; isSwiping = false; }, {passive: true}); card.addEventListener('touchmove', function (e) { var dx = e.touches[0].clientX - startX; var dy = e.touches[0].clientY - startY; if (!isSwiping && Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 15) { isSwiping = true; card.classList.add('swiping'); } if (isSwiping) { currentX = dx; var translateX = dx * 0.5; card.style.transform = 'translateX(' + translateX + 'px)'; card.style.opacity = Math.max(0.2, 1 - Math.abs(dx) / 400); } }, {passive: true}); card.addEventListener('touchend', function () { if (isSwiping) { card.classList.remove('swiping'); if (Math.abs(currentX) > 120) { var dir = currentX > 0 ? 100 : -100; card.style.transform = 'translateX(' + dir + '%)'; card.style.opacity = '0'; var ids = String(card.dataset.tweetIds || "").split(/\s+/).filter(Boolean); if (viewMode === "feed") { ids.forEach(function (id) { archivedIds[id] = true; }); } else { ids.forEach(function (id) { delete archivedIds[id]; }); } saveArchivedIds(); setTimeout(function () { card.remove(); if (document.querySelectorAll('#feed .card').length === 0) render(); }, 250); } else { card.style.transform = ''; card.style.opacity = ''; } } isSwiping = false; currentX = 0; }, {passive: true}); }
    function render() { var queryRaw = document.getElementById("search").value.trim(); var query = queryRaw.toLowerCase(); var feed = document.getElementById("feed"); var groups = groupNews(news); groups = groups.map(function (group) { return group.filter(function (item) { var id = String(item.tweet_id || "").trim(); return viewMode === "feed" ? !archivedIds[id] : !!archivedIds[id]; }); }).filter(function (group) { return group.length > 0; }); if (query) { groups = groups.map(function (group) { return group.filter(function (item) { var text = String(item.text || "").toLowerCase(); var tag = String(item.tag || "").toLowerCase(); return text.indexOf(query) !== -1 || tag.indexOf(query) !== -1; }); }).filter(function (group) { return group.length > 0; }); } if (groups.length === 0) { feed.innerHTML = '<div class="empty">' + escapeHtml(t("noNews")) + '</div>'; return; } var html = ""; for (var gi = 0; gi < groups.length; gi++) { var group = groups[gi]; var latest = group[group.length - 1]; var chips = []; var tweetIds = ""; var hasUnseen = false; var isFresh = false; for (var i = 0; i < group.length; i++) { var id = String(group[i].tweet_id || "").trim(); if (id) tweetIds += (tweetIds ? " " : "") + id; if (id && !seenIds[id]) hasUnseen = true; if (id && !renderedIds[id]) isFresh = true; } if (hasUnseen) chips.push('<span class="chip new">' + escapeHtml(t("newLabel")) + '</span>'); if (latest.tag) chips.push('<span class="chip">' + escapeHtml(latest.tag) + '</span>'); if (group.length > 1) chips.push('<span class="chip soft">' + escapeHtml(t("thread")) + ' · ' + numberFormatter.format(group.length) + ' ' + escapeHtml(t("parts")) + '</span>'); var texts = ""; for (var j = 0; j < group.length; j++) texts += '<div class="text">' + highlightText(group[j].text, queryRaw) + '</div>'; html += '<article class="card' + (isFresh ? ' fresh' : '') + '" data-unseen="' + (hasUnseen ? 'true' : 'false') + '" data-tweet-ids="' + escapeHtml(tweetIds) + '">' + (chips.length ? '<div class="chips">' + chips.join("") + '</div>' : '') + texts + '<div class="time">' + escapeHtml(formatTime(latest.created_at)) + '</div></article>'; } feed.innerHTML = html; observeUnseenCards(); document.querySelectorAll('.card').forEach(setupSwipe); for (var g2 = 0; g2 < groups.length; g2++) for (var k = 0; k < groups[g2].length; k++) { var id2 = String(groups[g2][k].tweet_id || "").trim(); if (id2) renderedIds[id2] = true; } }
    function loadNews() { var searchActive = Boolean(document.getElementById("search").value.trim()); var stickToTop = !initialLoaded || (!searchActive && isNearTop()); loadFailed = false; updateStatus(); var controller = new AbortController(); var timer = setTimeout(function () { controller.abort(); }, 10000); fetch("/api/news", { signal: controller.signal }).then(function (res) { clearTimeout(timer); return res.json(); }).then(function (data) { var freshData = Array.isArray(data) ? data : []; var changed = JSON.stringify(freshData) !== JSON.stringify(news); news = freshData; maybeInitializeSeenIds(news); lastLoadDate = new Date(); updateStatus(); if (changed) render(); if (stickToTop) setTimeout(scrollToTop, 0); initialLoaded = true; }).catch(function (err) { clearTimeout(timer); loadFailed = true; updateStatus(); }); }
    function openSettings() { document.getElementById("sheet").classList.add("open"); document.getElementById("overlay").classList.add("show"); }
    function closeSettings() { document.getElementById("sheet").classList.remove("open"); document.getElementById("overlay").classList.remove("show"); }
    function applyTheme() { document.body.dataset.theme = settings.theme; var themeColors = { light: "#f5f6fa", dark: "#070b12", comfort: "#171310" }; var themeMeta = document.querySelector('meta[name="theme-color"]'); if (themeMeta) themeMeta.setAttribute("content", themeColors[settings.theme] || "#070b12"); if (window.AndroidBridge) window.AndroidBridge.setWindowBg(themeColors[settings.theme] || "#070b12"); document.querySelectorAll("[data-theme-choice]").forEach(function (btn) { btn.classList.toggle("active", btn.dataset.themeChoice === settings.theme); }); }
    function applyFont() { document.documentElement.style.setProperty("--font-family", FONT_MAP[settings.font] || FONT_MAP.vazirmatn); document.querySelectorAll("[data-font-choice]").forEach(function (btn) { btn.classList.toggle("active", btn.dataset.fontChoice === settings.font); }); }
    function applyFontSize() { document.documentElement.style.setProperty("--base-size", String(settings.fontSize)); document.getElementById("fontSizeRange").value = settings.fontSize; }
    function applyView() { document.querySelectorAll("[data-view-choice]").forEach(function (b) { b.classList.toggle("active", b.dataset.viewChoice === viewMode); }); }
    function applyLanguage() { var i18n = currentI18n(); document.documentElement.lang = settings.lang; document.documentElement.dir = i18n.dir; document.title = i18n.appTitle; dateFormatter = new Intl.DateTimeFormat(i18n.dateLocale, { dateStyle: "medium", timeStyle: "short" }); numberFormatter = new Intl.NumberFormat(i18n.numberLocale); document.getElementById("search").placeholder = t("searchPlaceholder"); document.getElementById("settingsTitle").textContent = t("settings"); document.getElementById("viewLabel").textContent = t("view"); document.getElementById("viewFeedBtn").textContent = t("viewFeed"); document.getElementById("viewArchiveBtn").textContent = t("viewArchive"); document.getElementById("themeLabel").textContent = t("theme"); document.getElementById("themeLightBtn").textContent = t("themeLight"); document.getElementById("themeDarkBtn").textContent = t("themeDark"); document.getElementById("themeComfortBtn").textContent = t("themeComfort"); document.getElementById("fontLabel").textContent = t("font"); document.getElementById("fontVazirmatnBtn").textContent = t("fontVazirmatn"); document.getElementById("fontSystemBtn").textContent = t("fontSystem"); document.getElementById("fontClassicBtn").textContent = t("fontClassic"); document.getElementById("textSizeLabel").textContent = t("textSize"); document.getElementById("languageLabel").textContent = t("language"); document.getElementById("refreshBtn").textContent = t("refresh"); document.getElementById("resetBtn").textContent = t("reset"); document.querySelectorAll("[data-lang-choice]").forEach(function (btn) { btn.classList.toggle("active", btn.dataset.langChoice === settings.lang); }); updateStatus(); render(); }
    function applyAll() { applyView(); applyTheme(); applyFont(); applyFontSize(); applyLanguage(); }
    document.getElementById("fabBtn").addEventListener("click", openSettings);
    document.getElementById("closeSettingsBtn").addEventListener("click", closeSettings);
    document.getElementById("overlay").addEventListener("click", closeSettings);
    document.querySelectorAll("[data-view-choice]").forEach(function (btn) { btn.addEventListener("click", function () { viewMode = btn.dataset.viewChoice; applyView(); render(); closeSettings(); }); });
    document.querySelectorAll("[data-theme-choice]").forEach(function (btn) { btn.addEventListener("click", function () { settings.theme = btn.dataset.themeChoice; saveSettings(); applyTheme(); }); });
    document.querySelectorAll("[data-font-choice]").forEach(function (btn) { btn.addEventListener("click", function () { settings.font = btn.dataset.fontChoice; saveSettings(); applyFont(); }); });
    document.querySelectorAll("[data-lang-choice]").forEach(function (btn) { btn.addEventListener("click", function () { settings.lang = btn.dataset.langChoice; saveSettings(); applyLanguage(); }); });
    document.getElementById("fontSizeRange").addEventListener("input", function (e) { settings.fontSize = parseFloat(e.target.value); saveSettings(); applyFontSize(); });
    document.getElementById("refreshBtn").addEventListener("click", function () { loadNews(); closeSettings(); });
    document.getElementById("resetBtn").addEventListener("click", function () { settings = JSON.parse(JSON.stringify(DEFAULT_SETTINGS)); saveSettings(); applyAll(); });
    var ptrEl = document.getElementById("ptr"); var ptrTextEl = document.getElementById("ptrText"); var ptrState = "idle"; var ptrStartY = null;
    function ptrUpdateText() { if (ptrState === "ready") ptrTextEl.textContent = t("releaseHint"); else if (ptrState === "refreshing") ptrTextEl.textContent = t("refreshingHint"); else ptrTextEl.textContent = t("pullHint"); }
    function sbPad() { var v = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--sb-pad") || "0"); return isNaN(v) ? 0 : v; }
    function ptrSetOffset(offset) { var y = offset <= 0 ? 0 : sbPad() + offset; ptrEl.style.transform = "translateY(calc(-100% + " + y + "px))"; }
    document.addEventListener("touchstart", function (e) { var sheetOpen = document.getElementById("sheet").classList.contains("open"); if (!sheetOpen && window.scrollY <= 0) ptrStartY = e.touches[0].clientY; else ptrStartY = null; }, { passive: true });
    document.addEventListener("touchmove", function (e) { if (ptrStartY === null || ptrState === "refreshing") return; if (window.scrollY > 0) { ptrStartY = null; ptrSetOffset(0); return; } var delta = e.touches[0].clientY - ptrStartY; if (delta <= 0) { ptrState = "idle"; ptrSetOffset(0); return; } e.preventDefault(); ptrEl.style.transition = "none"; var offset = Math.min(90, delta * 0.45); ptrSetOffset(offset); ptrState = offset >= 60 ? "ready" : "pulling"; ptrUpdateText(); }, { passive: false });
    document.addEventListener("touchend", function () { ptrEl.style.transition = ""; if (ptrState === "ready") { ptrState = "refreshing"; ptrEl.classList.add("refreshing"); ptrSetOffset(64); ptrUpdateText(); loadNews(); setTimeout(function () { ptrEl.classList.remove("refreshing"); ptrState = "idle"; ptrSetOffset(0); }, 1200); } else { ptrState = "idle"; ptrSetOffset(0); } ptrStartY = null; });
    var toolbarEl = document.querySelector(".toolbar"); var fabEl = document.getElementById("fabBtn"); var searchEl = document.getElementById("search"); var lastY = window.scrollY; var searchLocked = false;
    function setBarsHidden(hidden) { toolbarEl.classList.toggle("hidden", hidden); fabEl.classList.toggle("hidden", hidden); }
    searchEl.addEventListener("focus", function () { searchLocked = true; setBarsHidden(false); });
    searchEl.addEventListener("blur", function () { searchLocked = false; });
    window.addEventListener("scroll", function () { var y = window.scrollY; if (searchLocked || document.getElementById("sheet").classList.contains("open")) { lastY = y; return; } if (y <= 24) setBarsHidden(false); else if (y > lastY + 3) setBarsHidden(true); else if (y < lastY - 3) setBarsHidden(false); lastY = y; }, { passive: true });
    try {
      applyAll();
      loadNews();
      setInterval(loadNews, 30000);
      window.__ok = true;
    } catch (e) {
      try { document.getElementById("feed").innerHTML = '<div class="empty" style="text-align:left;direction:ltr">INIT error: ' + e.message + '</div>'; } catch (e2) {}
    }
    if ("serviceWorker" in navigator) { window.addEventListener("load", function () { navigator.serviceWorker.register("/sw.js").catch(function () {}); }); }
  </script>
</body>
</html>"""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/manifest.json")
def manifest(): return send_from_directory(BASE_DIR, "manifest.json", mimetype="application/manifest+json")

@app.route("/sw.js")
def service_worker():
    resp = send_from_directory(BASE_DIR, "sw.js", mimetype="application/javascript")
    resp.headers["Cache-Control"] = "no-cache"
    return resp

@app.route("/icon-192.png")
def icon192(): return send_from_directory(BASE_DIR, "icon-192.png", mimetype="image/png")

@app.route("/icon-512.png")
def icon512(): return send_from_directory(BASE_DIR, "icon-512.png", mimetype="image/png")

@app.route("/")
def home(): return PAGE

@app.route("/api/news")
def api_news(): return jsonify(load_news())

@app.route("/favicon.ico")
def favicon(): return "", 204

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, threaded=True)
'''

Path("app.py").write_text(code, encoding="utf-8")
print("app.py written clean")
