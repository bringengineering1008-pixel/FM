from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import winreg
import wave
from dataclasses import dataclass
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pepsi_jet_v2"
SOURCE = ROOT / "output" / "pepsi_jet_pilot" / "assets"
FFMPEG = Path(r"C:\Users\user\AppData\Local\CivilStudioBeta\tools\ffmpeg\ffmpeg.exe")
VOICE_ID = "tc_68257f68bc6e3c161ab5078d"
FONT = Path(r"C:\Windows\Fonts\malgunbd.ttf")
W, H = 1080, 1920


SCRIPT_LINES = [
    "1996년, 펩시 광고를 보고 진짜 전투기 한 대를 주문한 스물한 살 대학생이 있었습니다.",
    "그의 이름은 존 레너드. 당시 펩시는 음료에 붙은 포인트를 모으면 티셔츠와 가죽 재킷 같은 상품을 주는 행사를 열었죠.",
    "그런데 광고 마지막, 학생 한 명이 해리어 전투기를 타고 학교에 착륙합니다. 화면에는 분명히 이렇게 적혀 있었습니다. 해리어 전투기, 700만 펩시 포인트.",
    "펩시 입장에서는 누가 봐도 농담이었습니다. 그런데 존은 웃지 않고 계산기를 켰습니다.",
    "상품 카탈로그에는 부족한 포인트를 개당 10센트에 살 수 있다고 적혀 있었거든요. 단, 실제 포인트 15개만 함께 보내면 됐습니다.",
    "700만 포인트를 돈으로 바꾸면 약 70만 달러. 당시 해리어 전투기는 수천만 달러짜리 군용기였습니다. 전투기를 거의 98퍼센트 할인받는 셈이었죠.",
    "이 정도면 할인 행사가 아니라 국가 예산 절감 프로젝트 아닙니까. 존은 지인들에게 계획을 설명했고 약 70만 달러를 모았습니다.",
    "그리고 1996년 3월 27일, 주문서에 직접 한 줄을 적었습니다. 해리어 전투기 한 대.",
    "봉투 안에는 원본 15포인트와 700,008.50달러 수표까지 들어 있었습니다. 농담을 숫자와 수표로 현실에 끌어낸 겁니다.",
    "펩시는 당연히 주문을 거절했습니다. 전투기는 광고를 재미있게 만들기 위한 장면일 뿐이라며 무료 음료 쿠폰까지 돌려보냈죠.",
    "그러자 존은 말했습니다. 광고에는 농담이라고 안 적혀 있었는데요. 그리고 펩시를 상대로 소송을 시작합니다.",
    "법정의 질문은 단순했습니다. 광고에 상품과 정확한 가격이 적혀 있다면, 회사는 정말 그 물건을 줘야 할까요.",
    "1999년 법원은 펩시의 손을 들어줬습니다. 첫째, 일반적인 광고는 바로 계약이 되는 청약이 아니었습니다.",
    "둘째, 합리적인 사람이라면 음료 회사가 군용 전투기를 판매한다고 믿지 않을 것이라고 봤습니다. 셋째, 전투기 계약에 필요한 서면 요건도 갖추지 못했습니다.",
    "결국 존은 전투기를 받지 못했습니다. 하지만 이 사건은 지금도 미국 계약법 수업에 등장하는 전설적인 판례가 됐죠.",
    "여러분이라면 어떻게 판결하시겠습니까. 가격까지 적었으니 전투기를 줘야 한다, 아니면 누가 봐도 농담이다. 판결은 댓글 법정에 맡기겠습니다.",
]


@dataclass(frozen=True)
class State:
    source: str
    duration: float
    label: str
    focus_x: float = 0.5
    focus_y: float = 0.5
    zoom: float = 1.0
    accent: str = "white"


