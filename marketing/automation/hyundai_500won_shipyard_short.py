from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
import sys
import wave
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


AUTOMATION_DIR = Path(__file__).resolve().parent
if str(AUTOMATION_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_DIR))

import pepsi_jet_v2 as v2
import pepsi_jet_v3 as v3


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "hyundai_500won_shipyard_evidence_v1"
SOURCE = OUT / "source"
ASSETS = OUT / "assets"
FRAMES = OUT / "frames"
AUDIO = OUT / "audio"
VIDEO = OUT / "video"
QC = OUT / "qc"
PUBLISH = OUT / "publish"
LEDGER = ROOT / "production" / "domestic_cases" / "hyundai_500won_shipyard_evidence_v1.json"
FINAL_VIDEO = VIDEO / "hyundai_500won_shipyard_final.mp4"

W, H = 1080, 1920
VISUAL_SIZE = (900, 1100)
VISUAL_POSITION = (90, 450)
CAPTION_MAX_CHARS = 14
VOICE_ID = "tc_69fc0cff784968297fb45daa"
VOICE_TEMPO = 1.00
AUDIO_TARGET_LUFS = -11
AUDIO_PREPROCESS_FILTER = "volume=12dB,alimiter=limit=0.5:attack=5:release=50:level=false"
LOUDNORM_TARGET_I = -11
LOUDNORM_TARGET_TP = -2.0
LOUDNORM_TARGET_LRA = 7

FONT_PATH = Path(r"C:\Windows\Fonts\malgunbd.ttf")
TITLE_LINES = ("500원 지폐로", "조선소를 세웠다?")
TITLE_COLORS = ("#62C8FF", "#FFFFFF")

SCRIPT_LINES = [
    "500원짜리 지폐 한 장을 보여주고 수천억 원짜리 조선소 돈을 빌려달라고 하면, 여러분은 빌려주시겠습니까?",
    "그런데 실제로 이 황당한 설득을 시작한 사람이 있었습니다.",
    "1970년대 초, 한국은 대형 유조선을 제대로 만들어 본 적도 없었습니다.",
    "정주영은 영국에서 조선소 건설 자금을 구하려 했지만, 상대가 보기에는 공장도 없고 실적도 없는 회사였습니다.",
    "말 그대로 배를 팔겠다는 사람이 보여줄 배가 없었습니다.",
    "그가 내민 첫 번째 증거는 울산 미포만의 백사장 사진과 조선소 계획도였습니다.",
    "여기에 영국 애플도어와 기술과 판매 협력을 추진한 기록도 붙었습니다.",
    "그래도 상대는 물었습니다. 한국이 정말 큰 배를 만들 수 있습니까?",
    "그때 정주영이 꺼낸 것이 당시 유통되던 500원권이었습니다.",
    "한국은행 기록을 보면 앞면에는 남대문, 뒷면에는 거북선과 판옥선이 그려져 있었습니다.",
    "그는 이 배를 가리키며, 우리는 이미 수백 년 전에 이런 배를 만든 나라라고 설득했습니다.",
    "여기까지만 들으면 지폐 한 장이 차관으로 변한 것 같죠?",
    "하지만 공식 기록을 순서대로 보면 이야기는 훨씬 복잡합니다.",
    "애플도어와의 협력, 정부의 지원, 울산 부지 자료, 그리고 사업 계획이 함께 움직였습니다.",
    "1971년 9월에는 영국 버클레이즈은행과 조선소 건설 차관 도입에 서명한 기록이 남아 있습니다.",
    "그런데 돈만 빌린다고 끝이 아니었습니다.",
    "은행 입장에서는 이 조선소가 만들 배를 누가 사 줄지도 중요했습니다.",
    "정주영은 다시 선주를 찾아다녔고, 1971년 12월 리바노스와 첫 선박 계약을 맺었습니다.",
    "주문을 받은 뒤 조선소를 지은 것이 아니라, 조선소 건설과 첫 배 건조를 동시에 밀어붙인 겁니다.",
    "그러니까 500원권은 조선소의 자본이 아니었습니다.",
    "백사장만 있던 계획에 상대가 한 번 더 귀를 기울이게 만든, 강력한 설득의 상징에 가까웠습니다.",
    "지폐 한 장 뒤에는 기술, 정부 지원, 금융, 수주가 차례로 연결돼 있었습니다.",
    "결국 전설의 핵심은 돈의 크기가 아니라, 아무것도 없는 순간에 무엇을 증거로 보여주느냐였습니다.",
    "여러분이라면 공장도 제품도 없는 회사에 배 두 척을 주문하시겠습니까?",
]
NARRATION = " ".join(SCRIPT_LINES)

