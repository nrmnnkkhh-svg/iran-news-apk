from pathlib import Path

p = Path("app.py")
src = p.read_text(encoding="utf-8")

CSS_OLD = """      border-radius: 22px;
      padding: 18px 18px 16px;
      box-shadow: var(--shadow);
      animation: fadeUp 0.28s ease;
    }"""
CSS_NEW = """      border-radius: 22px;
      padding: 18px 18px 16px;
      box-shadow: var(--shadow);
    }

    .card.fresh {
      animation: fadeUp 0.28s ease;
    }"""

JS_TOP_OLD = "    let news = [];"
JS_TOP_NEW = """    let renderedIds = new Set();

    let news = [];"""

FRESH_OLD = """        const hasUnseen = group.some(item => {
          const id = String(item.tweet_id || "").trim();
          return id && !seenIds.has(id);
        });"""
FRESH_NEW = """        const hasUnseen = group.some(item => {
          const id = String(item.tweet_id || "").trim();
          return id && !seenIds.has(id);
        });

        const isFresh = group.some(item => {
          const id = String(item.tweet_id || "").trim();
          return id && !renderedIds.has(id);
        });"""

ARTICLE_OLD = '          <article class="card" data-unseen="${hasUnseen ? "true" : "false"}" data-tweet-ids="${escapeHtml(tweetIds)}">'
ARTICLE_NEW = '          <article class="card${isFresh ? " fresh" : ""}" data-unseen="${hasUnseen ? "true" : "false"}" data-tweet-ids="${escapeHtml(tweetIds)}">'

OBSERVE_OLD = "      observeUnseenCards();"
OBSERVE_NEW = """      observeUnseenCards();

      groups.forEach(group => {
        group.forEach(item => {
          const id = String(item.tweet_id || "").trim();
          if (id) renderedIds.add(id);
        });
      });"""

LOAD_OLD = """        const data = await res.json();

        news = Array.isArray(data) ? data : [];

        maybeInitializeSeenIds(news);

        lastLoadDate = new Date();

        updateStatus();
        render();"""
LOAD_NEW = """        const data = await res.json();

        const freshData = Array.isArray(data) ? data : [];
        const changed = JSON.stringify(freshData) !== JSON.stringify(news);

        news = freshData;

        maybeInitializeSeenIds(news);

        lastLoadDate = new Date();

        updateStatus();

        if (changed) {
          render();
        }"""

for old, new in [
    (CSS_OLD, CSS_NEW),
    (JS_TOP_OLD, JS_TOP_NEW),
    (FRESH_OLD, FRESH_NEW),
    (ARTICLE_OLD, ARTICLE_NEW),
    (OBSERVE_OLD, OBSERVE_NEW),
    (LOAD_OLD, LOAD_NEW),
]:
    if old not in src:
        print("NOT FOUND:", old[:70])
        raise SystemExit(1)
    src = src.replace(old, new, 1)

Path("app.py.bak").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
p.write_text(src, encoding="utf-8")
print("smooth refresh patch applied")