def build_states() -> list[State]:
    raw = [
        ("scenes/01_opening.png", "전투기를 주문한 대학생", .48, .48, 1.00, "red"),
        ("scenes/01_opening.png", "1996년 미국", .50, .25, 1.28, "white"),
        ("scenes/01_opening.png", "존 레너드 · 21세", .35, .58, 1.36, "yellow"),
        ("scenes/02_tv_ad.png", "펩시 포인트 행사", .50, .42, 1.00, "yellow"),
        ("scenes/02_tv_ad.png", "티셔츠", .28, .30, 1.38, "white"),
        ("scenes/02_tv_ad.png", "가죽 재킷", .68, .32, 1.42, "white"),
        ("scenes/02_tv_ad.png", "광고의 마지막 상품", .50, .48, 1.12, "red"),
        ("archive/harrier_1994_public_domain.jpg", "해리어 전투기 등장", .50, .48, 1.05, "yellow"),
        ("archive/harrier_1994_public_domain.jpg", "학교에 수직 착륙", .58, .47, 1.32, "white"),
        ("scenes/02_tv_ad.png", "700만 포인트", .66, .48, 1.38, "yellow"),
        ("scenes/05_office_shock.png", "펩시: 그냥 농담인데?", .52, .45, 1.02, "white"),
        ("scenes/01_opening.png", "존은 웃지 않았습니다", .34, .62, 1.34, "red"),
        ("scenes/03_calculator.png", "계산기 ON", .38, .48, 1.18, "yellow"),
        ("scenes/03_calculator.png", "포인트 구매 가능", .52, .37, 1.36, "white"),
        ("scenes/03_calculator.png", "1포인트 = 10센트", .52, .50, 1.42, "yellow"),
        ("scenes/03_calculator.png", "조건: 원본 15포인트", .46, .67, 1.30, "red"),
        ("scenes/03_calculator.png", "7,000,000 × $0.10", .52, .46, 1.22, "white"),
        ("scenes/03_calculator.png", "약 70만 달러", .52, .52, 1.46, "yellow"),
        ("archive/harrier_1994_public_domain.jpg", "실제 가치는 수천만 달러", .50, .46, 1.08, "red"),
        ("scenes/03_calculator.png", "거의 98% 할인", .50, .48, 1.38, "yellow"),
        ("scenes/01_opening.png", "이건 못 참지", .34, .61, 1.42, "red"),
        ("scenes/04_investors.png", "투자자 모집", .52, .43, 1.03, "yellow"),
        ("scenes/04_investors.png", "계획 설명", .46, .40, 1.34, "white"),
        ("scenes/04_investors.png", "약 70만 달러 확보", .62, .48, 1.26, "yellow"),
        ("scenes/03_calculator.png", "1996년 3월 27일", .48, .24, 1.30, "white"),
        ("scenes/03_calculator.png", "주문서 작성", .44, .56, 1.30, "yellow"),
        ("scenes/03_calculator.png", "품목: 해리어 1대", .54, .56, 1.48, "red"),
        ("scenes/03_calculator.png", "원본 15포인트", .30, .72, 1.38, "white"),
        ("scenes/03_calculator.png", "$700,008.50 수표", .64, .67, 1.38, "yellow"),
        ("scenes/05_office_shock.png", "펩시 본사 도착", .50, .45, 1.02, "white"),
        ("scenes/05_office_shock.png", "직원들 단체 정지", .52, .45, 1.28, "red"),
        ("scenes/05_office_shock.png", "주문 거절", .64, .45, 1.40, "red"),
        ("scenes/05_office_shock.png", "대신 무료 음료 쿠폰", .34, .66, 1.34, "yellow"),
        ("scenes/01_opening.png", "광고엔 농담 표시가 없는데?", .34, .60, 1.38, "white"),
        ("scenes/06_courtroom.png", "존 vs 펩시", .50, .48, 1.00, "yellow"),
        ("scenes/06_courtroom.png", "광고도 계약일까?", .55, .40, 1.25, "white"),
        ("scenes/06_courtroom.png", "상품 + 정확한 가격", .34, .56, 1.34, "yellow"),
        ("scenes/08_verdict.png", "1999년 판결", .50, .48, 1.00, "white"),
        ("scenes/08_verdict.png", "1. 광고는 청약이 아님", .27, .42, 1.38, "yellow"),
        ("scenes/08_verdict.png", "2. 합리적 사람 기준", .50, .48, 1.28, "yellow"),
        ("archive/harrier_1994_public_domain.jpg", "음료 회사가 군용기를?", .52, .46, 1.24, "red"),
        ("scenes/08_verdict.png", "3. 서면 요건 불충족", .73, .43, 1.38, "yellow"),
        ("scenes/07_defeat.png", "전투기는 못 받았습니다", .50, .48, 1.00, "red"),
        ("scenes/07_defeat.png", "수표도 돌아왔습니다", .38, .55, 1.32, "white"),
        ("scenes/06_courtroom.png", "그러나 전설적인 판례", .50, .45, 1.14, "yellow"),
        ("scenes/08_verdict.png", "여러분의 판결은?", .50, .47, 1.10, "yellow"),
        ("scenes/08_verdict.png", "전투기를 줘야 한다", .25, .48, 1.36, "white"),
        ("scenes/08_verdict.png", "누가 봐도 농담이다", .75, .48, 1.36, "white"),
        ("scenes/01_opening.png", "댓글 법정 개정", .34, .60, 1.34, "red"),
    ]
    return [State(src, 2.25, label, x, y, zoom, accent) for src, label, x, y, zoom, accent in raw]


