from __future__ import annotations

import argparse
from email import policy
from email.parser import BytesParser
import html
from io import BytesIO
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "blog" / "batches" / "2026-08-22-bringissue-ten-posts.json"
SCENE_ROLES = (
    "도입",
    "계기",
    "첫 선택",
    "반응",
    "질문",
    "결정적 행동",
    "반전 직전",
    "반전",
    "후일담",
    "결론",
)
SCENE_TIMESTAMPS = {
    "jipdaesung-bigbang-camping": [35, 200, 407, 939, 1165, 1290, 1500, 2010, 2760, 3420],
    "yanghongwon-heatwave": [0, 180, 360, 540, 720, 930, 1050, 1200, 1320, 1500],
    "parkgane-fold8-japan": [30, 90, 180, 240, 400, 480, 590, 680, 960, 1140],
    "kimjiyu-bbq-parttime": [30, 183, 323, 426, 696, 990, 1230, 1410, 1515, 1650],
    "itsub-trifold-repair": [0, 30, 93, 123, 154, 185, 216, 248, 495, 555],
    "mocar-gv90": [0, 32, 280, 590, 1020, 1230, 1620, 1780, 1890, 2020],
    "congbeen-korea-return": [90, 235, 330, 535, 885, 1075, 1125, 1175, 1390, 1470],
    "lijulike-goodbye": [30, 125, 280, 350, 380, 540, 780, 1040, 1330, 1460],
    "wonmin-carrot-scam": [0, 60, 156, 240, 360, 430, 570, 660, 780, 890],
    "yenmad-blog-income": [0, 31, 93, 155, 218, 280, 342, 405, 435, 465],
}
THUMBNAIL_SPECS = {
    "jipdaesung-bigbang-camping": (9, "빅뱅 캠핑 준비", "역할이 이렇게 갈렸다"),
    "yanghongwon-heatwave": (8, "폭염 속 육아", "계획보다 먼저 바뀐 것"),
    "parkgane-fold8-japan": (5, "일본의 폴드8", "현장 반응은 달랐다"),
    "kimjiyu-bbq-parttime": (8, "고깃집 막내 체험", "손님은 몰랐던 반복"),
    "itsub-trifold-repair": (5, "359만원 폰 파손", "실제 수리비의 반전"),
    "mocar-gv90": (8, "GV90 첫 공개", "외관보다 놀란 기능"),
    "congbeen-korea-return": (10, "1년 만의 한국", "가장 먼저 찾은 것"),
    "lijulike-goodbye": (5, "잠깐 만난 가족", "다시 헤어질 준비"),
    "wonmin-carrot-scam": (10, "첫 당근 거래", "장난 뒤 돌아온 반응"),
    "yenmad-blog-income": (1, "하루 10분 블로그", "돈 되려면 필요한 일"),
}


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
        "--js-runtimes",
        "node",
        "-f",
        (
            "bestvideo[height<=480][vcodec^=avc1][ext=mp4]"
            "/bestvideo[height<=480][ext=mp4]"
        ),
        "--get-url",
        post["url"],
    ]


def storyboard_command(post: dict, dest: Path) -> list[str]:
    return [
        sys.executable,
        "-m",
        "yt_dlp",
        "--no-warnings",
        "-f",
        "sb0",
        "-o",
        str(dest / "storyboard.mhtml"),
        post["url"],
    ]


def nearest_transcript_caption(dest: Path, timestamp: int) -> str:
    candidates = []
    for line in (dest / "transcript-sampled.txt").read_text(encoding="utf-8").splitlines():
        match = re.match(r"\[(\d+):(\d+)\]\s*(.+)", line)
        if match:
            seconds = int(match.group(1)) * 60 + int(match.group(2))
            candidates.append((abs(seconds - timestamp), match.group(3)))
    return min(candidates, default=(0, "장면 설명 확인 필요"))[1]


def storyboard_tiles(source: Path) -> list[Image.Image]:
    message = BytesParser(policy=policy.default).parsebytes(source.read_bytes())
    tiles = []
    for part in list(message.iter_parts())[1:]:
        if part.get_content_type() != "image/jpeg":
            continue
        sheet = Image.open(BytesIO(part.get_payload(decode=True))).convert("RGB")
        for top in range(0, sheet.height, 180):
            for left in range(0, sheet.width, 320):
                tiles.append(sheet.crop((left, top, left + 320, top + 180)))
    return tiles


def prepare_scene(image: Image.Image) -> Image.Image:
    image = image.resize((1280, 720), Image.Resampling.LANCZOS)
    image = ImageEnhance.Contrast(image).enhance(1.04)
    image = ImageEnhance.Color(image).enhance(1.03)
    return image.filter(ImageFilter.UnsharpMask(radius=1.2, percent=125, threshold=3))


