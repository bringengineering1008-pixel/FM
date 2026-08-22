from __future__ import annotations

import base64
import json
import re
import wave
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

import pepsi_jet_v2 as v2


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pepsi_jet_v3"
NEW = OUT / "images"
REACTIONS = ROOT / "production" / "assets" / "stickman_reactions" / "individual"
LEGACY = ROOT / "output" / "pepsi_jet_pilot" / "assets"
W, H = 1080, 1920
FONT = v2.FONT
SANGHYUN_VOICE_ID = "tc_69fc0cff784968297fb45daa"
SANGHYUN_TEMPO = 1.00


def validate_narration_config(voice_id: str, tempo: float) -> None:
    if voice_id != SANGHYUN_VOICE_ID:
        raise ValueError(f"Narration voice must be Sanghyun: {voice_id}")
    if tempo != SANGHYUN_TEMPO:
        raise ValueError(f"Narration tempo must be 1.00: {tempo}")


def prepare_continuous_narration(raw: Path) -> Path:
    """Return the untouched Typecast waveform; timestamps drive only visuals/captions."""
    return raw


def build_typecast_payload(text: str) -> dict:
    validate_narration_config(SANGHYUN_VOICE_ID, SANGHYUN_TEMPO)
    return {
        "voice_id": SANGHYUN_VOICE_ID,
        "text": text,
        "model": "ssfm-v30",
        "language": "kor",
        "prompt": {
            "emotion_type": "preset",
            "emotion_preset": "normal",
            "emotion_intensity": 0.85,
        },
        "output": {
            "volume": 100,
            "audio_pitch": 0,
            "audio_tempo": SANGHYUN_TEMPO,
            "audio_format": "wav",
        },
        "seed": 42,
    }


def synthesize_sanghyun() -> tuple[Path, dict]:
    audio_dir = OUT / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    raw = audio_dir / "narration_sanghyun.wav"
    meta = audio_dir / "narration_sanghyun.json"
    if raw.exists() and meta.exists():
        metadata = json.loads(meta.read_text(encoding="utf-8"))
        if metadata.get("_voice_id") == SANGHYUN_VOICE_ID and metadata.get("_tempo") == SANGHYUN_TEMPO:
            return raw, metadata

    key = v2.user_env("TYPECAST_API_KEY")
    if not key:
        raise RuntimeError("TYPECAST_API_KEY is missing")
    response = v2.requests.post(
        "https://api.typecast.ai/v1/text-to-speech/with-timestamps?granularity=word",
        headers={"X-API-KEY": key, "Content-Type": "application/json"},
        json=build_typecast_payload(" ".join(v2.SCRIPT_LINES)),
        timeout=240,
    )
    response.raise_for_status()
    payload = response.json()
    raw.write_bytes(base64.b64decode(payload["audio"]))
    metadata = {key: value for key, value in payload.items() if key != "audio"}
    metadata["_voice_id"] = SANGHYUN_VOICE_ID
    metadata["_tempo"] = SANGHYUN_TEMPO
    meta.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return raw, metadata


@dataclass(frozen=True)
class Shot:
    source: Path
    label: str
    accent: str = "white"
    zoom: float = 1.0
    focus_x: float = 0.5
    focus_y: float = 0.5


@dataclass(frozen=True)
class CaptionSegment:
    text: str
    source_start: float
    source_end: float
    output_start: float
    output_end: float
    word_ranges: tuple[tuple[float, float], ...]


def build_continuous_timeline(words: list[dict], max_chars: int = 14) -> list[CaptionSegment]:
    groups: list[list[dict]] = []
    current: list[dict] = []
    for word in words:
        candidate = current + [word]
        length = len("".join(str(item["text"]).replace(" ", "") for item in candidate))
        if current and length > max_chars:
            groups.append(current)
            current = [word]
        else:
            current = candidate
    if current:
        groups.append(current)

    return [
        CaptionSegment(
            text=" ".join(str(item["text"]) for item in group),
            source_start=float(group[0]["start"]),
            source_end=float(group[-1]["end"]),
            output_start=float(group[0]["start"]),
            output_end=float(group[-1]["end"]),
            word_ranges=tuple((float(item["start"]), float(item["end"])) for item in group),
        )
        for group in groups
    ]


