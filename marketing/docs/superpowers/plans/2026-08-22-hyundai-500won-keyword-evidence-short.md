# Hyundai 500-Won Keyword-Anchor Evidence Short Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce and publish a 100–130 second vertical Short that verifies the “500원 지폐로 조선소를 세웠다” story using actual records, keyword-anchored visuals, licensed open assets, continuous narration, and one-line subtitles.

**Architecture:** Store factual claims, source URLs, visual roles, and rights status in one fail-closed evidence ledger. A separate open-asset module downloads only allowlisted licenses and writes immutable provenance receipts. The renderer consumes a sentence-first storyboard in which every caption has one `anchor_keyword`, then assembles official evidence, literal photos, licensed icons, and original stickman reactions into a synchronized 1080×1920 video.

**Tech Stack:** Python 3.11, Pillow, requests, Typecast TTS, FFmpeg, pytest, YouTube Data API, official HD Hyundai and Bank of Korea records, Openclipart CC0, OpenMoji CC BY-SA 4.0, Twemoji CC BY 4.0.

---

## File structure

- Create `production/domestic_cases/hyundai_500won_shipyard_evidence_v1.json`: claim ledger, source ledger, asset licenses, storyboard mapping.
- Create `automation/open_asset_library.py`: license validation, deterministic downloads, SHA-256 receipts.
- Create `automation/hyundai_500won_shipyard_short.py`: narration, caption grouping, keyword anchors, frame rendering, TTS, video assembly, QC manifest.
- Create `tests/test_open_asset_library.py`: fail-closed licensing and receipt tests.
- Create `tests/test_hyundai_500won_shipyard_short.py`: facts, storyboard, safe layout, synchronization, and documentary-ratio tests.
- Modify `docs/AI_SHORTS_AUTOMATION_MANUAL.md`: make keyword-anchor and licensed-asset rules permanent.
- Create `output/hyundai_500won_shipyard_evidence_v1/source/*`: unmodified official evidence captures.
- Create `output/hyundai_500won_shipyard_evidence_v1/assets/*`: licensed open assets and receipt JSON.
- Create `output/hyundai_500won_shipyard_evidence_v1/video/*`: rendered video.
- Create `output/hyundai_500won_shipyard_evidence_v1/qc/*`: contact sheet, sampled frames, loudness and decode reports.
- Create `output/hyundai_500won_shipyard_evidence_v1/publish/youtube_manifest.json`: public metadata and source attribution.

### Task 1: Evidence ledger and myth qualification

**Files:**
- Create: `production/domestic_cases/hyundai_500won_shipyard_evidence_v1.json`
- Create: `tests/test_hyundai_500won_shipyard_short.py`

- [ ] **Step 1: Write the failing claim-ledger test**

```python
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "production/domestic_cases/hyundai_500won_shipyard_evidence_v1.json"


def test_every_spoken_claim_has_two_sources_and_qualified_wording():
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    assert len(data["claims"]) >= 7
    for claim in data["claims"]:
        assert claim["primary_source_url"].startswith("https://")
        assert claim["crosscheck_source_url"].startswith("https://")
        assert claim["status"] in {
            "PASS", "PRIMARY_RECORD", "OFFICIAL_RETROSPECTIVE", "MYTH_QUALIFIED"
        }
    myth = next(item for item in data["claims"] if item["id"] == "banknote_myth")
    assert myth["status"] == "MYTH_QUALIFIED"
    assert "지폐 한 장만으로" not in myth["spoken_wording"]
    assert all(word in myth["spoken_wording"] for word in ["지폐", "백사장", "차관", "수주"])
```

- [ ] **Step 2: Run the focused test and confirm the expected failure**

Run: `python -m pytest tests/test_hyundai_500won_shipyard_short.py::test_every_spoken_claim_has_two_sources_and_qualified_wording -q`

Expected: FAIL because the ledger does not exist.

- [ ] **Step 3: Create the claim ledger with exact verified wording**

The ledger must include these records and no stronger claim than the sources support:

