from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "blog" / "assets" / "2026-08-23-chuseok-train-ticket"
FONT_BOLD = "C:/Windows/Fonts/malgunbd.ttf"
FONT_REGULAR = "C:/Windows/Fonts/malgun.ttf"


def font(size: int, bold: bool = False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


def fit_cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    image = image.convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)))
    left = (resized.width - size[0]) // 2
    top = (resized.height - size[1]) // 2
    return resized.crop((left, top, left + size[0], top + size[1]))


def cover():
    source = Image.open(OUT / "ktx-unsplash.jpg")
    canvas = fit_cover(source, (1080, 1080))
    canvas = ImageEnhance.Brightness(canvas).enhance(0.58)
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rounded_rectangle((70, 70, 392, 142), 26, fill=(255, 214, 72, 245))
    draw.text((105, 85), "2026 추석 기차표", font=font(34, True), fill="#172033")
    draw.text((76, 600), "예매 날짜보다", font=font(69, True), fill="white")
    draw.text((76, 690), "먼저 볼 것", font=font(84, True), fill="#FFD648")
    draw.rounded_rectangle((74, 827, 1000, 943), 24, fill=(18, 29, 51, 220))
    draw.text((108, 850), "통합회원 확인 안 하면 시작도 못 합니다", font=font(40, True), fill="white")
    canvas.save(OUT / "cover.jpg", quality=94)


def card(title: str, subtitle: str, rows: list[tuple[str, str]], filename: str):
    canvas = Image.new("RGB", (1200, 900), "#F6F4EE")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((55, 48, 1145, 160), 28, fill="#172A46")
    draw.text((94, 73), title, font=font(49, True), fill="white")
    draw.text((72, 190), subtitle, font=font(29), fill="#536071")
    y = 270
    for left, right in rows:
        draw.rounded_rectangle((70, y, 1130, y + 96), 22, fill="white", outline="#D9D4C7", width=2)
        draw.text((105, y + 26), left, font=font(31, True), fill="#172A46")
        draw.text((430, y + 27), right, font=font(29), fill="#20252D")
        y += 112
    draw.text((72, 844), "자료: 한국철도공사 공식 보도자료 · 확인 2026.08.23", font=font(24), fill="#7A746B")
    canvas.save(OUT / filename, quality=95)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cover()
    card(
        "일반 예매는 9월 7일~11일",
        "매일 오전 7시부터 오후 1시까지 · 통합회원만 가능",
        [
            ("9월 7일", "모든 노선 일반열차"),
            ("9월 8일", "경전·강릉·동해·중앙·중부내륙선 KTX"),
            ("9월 9일", "호남·전라선 KTX"),
            ("9월 10일", "수서 출발·도착 KTX 지정 노선"),
            ("9월 11일", "경부선 KTX"),
        ],
        "schedule-card.jpg",
    )
    card(
        "예매 전날까지 확인할 4가지",
        "예매 화면에 들어간 뒤 준비하면 늦을 수 있습니다",
        [
            ("① 통합회원", "SR 단독 회원은 사전 전환"),
            ("② 회원정보", "회원번호·비밀번호 미리 확인"),
            ("③ 노선과 날짜", "내 KTX가 어느 날 열리는지 확인"),
            ("④ 후보 열차", "1순위와 대체 시간까지 메모"),
        ],
        "checklist-card.jpg",
    )
    card(
        "예약이 끝나도 결제는 따로",
        "예약 성공 화면만 보고 앱을 닫으면 승차권이 취소될 수 있습니다",
        [
            ("결제 시작", "9월 12일 0시"),
            ("일반 예매", "9월 15일까지 결제"),
            ("교통약자", "9월 18일까지 결제"),
            ("기한 경과", "자동 취소 후 예약대기자에게 배정"),
        ],
        "payment-card.jpg",
    )


if __name__ == "__main__":
    main()
