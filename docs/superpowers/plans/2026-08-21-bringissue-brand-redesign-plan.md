# BringIssue Brand Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 브링이슈 네이버 블로그를 에디토리얼 시그널 브랜드로 전환하고, 카테고리·프로필·커버·배경·기존 공개글 5편의 대표 이미지를 같은 체계로 통일한다.

**Architecture:** 브랜드 문구와 색상을 JSON 계약으로 고정하고, Pillow 기반 단일 빌더가 커버·배경·프로필·5개 썸네일을 재현 가능하게 생성한다. 로컬 테스트와 렌더 검수를 먼저 통과시킨 뒤 인증된 네이버 UI에서 삭제 없이 이름 변경·이미지 교체를 수행하고, 실제 공개 저장 직전에 확인을 받는다.

**Tech Stack:** Python 3.11, Pillow 12, `unittest`, Naver SmartEditor/블로그 관리 UI, Chrome browser control, local screenshot QA

---

## 파일 구조

- Create: `brand/bringissue/brand-system.json` — 브랜드 문구, 색상, 카테고리 매핑, 썸네일 콘텐츠 계약
- Create: `scripts/build_bringissue_brand_assets.py` — 모든 래스터 자산을 생성하는 단일 빌더
- Create: `tests/test_bringissue_brand_assets.py` — 계약·크기·핵심 색상·출력 존재 검증
- Create: `brand/bringissue/output/cover.png` — 네이버 커버 마스터
- Create: `brand/bringissue/output/background.png` — 전체 배경 마스터
- Create: `brand/bringissue/output/profile.png` — BI 프로필 마스터
- Create: `brand/bringissue/output/thumbnails/*.jpg` — 공개글 5편의 통일 대표 이미지
- Create: `brand/bringissue/qa/contact-sheet.jpg` — 전체 자산 시각 검수판
- Create: `brand/bringissue/audit-before.json` — 네이버 변경 전 공개 상태
- Create: `brand/bringissue/audit-after.json` — 네이버 변경 후 공개 상태와 URL 검증
- Modify: `blog/batches/2026-08-21-bringissue-five-posts.md` — 새 대표 이미지와 리디자인 완료 상태 기록

### Task 1: 브랜드 계약 고정

**Files:**
- Create: `brand/bringissue/brand-system.json`
- Test: `tests/test_bringissue_brand_assets.py`

- [ ] **Step 1: 계약 파일이 없어서 실패하는 테스트 작성**

```python
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "brand" / "bringissue" / "brand-system.json"


class BringIssueBrandContractTests(unittest.TestCase):
    def test_contract_contains_approved_identity(self):
        self.assertTrue(CONTRACT.exists())
        data = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(data["name"], "브링이슈")
        self.assertEqual(data["tagline"], "지금 뜬 영상 속 결정적 한 장면")
        self.assertEqual(data["palette"]["navy"], "#14233B")
        self.assertEqual(data["palette"]["yellow"], "#FFCC36")
        self.assertEqual(data["categories"][0]["after"], "오늘 뜬 유튜브")
        self.assertEqual(len(data["published_posts"]), 5)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 테스트가 예상대로 실패하는지 실행**

Run: `python -m unittest tests.test_bringissue_brand_assets.BringIssueBrandContractTests -v`

Expected: `FAIL` because `brand/bringissue/brand-system.json` does not exist.

- [ ] **Step 3: 승인된 브랜드 계약 작성**

```json
{
  "name": "브링이슈",
  "blog_title": "브링이슈 | 지금 뜬 영상 속 결정적 한 장면",
  "tagline": "지금 뜬 영상 속 결정적 한 장면",
  "description": "사람들이 멈춰 본 장면, 그 뒤의 선택과 이유를 읽습니다.",
  "palette": {
    "navy": "#14233B",
    "yellow": "#FFCC36",
    "ivory": "#F4F1E8",
    "white": "#FFFFFF",
    "text": "#172033"
  },
  "categories": [
    {"before": "오늘 뜬 유튜브", "after": "오늘 뜬 유튜브"},
    {"before": "국내 경제 뉴스", "after": "스타·인물 비하인드"},
    {"before": "국외 경제 뉴스", "after": "선택의 반전"},
    {"before": "경제 용어 및 기본적인 상식", "after": "돈 되는 아이템"},
    {"before": "공지사항", "after": "브링이슈 안내"}
  ],
  "published_posts": [
    {"slug": "yoo-gunsan", "log_no": "224386096315", "label": "오늘 뜬 영상", "text": ["짬뽕 먹으러 갔는데", "전원 간짜장으로 바꾼 이유"], "source": "blog-assets/2026-08-21-ddeunddeun-roadtrip/scene-09.jpg"},
    {"slug": "fairy-leftovers", "log_no": "224386096430", "label": "선택의 반전", "text": ["남은 음식 싸간 친구", "다음 날 인정한 이유"], "source": "blog-assets/2026-08-21-fairyjaehyung-30year/scene-03.jpg"},
    {"slug": "hajiwon-stage", "log_no": "224386096521", "label": "스타 비하인드", "text": ["안무 틀렸는데", "아무도 몰랐다"], "source": "blog-assets/2026-08-21-hajiwon-yuinradio/scene-07.jpg"},
    {"slug": "heo-water", "log_no": "224386096592", "label": "스타 비하인드", "text": ["신인 시절", "정수기 물도 눈치 봤다"], "source": "blog-assets/2026-08-21-heokyunghwan-salondrip/scene-06.jpg"},
    {"slug": "leejihyun-staff", "log_no": "224386096661", "label": "인물의 선택", "text": ["“저 여기 직원이에요”", "미용실에서 드러난 현실"], "source": "blog-assets/2026-08-21-seoinyoung-leejihyun/scene-03.jpg"}
  ]
}
```

- [ ] **Step 4: 계약 테스트 통과 확인**

Run: `python -m unittest tests.test_bringissue_brand_assets.BringIssueBrandContractTests -v`

Expected: `OK`, 1 test passed.

- [ ] **Step 5: 계약과 테스트 커밋**

```bash
git add brand/bringissue/brand-system.json tests/test_bringissue_brand_assets.py
git commit -m "test: define bringissue brand contract"
```

### Task 2: 재현 가능한 브랜드 자산 빌더

**Files:**
- Create: `scripts/build_bringissue_brand_assets.py`
- Modify: `tests/test_bringissue_brand_assets.py`

- [ ] **Step 1: 출력 크기와 색상 검증 테스트 추가**

```python
from PIL import Image