def build_aligned_timeline(
    words: list[dict], max_chars: int = 14, gap: float = 0.06, intra_word_gap: float = 0.035
) -> list[CaptionSegment]:
    groups: list[list[dict]] = []
    current: list[dict] = []
    for word in words:
        candidate = current + [word]
        length = len("".join(str(item["text"]).replace(" ", "") for item in candidate))
        if current and length > max_chars:
            groups.append(current)
            current = [word]
        else:
            current = candidate
    if current:
        groups.append(current)

    timeline: list[CaptionSegment] = []
    cursor = 0.0
    for group in groups:
        source_start = float(group[0]["start"])
        source_end = float(group[-1]["end"])
        ranges = tuple((float(item["start"]), float(item["end"])) for item in group)
        duration = sum(end - start for start, end in ranges) + intra_word_gap * (len(ranges) - 1)
        timeline.append(CaptionSegment(
            text=" ".join(str(item["text"]) for item in group),
            source_start=source_start,
            source_end=source_end,
            output_start=cursor,
            output_end=cursor + duration,
            word_ranges=ranges,
        ))
        cursor += duration + gap
    return timeline


def ass_time(value: float) -> str:
    cs = round(max(0.0, value) * 100)
    hour, cs = divmod(cs, 360000)
    minute, cs = divmod(cs, 6000)
    second, cs = divmod(cs, 100)
    return f"{hour}:{minute:02d}:{second:02d}.{cs:02d}"


def build_reference_ass(timeline: list[CaptionSegment]) -> str:
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Main,Malgun Gothic,72,&H0000FFFF,&H0000FFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,16,0,2,70,70,515,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    events = "".join(
        f"Dialogue: 0,{ass_time(item.output_start)},{ass_time(item.output_end)},Main,,0,0,0,,{item.text}\n"
        for item in timeline
    )
    return header + events


def _token(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z가-힣]", "", text)


def resolve_continuous_visual_starts(words: list[dict], anchors: list[str]) -> list[float]:
    tokens = [_token(str(word["text"])) for word in words]
    starts: list[float] = []
    search_from = 0
    for anchor in anchors:
        wanted = [_token(part) for part in anchor.split()]
        found = -1
        for index in range(search_from, len(tokens) - len(wanted) + 1):
            if tokens[index:index + len(wanted)] == wanted:
                found = index
                break
        if found < 0:
            raise ValueError(f"Narration anchor not found after word {search_from}: {anchor}")
        starts.append(float(words[found]["start"]))
        search_from = found + 1
    return starts


def resolve_visual_starts(
    words: list[dict], timeline: list[CaptionSegment], anchors: list[str], intra_word_gap: float = 0.035
) -> list[float]:
    output_starts: list[float] = []
    for segment in timeline:
        cursor = segment.output_start
        for start, end in segment.word_ranges:
            output_starts.append(cursor)
            cursor += end - start + intra_word_gap
    tokens = [_token(str(word["text"])) for word in words]
    starts: list[float] = []
    search_from = 0
    for anchor in anchors:
        wanted = [_token(part) for part in anchor.split()]
        found = -1
        for index in range(search_from, len(tokens) - len(wanted) + 1):
            if tokens[index:index + len(wanted)] == wanted:
                found = index
                break
        if found < 0:
            raise ValueError(f"Narration anchor not found after word {search_from}: {anchor}")
        starts.append(output_starts[found])
        search_from = found + 1
    return starts