```json
{
  "claims": [
    {
      "id": "banknote_design",
      "spoken_wording": "정주영이 꺼낸 것은 당시 유통되던 500원권이었고, 뒷면에는 거북선과 판옥선이 그려져 있었습니다.",
      "primary_source_url": "https://www.bok.or.kr/eng/main/contents.do?menuNo=400179",
      "crosscheck_source_url": "https://file-cdn.bok.or.kr/portal/46ec711571a90732c6148aeb8b319562/1/FILE_201803300830040051.pdf",
      "status": "PRIMARY_RECORD"
    },
    {
      "id": "barclays_loan",
      "spoken_wording": "현대중공업 50년사는 1971년 9월 영국 버클레이즈은행과 조선소 건설 차관 도입에 서명했다고 기록합니다.",
      "primary_source_url": "https://www.hhi.co.kr/filedown/hdhyundai_50_3.pdf",
      "crosscheck_source_url": "https://www.hhi.co.kr/resources/front/assets/file/%ED%98%84%EB%8C%80%EC%A4%91%EA%B3%B5%EC%97%85%EA%B7%B8%EB%A3%B9_50%EB%85%84%EC%82%AC_1%EA%B6%8C%28%ED%86%B5%EC%82%AC%29.pdf",
      "status": "OFFICIAL_RETROSPECTIVE"
    },
    {
      "id": "livanos_order",
      "spoken_wording": "같은 공식 기록에는 1971년 12월 리바노스 회장과 1호선 계약을 체결한 자료가 남아 있습니다.",
      "primary_source_url": "https://www.hhi.co.kr/filedown/hdhyundai_50_3.pdf",
      "crosscheck_source_url": "https://www.hhi.co.kr/resources/front/assets/file/%ED%98%84%EB%8C%80%EC%A4%91%EA%B3%B5%EC%97%85%EA%B7%B8%EB%A3%B9_50%EB%85%84%EC%82%AC_1%EA%B6%8C%28%ED%86%B5%EC%82%AC%29.pdf",
      "status": "OFFICIAL_RETROSPECTIVE"
    },
    {
      "id": "banknote_myth",
      "spoken_wording": "500원 지폐는 설득의 상징이었지만, 지폐와 백사장 사진 뒤에는 기술제휴, 정부 지원, 버클레이즈 차관, 리바노스의 선박 수주가 함께 있었습니다.",
      "primary_source_url": "https://naval-special.hhi.co.kr/ko/media01_view/19",
      "crosscheck_source_url": "https://www.hhi.co.kr/resources/front/assets/file/%ED%98%84%EB%8C%80%EC%A4%91%EA%B3%B5%EC%97%85%EA%B7%B8%EB%A3%B9_50%EB%85%84%EC%82%AC_1%EA%B6%8C%28%ED%86%B5%EC%82%AC%29.pdf",
      "status": "MYTH_QUALIFIED"
    }
  ]
}
```

Append these three exact claim records, then add `source_date`, `source_pages`, and `scene_ids` to all seven records:

