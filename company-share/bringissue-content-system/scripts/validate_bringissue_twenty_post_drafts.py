from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.prepare_bringissue_twenty_post_batch import asset_dir, load_registry


def visible_text(line: str) -> str:
    return re.sub(r"<[^>]+>", "", line).strip()


def validate_draft(text: str) -> list[str]:
    errors = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    prose = [
        visible_text(line)
        for line in lines
        if not line.startswith(("#", ">", "![", "*", "원본 영상:", "출처:", "※"))
    ]
    if any(len(line) > 70 for line in prose):
        errors.append("body paragraph exceeds 70 visible characters")
    if not 3 <= text.count("<b>") <= 5:
        errors.append("bold count must be 3 to 5")
    if text.count("<u>") > 1:
        errors.append("underline count must be zero or one")
    if not 2 <= text.count("\n> ") <= 3:
        errors.append("quote transition count must be 2 to 3")
    if text.count("![장면") != 9:
        errors.append("draft must include exactly nine scene images")
    if not 1 <= sum(text.count(emoji) for emoji in ("👀", "🙂")) <= 2:
        errors.append("emoji count must be 1 to 2")
    return errors


def main() -> None:
    failed = False
    for post in load_registry()["posts"]:
        draft_path = asset_dir(post) / "post-draft.md"
        errors = validate_draft(draft_path.read_text(encoding="utf-8"))
        if errors:
            failed = True
            print(f"FAIL {post['slug']}: {', '.join(errors)}")
        else:
            print(f"OK   {post['slug']}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
