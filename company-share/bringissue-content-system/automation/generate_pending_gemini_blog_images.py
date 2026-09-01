from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MODEL = "gemini-3.1-flash-image"
API_URL = f"https://generativelanguage.googleapis.com/v1/models/{MODEL}:generateContent"

JOBS = [
    (
        ROOT / "blog/assets/2026-08-23-chuseok-gift-guide/flow-gift-planning.jpg",
        "한국의 40대 부부가 단정한 거실 테이블에서 추석 선물을 가족용, 직장용, 지인용 세 그룹으로 나누어 계획하는 현실적인 한국 라이프스타일 매거진 사진. 포장된 선물 상자, 빈 메모 카드, 노트북이 자연스럽게 놓여 있다. 실제 판매상품이나 브랜드가 식별되지 않으며 로고, 읽을 수 있는 글자, 숫자, 워터마크가 없다. 따뜻한 가을 햇빛, 깔끔하고 신뢰감 있는 분위기, 16:9 가로 구도, 블로그용 고해상도, 정확한 손 형태.",
    ),
    (
        ROOT / "blog/assets/2026-08-23-youtube-view-count/gemini-viewer-confusion.png",
        "한국의 40대 성인이 거실 소파에서 스마트폰으로 온라인 영상을 보다가 조회 지표가 평소보다 빠르게 오르는 듯한 상황에 고개를 갸웃하는 현실적인 에디토리얼 사진. 스마트폰 화면에는 실제 유튜브 UI, 로고, 읽을 수 있는 글자나 숫자를 넣지 말고 추상적인 영상 카드와 상승 점만 표현. 따뜻한 자연광, 단정한 집, 16:9 가로 구도, 블로그 본문용 고해상도, 손가락과 손 형태 정확히, 워터마크와 브랜드 로고 없음.",
    ),
    (
        ROOT / "blog/assets/2026-08-23-youtube-view-count/gemini-creator-analysis.png",
        "한국의 30~40대 콘텐츠 운영자가 노트북과 메모장을 보며 두 종류의 성과를 비교하는 현실적인 에디토리얼 사진. 화면에는 실제 유튜브 UI나 로고, 읽을 수 있는 글자와 숫자 없이 왼쪽은 재생 시작을 상징하는 점들, 오른쪽은 오래 머문 시청을 상징하는 완만한 막대만 표현. 깨끗한 작업실, 차분한 파란색과 붉은색 포인트, 16:9 가로 구도, 고해상도, 인물 한 명, 손 형태 정확히, 워터마크 없음.",
    ),
]


def generate(target: Path, prompt: str) -> None:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "16:9", "imageSize": "2K"},
        },
    }
    request = Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=300) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini HTTP {exc.code}: {detail}") from exc
    for candidate in result.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and str(inline.get("mimeType") or inline.get("mime_type", "")).startswith("image/"):
                target.parent.mkdir(parents=True, exist_ok=True)
                raw = base64.b64decode(inline["data"])
                target.write_bytes(raw)
                if target.suffix.lower() in {".jpg", ".jpeg"}:
                    with Image.open(target) as image:
                        converted = image.convert("RGB")
                        converted.save(target, "JPEG", quality=94)
                return
    raise RuntimeError(f"No image returned for {target.name}")


for output, text in JOBS:
    print(f"Generating {output.name}", flush=True)
    generate(output, text)
    with Image.open(output) as image:
        print(f"PASS {output.name}: {image.width}x{image.height}", flush=True)
