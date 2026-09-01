from __future__ import annotations

import argparse
import concurrent.futures
import html
import json
import re
import statistics
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path


BLOG_ID = "blogpeople"
LIST_URL = "https://blog.naver.com/PostTitleListAsync.naver"
VIEW_URL = "https://blog.naver.com/PostView.naver"
EMOJI_PATTERN = re.compile(
    r"(?:[\U0001F1E6-\U0001F1FF]|[\U0001F300-\U0001FAFF]|[\u2600-\u27BF])"
    r"(?:[\uFE0E\uFE0F])?(?:[\U0001F3FB-\U0001F3FF])?"
    r"(?:\u200D(?:[\U0001F300-\U0001FAFF]|[\u2600-\u27BF])(?:[\uFE0E\uFE0F])?)*"
)


def fetch(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/126 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        raw = response.read()
        charset = response.headers.get_content_charset()
        if charset:
            return raw.decode(charset, errors="replace")
        for candidate in ("utf-8", "euc-kr"):
            decoded = raw.decode(candidate, errors="replace")
            if decoded.count("�") < max(1, len(decoded) // 5000):
                return decoded
        return raw.decode("euc-kr", errors="replace")


def collect_posts(limit: int) -> list[dict]:
    posts: list[dict] = []
    page = 1
    while len(posts) < limit:
        query = urllib.parse.urlencode(
            {
                "blogId": BLOG_ID,
                "viewdate": "",
                "currentPage": page,
                "categoryNo": 0,
                "parentCategoryNo": "",
                "countPerPage": 30,
            }
        )
        raw_payload = fetch(f"{LIST_URL}?{query}")
        raw_payload = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', raw_payload)
        payload = json.loads(raw_payload)
        batch = payload.get("postList", [])
        if not batch:
            break
        for item in batch:
            if item.get("isPostNotOpen") == "1" or item.get("isPostBlocked") == 1:
                continue
            posts.append(
                {
                    "logNo": item["logNo"],
                    "title": urllib.parse.unquote_plus(item.get("title", "")),
                    "date": item.get("addDate", ""),
                    "categoryNo": item.get("categoryNo", ""),
                    "commentCount": int("".join(re.findall(r"\d", str(item.get("commentCount") or 0))) or 0),
                    "url": f"https://blog.naver.com/{BLOG_ID}/{item['logNo']}",
                }
            )
            if len(posts) >= limit:
                break
        page += 1
    return posts


def strip_tags(fragment: str) -> str:
    fragment = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.I)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    return html.unescape(fragment).replace("\u200b", "").strip()


def analyze_post(post: dict) -> dict:
    query = urllib.parse.urlencode(
        {
            "blogId": BLOG_ID,
            "logNo": post["logNo"],
            "redirect": "Dlog",
            "widgetTypeCall": "true",
            "directAccess": "false",
        }
    )
    page = fetch(f"{VIEW_URL}?{query}")
    paragraphs = [
        strip_tags(value)
        for value in re.findall(
            r'<p[^>]*class="[^"]*se-text-paragraph[^"]*"[^>]*>(.*?)</p>',
            page,
            flags=re.I | re.S,
        )
    ]
    paragraphs = [value for value in paragraphs if value]
    body = "\n".join(paragraphs)
    image_count = len(re.findall(r'class="[^"]*se-image-resource', page, flags=re.I))
    link_count = len(re.findall(r'class="[^"]*se-oglink-info', page, flags=re.I))
    quote_count = len(re.findall(r'class="[^"]*se-quotation', page, flags=re.I))
    divider_count = len(re.findall(r'class="[^"]*se-horizontalLine', page, flags=re.I))
    table_count = len(re.findall(r'class="[^"]*se-table', page, flags=re.I))
    video_count = len(re.findall(r'class="[^"]*se-video', page, flags=re.I))
    sticker_count = len(re.findall(r'class="[^"]*se-sticker', page, flags=re.I))
    # The rendered body can repeat the post title. Count the title only when it
    # is not already present near the beginning, avoiding inflated frequencies.
    emoji_source = body
    title_probe = post["title"].strip()
    if title_probe and title_probe not in body[: max(300, len(title_probe) + 80)]:
        emoji_source = post["title"] + "\n" + body
    emoji_characters = EMOJI_PATTERN.findall(emoji_source)
    emoji_count = len(emoji_characters)
    question_count = (post["title"] + body).count("?")
    numbered = sum(bool(re.match(r"^\s*(?:\d+[.)]|STEP\s*\d+|[①-⑳])", p, re.I)) for p in paragraphs)
    short_paragraphs = sum(len(p) <= 60 for p in paragraphs)
    return {
        **post,
        "paragraphCount": len(paragraphs),
        "charCount": len(body),
        "medianParagraphChars": int(statistics.median([len(p) for p in paragraphs])) if paragraphs else 0,
        "shortParagraphShare": round(short_paragraphs / len(paragraphs), 3) if paragraphs else 0,
        "imageCount": image_count,
        "linkCount": link_count,
        "quoteCount": quote_count,
        "dividerCount": divider_count,
        "tableCount": table_count,
        "videoCount": video_count,
        "stickerCount": sticker_count,
        "emojiCount": emoji_count,
        "emojiCharacters": emoji_characters,
        "questionCount": question_count,
        "numberedParagraphCount": numbered,
        "hasBracketLabel": bool(re.match(r"^\[[^\]]+\]", post["title"])),
        "hasQuestionTitle": "?" in post["title"],
        "hasNumberTitle": bool(re.search(r"\d", post["title"])),
        "hasColonTitle": ":" in post["title"] or "：" in post["title"],
        "firstParagraph": paragraphs[0][:160] if paragraphs else "",
    }


def median(rows: list[dict], key: str) -> float:
    return round(statistics.median([row[key] for row in rows]), 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    posts = collect_posts(args.limit)
    rows_by_id: dict[str, dict] = {}
    failures: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(analyze_post, post): post for post in posts}
        for index, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            post = futures[future]
            try:
                rows_by_id[post["logNo"]] = future.result()
            except Exception as exc:  # noqa: BLE001 - preserve failed posts in the audit
                failures.append({"logNo": post["logNo"], "error": type(exc).__name__})
            if index % 10 == 0:
                print(f"analyzed {index}/{len(posts)}", flush=True)
    rows = [rows_by_id[post["logNo"]] for post in posts if post["logNo"] in rows_by_id]

    title_tokens = Counter()
    emoji_tokens = Counter()
    for row in rows:
        title_tokens.update(re.findall(r"[가-힣A-Za-z0-9]+", row["title"].lower()))
        emoji_tokens.update(row["emojiCharacters"])
    summary = {
        "blogId": BLOG_ID,
        "requested": args.limit,
        "collected": len(posts),
        "analyzed": len(rows),
        "failures": failures,
        "dateRange": {"newest": rows[0]["date"] if rows else "", "oldest": rows[-1]["date"] if rows else ""},
        "categoryCounts": Counter(row["categoryNo"] for row in rows),
        "medians": {
            key: median(rows, key)
            for key in [
                "charCount",
                "paragraphCount",
                "medianParagraphChars",
                "shortParagraphShare",
                "imageCount",
                "linkCount",
                "quoteCount",
                "dividerCount",
                "tableCount",
                "videoCount",
                "emojiCount",
            ]
        },
        "shares": {
            key: round(sum(bool(row[key]) for row in rows) / len(rows), 3) if rows else 0
            for key in [
                "hasBracketLabel",
                "hasQuestionTitle",
                "hasNumberTitle",
                "hasColonTitle",
                "imageCount",
                "linkCount",
                "quoteCount",
                "dividerCount",
                "tableCount",
                "videoCount",
                "emojiCount",
            ]
        },
        "topTitleTokens": title_tokens.most_common(30),
        "emojiFrequency": emoji_tokens.most_common(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"summary": summary, "posts": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, default=dict))


if __name__ == "__main__":
    main()
