from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "brand" / "bringissue" / "brand-system.json"
OUTPUT = ROOT / "brand" / "bringissue" / "output"
FONT_BOLD = Path(r"C:\Windows\Fonts\malgunbd.ttf")
FONT_REGULAR = Path(r"C:\Windows\Fonts\malgun.ttf")


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if not path.exists():
        raise FileNotFoundError(f"Required font missing: {path}")
    return ImageFont.truetype(str(path), size)


def build_cover(data: dict) -> Image.Image:
    navy = hex_rgb(data["palette"]["navy"])
    yellow = hex_rgb(data["palette"]["yellow"])
    image = Image.new("RGB", (1600, 400), navy)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((120, 92, 182, 103), fill=yellow)
    draw.text((120, 126), "BRING ISSUE", font=font(FONT_BOLD, 74), fill="white")
    draw.text(
        (122, 226),
        data["tagline"],
        font=font(FONT_REGULAR, 31),
        fill=(220, 228, 239),
    )
    draw.ellipse((1235, -135, 1675, 305), outline=(*yellow, 38), width=42)
    draw.ellipse((1315, -55, 1595, 225), outline=(*yellow, 24), width=22)
    return image


def build_background(data: dict) -> Image.Image:
    ivory = hex_rgb(data["palette"]["ivory"])
    navy = hex_rgb(data["palette"]["navy"])
    yellow = hex_rgb(data["palette"]["yellow"])
    image = Image.new("RGB", (1920, 1200), ivory)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse((-220, -260, 480, 440), outline=(*navy, 18), width=16)
    draw.ellipse((1540, 760, 2050, 1270), outline=(*yellow, 32), width=18)
    return image


def build_profile(data: dict) -> Image.Image:
    navy = hex_rgb(data["palette"]["navy"])
    yellow = hex_rgb(data["palette"]["yellow"])
    image = Image.new("RGB", (600, 600), yellow)
    draw = ImageDraw.Draw(image)
    label = "BI"
    face = font(FONT_BOLD, 220)
    box = draw.textbbox((0, 0), label, font=face)
    x = (600 - (box[2] - box[0])) // 2
    y = (600 - (box[3] - box[1])) // 2 - box[1]
    draw.text((x, y), label, font=face, fill=navy)
    return image


def build_thumbnail(post: dict, data: dict) -> Image.Image:
    source = ROOT / post["source"]
    if not source.exists():
        raise FileNotFoundError(f"Thumbnail source missing: {source}")
    navy = hex_rgb(data["palette"]["navy"])
    yellow = hex_rgb(data["palette"]["yellow"])
    with Image.open(source).convert("RGB") as original:
        image = original.resize((1280, 720), Image.Resampling.LANCZOS)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 430, 1280, 720), fill=(*navy, 214))
    draw.rounded_rectangle((68, 454, 428, 494), radius=10, fill=yellow)
    draw.text(
        (86, 460),
        f"BRING ISSUE · {post['label']}",
        font=font(FONT_BOLD, 20),
        fill=navy,
    )
    title_font = font(FONT_BOLD, 57)
    draw.text((70, 520), post["text"][0], font=title_font, fill="white")
    draw.text((70, 596), post["text"][1], font=title_font, fill="white")
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def build_contact_sheet(thumbnails: list[Path]) -> Image.Image:
    sheet = Image.new("RGB", (960, 852), (244, 241, 232))
    for index, path in enumerate(thumbnails):
        with Image.open(path).convert("RGB") as image:
            thumb = image.resize((448, 252), Image.Resampling.LANCZOS)
        x = 24 + (index % 2) * 472
        y = 24 + (index // 2) * 276
        sheet.paste(thumb, (x, y))
    return sheet


def build_all() -> list[Path]:
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    thumb_dir = OUTPUT / "thumbnails"
    qa_dir = ROOT / "brand" / "bringissue" / "qa"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    qa_dir.mkdir(parents=True, exist_ok=True)
    build_cover(data).save(OUTPUT / "cover.png", optimize=True)
    build_background(data).save(OUTPUT / "background.png", optimize=True)
    build_profile(data).save(OUTPUT / "profile.png", optimize=True)
    thumbnails = []
    for post in data["published_posts"]:
        output = thumb_dir / f"{post['slug']}.jpg"
        build_thumbnail(post, data).save(output, quality=94, optimize=True)
        thumbnails.append(output)
    build_contact_sheet(thumbnails).save(
        qa_dir / "contact-sheet.jpg", quality=92, optimize=True
    )
    return [
        OUTPUT / "cover.png",
        OUTPUT / "background.png",
        OUTPUT / "profile.png",
        *thumbnails,
    ]


if __name__ == "__main__":
    for path in build_all():
        print(path)