OUTPUT = ROOT / "brand" / "bringissue" / "output"


class BringIssueAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from scripts.build_bringissue_brand_assets import build_all
        build_all()

    def test_master_asset_sizes(self):
        expected = {
            "cover.png": (1600, 400),
            "background.png": (1920, 1200),
            "profile.png": (600, 600),
        }
        for name, size in expected.items():
            with self.subTest(name=name):
                with Image.open(OUTPUT / name) as image:
                    self.assertEqual(image.size, size)

    def test_five_thumbnail_outputs(self):
        files = sorted((OUTPUT / "thumbnails").glob("*.jpg"))
        self.assertEqual(len(files), 5)
        for file in files:
            with Image.open(file) as image:
                self.assertEqual(image.size, (1280, 720))

    def test_profile_uses_approved_signal_colors(self):
        with Image.open(OUTPUT / "profile.png").convert("RGB") as image:
            colors = image.getcolors(maxcolors=image.width * image.height)
        present = {rgb for _, rgb in colors}
        self.assertIn((255, 204, 54), present)
        self.assertIn((20, 35, 59), present)
```

- [ ] **Step 2: 빌더가 없어서 실패하는지 실행**

Run: `python -m unittest tests.test_bringissue_brand_assets.BringIssueAssetTests -v`

Expected: `ERROR` with `ModuleNotFoundError: scripts.build_bringissue_brand_assets`.

- [ ] **Step 3: Pillow 빌더 구현**

Implement `scripts/build_bringissue_brand_assets.py` with these exact public functions:

```python
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
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


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
    draw.text((122, 226), data["tagline"], font=font(FONT_REGULAR, 31), fill=(220, 228, 239))
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
    draw.rounded_rectangle((68, 454, 68 + 360, 494), radius=10, fill=yellow)
    draw.text((86, 460), f"BRING ISSUE · {post['label']}", font=font(FONT_BOLD, 20), fill=navy)
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
    build_contact_sheet(thumbnails).save(qa_dir / "contact-sheet.jpg", quality=92, optimize=True)
    return [OUTPUT / "cover.png", OUTPUT / "background.png", OUTPUT / "profile.png", *thumbnails]


if __name__ == "__main__":
    for path in build_all():
        print(path)