NARRATION_ANCHORS = [
    "500원짜리 지폐",
    "여러분은 빌려주시겠습니까",
    "그런데 실제로",
    "1970년대 초",
    "공장도 없고",
    "그가 내민 첫 번째",
    "여기에 영국 애플도어와",
    "그래도 상대는",
    "그때 정주영이",
    "한국은행 기록을 보면",
    "뒷면에는 거북선과",
    "그는 이 배를",
    "여기까지만 들으면",
    "하지만 공식 기록을",
    "애플도어와의 협력",
    "1971년 9월에는",
    "그런데 돈만",
    "은행 입장에서는",
    "정주영은 다시 선주를",
    "1971년 12월",
    "주문을 받은 뒤",
    "조선소 건설과 첫 배",
    "그러니까 500원권은",
    "백사장만 있던",
    "지폐 한 장 뒤에는 기술",
    "정부 지원",
    "수주가 차례로",
    "결국 전설의",
    "아무것도 없는 순간에",
    "여러분이라면",
]


@dataclass(frozen=True)
class StoryboardItem:
    caption: str
    anchor_keyword: str
    source: Path
    visual_role: str
    attribution: str
    claim_id: str | None = None
    crop_policy: str = "cover"
    visual_start_offset: float = -0.08
    focus_x: float = 0.5
    focus_y: float = 0.5


@dataclass(frozen=True)
class CaptionSegment:
    text: str
    output_start: float
    output_end: float


def _font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size)


def _save_reaction(path: Path, mode: str) -> None:
    image = Image.new("RGB", VISUAL_SIZE, "#DCEBF2")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 900, 1100), fill="#DCEBF2")
    draw.ellipse((290, 155, 610, 475), fill="#FFFFFF", outline="#111820", width=12)
    draw.line((450, 475, 450, 805), fill="#111820", width=15)
    draw.line((450, 575, 270, 700), fill="#111820", width=15)
    draw.line((450, 575, 650, 670), fill="#111820", width=15)
    draw.line((450, 805, 320, 1030), fill="#111820", width=15)
    draw.line((450, 805, 580, 1030), fill="#111820", width=15)
    draw.ellipse((370, 270, 405, 305), fill="#111820")
    draw.ellipse((495, 270, 530, 305), fill="#111820")
    if mode == "construction":
        draw.arc((390, 320, 510, 405), 10, 170, fill="#111820", width=10)
        draw.polygon([(630, 650), (805, 650), (765, 840), (590, 840)], fill="#F4B942", outline="#111820")
        draw.line((610, 675, 785, 815), fill="#111820", width=12)
        draw.text((88, 65), "공장도 실적도 0", font=_font(64), fill="#0B426A")
    else:
        draw.arc((390, 345, 510, 410), 190, 350, fill="#111820", width=10)
        draw.text((75, 65), "여러분의 선택은?", font=_font(61), fill="#0B426A")
        draw.rounded_rectangle((590, 625, 835, 875), radius=28, fill="#111820")
        draw.text((655, 670), "주문", font=_font(62), fill="#62C8FF")
        draw.text((670, 755), "한다?", font=_font(50), fill="#FFFFFF")
    image.save(path, quality=95)