```json
{
  "id": "appledore_cooperation",
  "spoken_wording": "공식 50년사에는 1971년 9월 영국 애플도어와 조선소 건설을 위한 기술·판매 협력을 논의한 기록이 남아 있습니다.",
  "primary_source_url": "https://www.hhi.co.kr/filedown/hdhyundai_50_3.pdf",
  "crosscheck_source_url": "https://www.hhi.co.kr/resources/front/assets/file/%ED%98%84%EB%8C%80%EC%A4%91%EA%B3%B5%EC%97%85%EA%B7%B8%EB%A3%B9_50%EB%85%84%EC%82%AC_1%EA%B6%8C%28%ED%86%B5%EC%82%AC%29.pdf",
  "source_date": "1971-09",
  "source_pages": ["pictorial chronology: 1971.09", "volume 1: shipbuilding founding chapter"],
  "scene_ids": [12, 13],
  "status": "OFFICIAL_RETROSPECTIVE"
},
{
  "id": "ulsan_beach_evidence",
  "spoken_wording": "그가 함께 내민 것은 울산 미포만 백사장 사진과 조선소 계획도였습니다.",
  "primary_source_url": "https://www.hhi.co.kr/resources/front/assets/file/%ED%98%84%EB%8C%80%EC%A4%91%EA%B3%B5%EC%97%85%EA%B7%B8%EB%A3%B9_50%EB%85%84%EC%82%AC_1%EA%B6%8C%28%ED%86%B5%EC%82%AC%29.pdf",
  "crosscheck_source_url": "https://www.hhi.co.kr/filedown/hdhyundai_50_3.pdf",
  "source_date": "1971",
  "source_pages": ["volume 1: overseas financing episode", "pictorial: founding episode"],
  "scene_ids": [8, 9],
  "status": "OFFICIAL_RETROSPECTIVE"
},
{
  "id": "simultaneous_build",
  "spoken_wording": "현대는 조선소를 먼저 완성한 뒤 배를 만든 것이 아니라, 조선소 건설과 첫 선박 건조를 함께 밀어붙였습니다.",
  "primary_source_url": "https://www.hhi.co.kr/resources/front/assets/file/%ED%98%84%EB%8C%80%EC%A4%91%EA%B3%B5%EC%97%85%EA%B7%B8%EB%A3%B9_50%EB%85%84%EC%82%AC_1%EA%B6%8C%28%ED%86%B5%EC%82%AC%29.pdf",
  "crosscheck_source_url": "https://www.hhi.co.kr/filedown/hdhyundai_50_3.pdf",
  "source_date": "1972-1974",
  "source_pages": ["volume 1: shipyard and first-vessel construction", "pictorial chronology: 1972-1974"],
  "scene_ids": [22, 23, 24],
  "status": "OFFICIAL_RETROSPECTIVE"
}
```

During acquisition, replace the descriptive `source_pages` labels with verified PDF page numbers before the ledger can pass validation; the validator rejects non-numeric page references in the final manifest.

- [ ] **Step 4: Run the claim-ledger test**

Run: `python -m pytest tests/test_hyundai_500won_shipyard_short.py::test_every_spoken_claim_has_two_sources_and_qualified_wording -q`

Expected: PASS.

- [ ] **Step 5: Commit the evidence ledger**

```powershell
git add production/domestic_cases/hyundai_500won_shipyard_evidence_v1.json tests/test_hyundai_500won_shipyard_short.py
git commit -m "test: lock Hyundai 500-won evidence claims"
```

### Task 2: Fail-closed open-asset library

**Files:**
- Create: `automation/open_asset_library.py`
- Create: `tests/test_open_asset_library.py`

- [ ] **Step 1: Write failing tests for license allowlisting**

```python
import pytest
from open_asset_library import OpenAsset, validate_asset


def test_only_approved_provider_license_pairs_are_accepted():
    pairs = (
        ("Openclipart", "CC0-1.0", "https://openclipart.org/", "Public domain / CC0"),
        ("OpenMoji", "CC-BY-SA-4.0", "https://openmoji.org/", "OpenMoji – CC BY-SA 4.0"),
        ("Twemoji", "CC-BY-4.0", "https://github.com/twitter/twemoji", "Twemoji – CC BY 4.0"),
    )
    for provider, license_id, page_url, attribution in pairs:
        asset = OpenAsset(
            asset_id="sample",
            provider=provider,
            canonical_page_url=page_url,
            download_url="https://openmoji.org/data/color/svg/1F631.svg",
            license_id=license_id,
            attribution=attribution,
        )
        assert validate_asset(asset) is None


def test_unknown_or_meme_site_license_is_rejected():
    asset = OpenAsset(
        asset_id="frog",
        provider="random-meme-site",
        canonical_page_url="https://example.com/frog",
        download_url="https://example.com/frog.png",
        license_id="UNKNOWN",
        attribution="",
    )
    with pytest.raises(ValueError, match="license"):
        validate_asset(asset)
```

- [ ] **Step 2: Run the tests and verify failure**

