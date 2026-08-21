from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "blog" / "batches" / "2026-08-22-bringissue-twenty-posts.json"


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def asset_dir(post: dict) -> Path:
    scheduled_date = post["scheduled_at"][:10]
    return ROOT / "blog-assets" / f"{scheduled_date}-{post['slug']}"


def metadata_command(post: dict) -> list[str]:
    dest = asset_dir(post)
    return [
        sys.executable,
        "-m",
        "yt_dlp",
        "--no-update",
        "--skip-download",
        "--write-info-json",
        "-o",
        str(dest / "source.%(ext)s"),
        post["url"],
    ]


def subtitle_command(post: dict) -> list[str]:
    dest = asset_dir(post)
    return [
        sys.executable,
        "-m",
        "yt_dlp",
        "--no-update",
        "--skip-download",
        "--write-auto-subs",
        "--write-subs",
        "--sub-langs",
        "ko.*,ko,en.*",
        "--sub-format",
        "vtt",
        "-o",
        str(dest / "source.%(ext)s"),
        post["url"],
    ]


def video_command(post: dict) -> list[str]:
    dest = asset_dir(post)
    return [
        sys.executable,
        "-m",
        "yt_dlp",
        "--no-update",
        "--js-runtimes",
        "node",
        "-f",
        (
            "bestvideo[height<=2160]/"
            "bestvideo[height<=1440]/"
            "bestvideo[height<=1080]/bestvideo"
        ),
        "-o",
        str(dest / "source-video.%(ext)s"),
        post["url"],
    ]


def selected_posts(slug: str | None = None) -> list[dict]:
    posts = load_registry()["posts"]
    if slug is None:
        return posts
    selected = [post for post in posts if post["slug"] == slug]
    if not selected:
        raise ValueError(f"Unknown slug: {slug}")
    return selected


def collect(stage: str, slug: str | None = None) -> None:
    builders = {
        "metadata": metadata_command,
        "subtitles": subtitle_command,
        "video": video_command,
    }
    for post in selected_posts(slug):
        dest = asset_dir(post)
        dest.mkdir(parents=True, exist_ok=True)
        print(f"[{stage}] {post['slug']}", flush=True)
        subprocess.run(builders[stage](post), cwd=ROOT, check=True)
        source_info = dest / "source.info.json"
        if stage == "metadata" and source_info.exists():
            source_info.replace(dest / "info.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("metadata", "subtitles", "video"))
    parser.add_argument("--slug")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    collect(args.stage, args.slug)


if __name__ == "__main__":
    main()
