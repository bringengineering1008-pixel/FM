from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation"))

LEDGER = ROOT / "production" / "domestic_cases" / "hyundai_500won_shipyard_evidence_v1.json"


def test_every_spoken_claim_has_two_sources_and_qualified_wording() -> None:
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    assert len(data["claims"]) >= 7
    for claim in data["claims"]:
        assert claim["primary_source_url"].startswith("https://")
        assert claim["crosscheck_source_url"].startswith("https://")
        assert claim["status"] in {
            "PASS",
            "PRIMARY_RECORD",
            "OFFICIAL_RETROSPECTIVE",
            "MYTH_QUALIFIED",
        }
        assert claim["scene_ids"]
        assert claim["source_pages"]
    myth = next(item for item in data["claims"] if item["id"] == "banknote_myth")
    assert myth["status"] == "MYTH_QUALIFIED"
    assert "지폐 한 장만으로" not in myth["spoken_wording"]
    assert all(word in myth["spoken_wording"] for word in ["지폐", "백사장", "차관", "수주"])


def test_every_visual_has_provenance_and_no_unknown_memes() -> None:
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    allowed = {
        "OFFICIAL",
        "LIMITED_QUOTATION",
        "CC0-1.0",
        "CC-BY-4.0",
        "CC-BY-SA-4.0",
        "ORIGINAL",
    }
    assert len(data["visuals"]) >= 10
    assert all(item["rights_status"] in allowed for item in data["visuals"])
    assert all(item["attribution"] for item in data["visuals"])
    assert not any(
        item["provider"] in {"GIPHY", "Tenor", "random-meme-site"}
        for item in data["visuals"]
    )


def test_every_caption_has_one_keyword_anchor_and_matching_shot() -> None:
    import hyundai_500won_shipyard_short as video

    items = video.storyboard()
    assert 28 <= len(items) <= 42
    assert all(item.caption and item.anchor_keyword for item in items)
    assert all(len(item.caption.replace(" ", "")) <= 14 for item in items)
    assert all(-0.10 <= item.visual_start_offset <= -0.05 for item in items)
    assert all(item.source.exists() for item in items)


def test_actual_evidence_precedes_reaction_for_claims() -> None:
    import hyundai_500won_shipyard_short as video

    items = video.storyboard()
    factual = [item for item in items if item.claim_id]
    assert factual
    assert all(
        item.visual_role in {"official_record", "article_excerpt", "literal_photo"}
        for item in factual
    )
    documentary = [
        item
        for item in items
        if item.visual_role in {"official_record", "article_excerpt"}
    ]
    assert len(documentary) / len(items) >= 0.35


def test_master_layout_and_voice_are_locked() -> None:
    import hyundai_500won_shipyard_short as video

    assert video.VOICE_ID == "tc_69fc0cff784968297fb45daa"
    assert video.VOICE_TEMPO == 1.00
    assert video.W == 1080 and video.H == 1920
    assert video.VISUAL_SIZE == (900, 1100)
    assert video.CAPTION_MAX_CHARS == 14
    assert video.AUDIO_TARGET_LUFS == -11


def test_phrase_timeline_keeps_one_line_captions_short() -> None:
    import hyundai_500won_shipyard_short as video

    words = [
        {"text": "500원짜리", "start": 0.0, "end": 0.5},
        {"text": "지폐", "start": 0.55, "end": 0.8},
        {"text": "한", "start": 0.85, "end": 0.95},
        {"text": "장을", "start": 1.0, "end": 1.2},
        {"text": "보여줬습니다.", "start": 1.25, "end": 1.9},
    ]
    timeline = video.phrase_timeline(words)
    assert timeline
    assert all(len(item.text.replace(" ", "")) <= video.CAPTION_MAX_CHARS for item in timeline)
    assert timeline[-1].text.endswith(".")


def test_rendered_frames_are_fixed_and_safe() -> None:
    import hyundai_500won_shipyard_short as video

    frames = video.render_frames()
    assert len(frames) == len(video.storyboard())
    from PIL import Image

    with Image.open(frames[0]) as image:
        assert image.size == (1080, 1920)
        assert image.getpixel((0, 1000)) == (0, 0, 0)


def test_every_visual_anchor_occurs_in_narration_order() -> None:
    import hyundai_500won_shipyard_short as video

    words = [
        {"text": token, "start": index * 0.1, "end": index * 0.1 + 0.08}
        for index, token in enumerate(video.NARRATION.split())
    ]
    starts = video.v3.resolve_continuous_visual_starts(words, video.NARRATION_ANCHORS)
    assert len(starts) == len(video.storyboard())
    assert all(a < b for a, b in zip(starts, starts[1:]))


def test_audio_filter_controls_peaks_before_loudness_normalization() -> None:
    import hyundai_500won_shipyard_short as video

    assert "volume=12dB" in video.AUDIO_PREPROCESS_FILTER
    assert "alimiter=limit=0.5" in video.AUDIO_PREPROCESS_FILTER
    assert video.LOUDNORM_TARGET_I == -11
    assert video.LOUDNORM_TARGET_TP == -2.0


def test_loudness_json_parser_extracts_measured_values() -> None:
    import hyundai_500won_shipyard_short as video

    stderr = 'prefix\n{\n  "input_i" : "-11.24",\n  "input_tp" : "-1.02",\n  "input_lra" : "2.10",\n  "input_thresh" : "-22.40",\n  "target_offset" : "0.14"\n}\nsuffix'
    assert video.parse_loudness(stderr) == {
        "input_i": -11.24,
        "input_tp": -1.02,
        "input_lra": 2.10,
        "input_thresh": -22.40,
        "target_offset": 0.14,
    }


def test_loudness_probe_decodes_ffmpeg_output_as_utf8(monkeypatch, tmp_path) -> None:
    import hyundai_500won_shipyard_short as video

    received = {}

    class Completed:
        stderr = '{"input_i":"-11.10","input_tp":"-1.00"}'

    def fake_run(*args, **kwargs):
        received.update(kwargs)
        return Completed()

    monkeypatch.setattr(video.subprocess, "run", fake_run)
    assert video.measure_loudness(tmp_path / "한글경로.mp4")["input_i"] == -11.10
    assert received["encoding"] == "utf-8"
    assert received["errors"] == "replace"