Run: `python -m pytest tests/test_open_asset_library.py -q`

Expected: FAIL because `open_asset_library` does not exist.

- [ ] **Step 3: Implement the asset contract and deterministic downloader**

```python
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
import json
import requests

PROVIDER_LICENSES = {
    "Openclipart": "CC0-1.0",
    "OpenMoji": "CC-BY-SA-4.0",
    "Twemoji": "CC-BY-4.0",
}


@dataclass(frozen=True)
class OpenAsset:
    asset_id: str
    provider: str
    canonical_page_url: str
    download_url: str
    license_id: str
    attribution: str


def validate_asset(asset: OpenAsset) -> None:
    if asset.provider not in PROVIDER_LICENSES:
        raise ValueError(f"unapproved provider: {asset.provider}")
    if asset.license_id != PROVIDER_LICENSES[asset.provider]:
        raise ValueError(f"unapproved license for {asset.provider}: {asset.license_id}")
    if not asset.attribution:
        raise ValueError("attribution is required")
    if not asset.canonical_page_url.startswith("https://"):
        raise ValueError("canonical page URL is required")


def download_asset(asset: OpenAsset, target: Path, receipt_path: Path) -> dict:
    validate_asset(asset)
    response = requests.get(asset.download_url, timeout=30)
    response.raise_for_status()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(response.content)
    receipt = {**asdict(asset), "sha256": sha256(response.content).hexdigest()}
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
    return receipt
```

- [ ] **Step 4: Add tests for SHA-256 receipts and missing attribution**

Use a mocked `requests.get` response so tests never depend on network state. Assert that the downloaded bytes and recorded hash match exactly.

- [ ] **Step 5: Run and commit**

Run: `python -m pytest tests/test_open_asset_library.py -q`

Expected: PASS.

```powershell
git add automation/open_asset_library.py tests/test_open_asset_library.py
git commit -m "feat: add licensed open asset gate"
```

### Task 3: Acquire official evidence and licensed keyword visuals

**Files:**
- Create: `output/hyundai_500won_shipyard_evidence_v1/source/*`
- Create: `output/hyundai_500won_shipyard_evidence_v1/assets/*`
- Modify: `production/domestic_cases/hyundai_500won_shipyard_evidence_v1.json`

- [ ] **Step 1: Capture the official HD Hyundai records with context**

Download the official 50-year-history PDFs without modification and render only the relevant pages. Preserve the cover/institution identity, page number, date, and caption. Store:

- `source/hdhyundai_50years_volume1.pdf`
- `source/hdhyundai_50years_pictorial.pdf`
- `source/hdhyundai_500won_page.png`
- `source/hdhyundai_barclays_page.png`
- `source/hdhyundai_livanos_page.png`
- `source/hdhyundai_press_release.png`

- [ ] **Step 2: Capture the Bank of Korea currency record**

Capture the official page showing that the second 500-won note was first issued on 1966-08-16 and used Namdaemun on the front and the turtle ship/panokseon on the back. Store `source/bok_500won_record.png` and the unmodified source response.

- [ ] **Step 3: Select no more than six open assets**

Use only:

- one OpenMoji shocked face for `문화 충격`
- one OpenMoji thinking face for `정말 지폐 한 장?`
- one Twemoji banknote for `500원 지폐`
- one Twemoji ship for `선박 수주`
- one Openclipart construction-tool icon for `조선소 건설`
- one Openclipart three-way sign or three-door illustration for `선택지는 세 개`

For each semantic role, search only the named provider's official site/repository, choose one asset whose canonical page and raw download URL both resolve, and record those final URLs in the ledger before downloading. Each item must pass `validate_asset`, retain its canonical page URL, and produce an adjacent `.receipt.json`; if no compliant Openclipart illustration can be verified, render that role as an original stickman drawing instead of substituting an unknown asset.

- [ ] **Step 4: Extend the evidence-ledger test for rights**

