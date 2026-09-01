from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from imageio_ffmpeg import get_ffmpeg_exe
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = Path(
    os.environ.get(
        "BRINGISSUE_REGISTRY",
        ROOT / "blog" / "batches" / "2026-08-22-bringissue-twenty-posts.json",
    )
)
NODE_EXE = (
    Path.home()
    / ".cache"
    / "codex-runtimes"
    / "codex-primary-runtime"
    / "dependencies"
    / "node"
    / "bin"
    / "node.exe"
)


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
        "ko-orig,ko",
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
        f"node:{NODE_EXE}",
        "--remote-components",
        "ejs:github",
        "--ffmpeg-location",
        get_ffmpeg_exe(),
        "-f",
        (
            "bestvideo[height<=1080]/"
            "bestvideo[height<=720]/bestvideo"
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


def parse_vtt_cues(vtt: str) -> list[dict[str, float | str]]:
    cues = []
    seen = set()
    blocks = re.split(r"\r?\n\s*\r?\n", vtt)
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        timing_index = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if timing_index is None:
            continue
        start = lines[timing_index].split("-->", 1)[0].strip()
        parts = start.replace(",", ".").split(":")
        try:
            seconds = sum(float(value) * (60 ** power) for power, value in enumerate(reversed(parts)))
        except ValueError:
            continue
        raw_text = " ".join(lines[timing_index + 1 :])
        text = html.unescape(re.sub(r"<[^>]+>", "", raw_text))
        text = re.sub(r"\s+", " ", text).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        cues.append({"seconds": seconds, "text": text})
    return cues


def sample_cues(
    cues: list[dict[str, float | str]],
    interval_seconds: int = 20,
) -> list[dict[str, float | str]]:
    sampled = []
    seen_buckets = set()
    for cue in cues:
        bucket = int(float(cue["seconds"])) // interval_seconds
        if bucket in seen_buckets:
            continue
        seen_buckets.add(bucket)
        sampled.append(cue)
    return sampled


def write_sampled_transcript(post: dict) -> Path:
    dest = asset_dir(post)
    preferred_names = (
        "source.ko-orig.vtt",
        "source.ko.vtt",
        "source.en-orig.vtt",
        "source.en.vtt",
    )
    source = next((dest / name for name in preferred_names if (dest / name).exists()), None)
    output = dest / "transcript-sampled.txt"
    if source is None:
        output.write_text(
            "사용 가능한 공개 자막 없음 — 실제 화면과 공식 설명만 사용하고 대사를 추정하지 않음.\n",
            encoding="utf-8",
        )
        return output
    cues = sample_cues(parse_vtt_cues(source.read_text(encoding="utf-8")))
    lines = [
        f"[{int(float(cue['seconds'])) // 60:02d}:{int(float(cue['seconds'])) % 60:02d}] {cue['text']}"
        for cue in cues
    ]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def build_scene_plan(post: dict, duration: float) -> dict:
    beats = (
        (0.05, "도입", "처음 시선을 끄는 장면", "글의 질문과 대상을 한눈에 소개"),
        (0.15, "상황", "이야기가 시작된 순간", "사건이 시작된 배경을 설명"),
        (0.27, "변화", "첫 번째 변화", "초반 분위기가 달라지는 지점을 제시"),
        (0.38, "맥락", "놓치면 안 될 맥락", "핵심 판단에 필요한 정보를 보충"),
        (0.50, "선택", "선택이 드러난 장면", "인물이나 제작진의 선택을 해석"),
        (0.62, "반전", "분위기가 뒤집힌 순간", "제목의 궁금증을 본문에서 회수"),
        (0.73, "핵심", "가장 중요한 장면", "영상의 중심 메시지를 구체화"),
        (0.84, "결과", "결과가 보인 순간", "선택 뒤에 이어진 결과를 정리"),
        (0.93, "여운", "마지막에 남은 여운", "독자 질문과 편집자 관점으로 연결"),
    )
    scenes = []
    for number, (ratio, role, caption, purpose) in enumerate(beats, start=1):
        seconds = round(min(max(duration * ratio, 0), max(duration - 0.1, 0)), 2)
        scenes.append(
            {
                "number": number,
                "timestamp_seconds": seconds,
                "role": role,
                "caption": caption,
                "body_purpose": f"{purpose}: {post['editorial_angle']}",
            }
        )
    return {"video_id": post["video_id"], "duration": duration, "scenes": scenes}


def write_scene_plan(post: dict) -> Path:
    dest = asset_dir(post)
    info = json.loads((dest / "info.json").read_text(encoding="utf-8"))
    plan = build_scene_plan(post, float(info["duration"]))
    output = dest / "scene-plan.json"
    output.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def find_video(post: dict) -> Path:
    videos = [
        path
        for path in asset_dir(post).glob("source-video.*")
        if path.suffix not in {".part", ".ytdl"}
    ]
    if len(videos) != 1:
        raise FileNotFoundError(f"Expected one completed source video for {post['slug']}")
    return videos[0]


def video_complete(post: dict) -> bool:
    dest = asset_dir(post)
    return (dest / "video-complete.json").exists() or (dest / "scene-09.jpg").exists()


def frame_command(video_path: Path, seconds: float, output_path: Path) -> list[str]:
    return [
        get_ffmpeg_exe(),
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        str(seconds),
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        "-vf",
        "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080",
        "-y",
        str(output_path),
    ]


def extract_scenes(post: dict) -> list[Path]:
    dest = asset_dir(post)
    video = find_video(post)
    plan = json.loads((dest / "scene-plan.json").read_text(encoding="utf-8"))
    outputs = []
    for scene in plan["scenes"]:
        output = dest / f"scene-{scene['number']:02d}.jpg"
        subprocess.run(
            frame_command(video, scene["timestamp_seconds"], output),
            cwd=ROOT,
            check=True,
        )
        outputs.append(output)
    return outputs


def thumbnail_lines(post: dict) -> tuple[str, str]:
    if "thumbnail_text" in post:
        return tuple(post["thumbnail_text"])
    title = re.sub(r"\[[^]]+\]", "", post["source_title"])
    title = re.sub(r"\s+", " ", title).strip()
    words = title.split()
    lines = [""]
    for word in words:
        candidate = f"{lines[-1]} {word}".strip()
        if len(candidate) <= 18:
            lines[-1] = candidate
        elif len(lines) == 1:
            lines.append(word[:18])
        else:
            break
    if len(lines) == 1:
        midpoint = max(1, len(lines[0]) // 2)
        lines = [lines[0][:midpoint], lines[0][midpoint:18]]
    return lines[0], lines[1]


def thumbnail_scene_number(post: dict) -> int:
    return 3 if post["engine"] == "product" else 6


def _cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)))
    left = (resized.width - size[0]) // 2
    top = (resized.height - size[1]) // 2
    return resized.crop((left, top, left + size[0], top + size[1]))


