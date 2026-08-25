import asyncio
import json
import sys
import difflib
from datetime import datetime, timezone
from pathlib import Path

from twikit import Client

TARGET_USER = "IranIntlBrk"

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


def parse_cookies(cookie_string: str) -> dict:
    cookies = {}
    for part in cookie_string.split(";"):
        if "=" in part:
            k, v = part.strip().split("=", 1)
            cookies[k] = v
    return cookies


def is_similar(text1: str, text2: str, threshold: float = 0.75) -> bool:
    if not text1 or not text2:
        return False
    return difflib.SequenceMatcher(None, text1, text2).ratio() >= threshold


def parse_date(tweet_result):
    legacy = tweet_result.get("legacy", {})
    created_at = legacy.get("created_at", "")
    if created_at:
        try:
            return datetime.fromisoformat(created_at.replace("Z", "+00:00")).isoformat()
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


def merge_news(old_items, new_items):
    conv_map = {}
    for item in old_items:
        cid = item.get("conversation_id")
        if cid:
            conv_map.setdefault(cid, []).append(item)

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

        if cid and cid in conv_map and conv_map[cid]:
            last_old_item = conv_map[cid][-1]
            old_text = last_old_item.get("text", "")
            new_text = new_item.get("text", "")
            if is_similar(old_text, new_text):
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
    cookies = parse_cookies(cookie)

    client = Client(language="en-US")
    client.set_cookies(cookies)

    # Bypass broken x-client-transaction-id init
    async def noop_transaction_init(http, ct_headers):
        print("Bypassing x-client-transaction-id init")
        return

    def fake_generate_transaction_id(method="GET", path="/"):
        return "00000000000000000000000000000000"

    client.client_transaction.init = noop_transaction_init
    client.client_transaction.generate_transaction_id = fake_generate_transaction_id
    if not hasattr(client.client_transaction, "key"):
        try:
            client.client_transaction.key = ""
        except Exception:
            pass

    # Raw user lookup
    raw_user_response, _ = await client.gql.user_by_screen_name(TARGET_USER)
    user_data = raw_user_response.get("data", {}).get("user", {}).get("result", {})
    user_id = (
        user_data.get("rest_id")
        or user_data.get("id_str")
        or str(user_data.get("id", ""))
    )
    if not user_id:
        print(f"Could not find user ID: {json.dumps(raw_user_response)[:300]}")
        sys.exit(1)

    print(f"User ID: {user_id}")

    # Raw tweets fetch
    raw_tweets_response, _ = await client.gql.user_tweets(user_id, cursor=None, count=FETCH_LIMIT)

    tweets = []
    instructions = (
        raw_tweets_response.get("data", {})
        .get("user", {})
        .get("result", {})
        .get("timeline_v2", {})
        .get("timeline", {})
        .get("instructions", [])
    )

    for instruction in instructions:
        if instruction.get("type") != "TimelineAddEntries":
            continue
        for entry in instruction.get("entries", []):
            tweet_result = (
                entry.get("content", {})
                .get("itemContent", {})
                .get("tweet_results", {})
                .get("result", {})
            )
            if not tweet_result:
                continue
            tid = tweet_result.get("rest_id")
            legacy = tweet_result.get("legacy", {})
            text = legacy.get("full_text", "")
            conversation_id = str(legacy.get("conversation_id_str") or tid)

            if tid and text:
                tweets.append({
                    "tweet_id": str(tid),
                    "conversation_id": conversation_id,
                    "created_at": parse_date(tweet_result),
                    "tag": "",
                    "text": text,
                })

    if not tweets:
        print("No tweets were fetched.")
        sys.exit(1)

    new_items = [t for t in tweets if str(t.get("tweet_id", "")).strip()]
    if reset and len(new_items) < 10:
        print("Reset fetch suspiciously small, aborting to avoid data loss.")
        sys.exit(1)

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


if __name__ == "__main__":
    asyncio.run(main())
