from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts/create_bringissue_manual.py"


def test_manual_builder_contains_gemini_editorial_rules():
    text = BUILDER.read_text(encoding="utf-8")
    required = [
        "제미나이 매거진 일러스트",
        "AI로 제작한 이해용 이미지입니다.",
        "문장 전용 정보 카드",
        "실존 인물의 얼굴을 그대로 복제하지",
        "1200×675",
    ]
    for phrase in required:
        assert phrase in text