VISUAL_ANCHORS = [
    "1996년",
    "스물한 살 대학생이",
    "당시 펩시는",
    "티셔츠와 가죽 재킷",
    "그런데 광고 마지막",
    "해리어 전투기를 타고",
    "700만 펩시 포인트",
    "펩시 입장에서는",
    "누가 봐도 농담이었습니다",
    "그런데 존은",
    "계산기를 켰습니다",
    "상품 카탈로그에는",
    "부족한 포인트를",
    "개당 10센트에",
    "실제 포인트 15개만",
    "700만 포인트를",
    "돈으로 바꾸면 약",
    "당시 해리어 전투기는",
    "수천만 달러짜리 군용기였습니다",
    "98퍼센트 할인받는",
    "셈이었죠",
    "이 정도면",
    "국가 예산 절감",
    "존은 지인들에게",
    "계획을 설명했고",
    "약 70만 달러를 모았습니다",
    "그리고 1996년",
    "3월 27일",
    "주문서에 직접",
    "해리어 전투기 한 대",
    "원본 15포인트와",
    "70000850달러 수표까지",
    "수표까지",
    "농담을 숫자와 수표로",
    "펩시는 당연히",
    "주문을 거절했습니다",
    "전투기는 광고를",
    "재미있게 만들기 위한",
    "무료 음료 쿠폰까지",
    "광고에는 농담이라고",
    "펩시를 상대로 소송을",
    "법정의 질문은",
    "광고에 상품과",
    "회사는 정말",
    "1999년 법원은",
    "첫째",
    "둘째",
    "합리적인 사람이라면",
    "셋째",
    "결국 존은",
    "받지 못했습니다",
    "하지만 이 사건은",
    "여러분이라면",
    "가격까지 적었으니",
    "아니면",
]


def build_aligned_audio(
    raw: Path, timeline: list[CaptionSegment], target: Path, gap: float = 0.06, intra_word_gap: float = 0.035
) -> float:
    with wave.open(str(raw), "rb") as source:
        params = source.getparams()
        frame_rate = source.getframerate()
        sample_width = source.getsampwidth()
        channels = source.getnchannels()
        source_frames = source.readframes(source.getnframes())
    frame_size = sample_width * channels
    caption_silence = b"\x00" * (round(gap * frame_rate) * frame_size)
    word_silence = b"\x00" * (round(intra_word_gap * frame_rate) * frame_size)
    pieces: list[bytes] = []
    for index, item in enumerate(timeline):
        for word_index, (start, end) in enumerate(item.word_ranges):
            first = round(start * frame_rate) * frame_size
            last = round(end * frame_rate) * frame_size
            pieces.append(source_frames[first:last])
            if word_index < len(item.word_ranges) - 1:
                pieces.append(word_silence)
        if index < len(timeline) - 1:
            pieces.append(caption_silence)
    with wave.open(str(target), "wb") as output:
        output.setparams(params)
        output.writeframes(b"".join(pieces))
    return sum(item.output_end - item.output_start for item in timeline) + gap * (len(timeline) - 1)


def fit_font_size(
    draw: ImageDraw.ImageDraw, text: str, font_path: Path, start_size: int, max_width: int
) -> ImageFont.FreeTypeFont:
    size = start_size
    while size > 24:
        font = ImageFont.truetype(str(font_path), size)
        box = draw.textbbox((0, 0), text, font=font)
        if box[2] - box[0] <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(str(font_path), size)