```

- [ ] **Step 4: 자산 테스트 통과 확인**

Run: `python -m unittest tests.test_bringissue_brand_assets -v`

Expected: `OK`, 4 tests passed.

- [ ] **Step 5: 빌더와 테스트 커밋**

```bash
git add scripts/build_bringissue_brand_assets.py tests/test_bringissue_brand_assets.py
git commit -m "feat: build bringissue brand assets"
```

### Task 3: 로컬 자산 렌더 및 시각 QA

**Files:**
- Create: `brand/bringissue/output/cover.png`
- Create: `brand/bringissue/output/background.png`
- Create: `brand/bringissue/output/profile.png`
- Create: `brand/bringissue/output/thumbnails/*.jpg`
- Create: `brand/bringissue/qa/contact-sheet.jpg`

- [ ] **Step 1: 전체 자산 생성**

Run: `python scripts/build_bringissue_brand_assets.py`

Expected: 8개 출력 경로(커버, 배경, 프로필, 썸네일 5개)가 표시된다.

- [ ] **Step 2: 테스트 전체 실행**

Run: `python -m unittest tests.test_bringissue_brand_assets -v`

Expected: `OK`, 4 tests passed.

- [ ] **Step 3: 시각 검수**

Open these exact files with `view_image`:

- `brand/bringissue/output/cover.png`
- `brand/bringissue/output/background.png`
- `brand/bringissue/output/profile.png`
- `brand/bringissue/qa/contact-sheet.jpg`

Check: 글자가 잘리지 않음, BI가 중앙 정렬됨, 5개 인물 얼굴이 하단 바에 가려지지 않음, 노란 라벨과 흰 제목이 모바일 축소에서도 읽힘, 유튜브 UI가 없음.

- [ ] **Step 4: 생성 자산 커밋**

```bash
git add brand/bringissue/output brand/bringissue/qa/contact-sheet.jpg
git commit -m "assets: add bringissue editorial signal visuals"
```

### Task 4: 네이버 변경 전 상태 기록과 프로필·카테고리·스킨 준비

**Files:**
- Create: `brand/bringissue/audit-before.json`

- [ ] **Step 1: 인증된 브링이슈 홈을 읽기 전용으로 점검**

Open `https://blog.naver.com/bringissue` and record:

- blog title and description
- nickname and blog address
- current background image visible state
- category names, order, category numbers, post counts
- published URLs `224386096315`, `224386096430`, `224386096521`, `224386096592`, `224386096661`

- [ ] **Step 2: 변경 전 감사 파일 작성**

Write `brand/bringissue/audit-before.json` with this shape and values read from the page:

```json
{
  "checked_at": "2026-08-21T23:00:00+09:00",
  "blog_url": "https://blog.naver.com/bringissue",
  "blog_title": "브링이슈 | 세상의 돈과 선택 이야기",
  "nickname": "브링이슈",
  "categories": [
    {"name": "공지사항", "category_no": 11, "post_count": 0},
    {"name": "국내 경제 뉴스", "category_no": 23, "post_count": 0},
    {"name": "국외 경제 뉴스", "category_no": 24, "post_count": 0},
    {"name": "경제 용어 및 기본적인 상식", "category_no": 25, "post_count": 0},
    {"name": "오늘 뜬 유튜브", "category_no": 26, "post_count": 7}
  ],
  "published_log_nos": ["224386096315", "224386096430", "224386096521", "224386096592", "224386096661"]
}
```

If the page shows different numbers, store the observed values instead of the example values.

- [ ] **Step 3: 네이버 UI에서 변경값 입력하되 공개 저장 전 정지**

Prepare these exact values:

- 블로그명(title): `브링이슈 | 지금 뜬 영상 속 결정적 한 장면`
- description: `사람들이 멈춰 본 장면, 그 뒤의 선택과 이유를 읽습니다.`
- profile image: `brand/bringissue/output/profile.png`
- cover image: `brand/bringissue/output/cover.png`
- background image: `brand/bringissue/output/background.png`
- categories and order from `brand-system.json`

Do not change blog address, nickname, post visibility, or category numbers. Do not delete a category. Stop immediately before the UI action that saves the public profile/skin/category changes.

- [ ] **Step 4: 공개 변경 확인 요청**

Ask one action-time confirmation describing the exact destination (`blog.naver.com/bringissue`) and the exact public changes (title, description, profile, cover/background, five category labels/order).

- [ ] **Step 5: 승인 후 저장하고 공개 홈 검증**

Save only after confirmation. Reload the public home and verify the old clothing background and economic category names are absent, while blog address and nickname are unchanged.

- [ ] **Step 6: 감사 파일 커밋**

```bash
git add brand/bringissue/audit-before.json
git commit -m "docs: record bringissue pre-redesign state"
```

### Task 5: 공개글 5편 대표 이미지 교체

**Files:**
- Modify: five public Naver posts only through authenticated UI

- [ ] **Step 1: 첫 글을 편집 모드로 열고 대표 이미지 교체 준비**

Open `https://blog.naver.com/bringissue/224386096315` and enter edit mode. Replace only the first representative image with `brand/bringissue/output/thumbnails/yoo-gunsan.jpg`. Preserve title, all body paragraphs, 10 scene images, source, tags, category 26, public/search/comment/sympathy settings. Stop before the final save.

- [ ] **Step 2: 첫 글 공개 수정 확인 요청과 저장**

Ask action-time confirmation for modifying the public post. After approval, save and verify the same URL opens with the new representative image and unchanged title.

- [ ] **Step 3: 나머지 네 글도 한 편씩 준비·검증**

Use this exact mapping:

| URL | New thumbnail |
|---|---|
| `https://blog.naver.com/bringissue/224386096430` | `fairy-leftovers.jpg` |
| `https://blog.naver.com/bringissue/224386096521` | `hajiwon-stage.jpg` |
| `https://blog.naver.com/bringissue/224386096592` | `heo-water.jpg` |
| `https://blog.naver.com/bringissue/224386096661` | `leejihyun-staff.jpg` |

For each post, verify before saving: title unchanged, total image count remains 11, category is `오늘 뜬 유튜브`, search is allowed, and only the first image differs.

- [ ] **Step 4: 나머지 네 공개 수정 묶음 확인 요청과 저장**

After all four editors are staged, ask one grouped action-time confirmation identifying the four posts and replacement images. Save only after confirmation.

- [ ] **Step 5: 공개 URL 검증**

Reload all five public URLs. Expected: each resolves to `PostView.naver`, retains its log number and title, uses category 26, and shows the new first image.

### Task 6: 데스크톱·모바일 최종 QA와 운영 기록

**Files:**
- Create: `brand/bringissue/audit-after.json`
- Modify: `blog/batches/2026-08-21-bringissue-five-posts.md`

- [ ] **Step 1: 데스크톱 홈 검수**

At the normal browser viewport, verify:

- navy cover and ivory background are visible
- profile `BI` is readable
- tagline is not clipped
- category order matches the contract
- the five recent posts show consistent thumbnails

- [ ] **Step 2: 모바일 홈 검수**

Use the browser viewport capability at approximately `390 × 844`. Verify the cover safe zone, profile, category navigation, and two-line thumbnail titles remain readable. Reset the viewport override afterward.

- [ ] **Step 3: 변경 후 감사 파일 작성**

Write `brand/bringissue/audit-after.json` containing:

```json
{
  "checked_at": "2026-08-21T23:30:00+09:00",
  "blog_url": "https://blog.naver.com/bringissue",
  "blog_title": "브링이슈 | 지금 뜬 영상 속 결정적 한 장면",
  "description": "사람들이 멈춰 본 장면, 그 뒤의 선택과 이유를 읽습니다.",
  "desktop_qa": true,
  "mobile_qa": true,
  "categories_ok": true,
  "profile_ok": true,
  "cover_ok": true,
  "background_ok": true,
  "post_thumbnail_log_nos": ["224386096315", "224386096430", "224386096521", "224386096592", "224386096661"]
}
```

Use the actual completion timestamp.

- [ ] **Step 4: 배치 원장 업데이트**

Append the redesign date, approved palette, category mapping, generated asset paths, and five verified public URLs to `blog/batches/2026-08-21-bringissue-five-posts.md`.

- [ ] **Step 5: 최종 테스트와 diff 검수**

Run:

```bash
python -m unittest tests.test_bringissue_brand_assets -v
git diff --check
git status --short
```

Expected: brand asset tests pass, `git diff --check` has no output, and status shows only intended audit/doc changes.

- [ ] **Step 6: 최종 기록 커밋**

```bash
git add brand/bringissue/audit-after.json blog/batches/2026-08-21-bringissue-five-posts.md
git commit -m "docs: record bringissue brand rollout"
```

## 실행 중지 조건

- 카테고리 번호가 예상과 다르거나 글이 들어 있는 기존 카테고리 삭제가 요구되는 경우
- 네이버가 프로필·커버·배경 중 하나를 지원하지 않거나 업로드 후 강제 크롭으로 문구가 잘리는 경우
- 공개글 편집기가 첫 이미지만 교체하지 못하고 본문 전체를 재작성하려는 경우
- CAPTCHA, 재로그인, 계정 권한 경고가 나타나는 경우
- 사용자 확인 전 공개 저장 또는 공개글 수정 버튼을 눌러야 하는 경우
