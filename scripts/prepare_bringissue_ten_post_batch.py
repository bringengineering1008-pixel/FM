from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "blog" / "batches" / "2026-08-22-bringissue-ten-posts.json"


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def asset_dir(post: dict) -> Path:
    return ROOT / "blog-assets" / f"2026-08-22-{post['slug']}"


def metadata_command(post: dict, dest: Path) -> list[str]:
    return [
        sys.executable,
        "-m",
        "yt_dlp",
        "--skip-download",
        "--write-info-json",
        "-o",
        str(dest / "source.%(ext)s"),
        post["url"],
    ]


def subtitle_command(post: dict, dest: Path) -> list[str]:
    return [
        sys.executable,
        "-m",
        "yt_dlp",
        "--skip-download",
        "--write-auto-subs",
        "--write-subs",
        "--sub-langs",
        "ko",
        "--sub-format",
        "vtt",
        "-o",
        str(dest / "source.%(ext)s"),
        post["url"],
    ]


def video_command(post: dict, dest: Path) -> list[str]:
    return [
        sys.executable,
        "-m",
        "yt_dlp",
        "-f",
        "best[height<=480][ext=mp4]/best[height<=480]/worst",
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


def run_command(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def timestamp_seconds(value: str) -> float:
    hours, minutes, seconds = value.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def vtt_to_samples(vtt_text: str, interval_seconds: int = 30) -> list[str]:
    cue_pattern = re.compile(
        r"(?m)^(\d{2}:\d{2}:\d{2}[.,]\d{3})\s+-->[^\n]*\n(.+?)(?=\n\n|\Z)",
        re.DOTALL,
    )
    samples = []
    next_sample = 0.0
    previous_text = ""
    for match in cue_pattern.finditer(vtt_text.replace("\r\n", "\n")):
        start = timestamp_seconds(match.group(1))
        text = re.sub(r"<[^>]+>", "", match.group(2))
        text = html.unescape(" ".join(text.split())).strip()
        if not text or text == previous_text:
            continue
        previous_text = text
        if start < next_sample:
            continue
        minutes, seconds = divmod(int(start), 60)
        samples.append(f"[{minutes:02d}:{seconds:02d}] {text}")
        next_sample = start + interval_seconds
    return samples


def write_transcript_sample(post: dict, dest: Path) -> None:
    preferred = dest / "source.ko.vtt"
    candidates = [preferred] if preferred.exists() else sorted(dest.glob("source*.vtt"))
    if not candidates:
        raise FileNotFoundError(f"No subtitle file for {post['slug']}")
    lines = vtt_to_samples(candidates[0].read_text(encoding="utf-8-sig"))
    if not lines:
        raise ValueError(f"No transcript samples for {post['slug']}")
    (dest / "transcript-sampled.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def collect(stage: str, slug: str | None = None) -> None:
    command_builders = {
        "metadata": metadata_command,
        "subtitles": subtitle_command,
        "video": video_command,
    }
    for post in selected_posts(slug):
        dest = asset_dir(post)
        dest.mkdir(parents=True, exist_ok=True)
        print(f"[{stage}] {post['slug']}", flush=True)
        if stage == "transcripts":
            write_transcript_sample(post, dest)
            continue
        builder = command_builders[stage]
        run_command(builder(post, dest))
        source_info = dest / "source.info.json"
        if stage == "metadata" and source_info.exists():
            source_info.replace(dest / "info.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "stage", choices=("metadata", "subtitles", "transcripts", "video")
    )
    parser.add_argument("--slug")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    collect(args.stage, args.slug)


if __name__ == "__main__":
    main()