def shots() -> list[Shot]:
    n = lambda i: NEW / f"scene_{i:02d}.png"
    r = lambda name: REACTIONS / name
    s = lambda name: LEGACY / "scenes" / name
    a = lambda name: LEGACY / "archive" / name
    return [
        Shot(n(1), "광고 보고 전투기 주문", "red"),
        Shot(r("reaction_03_shocked.png"), "스물한 살 대학생"),
        Shot(n(2), "1996년 포인트 행사", "yellow"),
        Shot(r("reaction_01_default.png"), "티셔츠와 재킷을 주던 행사"),
        Shot(n(3), "광고 끝에 전투기 등장", "yellow"),
        Shot(a("harrier_1994_public_domain.jpg"), "해리어 전투기"),
        Shot(n(4), "무려 700만 포인트", "yellow"),
        Shot(r("reaction_02_baffled.png"), "펩시는 농담이었습니다"),
        Shot(n(6), "광고팀도 웃고 있었죠"),
        Shot(r("reaction_07_suspicious.png"), "그런데 존은 안 웃었습니다", "red"),
        Shot(n(7), "계산기를 켰습니다", "yellow"),
        Shot(r("reaction_09_realization.png"), "부족한 포인트를 살 수 있다"),
        Shot(n(8), "카탈로그의 작은 조건"),
        Shot(n(9), "1포인트에 10센트", "yellow"),
        Shot(n(10), "원본은 단 15개"),
        Shot(n(11), "필요한 포인트는 700만"),
        Shot(r("reaction_18_calculator.png"), "계산 결과 약 70만 달러", "yellow"),
        Shot(n(12), "현금으로 바꾸면 70만 달러"),
        Shot(n(13), "전투기 실제 값은 수천만 달러", "red"),
        Shot(r("reaction_03_shocked.png"), "거의 98% 할인"),
        Shot(n(14), "이건 못 참지", "red"),
        Shot(r("reaction_10_scheming.png"), "존은 계획을 짭니다"),
        Shot(n(15), "자금 조달 작전"),
        Shot(n(16), "친구들에게 투자 제안"),
        Shot(r("reaction_07_suspicious.png"), "처음엔 다들 의심했지만"),
        Shot(n(18), "결국 투자자가 나타납니다"),
        Shot(n(19), "약 70만 달러 확보", "yellow"),
        Shot(n(20), "1996년 3월 27일"),
        Shot(n(21), "주문서 작성"),
        Shot(n(22), "품목: 전투기 한 대", "red"),
        Shot(n(23), "원본 포인트 15개"),
        Shot(n(24), "70만 달러 수표", "yellow"),
        Shot(n(25), "주문 봉투를 봉인"),
        Shot(n(26), "진짜 우편으로 발송"),
        Shot(n(27), "펩시 본사 도착"),
        Shot(n(28), "직원이 봉투를 열었습니다"),
        Shot(r("reaction_03_shocked.png"), "회사 전체가 멈췄습니다", "red"),
        Shot(s("05_office_shock.png"), "주문은 당연히 거절"),
        Shot(r("reaction_02_baffled.png"), "대신 무료 음료 쿠폰"),
        Shot(r("reaction_04_angry.png"), "광고엔 농담 표시가 없는데?", "red"),
        Shot(r("reaction_27_court_argument.png"), "존은 소송을 시작합니다"),
        Shot(s("06_courtroom.png"), "광고도 계약일까?", "yellow"),
        Shot(r("reaction_21_reading_document.png"), "상품과 가격이 적혀 있다면"),
        Shot(r("reaction_29_asking_audience.png"), "회사는 정말 줘야 할까?"),
        Shot(s("08_verdict.png"), "1999년 법원의 판단"),
        Shot(r("reaction_01_default.png"), "첫째 광고는 청약이 아님"),
        Shot(r("reaction_28_magnifier.png"), "둘째 합리적 사람 기준"),
        Shot(a("harrier_1994_public_domain.jpg"), "음료 회사가 군용기를?", "red"),
        Shot(r("reaction_21_reading_document.png"), "셋째 서면 요건 불충족"),
        Shot(s("07_defeat.png"), "결국 전투기는 못 받았습니다", "red"),
        Shot(r("reaction_06_resigned.png"), "수표도 돌아왔습니다"),
        Shot(s("06_courtroom.png"), "하지만 전설적인 판례가 됐죠", "yellow"),
        Shot(r("reaction_29_asking_audience.png"), "여러분의 판결은?", "yellow"),
        Shot(r("reaction_27_court_argument.png"), "가격을 적었으니 줘야 한다"),
        Shot(r("reaction_02_baffled.png"), "아니다, 누가 봐도 농담이다"),
    ]