def create_scenes(post: dict, dest: Path) -> None:
    info = json.loads((dest / "info.json").read_text(encoding="utf-8"))
    duration = float(info["duration"])
    tiles = storyboard_tiles(dest / "storyboard.mhtml")
    interval = duration / len(tiles)
    plan = []
    scenes = []
    for number, (role, timestamp) in enumerate(
        zip(SCENE_ROLES, SCENE_TIMESTAMPS[post["slug"]]), start=1
    ):
        tile_index = min(round(timestamp / interval), len(tiles) - 1)
        scene = prepare_scene(tiles[tile_index])
        scene.save(dest / f"scene-{number:02d}.jpg", quality=94, subsampling=0)
        scenes.append(scene)
        minutes, seconds = divmod(timestamp, 60)
        plan.append(
            {
                "number": number,
                "role": role,
                "timestamp_seconds": timestamp,
                "timestamp": f"{minutes:02d}:{seconds:02d}",
                "caption": nearest_transcript_caption(dest, timestamp),
                "storyboard_frame_seconds": round(tile_index * interval, 3),
            }
        )
    (dest / "scene-plan.json").write_text(
        json.dumps({"video_id": post["video_id"], "scenes": plan}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    contact = Image.new("RGB", (1600, 420), "white")
    draw = ImageDraw.Draw(contact)
    for index, scene in enumerate(scenes):
        column, row = index % 5, index // 5
        preview = scene.resize((320, 180), Image.Resampling.LANCZOS)
        x, y = column * 320, row * 210
        contact.paste(preview, (x, y))
        draw.rectangle((x, y + 180, x + 320, y + 210), fill=(20, 24, 31))
        draw.text((x + 10, y + 187), f"{index + 1:02d}  {plan[index]['timestamp']}", fill="white")
    contact.save(dest / "contact-sheet.jpg", quality=92, subsampling=0)


def create_thumbnail(post: dict, dest: Path) -> None:
    scene_number, first_line, second_line = THUMBNAIL_SPECS[post["slug"]]
    image = Image.open(dest / f"scene-{scene_number:02d}.jpg").convert("RGB")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pixels = overlay.load()
    start_y = 310
    for y in range(start_y, image.height):
        alpha = int(215 * ((y - start_y) / (image.height - start_y)) ** 0.75)
        for x in range(image.width):
            pixels[x, y] = (8, 13, 24, alpha)
    image = Image.alpha_composite(image.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(image)
    bold_font = "C:/Windows/Fonts/malgunbd.ttf"
    regular_font = "C:/Windows/Fonts/malgun.ttf"
    label_font = ImageFont.truetype(bold_font, 26)
    title_font = ImageFont.truetype(bold_font, 68)
    brand_font = ImageFont.truetype(regular_font, 22)
    draw.rounded_rectangle((54, 390, 246, 438), radius=20, fill=(255, 106, 47, 240))
    draw.text((78, 398), "오늘 뜬 유튜브", font=label_font, fill="white")
    draw.text(
        (56, 458), first_line, font=title_font, fill="white", stroke_width=2, stroke_fill=(0, 0, 0)
    )
    draw.text(
        (56, 550), second_line, font=title_font, fill=(255, 226, 118), stroke_width=2, stroke_fill=(0, 0, 0)
    )
    draw.text((1070, 668), "BRING ISSUE", font=brand_font, fill=(255, 255, 255, 185))
    image.convert("RGB").save(dest / "thumbnail.jpg", quality=95, subsampling=0)
    (dest / "thumbnail-text.txt").write_text(
        f"{first_line}\n{second_line}\n", encoding="utf-8"
    )


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
        "storyboard": storyboard_command,
    }
    for post in selected_posts(slug):
        dest = asset_dir(post)
        dest.mkdir(parents=True, exist_ok=True)
        print(f"[{stage}] {post['slug']}", flush=True)
        if stage == "transcripts":
            write_transcript_sample(post, dest)
            continue
        if stage == "scenes":
            create_scenes(post, dest)
            continue
        if stage == "thumbnail":
            create_thumbnail(post, dest)
            continue
        builder = command_builders[stage]
        run_command(builder(post, dest))
        source_info = dest / "source.info.json"
        if stage == "metadata" and source_info.exists():
            source_info.replace(dest / "info.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "stage",
        choices=("metadata", "subtitles", "transcripts", "storyboard", "scenes", "thumbnail"),
    )
    parser.add_argument("--slug")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    collect(args.stage, args.slug)


if __name__ == "__main__":
    main()