def subtitle_chunks(text: str, limit: int = 14) -> list[str]:
    chunks: list[str] = []
    current = ""
    for word in text.replace(". ", ".| ").replace("? ", "?| ").split():
        force = word.endswith("|")
        word = word.rstrip("|")
        candidate = f"{current} {word}".strip()
        if current and len(candidate.replace(" ", "")) > limit:
            chunks.append(current)
            current = word
        else:
            current = candidate
        if force and current:
            chunks.append(current)
            current = ""
    if current:
        chunks.append(current)
    return chunks


def user_env(name: str) -> str | None:
    if os.environ.get(name):
        return os.environ[name]
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            return winreg.QueryValueEx(key, name)[0]
    except OSError:
        return None


def run(args: list[str]) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as stream:
        return stream.getnframes() / stream.getframerate()


def synthesize() -> tuple[Path, float]:
    audio_dir = OUT / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    raw = audio_dir / "narration_raw.wav"
    compact = audio_dir / "narration_compact.wav"
    meta = audio_dir / "narration.json"
    if not raw.exists():
        key = user_env("TYPECAST_API_KEY")
        if not key:
            raise RuntimeError("TYPECAST_API_KEY is missing")
        response = requests.post(
            "https://api.typecast.ai/v1/text-to-speech/with-timestamps?granularity=word",
            headers={"X-API-KEY": key, "Content-Type": "application/json"},
            json={
                "voice_id": VOICE_ID,
                "text": " ".join(SCRIPT_LINES),
                "model": "ssfm-v30",
                "language": "kor",
                "prompt": {"emotion_type": "preset", "emotion_preset": "normal", "emotion_intensity": 0.85},
                "output": {"volume": 100, "audio_pitch": 0, "audio_tempo": 1.02, "audio_format": "wav"},
                "seed": 42,
            },
            timeout=240,
        )
        response.raise_for_status()
        payload = response.json()
        raw.write_bytes(base64.b64decode(payload["audio"]))
        meta.write_text(json.dumps({k: v for k, v in payload.items() if k != "audio"}, ensure_ascii=False, indent=2), encoding="utf-8")
    run([
        str(FFMPEG), "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw),
        "-af", "silenceremove=start_periods=1:start_duration=0:start_threshold=-42dB:stop_periods=-1:stop_duration=0.13:stop_threshold=-42dB:stop_silence=0.05",
        "-ar", "48000", "-ac", "2", str(compact),
    ])
    return compact, wav_duration(compact)


def _fit_source(path: Path, state: State) -> Image.Image:
    image = Image.open(path).convert("RGB")
    target_w, target_h = W, 1180
    scale = max(target_w / image.width, target_h / image.height) * state.zoom
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left = int((resized.width - target_w) * state.focus_x)
    top = int((resized.height - target_h) * state.focus_y)
    left = max(0, min(left, resized.width - target_w))
    top = max(0, min(top, resized.height - target_h))
    return resized.crop((left, top, left + target_w, top + target_h))