def fit(path: Path, shot: Shot, target_h: int = 1070) -> Image.Image:
    image = Image.open(path).convert("RGB")
    scale = max(W / image.width, target_h / image.height) * shot.zoom
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, min(round((resized.width - W) * shot.focus_x), resized.width - W))
    top = max(0, min(round((resized.height - target_h) * shot.focus_y), resized.height - target_h))
    return resized.crop((left, top, left + W, top + target_h))


def render_frames(items: list[Shot]) -> list[Path]:
    frames_dir = OUT / "frames_v3"
    frames_dir.mkdir(parents=True, exist_ok=True)
    sizing_draw = ImageDraw.Draw(Image.new("RGB", (W, H), "black"))
    first = "광고 보고 전투기 주문한"
    second = "대학생의 결말"
    title_blue = fit_font_size(sizing_draw, first, FONT, 114, 970)
    title_white = fit_font_size(sizing_draw, second, FONT, 122, 970)
    rendered: list[Path] = []
    for index, item in enumerate(items, 1):
        visual = ImageEnhance.Contrast(fit(item.source, item)).enhance(1.03)
        canvas = Image.new("RGBA", (W, H), "black")
        canvas.paste(visual, (0, 420))
        draw = ImageDraw.Draw(canvas)
        first_box = draw.textbbox((0, 0), first, font=title_blue)
        second_box = draw.textbbox((0, 0), second, font=title_white)
        draw.text(((W - (first_box[2] - first_box[0])) // 2, 72), first, font=title_blue, fill="#55C7FF")
        draw.text(((W - (second_box[2] - second_box[0])) // 2, 205), second, font=title_white, fill="white")
        target = frames_dir / f"shot_{index:02d}.jpg"
        canvas.convert("RGB").save(target, quality=93, subsampling=0)
        rendered.append(target)
    return rendered


def render_video(
    frames: list[Path], duration: float, audio: Path, captions: Path, visual_starts: list[float]
) -> Path:
    concat = OUT / "frames_v3.txt"
    lines: list[str] = []
    boundaries = visual_starts[1:] + [duration]
    for frame, start, end in zip(frames, visual_starts, boundaries):
        lines += [f"file '{frame.resolve().as_posix()}'", f"duration {max(0.04, end - start):.6f}"]
    lines.append(f"file '{frames[-1].resolve().as_posix()}'")
    concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
    visual = OUT / "visual_v3.mp4"
    v2.run([str(v2.FFMPEG), "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat), "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-t", f"{duration:.4f}", str(visual)])
    final = OUT / "pepsi_jet_v3_final.mp4"
    ass = captions.resolve().as_posix().replace(":", r"\:")
    v2.run([str(v2.FFMPEG), "-y", "-hide_banner", "-loglevel", "error", "-i", str(visual), "-i", str(audio), "-vf", f"ass='{ass}'", "-af", "loudnorm=I=-14:TP=-1.5:LRA=7", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(final)])
    return final


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    items = shots()
    missing = [str(x.source) for x in items if not x.source.exists()]
    if missing:
        raise FileNotFoundError(json.dumps(missing, ensure_ascii=False, indent=2))
    raw_audio, metadata = synthesize_sanghyun()
    audio = prepare_continuous_narration(raw_audio)
    timeline = build_continuous_timeline(metadata["words"], max_chars=14)
    if len(VISUAL_ANCHORS) != len(items):
        raise ValueError(f"Visual anchor count {len(VISUAL_ANCHORS)} != shot count {len(items)}")
    visual_starts = resolve_continuous_visual_starts(metadata["words"], VISUAL_ANCHORS)
    duration = v2.wav_duration(audio)
    captions = OUT / "captions_aligned.ass"
    captions.write_text(build_reference_ass(timeline), encoding="utf-8-sig")
    frames = render_frames(items)
    final = render_video(frames, duration, audio, captions, visual_starts)
    print(json.dumps({"video": str(final), "duration": duration, "shots": len(items)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