def create_thumbnail(post: dict) -> Path:
    dest = asset_dir(post)
    base_path = dest / f"scene-{thumbnail_scene_number(post):02d}.jpg"
    if not base_path.exists():
        base_path = dest / "scene-01.jpg"
    with Image.open(base_path) as source:
        base = _cover(source.convert("RGB"), (1600, 900))
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 520, 1600, 900), fill=(10, 14, 22, 190))
    draw.rectangle((120, 570, 138, 810), fill=(255, 116, 72, 255))
    font_path = Path("C:/Windows/Fonts/malgunbd.ttf")
    font = ImageFont.truetype(str(font_path), 82)
    small = ImageFont.truetype(str(font_path), 30)
    line_one, line_two = thumbnail_lines(post)
    draw.text((180, 570), line_one, font=font, fill="white", stroke_width=2, stroke_fill="#10141c")
    draw.text((180, 675), line_two, font=font, fill="#ffb092", stroke_width=2, stroke_fill="#10141c")
    draw.text((182, 790), "BRING ISSUE", font=small, fill="#d7dce5")
    result = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    output = dest / "thumbnail.jpg"
    result.save(output, quality=94, subsampling=0)
    (dest / "thumbnail-text.txt").write_text(
        f"{line_one}\n{line_two}\n", encoding="utf-8"
    )
    return output


def create_contact_sheet(post: dict) -> Path:
    dest = asset_dir(post)
    sheet = Image.new("RGB", (1440, 810), "#10141c")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 22)
    for index, scene_path in enumerate(sorted(dest.glob("scene-*.jpg"))[:9]):
        with Image.open(scene_path) as source:
            cell = _cover(source.convert("RGB"), (480, 270))
        x = (index % 3) * 480
        y = (index // 3) * 270
        sheet.paste(cell, (x, y))
        draw.rectangle((x + 8, y + 8, x + 64, y + 42), fill=(0, 0, 0))
        draw.text((x + 17, y + 10), f"{index + 1:02d}", font=font, fill="white")
    output = dest / "contact-sheet.jpg"
    sheet.save(output, quality=92, subsampling=0)
    return output


def collect_posts(
    stage: str,
    posts: list[dict],
    runner=subprocess.run,
) -> list[dict[str, str]]:
    builders = {
        "metadata": metadata_command,
        "subtitles": subtitle_command,
        "video": video_command,
    }
    failures = []
    for post in posts:
        dest = asset_dir(post)
        dest.mkdir(parents=True, exist_ok=True)
        if stage == "video" and video_complete(post):
            print(f"[{stage}:existing] {post['slug']}", flush=True)
            continue
        print(f"[{stage}] {post['slug']}", flush=True)
        try:
            runner(builders[stage](post), cwd=ROOT, check=True)
        except Exception as exc:
            failures.append({"slug": post["slug"], "error": str(exc)})
            print(f"[{stage}:failed] {post['slug']}: {exc}", flush=True)
            continue
        source_info = dest / "source.info.json"
        if stage == "metadata" and source_info.exists():
            source_info.replace(dest / "info.json")
        if stage == "video":
            videos = [
                path
                for path in dest.glob("source-video.*")
                if path.suffix not in {".part", ".ytdl"}
            ]
            (dest / "video-complete.json").write_text(
                json.dumps(
                    [{"name": path.name, "bytes": path.stat().st_size} for path in videos],
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
    return failures


def collect(stage: str, slug: str | None = None) -> list[dict[str, str]]:
    failures = collect_posts(stage, selected_posts(slug))
    report = ROOT / "blog" / "batches" / f"2026-08-22-{stage}-failures.json"
    report.write_text(
        json.dumps(failures, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "stage",
        choices=(
            "metadata",
            "subtitles",
            "video",
            "transcript",
            "scene-plan",
            "scenes",
            "thumbnail",
        ),
    )
    parser.add_argument("--slug")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.stage == "transcript":
        for post in selected_posts(args.slug):
            write_sampled_transcript(post)
        return
    if args.stage == "scene-plan":
        for post in selected_posts(args.slug):
            write_scene_plan(post)
        return
    if args.stage == "scenes":
        for post in selected_posts(args.slug):
            extract_scenes(post)
            create_contact_sheet(post)
        return
    if args.stage == "thumbnail":
        for post in selected_posts(args.slug):
            create_thumbnail(post)
        return
    failures = collect(args.stage, args.slug)
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
