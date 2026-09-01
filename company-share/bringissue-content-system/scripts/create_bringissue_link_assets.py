from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FONT_REGULAR = Path(r"C:\Windows\Fonts\malgun.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\malgunbd.ttf")
SIZE = (1200, 675)


def font(size: int, bold: bool = False):
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size)


def fit_cover(image: Image.Image, size=SIZE):
    ratio = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize((round(image.width * ratio), round(image.height * ratio)), Image.Resampling.LANCZOS)
    left = (resized.width - size[0]) // 2
    top = (resized.height - size[1]) // 2
    return resized.crop((left, top, left + size[0], top + size[1]))


def gradient_overlay(image: Image.Image, start_y=270, max_alpha=225):
    result = image.convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    px = overlay.load()
    for y in range(start_y, image.height):
        alpha = round(max_alpha * (y - start_y) / max(1, image.height - start_y))
        for x in range(image.width):
            px[x, y] = (10, 10, 14, alpha)
    return Image.alpha_composite(result, overlay).convert("RGB")


def draw_cover(source: Path, output: Path, kicker: str, line1: str, line2: str):
    image = fit_cover(Image.open(source).convert("RGB"))
    image = ImageEnhance.Contrast(image).enhance(1.04)
    image = gradient_overlay(image)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((58, 370, 315, 420), 24, fill=(255, 230, 102))
    draw.text((82, 379), kicker, font=font(24, True), fill=(28, 28, 32))
    draw.text((58, 444), line1, font=font(56, True), fill="white", stroke_width=2, stroke_fill=(0, 0, 0))
    draw.text((58, 516), line2, font=font(56, True), fill="white", stroke_width=2, stroke_fill=(0, 0, 0))
    draw.text((60, 616), "BRING ISSUE", font=font(20, True), fill=(255, 230, 102))
    image.save(output, quality=95)


def make_card(output: Path, number: int, title: str, subtitle: str, palette):
    bg, panel, accent, ink = palette
    image = Image.new("RGB", SIZE, bg)
    draw = ImageDraw.Draw(image)
    draw.ellipse((900, -180, 1300, 220), fill=accent)
    draw.ellipse((-120, 500, 180, 800), fill=panel)
    draw.rounded_rectangle((90, 76, 1110, 599), 46, fill=panel)
    draw.rounded_rectangle((140, 126, 242, 178), 24, fill=accent)
    draw.text((169, 137), f"0{number}", font=font(22, True), fill=ink)
    title_font = font(46, True)
    draw.multiline_text((140, 220), title, font=title_font, fill=ink, spacing=12)
    title_box = draw.multiline_textbbox((140, 220), title, font=title_font, spacing=12)
    divider_y = max(326, title_box[3] + 26)
    draw.line((140, divider_y, 1060, divider_y), fill=accent, width=7)
    y = divider_y + 46
    for line in subtitle.split("\n"):
        draw.text((140, y), line, font=font(31), fill=ink)
        y += 52
    draw.text((918, 622), "BRING ISSUE", font=font(18, True), fill=ink)
    image.save(output, quality=95)


def main():
    first = ROOT / "blog-assets/2026-08-24-hayoonkyung-naejangtang"
    second = ROOT / "blog-assets/2026-08-24-goyounjung-rescene-gift"

    draw_cover(
        first / "scene-10.jpg",
        first / "cover.jpg",
        "오늘 뜬 유튜브",
        '"여긴 비밀이었는데…"',
        "하윤경 단골집의 반전",
    )
    draw_cover(
        second / "community-original.jpg",
        second / "cover.jpg",
        "오늘 뜬 이야기",
        '"숙소 앞에 이게 왔다"',
        "고윤정의 깜짝 이사 선물",
    )

    cards = [
        (2, "숙소 앞에 도착한\n비밀 선물", "받는 순간까지 알리지 않은\n고윤정의 깜짝 이사 선물"),
        (3, "말보다 먼저\n도착한 마음", "좋아한다는 말을 기억하고\n행동으로 답한 선배"),
        (4, "큰 전신거울\n+ 스툴 의자", "새 숙소에서 매일 쓸 수 있는\n실용적인 두 가지 선물"),
        (5, "왜 이사 선물로\n골랐을까?", "스타일과 무대 의상을 확인하는\n아이돌의 일상을 생각한 선택"),
        (6, "고윤정 배우님\n→ 윤정 언니", "팬들이 가장 먼저 발견한\n호칭의 따뜻한 변화"),
        (7, "호칭이 보여준\n거리의 변화", "공개된 사실 이상은 단정하지 않고\n가까워진 분위기만 읽었습니다"),
        (8, "기억하고, 골라서,\n몰래 보냈다", "이번 이야기가 짧지만\n오래 남은 세 가지 이유"),
        (9, "팬심이 인연이 된\n순간", "일방적인 좋아함에서 시작해\n따뜻한 선후배 이야기로"),
        (10, "마음을 움직인 건\n선물의 크기가 아니다", "상대의 말을 가볍게\n흘려듣지 않은 태도"),
    ]
    palettes = [
        ((255, 249, 229), (255, 255, 255), (255, 226, 93), (39, 37, 34)),
        ((255, 239, 235), (255, 252, 249), (255, 191, 169), (52, 38, 39)),
        ((239, 246, 255), (255, 255, 255), (174, 210, 255), (34, 45, 61)),
    ]
    for idx, title, subtitle in cards:
        make_card(second / f"card-{idx:02d}.jpg", idx, title, subtitle, palettes[(idx - 2) % len(palettes)])


if __name__ == "__main__":
    main()