```python
def test_every_visual_has_provenance_and_no_unknown_memes():
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    allowed = {"OFFICIAL", "LIMITED_QUOTATION", "CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0", "ORIGINAL"}
    assert all(item["rights_status"] in allowed for item in data["visuals"])
    assert all(item["attribution"] for item in data["visuals"])
    assert not any(item["provider"] in {"GIPHY", "Tenor", "random-meme-site"} for item in data["visuals"])
```

- [ ] **Step 5: Run the rights tests and commit only manifests and receipts**

Run: `python -m pytest tests/test_open_asset_library.py tests/test_hyundai_500won_shipyard_short.py -q`

Expected: PASS.

```powershell
git add production/domestic_cases/hyundai_500won_shipyard_evidence_v1.json output/hyundai_500won_shipyard_evidence_v1/assets/*.receipt.json
git commit -m "feat: register Hyundai evidence and licensed visuals"
```

### Task 4: Sentence-first storyboard and renderer

**Files:**
- Create: `automation/hyundai_500won_shipyard_short.py`
- Modify: `tests/test_hyundai_500won_shipyard_short.py`

- [ ] **Step 1: Write failing storyboard tests**

```python
def test_every_caption_has_one_keyword_anchor_and_matching_shot():
    import hyundai_500won_shipyard_short as video
    items = video.storyboard()
    assert 28 <= len(items) <= 42
    assert all(item.caption and item.anchor_keyword for item in items)
    assert all(len(item.caption.replace(" ", "")) <= 14 for item in items)
    assert all(item.visual_start_offset <= -0.05 for item in items)
    assert all(item.visual_start_offset >= -0.10 for item in items)


def test_actual_evidence_precedes_reaction_for_claims():
    import hyundai_500won_shipyard_short as video
    items = video.storyboard()
    factual = [item for item in items if item.claim_id]
    assert factual
    assert all(item.visual_role in {"official_record", "article_excerpt", "literal_photo"} for item in factual)
    assert sum(item.visual_role in {"official_record", "article_excerpt"} for item in items) / len(items) >= 0.35
```

- [ ] **Step 2: Run and verify failure**

Run: `python -m pytest tests/test_hyundai_500won_shipyard_short.py -q`

Expected: FAIL because the renderer does not exist.

- [ ] **Step 3: Implement the fixed storyboard contract**

```python
@dataclass(frozen=True)
class StoryboardItem:
    caption: str
    anchor_keyword: str
    source: Path
    visual_role: str
    attribution: str
    claim_id: str | None = None
    visual_start_offset: float = -0.08
    crop_policy: str = "cover"
```

The narration must explicitly distinguish the symbol from the full financing story:

```python
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
    "여러분이라면 공장도 제품도 없는 회사에 배 두 척을 주문하시겠습니까?"
]
```

Use this exact narration as the first render candidate. Typecast duration must fall between 100 and 130 seconds; if it does not, adjust pauses and remove redundant connective words only, without adding claims or invented quotations.

- [ ] **Step 4: Implement visual rendering without floating information cards**

Use a fixed top title, a 900×1100 central visual region, source text at `y <= 1620`, and a one-line subtitle safe zone. Evidence screenshots use `contain`; literal photos and open icons use `cover` or transparent centered placement. The renderer must not define a generic rounded information-card function.

- [ ] **Step 5: Run the storyboard and layout tests**

Run: `python -m pytest tests/test_hyundai_500won_shipyard_short.py -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add automation/hyundai_500won_shipyard_short.py tests/test_hyundai_500won_shipyard_short.py
git commit -m "feat: build keyword-anchor Hyundai storyboard"
```

### Task 5: Narration, subtitles, rendering, and QC

**Files:**
- Create: `output/hyundai_500won_shipyard_evidence_v1/audio/*`
- Create: `output/hyundai_500won_shipyard_evidence_v1/video/hyundai_500won_shipyard_final.mp4`
- Create: `output/hyundai_500won_shipyard_evidence_v1/qc/*`

- [ ] **Step 1: Generate continuous Typecast narration**

Use voice `tc_69fc0cff784968297fb45daa`, tempo `1.00`, word timestamps, and cache only when script hash, voice ID, and tempo all match.