def render_states(states: list[State]) -> list[Path]:
    frames_dir = OUT / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    title_font = ImageFont.truetype(str(FONT), 88)
    kicker_font = ImageFont.truetype(str(FONT), 39)
    label_font = ImageFont.truetype(str(FONT), 66)
    colors = {"white": "white", "yellow": "#FFF200", "red": "#FF4B3E"}
    outputs = []
    for index, state in enumerate(states, 1):
        canvas = Image.new("RGB", (W, H), "black")
        visual = _fit_source(SOURCE / state.source, state)
        visual = ImageEnhance.Contrast(visual).enhance(1.04)
        canvas.paste(visual, (0, 280))
        draw = ImageDraw.Draw(canvas)
        draw.text((62, 45), "광고 보고 전투기 주문한", font=kicker_font, fill="#FF4B3E")
        draw.text((62, 92), "미친 대학생의 결말", font=title_font, fill="white", stroke_width=2, stroke_fill="black")
        box = draw.textbbox((0, 0), state.label, font=label_font, stroke_width=4)
        text_w = box[2] - box[0]
        x = max(45, (W - text_w) // 2)
        y = 1255
        draw.rounded_rectangle((x - 25, y - 16, x + text_w + 25, y + 82), 14, fill=(0, 0, 0))
        draw.text((x, y), state.label, font=label_font, fill=colors[state.accent], stroke_width=2, stroke_fill="black")
        target = frames_dir / f"state_{index:02d}.jpg"
        canvas.save(target, quality=94, subsampling=0)
        outputs.append(target)
    return outputs


def ass_time(value: float) -> str:
    cs = round(max(0, value) * 100)
    hour, cs = divmod(cs, 360000)
    minute, cs = divmod(cs, 6000)
    second, cs = divmod(cs, 100)
    return f"{hour}:{minute:02d}:{second:02d}.{cs:02d}"


def build_subtitles(duration: float) -> Path:
    chunks = subtitle_chunks(" ".join(SCRIPT_LINES))
    weights = [max(1, len(chunk.replace(" ", ""))) for chunk in chunks]
    total = sum(weights)
    cursor = 0.08
    events = []
    for chunk, weight in zip(chunks, weights):
        length = duration * weight / total
        events.append((cursor, min(duration, cursor + length), chunk))
        cursor += length
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Main,Malgun Gothic,66,&H00FFFFFF,&H00FFFFFF,&H00101010,&H00000000,-1,0,0,0,100,100,0,0,1,6,1,2,70,70,405,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    body = "".join(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Main,,0,0,0,,{text}\n" for a, b, text in events)
    target = OUT / "captions.ass"
    target.write_text(header + body, encoding="utf-8-sig")
    return target


def render_video(frames: list[Path], duration: float, audio: Path, subtitles: Path) -> Path:
    states = build_states()
    scale = duration / sum(state.duration for state in states)
    concat = OUT / "frames.txt"
    lines = []
    for frame, state in zip(frames, states):
        lines.extend([f"file '{frame.resolve().as_posix()}'", f"duration {state.duration * scale:.5f}"])
    lines.append(f"file '{frames[-1].resolve().as_posix()}'")
    concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
    silent = OUT / "visual.mp4"
    run([str(FFMPEG), "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat), "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-t", f"{duration:.4f}", str(silent)])
    final = OUT / "pepsi_jet_v2_final.mp4"
    ass = subtitles.resolve().as_posix().replace(":", r"\:")
    run([str(FFMPEG), "-y", "-hide_banner", "-loglevel", "error", "-i", str(silent), "-i", str(audio), "-vf", f"ass='{ass}'", "-af", "loudnorm=I=-14:TP=-1.5:LRA=7", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(final)])
    return final


def write_manifest() -> Path:
    manifest = {
        "title": "펩시 광고 보고 전투기를 주문한 대학생의 결말 #shorts",
        "description": "펩시 포인트 광고 속 700만 포인트짜리 해리어 전투기. 존 레너드는 약관을 계산해 실제 주문서와 수표까지 보냈습니다. 법원은 어떻게 판단했을까요?\n\n사실 근거: Leonard v. Pepsico, Inc., 88 F. Supp. 2d 116 (S.D.N.Y. 1999)\nAI 이미지·음성을 활용해 제작했습니다.\n\n#펩시 #전투기 #실화 #판례 #브링이슈",
        "tags": ["펩시", "전투기", "펩시포인트", "실화", "미국판례", "계약법", "브링이슈", "shorts"],
        "category_id": "27",
        "privacy_status": "public",
        "contains_synthetic_media": True,
    }
    target = OUT / "youtube_manifest.json"
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    states = build_states()
    frames = render_states(states)
    audio, duration = synthesize()
    subtitles = build_subtitles(duration)
    final = render_video(frames, duration, audio, subtitles)
    manifest = write_manifest()
    print(json.dumps({"video": str(final), "manifest": str(manifest), "duration": duration, "states": len(states)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