def _save_icon_card(path: Path, icon: Path, label: str, background: str) -> None:
    image = Image.new("RGB", VISUAL_SIZE, background)
    with Image.open(icon) as source:
        item = source.convert("RGBA")
        item.thumbnail((610, 610), Image.Resampling.LANCZOS)
        image.paste(item, ((900 - item.width) // 2, 225), item)
    draw = ImageDraw.Draw(image)
    box = draw.textbbox((0, 0), label, font=_font(67))
    draw.text(((900 - (box[2] - box[0])) // 2, 905), label, font=_font(67), fill="#111820")
    image.save(path, quality=95)


def ensure_original_assets() -> None:
    SOURCE.mkdir(parents=True, exist_ok=True)
    _save_reaction(SOURCE / "original_construction_stickman.png", "construction")
    _save_reaction(SOURCE / "original_choice_stickman.png", "choice")
    cards = (
        ("shocked_card.png", "shocked_face.png", "이게 된다고?", "#F8EED2"),
        ("thinking_card.png", "thinking_face.png", "정말 지폐 한 장?", "#E8F1F5"),
        ("banknote_card.png", "banknote.png", "500원 지폐", "#E7F0DF"),
        ("ship_card.png", "ship.png", "첫 선박 수주", "#DCEBF2"),
    )
    for filename, icon, label, background in cards:
        _save_icon_card(SOURCE / filename, ASSETS / icon, label, background)


def storyboard() -> list[StoryboardItem]:
    ensure_original_assets()
    p16 = SOURCE / "hdhyundai_p16_intro_myth.png"
    p21 = SOURCE / "hdhyundai_p21_banknote_appledore.png"
    p22 = SOURCE / "hdhyundai_p22_loan_livanos.png"
    p31 = SOURCE / "hdhyundai_p31_shipyard_ship_parallel.png"
    p323 = SOURCE / "hdhyundai_p323_chronology.png"
    bok = SOURCE / "bok_500won_record.png"
    construction = SOURCE / "original_construction_stickman.png"
    choice = SOURCE / "original_choice_stickman.png"
    shocked = SOURCE / "shocked_card.png"
    thinking = SOURCE / "thinking_card.png"
    banknote = SOURCE / "banknote_card.png"
    ship = SOURCE / "ship_card.png"
    return [
        StoryboardItem("500원으로 조선소?", "500원", choice, "original_reaction", "BringIssue 자체 제작"),
        StoryboardItem("돈을 빌려주시겠습니까?", "빌려주다", shocked, "licensed_icon", "OpenMoji – CC BY-SA 4.0"),
        StoryboardItem("실제로 시작된 설득", "실제", p16, "official_record", "HD현대 50년사 028-029", "banknote_myth", "contain"),
        StoryboardItem("대형 유조선 경험 0", "경험", p16, "official_record", "HD현대 50년사 028-029", "banknote_myth", "contain"),
        StoryboardItem("공장도 실적도 없었다", "공장", construction, "original_reaction", "BringIssue 자체 제작"),
        StoryboardItem("첫 증거는 백사장 사진", "백사장", p16, "official_record", "HD현대 50년사 028-029", "ulsan_beach_evidence", "contain"),
        StoryboardItem("애플도어 기술 협력", "애플도어", p21, "official_record", "HD현대 50년사 038-039", "appledore_cooperation", "contain"),
        StoryboardItem("정말 큰 배를 만든다?", "큰 배", thinking, "licensed_icon", "OpenMoji – CC BY-SA 4.0"),
        StoryboardItem("그때 꺼낸 500원권", "500원권", banknote, "licensed_icon", "Twemoji – CC BY 4.0"),
        StoryboardItem("1966년 8월 발행", "1966년", bok, "official_record", "한국은행 Currency Validity", "banknote_design", "contain"),
        StoryboardItem("뒷면엔 거북선과 판옥선", "거북선", bok, "official_record", "한국은행 Currency Validity", "banknote_design", "contain"),
        StoryboardItem("수백 년 전 배를 만든 나라", "배", p21, "official_record", "HD현대 50년사 038-039", "banknote_design", "contain"),
        StoryboardItem("지폐가 차관으로 변했다?", "차관", thinking, "licensed_icon", "OpenMoji – CC BY-SA 4.0"),
        StoryboardItem("공식 기록은 더 복잡하다", "공식 기록", p21, "official_record", "HD현대 50년사 038-039", "banknote_myth", "contain"),
        StoryboardItem("기술·정부·부지·계획", "기술", p323, "official_record", "HD현대 50년사 642-643", "banknote_myth", "contain"),
        StoryboardItem("1971년 9월 차관 서명", "1971년 9월", p21, "official_record", "HD현대 50년사 038-039", "barclays_loan", "contain"),
        StoryboardItem("하지만 돈이 전부가 아니다", "돈", shocked, "licensed_icon", "OpenMoji – CC BY-SA 4.0"),
        StoryboardItem("배를 살 사람도 필요했다", "구매자", p22, "official_record", "HD현대 50년사 040-041", "livanos_order", "contain"),
        StoryboardItem("리바노스와 첫 계약", "리바노스", p22, "official_record", "HD현대 50년사 040-041", "livanos_order", "contain"),
        StoryboardItem("드디어 첫 선박 수주", "수주", ship, "licensed_icon", "Twemoji – CC BY 4.0"),
        StoryboardItem("조선소와 배를 동시에", "동시에", p31, "official_record", "HD현대 50년사 058-059", "simultaneous_build", "contain"),
        StoryboardItem("먼저 완성한 게 아니었다", "동시 건설", p31, "official_record", "HD현대 50년사 058-059", "simultaneous_build", "contain"),
        StoryboardItem("500원은 자본이 아니었다", "자본", banknote, "licensed_icon", "Twemoji – CC BY 4.0"),
        StoryboardItem("판단을 뒤집은 첫 장면", "판단", p21, "official_record", "HD현대 50년사 038-039", "banknote_myth", "contain"),
        StoryboardItem("기술이 연결되고", "기술", p323, "official_record", "HD현대 50년사 642-643", "banknote_myth", "contain"),
        StoryboardItem("정부와 금융이 연결되고", "금융", p22, "official_record", "HD현대 50년사 040-041", "banknote_myth", "contain"),
        StoryboardItem("마지막에 수주가 붙었다", "수주", ship, "licensed_icon", "Twemoji – CC BY 4.0"),
        StoryboardItem("전설의 핵심은 증거", "증거", p16, "official_record", "HD현대 50년사 028-029", "banknote_myth", "contain"),
        StoryboardItem("아무것도 없던 순간", "아무것도 없음", construction, "original_reaction", "BringIssue 자체 제작"),
        StoryboardItem("여러분이라면 주문할까요?", "여러분의 선택", choice, "original_reaction", "BringIssue 자체 제작"),
    ]


def build_typecast_payload(text: str) -> dict[str, object]:
    return {
        "voice_id": VOICE_ID,
        "text": text,
        "model": "ssfm-v30",
        "language": "kor",
        "prompt": {
            "emotion_type": "preset",
            "emotion_preset": "normal",
            "emotion_intensity": 0.88,
        },
        "output": {
            "volume": 100,
            "audio_pitch": 0,
            "audio_tempo": VOICE_TEMPO,
            "audio_format": "wav",
        },
        "seed": 42,
    }


def synthesize() -> tuple[Path, dict[str, object]]:
    AUDIO.mkdir(parents=True, exist_ok=True)
    wav = AUDIO / "narration.wav"
    meta = AUDIO / "narration.json"
    script_hash = hashlib.sha256(NARRATION.encode("utf-8")).hexdigest()
    if wav.exists() and meta.exists():
        cached = json.loads(meta.read_text(encoding="utf-8"))
        if (
            cached.get("_script_hash") == script_hash
            and cached.get("_voice_id") == VOICE_ID
            and cached.get("_tempo") == VOICE_TEMPO
        ):
            return wav, cached
    key = v2.user_env("TYPECAST_API_KEY")
    if not key:
        raise RuntimeError("TYPECAST_API_KEY is missing")
    response = v2.requests.post(
        "https://api.typecast.ai/v1/text-to-speech/with-timestamps?granularity=word",
        headers={"X-API-KEY": key, "Content-Type": "application/json"},
        json=build_typecast_payload(NARRATION),
        timeout=300,
    )
    response.raise_for_status()
    payload = response.json()
    wav.write_bytes(base64.b64decode(payload["audio"]))
    metadata = {key: value for key, value in payload.items() if key != "audio"}
    metadata.update(
        {"_script_hash": script_hash, "_voice_id": VOICE_ID, "_tempo": VOICE_TEMPO}
    )
    meta.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return wav, metadata


def phrase_timeline(words: list[dict]) -> list[CaptionSegment]:
    groups: list[list[dict]] = []
    current: list[dict] = []
    for word in words:
        candidate = current + [word]
        length = len("".join(str(item["text"]).replace(" ", "") for item in candidate))
        if current and length > CAPTION_MAX_CHARS:
            groups.append(current)
            current = [word]
        else:
            current = candidate
        if str(word["text"]).rstrip().endswith((".", "?", "!", "。", "？", "！")):
            groups.append(current)
            current = []
    if current:
        groups.append(current)
    return [
        CaptionSegment(
            text=" ".join(str(item["text"]) for item in group),
            output_start=float(group[0]["start"]),
            output_end=float(group[-1]["end"]),
        )
        for group in groups
    ]


def _fit_font(draw: ImageDraw.ImageDraw, text: str, size: int, max_width: int) -> ImageFont.FreeTypeFont:
    while size > 24:
        selected = _font(size)
        box = draw.textbbox((0, 0), text, font=selected)
        if box[2] - box[0] <= max_width:
            return selected
        size -= 2
    return _font(size)


def _centered(draw: ImageDraw.ImageDraw, y: int, text: str, size: int, fill: str) -> None:
    selected = _fit_font(draw, text, size, 960)
    box = draw.textbbox((0, 0), text, font=selected)
    draw.text(((W - (box[2] - box[0])) // 2, y), text, font=selected, fill=fill)


def _cover(source: Image.Image, focus_x: float = 0.5, focus_y: float = 0.5) -> Image.Image:
    image = source.convert("RGB")
    scale = max(VISUAL_SIZE[0] / image.width, VISUAL_SIZE[1] / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = round(max(0, resized.width - VISUAL_SIZE[0]) * focus_x)
    top = round(max(0, resized.height - VISUAL_SIZE[1]) * focus_y)
    return resized.crop((left, top, left + VISUAL_SIZE[0], top + VISUAL_SIZE[1]))


def _evidence_panel(source: Image.Image, focus_x: float = 0.5, focus_y: float = 0.5) -> Image.Image:
    full = source.convert("RGB")
    background = _cover(full, focus_x, focus_y).filter(ImageFilter.GaussianBlur(18))
    background = ImageEnhance.Brightness(background).enhance(0.28)
    full_copy = full.copy()
    full_copy.thumbnail((860, 430), Image.Resampling.LANCZOS)
    background.paste(full_copy, ((900 - full_copy.width) // 2, 26))
    detail_target = (860, 610)
    scale = max(detail_target[0] / full.width, detail_target[1] / full.height) * 1.75
    detail = full.resize(
        (round(full.width * scale), round(full.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = round(max(0, detail.width - detail_target[0]) * focus_x)
    top = round(max(0, detail.height - detail_target[1]) * focus_y)
    detail = detail.crop((left, top, left + detail_target[0], top + detail_target[1]))
    background.paste(detail, (20, 470))
    draw = ImageDraw.Draw(background)
    draw.line((20, 454, 880, 454), fill="#62C8FF", width=5)
    return background


def _focus_for(path: Path) -> tuple[float, float]:
    name = path.name
    if "p21" in name:
        return 0.29, 0.58
    if "p22" in name:
        return 0.78, 0.56
    if "p31" in name:
        return 0.52, 0.52
    if "p323" in name:
        return 0.48, 0.82
    if "bok" in name:
        return 0.66, 0.50
    return 0.50, 0.50


def render_frames() -> list[Path]:
    FRAMES.mkdir(parents=True, exist_ok=True)
    frames: list[Path] = []
    for index, item in enumerate(storyboard(), 1):
        with Image.open(item.source) as source:
            focus_x, focus_y = _focus_for(item.source)
            visual = (
                _evidence_panel(source, focus_x, focus_y)
                if item.crop_policy == "contain"
                else _cover(source, item.focus_x, item.focus_y)
            )
        canvas = Image.new("RGB", (W, H), "#000000")
        canvas.paste(visual, VISUAL_POSITION)
        draw = ImageDraw.Draw(canvas)
        _centered(draw, 58, TITLE_LINES[0], 108, TITLE_COLORS[0])
        _centered(draw, 200, TITLE_LINES[1], 112, TITLE_COLORS[1])
        draw.rectangle((90, 1470, 990, 1550), fill="#071019")
        draw.text((112, 1494), f"출처  {item.attribution}", font=_fit_font(draw, item.attribution, 27, 820), fill="#C6D8E3")
        target = FRAMES / f"shot_{index:02d}.jpg"
        canvas.save(target, quality=95, subsampling=0)
        frames.append(target)
    return frames


def build_ass(timeline: list[CaptionSegment]) -> Path:
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Main,Malgun Gothic,66,&H00FFC762,&H00FFC762,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,13,0,2,84,84,255,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    events = "".join(
        f"Dialogue: 0,{v3.ass_time(item.output_start)},{v3.ass_time(item.output_end)},Main,,0,0,0,,{item.text}\n"
        for item in timeline
    )
    target = OUT / "captions.ass"
    target.write_text(header + events, encoding="utf-8-sig")
    return target


def visual_starts(words: list[dict]) -> list[float]:
    starts = v3.resolve_continuous_visual_starts(words, NARRATION_ANCHORS)
    return [max(0.0, start + item.visual_start_offset) for start, item in zip(starts, storyboard())]


def render_video(
    frames: list[Path], starts: list[float], duration: float, audio: Path, captions: Path
) -> Path:
    VIDEO.mkdir(parents=True, exist_ok=True)
    concat = OUT / "frames.txt"
    lines: list[str] = []
    for frame, start, end in zip(frames, starts, starts[1:] + [duration]):
        lines.extend(
            (
                f"file '{frame.resolve().as_posix()}'",
                f"duration {max(0.05, end - start):.6f}",
            )
        )
    lines.append(f"file '{frames[-1].resolve().as_posix()}'")
    concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
    silent = VIDEO / "visual.mp4"
    v2.run(
        [
            str(v2.FFMPEG),
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-vf",
            "fps=30,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "19",
            "-t",
            f"{duration:.4f}",
            str(silent),
        ]
    )
    escaped_ass = captions.resolve().as_posix().replace(":", r"\:")
    v2.run(
        [
            str(v2.FFMPEG),
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(silent),
            "-i",
            str(audio),
            "-vf",
            f"ass='{escaped_ass}'",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-movflags",
            "+faststart",
            "-shortest",
            str(FINAL_VIDEO),
        ]
    )
    return FINAL_VIDEO


def parse_loudness(stderr: str) -> dict[str, float]:
    matches = re.findall(r"\{\s*\"input_i\".*?\}", stderr, flags=re.DOTALL)
    if not matches:
        raise ValueError("loudness JSON was not found in FFmpeg output")
    values = json.loads(matches[-1])
    keys = ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")
    return {key: float(values[key]) for key in keys if key in values}


def measure_loudness(path: Path) -> dict[str, float]:
    command = [
        str(v2.FFMPEG),
        "-hide_banner",
        "-i",
        str(path),
        "-af",
        "loudnorm=I=-11:TP=-1:LRA=7:print_format=json",
        "-f",
        "null",
        "NUL",
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return parse_loudness(completed.stderr)


def normalize_audio_two_pass(path: Path) -> Path:
    normalized = AUDIO / "narration_normalized.wav"
    mastering_filter = (
        f"{AUDIO_PREPROCESS_FILTER},"
        f"loudnorm=I={LOUDNORM_TARGET_I}:TP={LOUDNORM_TARGET_TP}:LRA={LOUDNORM_TARGET_LRA}"
    )
    v2.run(
        [
            str(v2.FFMPEG),
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(path),
            "-af",
            mastering_filter,
            "-ar",
            "48000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(normalized),
        ]
    )
    return normalized


def create_publish_manifest() -> Path:
    PUBLISH.mkdir(parents=True, exist_ok=True)
    payload = {
        "title": "500원 지폐로 조선소를 세웠다는 이야기, 사실일까? #shorts",
        "description": (
            "500원 지폐 한 장으로 조선소를 세웠다는 유명한 이야기를 공식 기록으로 확인했습니다.\n\n"
            "500원권은 설득의 상징이었지만 실제 과정에는 울산 백사장 사진, 기술 협력, 정부 지원, "
            "버클레이즈 차관, 리바노스의 선박 수주가 함께 있었습니다.\n\n"
            "주요 출처\n"
            "HD현대중공업그룹 50년사 제1권 통사: https://www.hhi.co.kr/resources/front/assets/file/%ED%98%84%EB%8C%80%EC%A4%91%EA%B3%B5%EC%97%85%EA%B7%B8%EB%A3%B9_50%EB%85%84%EC%82%AC_1%EA%B6%8C%28%ED%86%B5%EC%82%AC%29.pdf\n"
            "한국은행 Currency Validity: https://www.bok.or.kr/eng/main/contents.do?menuNo=400179\n\n"
            "그래픽: OpenMoji(CC BY-SA 4.0), Twemoji(CC BY 4.0), BringIssue 자체 제작"
        ),
        "tags": ["정주영", "현대중공업", "500원지폐", "기업이야기", "팩트체크", "shorts"],
        "category_id": "27",
        "privacy_status": "public",
        "contains_synthetic_media": True,
    }
    target = PUBLISH / "youtube_manifest.json"
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def write_qc(
    duration: float,
    starts: list[float],
    final: Path,
    loudness: dict[str, float],
) -> dict[str, object]:
    QC.mkdir(parents=True, exist_ok=True)
    validation = validate_only()
    report = {
        **validation,
        "duration": duration,
        "visual_starts_monotonic": all(a < b for a, b in zip(starts, starts[1:])),
        "video": str(final.relative_to(ROOT)),
        "video_sha256": hashlib.sha256(final.read_bytes()).hexdigest(),
        "width": W,
        "height": H,
        "fps": 30,
        "voice_id": VOICE_ID,
        "target_lufs": AUDIO_TARGET_LUFS,
        "measured_lufs": loudness["input_i"],
        "measured_true_peak_dbfs": loudness["input_tp"],
    }
    if not 100 <= duration <= 130:
        report["errors"] = [*report["errors"], "duration outside 100-130 seconds"]
        report["valid"] = False
    if not report["visual_starts_monotonic"]:
        report["errors"] = [*report["errors"], "visual starts are not strictly monotonic"]
        report["valid"] = False
    if not -12.5 <= loudness["input_i"] <= -10.5:
        report["errors"] = [*report["errors"], "integrated loudness outside -12.5 to -10.5 LUFS"]
        report["valid"] = False
    if loudness["input_tp"] > -0.8:
        report["errors"] = [*report["errors"], "true peak above -0.8 dBFS"]
        report["valid"] = False
    target = QC / "report.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def build() -> dict[str, object]:
    OUT.mkdir(parents=True, exist_ok=True)
    validation = validate_only()
    if not validation["valid"]:
        raise RuntimeError(json.dumps(validation, ensure_ascii=False, indent=2))
    raw_audio, metadata = synthesize()
    audio = normalize_audio_two_pass(raw_audio)
    words = metadata["words"]
    duration = v2.wav_duration(audio)
    starts = visual_starts(words)
    frames = render_frames()
    captions = build_ass(phrase_timeline(words))
    final = render_video(frames, starts, duration, audio, captions)
    manifest = create_publish_manifest()
    loudness = measure_loudness(final)
    report = write_qc(duration, starts, final, loudness)
    result = {**report, "manifest": str(manifest.relative_to(ROOT))}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def validate_only() -> dict[str, object]:
    items = storyboard()
    errors: list[str] = []
    if not 28 <= len(items) <= 42:
        errors.append("storyboard count outside 28-42")
    errors.extend(f"missing source: {item.source}" for item in items if not item.source.exists())
    errors.extend(
        f"caption too long: {item.caption}"
        for item in items
        if len(item.caption.replace(" ", "")) > CAPTION_MAX_CHARS
    )
    documentary = sum(item.visual_role in {"official_record", "article_excerpt"} for item in items)
    if documentary / len(items) < 0.35:
        errors.append("documentary ratio below 35%")
    return {
        "valid": not errors,
        "errors": errors,
        "shots": len(items),
        "documentary_ratio": documentary / len(items),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.validate_only:
        print(json.dumps(validate_only(), ensure_ascii=False, indent=2))
        return
    build()


if __name__ == "__main__":
    main()