- [ ] **Step 2: Generate phrase-complete one-line captions**

Group whole words up to 14 Korean characters. Move orphan particles and conjunctions to the following caption. End each caption on a complete phrase or sentence boundary.

- [ ] **Step 3: Align every visual to its caption anchor**

Resolve word timestamps from narration and start each visual 0.08 seconds before the first word of its caption. Do not insert silence between scenes.

- [ ] **Step 4: Render and normalize**

Render 1080×1920 H.264 at 30fps with AAC 48kHz audio. Normalize to approximately -12 to -11 LUFS and constrain true peak to -1dBFS or below.

- [ ] **Step 5: Run automated QC**

Run:

```powershell
python -m pytest tests/test_open_asset_library.py tests/test_hyundai_500won_shipyard_short.py -q
python automation/hyundai_500won_shipyard_short.py --validate-only
```

Then run a full FFmpeg decode, loudness measurement, and contact-sheet generation. Expected:

- zero decode errors
- 1080×1920, 30fps
- exactly one video stream and one audio stream
- 100–130 seconds
- integrated loudness between -12.5 and -10.5 LUFS
- true peak no higher than -1.0dBFS
- no cropped title, caption, or source strip
- evidence screen visible at every factual claim

- [ ] **Step 6: Review the contact sheet and sampled frames**

Reject the build if any caption shows an unrelated image, an evidence claim uses a reaction image, a screenshot hides its publisher/date, or a side border changes width between scenes.

- [ ] **Step 7: Commit renderer and QC metadata**

```powershell
git add automation/hyundai_500won_shipyard_short.py output/hyundai_500won_shipyard_evidence_v1/qc/report.json
git commit -m "feat: render and validate Hyundai 500-won short"
```

### Task 6: Manual update and public publication

**Files:**
- Modify: `docs/AI_SHORTS_AUTOMATION_MANUAL.md`
- Create: `output/hyundai_500won_shipyard_evidence_v1/publish/youtube_manifest.json`
- Create: `output/hyundai_500won_shipyard_evidence_v1/publish/youtube_result.json`

- [ ] **Step 1: Add the approved policy to the master manual**

Add these permanent rules:

- script → one-line caption → first keyword → visual assignment
- actual evidence before reaction imagery
- Openclipart CC0, OpenMoji CC BY-SA 4.0, Twemoji CC BY 4.0 only with receipts
- GIPHY, Tenor, Pepe, and recognizable third-party cartoon characters are blocked without explicit permission
- one visual per caption phrase, not a blind two-second timer

- [ ] **Step 2: Create public metadata with complete attribution**

Use a title such as `500원 지폐로 조선소를 세웠다는 이야기, 사실일까? #shorts`. The description must link HD Hyundai’s 50-year history, the Bank of Korea currency record, and list all OpenMoji/Twemoji/Openclipart attributions used in the final cut.

- [ ] **Step 3: Dry-run the uploader**

Run:

```powershell
python automation/youtube_uploader.py output/hyundai_500won_shipyard_evidence_v1/video/hyundai_500won_shipyard_final.mp4 output/hyundai_500won_shipyard_evidence_v1/publish/youtube_manifest.json --approve-non-private --dry-run
```

Expected: valid public metadata and a final video SHA-256.

- [ ] **Step 4: Upload only after every QC gate passes**

Use the existing authorized client secrets and YouTube token. Save the returned video ID, public URL, title, channel, upload time, and final SHA-256 in `youtube_result.json` and `qc/report.json`.

- [ ] **Step 5: Verify the public record**

Query YouTube oEmbed with the returned video ID and assert the title and channel are correct.

- [ ] **Step 6: Commit documentation and publication records**

```powershell
git add docs/AI_SHORTS_AUTOMATION_MANUAL.md output/hyundai_500won_shipyard_evidence_v1/publish/youtube_result.json output/hyundai_500won_shipyard_evidence_v1/qc/report.json
git commit -m "docs: publish Hyundai keyword-anchor evidence short"
```
