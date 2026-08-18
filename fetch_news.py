import asyncio
import json
import sys
import difflib
from datetime import datetime, timezone
from pathlib import Path

from twscrape import API

TARGET_USER = "IranIntlBrk"
BURNER_USERNAME = "NRMNDIDI"

COOKIE_FILE = Path("x_cookies_clone.txt")
NEWS_FILE = Path("news.json")

FETCH_LIMIT = 50
MAX_STORED = 200


def read_cookie():
    if not COOKIE_FILE.exists():
        print("Missing cookie file: x_cookies_clone.txt")
        sys.exit(1)

    cookie = COOKIE_FILE.read_text(encoding="utf-8").strip()
    if not cookie:
        print("Cookie file is empty.")
        sys.exit(1)
    return cookie


def parse_date(tweet):
    for attr in ("date", "created_at", "timestamp"):
        value = getattr(tweet, attr, None)
        if value is None:
            continue

        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc).isoformat()

        try:
            ts = float(value)
            if ts > 1_000_000_000_000:
                ts = ts / 1000
            return datetime.fromtimestamp(ts, timezone.utc).isoformat()
        except Exception:
            pass

    return datetime.now(timezone.utc).isoformat()


def load_existing_news():
    if not NEWS_FILE.exists():
        return []
    try:
        data = json.loads(NEWS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def is_similar(text1: str, text2: str, threshold: float = 0.75) -> bool:
    if not text1 or not text2:
        return False
    return difflib.SequenceMatcher(None, text1, text2).ratio() >= threshold


def merge_news(old_items, new_items):
    conv_map = {}
    for item in old_items:
        cid = item.get("conversation_id")
        if cid:
            conv_map.setdefault(cid, []).append(item)

    for cid in conv_map:
        conv_map[cid].sort(key=lambda x: (x.get("created_at", ""), int(x.get("tweet_id", "0") or 0)))

    final_items = []
    seen_ids = set()

    for item in old_items:
        tid = str(item.get("tweet_id", "")).strip()
        if tid:
            seen_ids.add(tid)
            final_items.append(item)

    for new_item in new_items:
        tid = str(new_item.get("tweet_id", "")).strip()
        if not tid or tid in seen_ids:
            continue

        cid = new_item.get("conversation_id")

        # Similarity dedup: check if it's an edit/repost of the last tweet in the thread
        if cid and cid in conv_map and conv_map[cid]:
            last_old_item = conv_map[cid][-1]
            old_text = last_old_item.get("text", "")
            new_text = new_item.get("text", "")

            if is_similar(old_text, new_text):
                # Replace the old item's data with the new one
                for i, item in enumerate(final_items):
                    if str(item.get("tweet_id", "")) == str(last_old_item.get("tweet_id", "")):
                        final_items[i]["text"] = new_text
                        final_items[i]["tweet_id"] = tid
                        final_items[i]["created_at"] = new_item.get("created_at")
                        conv_map[cid][-1] = final_items[i]
                        break
                seen_ids.add(tid)
                continue

        seen_ids.add(tid)
        final_items.append(new_item)
        if cid:
            conv_map.setdefault(cid, []).append(new_item)

    final_items.sort(
        key=lambda item: (
            item.get("created_at", ""),
            int(item.get("tweet_id", "0") or 0)
        ),
        reverse=True
    )

    return final_items[:MAX_STORED]


async def main():
    reset = "--reset" in sys.argv

    cookie = read_cookie()
    api = API()

    try:
        await api.pool.add_account_cookies(BURNER_USERNAME, cookie)
    except Exception as exc:
        print(f"Could not load clone cookies: {exc}")
        sys.exit(1)

    try:
        account = await api.pool.get_account(BURNER_USERNAME)
        if account is None or not account.active:
            print("Clone account is not active.")
            sys.exit(1)

        user = await api.user_by_login(TARGET_USER)
        user_id = user.id

        tweets = []
        seen = set()
        async for tweet in api.user_tweets(user_id, limit=FETCH_LIMIT):
            if tweet.id in seen:
                continue
            seen.add(tweet.id)
            tweets.append(tweet)
            if len(tweets) >= FETCH_LIMIT:
                break

        if not tweets:
            print("No tweets were fetched.")
            sys.exit(1)

        new_items = []
        for tweet in tweets:
            text = (getattr(tweet, "rawContent", "") or "").strip()
            if not text:
                continue

            conversation_id = str(getattr(tweet, "conversationId", "") or tweet.id)
            new_items.append({
                "tweet_id": str(tweet.id),
                "conversation_id": conversation_id,
                "created_at": parse_date(tweet),
                "tag": "",
                "text": text,
            })

        old_items = [] if reset else load_existing_news()
        merged = merge_news(old_items, new_items)

        temp_file = NEWS_FILE.with_suffix(".json.tmp")
        temp_file.write_text(
            json.dumps(merged, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        temp_file.replace(NEWS_FILE)

        print(f"Fetched {len(new_items)} tweets.")
        print(f"news.json now contains {len(merged)} items (duplicates merged).")

    except Exception as exc:
        print(f"Fetch failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
