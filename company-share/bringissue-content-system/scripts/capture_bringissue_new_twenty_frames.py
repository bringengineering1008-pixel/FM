from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import yt_dlp
from imageio_ffmpeg import get_ffmpeg_exe


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = Path(os.environ["BRINGISSUE_REGISTRY"])
RATIOS = (0.08, 0.22, 0.38, 0.55, 0.72, 0.88)


def destination(post: dict) -> Path:
    return ROOT / "blog-assets" / f"{post['scheduled_at'][:10]}-{post['slug']}"


def video_url(page_url: str) -> tuple[str, float]:
    options = {
        "quiet": True,
        "skip_download": True,
        "format": (
            "bestvideo[height<=1080][protocol^=http][vcodec^=avc1]/"
            "bestvideo[height<=720][protocol^=http][vcodec^=avc1]/"
            "bestvideo[height<=720][protocol^=http]"
        ),
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(page_url, download=False)
    return info["url"], float(info["duration"])


def main() -> None:
    posts = json.loads(REGISTRY.read_text(encoding="utf-8"))["posts"]
    requested_slug = os.environ.get("BRINGISSUE_SLUG")
    if requested_slug:
        posts = [post for post in posts if post["slug"] == requested_slug]
    ffmpeg = get_ffmpeg_exe()
    for post in posts:
        outdir = destination(post)
        outdir.mkdir(parents=True, exist_ok=True)
        if all((outdir / f"scene-{i:02d}.jpg").exists() for i in range(1, 7)):
            print(f"[existing] {post['slug']}", flush=True)
            continue
        print(f"[capture] {post['slug']}", flush=True)
        try:
            source, duration = video_url(post["url"])
            for i, ratio in enumerate(RATIOS, 1):
                output = outdir / f"scene-{i:02d}.jpg"
                timestamp = max(1.0, min(duration * ratio, duration - 1.0))
                subprocess.run(
                    [
                        ffmpeg,
                        "-hide_banner",
                        "-loglevel",
                        "error",
                        "-ss",
                        f"{timestamp:.2f}",
                        "-i",
                        source,
                        "-frames:v",
                        "1",
                        "-vf",
                        "scale='min(1600,iw)':-2",
                        "-q:v",
                        "2",
                        "-y",
                        str(output),
                    ],
                    check=True,
                )
        except Exception as exc:
            print(f"[failed] {post['slug']}: {exc}", flush=True)


if __name__ == "__main__":
    main()
