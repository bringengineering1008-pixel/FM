# BringIssue Twenty-Post Editorial Scheduling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 승인된 `어벤져스: 둠스데이` 원고를 기준으로 브링이슈용 총 20편을 제작하고, 사용자 최종 확인 후 2026년 8월 23일과 24일에 하루 10편씩 예약 발행한다.

**Architecture:** 20편의 출처·역할·예약 슬롯을 JSON 원장 하나에서 관리하고, 글별 독립 자산 폴더에 메타데이터·자막·고화질 장면·대표 이미지·최종 원고를 저장한다. 자동 테스트는 편수, 중복, 예약 슬롯, 이미지 품질, 문단·서식 계약을 검사하며, 네이버 편집기 입력과 예약 확정은 별도의 브라우저 단계로 분리한다.

**Tech Stack:** Python 3, `yt-dlp`, Pillow, FFmpeg/ffprobe, `unittest`, Markdown/JSON, Naver SmartEditor, Codex Browser control.

---

## 파일 구조

- Create: `blog/batches/2026-08-22-bringissue-twenty-posts.json` — 20편 출처, 역할, 제목, 예약 시각의 단일 원장
- Create: `blog/batches/2026-08-22-bringissue-twenty-posts.md` — 검증·제작·편집기·예약 상태 기록
- Create: `tests/test_bringissue_twenty_post_batch.py` — 20편 계약과 자산·원고 검수
- Create: `scripts/prepare_bringissue_twenty_post_batch.py` — 메타데이터, 자막, 고화질 영상, 장면, 대표 이미지 준비
- Create: `scripts/validate_bringissue_twenty_post_drafts.py` — 모바일 문단과 서식 계약 검사
- Create: `blog-assets/2026-08-23-<slug>/` — 8월 23일 예약 글의 독립 자산 폴더
- Create: `blog-assets/2026-08-24-<slug>/` — 8월 24일 예약 글의 독립 자산 폴더
- Preserve: `blog/batches/2026-08-22-bringissue-ten-posts.md` 및 현재 미추적 사용자 파일 전체

### Task 1: 20편 원장 계약과 예약 슬롯 테스트

**Files:**
- Create: `tests/test_bringissue_twenty_post_batch.py`
- Create: `blog/batches/2026-08-22-bringissue-twenty-posts.json`

- [ ] **Step 1: 실패하는 원장 계약 테스트 작성**

```python
import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "blog" / "batches" / "2026-08-22-bringissue-twenty-posts.json"
EXPECTED_SLOTS = [
    *(f"2026-08-23T{time}:00+09:00" for time in
      ("07:30", "09:00", "10:30", "12:00", "13:30", "15:00", "16:30", "18:00", "20:00", "22:00")),
    *(f"2026-08-24T{time}:00+09:00" for time in
      ("07:30", "09:00", "10:30", "12:00", "13:30", "15:00", "16:30", "18:00", "20:00", "22:00")),
]


class BringIssueTwentyPostContractTests(unittest.TestCase):
    def test_registry_has_twenty_unique_posts_and_exact_portfolio(self):
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        posts = data["posts"]
        self.assertEqual(len(posts), 20)
        self.assertEqual(len({post["slug"] for post in posts}), 20)
        self.assertEqual(len({post["video_id"] for post in posts if post["video_id"]}), 20)
        self.assertEqual(
            Counter(post["engine"] for post in posts),
            Counter({"entertainment": 12, "product": 5, "money": 3}),
        )
        self.assertEqual([post["scheduled_at"] for post in posts], EXPECTED_SLOTS)
        self.assertEqual(posts[0]["slug"], "avengers-doomsday-doctor-doom")
```

- [ ] **Step 2: 원장이 없어서 실패하는지 확인**

Run: `python -m unittest tests.test_bringissue_twenty_post_batch.BringIssueTwentyPostContractTests -v`

Expected: `FileNotFoundError` for `2026-08-22-bringissue-twenty-posts.json`.

- [ ] **Step 3: 20편 JSON 원장 작성**

원장 최상위와 각 게시물은 아래 필드를 정확히 사용한다.

```json
{
  "checked_at": "2026-08-22T00:00:00+09:00",
  "blog_id": "bringissue",
  "posts": [
    {
      "order": 1,
      "slug": "avengers-doomsday-doctor-doom",
      "engine": "entertainment",
      "video_id": "Bk6DeEedYGs",
      "url": "https://www.youtube.com/watch?v=Bk6DeEedYGs",
      "channel": "MarvelKorea",
      "source_title": "[어벤져스: 둠스데이] '둠의 심판' 예고편",
      "editorial_angle": "아이언맨의 상징이던 배우가 닥터 둠으로 돌아오며 영웅의 과거 선택을 심판하는 구조",
      "scheduled_at": "2026-08-23T07:30:00+09:00",
      "category": "오늘 뜬 유튜브",
      "topic": "스타·연예인"
    }
  ]
}
```

나머지 19편은 실행 당일 실제 공개 영상에서 선정하되, 12/5/3 포트폴리오와 20개 확정 슬롯을 바꾸지 않는다. 각 후보를 원장에 넣기 전에 URL을 직접 열어 제목, 채널, 공개일, 영상 ID를 확인한다.

- [ ] **Step 4: 계약 테스트 통과 확인**

Run: `python -m unittest tests.test_bringissue_twenty_post_batch.BringIssueTwentyPostContractTests -v`

Expected: `OK`, 1 test passed.

- [ ] **Step 5: 원장과 테스트 커밋**

```powershell
git add -- tests/test_bringissue_twenty_post_batch.py blog/batches/2026-08-22-bringissue-twenty-posts.json
git commit -m "test: define bringissue twenty-post batch"
```

### Task 2: 오늘의 후보 조사와 출처 검증

**Files:**
- Modify: `blog/batches/2026-08-22-bringissue-twenty-posts.json`
- Create: `blog/batches/2026-08-22-bringissue-twenty-posts.md`

- [ ] **Step 1: 후보 30개 수집**

2026년 8월 22일 기준 한국 유튜브 실시간 엔터테인먼트, 제품 리뷰, 돈·소비 영상에서 `엔터 18 / 제품 7 / 돈 5` 후보를 수집한다. 공개 영상 URL, 채널, 게시일, 조회 반응, 독자 질문, 수익 연결 가능성을 표로 기록한다.

- [ ] **Step 2: 기존 발행물 중복 검사**

Run:

```powershell
rg -o "youtube\.com/watch\?v=[A-Za-z0-9_-]+" blog blog-assets | Sort-Object -Unique
```

Expected: 새 원장의 20개 영상 ID가 기존 10편·5편 원장에 등장하지 않는다. 동일 인물이 있더라도 사건과 제목 각도가 같으면 제외한다.

- [ ] **Step 3: 20개 최종 후보 선정**

각 후보를 `현재 관심 20 / 클릭 15 / 검색 의도 15 / 독자 가치 15 / 근거·이미지 10 / 차별성 10 / 확장성 5 / 포트폴리오 보정 10`으로 평가한다. 75점 이상이며 사생활·권리·사실성 게이트를 통과한 후보만 원장에 넣는다.

- [ ] **Step 4: 선정 원장에 사실 경계 기록**

`blog/batches/2026-08-22-bringissue-twenty-posts.md`에 각 글의 확인된 사실, 금지할 추측, 원본 영상, 공식 보조 출처, 캡처 가능 장면, 제목 약속을 기록한다. 작품 공개일·가격·제품 사양은 공식 제작사나 제조사 페이지로 재확인한다.

- [ ] **Step 5: 출처 원장 커밋**

```powershell
git add -- blog/batches/2026-08-22-bringissue-twenty-posts.json blog/batches/2026-08-22-bringissue-twenty-posts.md
git commit -m "docs: verify twenty bringissue source videos"
```

### Task 3: 고화질 수집기 구현

**Files:**
- Create: `scripts/prepare_bringissue_twenty_post_batch.py`
- Modify: `tests/test_bringissue_twenty_post_batch.py`

- [ ] **Step 1: 수집 명령 계약 테스트 추가**

```python
class BringIssueHighResolutionCollectorTests(unittest.TestCase):
    def test_video_command_prefers_native_high_resolution_without_audio(self):
        from scripts.prepare_bringissue_twenty_post_batch import load_registry, video_command

        for post in load_registry()["posts"]:
            command = video_command(post)
            self.assertIn("bestvideo[height<=2160]", command)
            self.assertIn("--js-runtimes", command)
            self.assertNotIn("--merge-output-format", command)
```

- [ ] **Step 2: 모듈이 없어서 실패하는지 확인**

Run: `python -m unittest tests.test_bringissue_twenty_post_batch.BringIssueHighResolutionCollectorTests -v`

Expected: `ModuleNotFoundError`.

- [ ] **Step 3: 최소 수집기 구현**

```python
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "blog" / "batches" / "2026-08-22-bringissue-twenty-posts.json"


def load_registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def asset_dir(post):
    date = post["scheduled_at"][:10]
    return ROOT / "blog-assets" / f"{date}-{post['slug']}"


def video_command(post):
    dest = asset_dir(post)
    return [
        sys.executable, "-m", "yt_dlp", "--js-runtimes", "node",
        "-f", "bestvideo[height<=2160]/bestvideo[height<=1440]/bestvideo[height<=1080]",
        "-o", str(dest / "source-video.%(ext)s"), post["url"],
    ]
```

CLI 단계는 `metadata`, `subtitles`, `video`, `scenes`, `thumbnail`을 지원하고 `--slug`로 한 글만 실행할 수 있게 한다. 영상은 무음 비디오 스트림만 받아 사용자의 무음 작업 요구를 지킨다.

- [ ] **Step 4: 테스트 통과 확인**

Run: `python -m unittest tests.test_bringissue_twenty_post_batch.BringIssueHighResolutionCollectorTests -v`

Expected: `OK`.

- [ ] **Step 5: 수집기 커밋**

```powershell
git add -- scripts/prepare_bringissue_twenty_post_batch.py tests/test_bringissue_twenty_post_batch.py
git commit -m "feat: add high-resolution bringissue collector"
```

### Task 4: 메타데이터·자막·장면 계획 확보

**Files:**
- Create: `blog-assets/2026-08-23-*/info.json`
- Create: `blog-assets/2026-08-24-*/info.json`
- Create: `blog-assets/2026-08-23-*/source*.vtt`
- Create: `blog-assets/2026-08-24-*/source*.vtt`
- Create: twenty `scene-plan.json` files

- [ ] **Step 1: 메타데이터와 자막 수집**

```powershell
python scripts/prepare_bringissue_twenty_post_batch.py metadata
python scripts/prepare_bringissue_twenty_post_batch.py subtitles
```

Expected: 20개 자산 폴더마다 `info.json`과 사용할 수 있는 한국어 또는 영어 VTT가 존재한다. 자막이 없으면 해당 원본 영상의 공개 자막을 직접 내보내 검증하며, 들리지 않는 대사를 추정하지 않는다.

- [ ] **Step 2: 원본 영상 공개 상태 검증**

각 `info.json`에서 `id`, `title`, `channel`, `upload_date`, `duration`, `availability`를 원장과 대조한다. 삭제·비공개·연령 제한 영상은 같은 엔진의 차순위 후보로 교체한다.

- [ ] **Step 3: 대사 표본과 전체 맥락 작성**

VTT 태그와 반복 롤링 자막을 제거하고 20~30초 간격으로 `transcript-sampled.txt`를 만든다. 전체 내용을 읽고 `도입 / 변화 / 반전 / 결과 / 편집자 관점`을 글별 원장에 기록한다.

- [ ] **Step 4: 장면 계획 작성**

각 `scene-plan.json`에는 8~11개의 서로 다른 타임스탬프, 장면 역할, 짧은 캡션, 본문에서 설명할 의미를 저장한다.

```json
{
  "video_id": "Bk6DeEedYGs",
  "scenes": [
    {
      "number": 1,
      "timestamp_seconds": 8,
      "role": "과거의 빅터 소개",
      "caption": "다정했던 빅터의 과거",
      "body_purpose": "처음부터 악인이 아니었다는 도입 근거"
    }
  ]
}
```

- [ ] **Step 5: 검증 자료 커밋**

```powershell
git add -- blog-assets/2026-08-23-* blog-assets/2026-08-24-* blog/batches/2026-08-22-bringissue-twenty-posts.md
git commit -m "docs: capture twenty bringissue source contexts"
```

### Task 5: 고화질 장면 160~220장과 대표 이미지 20장

**Files:**
- Modify: `scripts/prepare_bringissue_twenty_post_batch.py`
- Modify: `tests/test_bringissue_twenty_post_batch.py`
- Create: `scene-01.jpg` through `scene-11.jpg` as defined per post
- Create: twenty `contact-sheet.jpg` files
- Create: twenty `thumbnail.jpg` and `thumbnail-text.txt` pairs

- [ ] **Step 1: 이미지 품질 테스트 추가**

```python
from PIL import Image


class BringIssueTwentyPostImageTests(unittest.TestCase):
    def test_scenes_are_native_wide_and_thumbnails_have_safe_size(self):
        from scripts.prepare_bringissue_twenty_post_batch import asset_dir, load_registry

        for post in load_registry()["posts"]:
            folder = asset_dir(post)
            scenes = sorted(folder.glob("scene-*.jpg"))
            self.assertGreaterEqual(len(scenes), 8, post["slug"])
            self.assertLessEqual(len(scenes), 11, post["slug"])
            for scene in scenes:
                with Image.open(scene) as image:
                    self.assertGreaterEqual(image.width, 1280)
                    self.assertAlmostEqual(image.width / image.height, 16 / 9, places=2)
            with Image.open(folder / "thumbnail.jpg") as thumb:
                self.assertEqual(thumb.size, (1600, 900))
```

- [ ] **Step 2: 결과가 없어서 실패하는지 확인**

Run: `python -m unittest tests.test_bringissue_twenty_post_batch.BringIssueTwentyPostImageTests -v`

Expected: missing scene and thumbnail failures.

- [ ] **Step 3: FFmpeg 프레임 추출 구현**

각 타임스탬프에서 원본 프레임을 JPEG 품질 2로 추출한다. 플레이어 화면을 캡처하지 않고 다운로드된 무음 비디오 파일에서 직접 프레임을 가져온다.

```python
def frame_command(video_path, seconds, output_path):
    return [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", str(seconds),
        "-i", str(video_path), "-frames:v", "1", "-q:v", "2",
        "-vf", "scale='min(1920,iw)':-2", str(output_path),
    ]
```

- [ ] **Step 4: 장면과 대표 이미지 생성**

```powershell
python scripts/prepare_bringissue_twenty_post_batch.py video
python scripts/prepare_bringissue_twenty_post_batch.py scenes
python scripts/prepare_bringissue_twenty_post_batch.py thumbnail
```

대표 이미지는 1600×900, 두 줄 문구는 줄당 18자 이하, 인물·제품 안전 여백은 좌우 8% 이상으로 만든다. 유튜브 UI, 재생 버튼, 가짜 인용문은 넣지 않는다.

- [ ] **Step 5: 연락처 시트 시각 검수**

20개의 `contact-sheet.jpg`를 모두 열어 흐림, 눈 감음, 장면 전환, 중복, UI, 얼굴을 덮는 자막을 제외한다. 교체한 장면은 `scene-plan.json` 타임스탬프와 함께 갱신한다.

- [ ] **Step 6: 이미지 테스트와 커밋**

```powershell
python -m unittest tests.test_bringissue_twenty_post_batch.BringIssueTwentyPostImageTests -v
git add -- scripts/prepare_bringissue_twenty_post_batch.py tests/test_bringissue_twenty_post_batch.py blog-assets/2026-08-23-* blog-assets/2026-08-24-*
git commit -m "assets: add twenty high-resolution bringissue scene sets"
```

### Task 6: 승인 문체로 총 20편 원고 작성

**Files:**
- Create: twenty `post-draft.md` files under the dated asset folders
- Create: `scripts/validate_bringissue_twenty_post_drafts.py`
- Modify: `tests/test_bringissue_twenty_post_batch.py`

- [ ] **Step 1: 원고 계약 테스트 작성**

```python
class BringIssueTwentyPostDraftTests(unittest.TestCase):
    def test_drafts_match_approved_mobile_editorial_style(self):
        from scripts.prepare_bringissue_twenty_post_batch import asset_dir, load_registry

        for post in load_registry()["posts"]:
            draft = (asset_dir(post) / "post-draft.md").read_text(encoding="utf-8")
            self.assertIn(post["url"], draft)
            self.assertGreaterEqual(draft.count("<b>"), 3, post["slug"])
            self.assertLessEqual(draft.count("<b>"), 5, post["slug"])
            self.assertLessEqual(draft.count("<u>"), 1, post["slug"])
            self.assertGreaterEqual(draft.count("\n> "), 2, post["slug"])
            self.assertLessEqual(draft.count("\n> "), 3, post["slug"])
            self.assertNotIn("그림 설명", draft)
            self.assertNotIn("브링이슈 해설", draft)
```

- [ ] **Step 2: 승인된 1번 원고 저장**

`blog-assets/2026-08-23-avengers-doomsday-doctor-doom/post-draft.md`에 승인된 제목과 본문을 저장한다. Markdown의 굵게를 `<b>`, 밑줄을 `<u>`, 인용 전환을 `> `로 통일한다.

- [ ] **Step 3: 추가 19편을 수동 에디토리얼 방식으로 작성**

각 글은 `짧은 훅 3~5묶음 → 인용 전환 2~3개 → 장면과 해석 교대 → 독자 질문 → 원본 출처 → 태그` 순서로 작성한다. 문단은 보통 20~45자이며 한 문단 최대 70자, 굵게 3~5회, 밑줄 0~1회, 이모티콘 1~2개를 사용한다. 영상 대사를 연속 복사하지 않고 전체 맥락을 편집자 관점으로 재구성한다.

- [ ] **Step 4: 문단·서식 검사기 구현**

```python
def validate_draft(text: str) -> list[str]:
    errors = []
    paragraphs = [line.strip() for line in text.splitlines() if line.strip()]
    body = [line for line in paragraphs if not line.startswith(("#", ">", "![", "원본 영상:", "#"))]
    if any(len(line) > 70 for line in body):
        errors.append("body paragraph exceeds 70 characters")
    if not 3 <= text.count("<b>") <= 5:
        errors.append("bold count must be 3 to 5")
    if text.count("<u>") > 1:
        errors.append("underline count must be zero or one")
    if not 2 <= text.count("\n> ") <= 3:
        errors.append("quote transition count must be 2 to 3")
    return errors
```

- [ ] **Step 5: 원고 테스트와 사람 검수**

Run:

```powershell
python scripts/validate_bringissue_twenty_post_drafts.py
python -m unittest tests.test_bringissue_twenty_post_batch.BringIssueTwentyPostDraftTests -v
```

Expected: 20편 모두 오류 0개. 각 글을 이미지 없이 한 번, 연락처 시트와 함께 한 번 읽어 장면 순서와 결론이 일치하는지 확인한다.

- [ ] **Step 6: 원고 커밋**

```powershell
git add -- scripts/validate_bringissue_twenty_post_drafts.py tests/test_bringissue_twenty_post_batch.py blog-assets/2026-08-23-*/post-draft.md blog-assets/2026-08-24-*/post-draft.md
git commit -m "content: write twenty bringissue editorial posts"
```

### Task 7: 네이버 편집기 20편 입력과 모바일 QA

**Files:**
- Modify: Naver SmartEditor drafts for `blog.naver.com/bringissue`
- Modify: `blog/batches/2026-08-22-bringissue-twenty-posts.md`

- [ ] **Step 1: 브라우저와 계정 상태 확인**

로그인된 브라우저에서 `blog.naver.com/bringissue`의 글쓰기 화면을 연다. 영상과 자동 재생은 모두 무음으로 유지한다. 로그인 만료, CAPTCHA, 권한 경고가 나오면 해당 단계에서 중단한다.

- [ ] **Step 2: 1번 글을 기준 템플릿으로 입력**

대표 이미지, 훅, 본문 장면 8~11장, 짧은 캡션, 인용구 2~3개, 굵게 3~5개, 밑줄 최대 1개, 원본 링크, 태그를 넣는다. 가운데 정렬과 의미 묶음 사이 빈 문단이 모바일 미리보기에서 보이는지 확인한다.

- [ ] **Step 3: 나머지 19편 입력**

각 글의 원장에 적힌 카테고리와 주제를 사용한다. 전체 공개, 댓글, 공감, 검색, 외부 공유를 허용한다. 제품 글의 승인된 제휴 링크 앞에는 광고 고지를 넣고, 승인 링크가 없으면 판매 링크를 삽입하지 않는다.

- [ ] **Step 4: 20편 편집기 QA**

각 편의 제목, 첫 이미지, 이미지 수, 굵게·밑줄·인용구, 원본 링크, 태그, 카테고리, 주제, 공개 설정을 원장에 기록한다. 어떤 글도 아직 예약 확정하지 않고 `예약 확인 대기` 상태로 둔다.

### Task 8: 사용자 최종 확인 후 하루 10편 예약 확정

**Files:**
- Modify: Naver SmartEditor schedule dialogs
- Modify: `blog/batches/2026-08-22-bringissue-twenty-posts.md`

- [ ] **Step 1: 자동 검증 실행**

```powershell
python -m unittest tests.test_bringissue_twenty_post_batch -v
python scripts/validate_bringissue_twenty_post_drafts.py
git diff --check
git status --short
```

Expected: 모든 테스트 통과, 원고 오류 0개, `git diff --check` 출력 없음, 기존 사용자 파일 보존.

- [ ] **Step 2: 사용자에게 최종 표 제시**

20편의 순서, 제목, 원본 채널, 카테고리, `2026-08-23` 또는 `2026-08-24`의 정확한 예약 시각을 한 표로 보여 준다. 하루 10편 운영 강도와 홈피드 노출 비보장도 함께 알린다.

- [ ] **Step 3: 행동 시점 최종 확인 받기**

네이버 블로그에 20개의 예약 게시물을 생성하는 외부 공개 행동임을 밝히고, 20편 전체 예약 확정을 실행해도 되는지 사용자에게 묻는다. 명확한 승인을 받기 전에는 어떤 예약 확정 버튼도 누르지 않는다.

- [ ] **Step 4: 20개 예약 확정**

승인 후 아래 순서대로 각 편의 예약 버튼을 누른다.

```text
2026-08-23 07:30, 09:00, 10:30, 12:00, 13:30, 15:00, 16:30, 18:00, 20:00, 22:00
2026-08-24 07:30, 09:00, 10:30, 12:00, 13:30, 15:00, 16:30, 18:00, 20:00, 22:00
```

- [ ] **Step 5: 예약 상태 재확인과 기록**

네이버 예약 글 목록에서 20개 제목과 시각이 원장과 일치하는지 확인한다. 각 글의 상태를 `예약 확정`으로 바꾸고 예약 식별 정보 또는 편집 URL을 원장에 기록한다.

- [ ] **Step 6: 최종 원장 커밋**

```powershell
git add -- blog/batches/2026-08-22-bringissue-twenty-posts.md
git commit -m "docs: record bringissue twenty-post schedule"
```

## 중지 조건

- 영상이 삭제·비공개·연령 제한 상태로 바뀐 경우
- 원본 자막과 실제 발언이 달라 핵심 내용을 검증할 수 없는 경우
- 가격·제품 사양·개봉일처럼 변동 가능한 사실을 공식 출처에서 확인하지 못한 경우
- 캡처가 원본을 대체할 정도로 연속적이거나 권리 표시를 훼손하는 경우
- 네이버 로그인 만료, CAPTCHA, 보안·권한 경고가 나타나는 경우
- 기존 공개글 또는 사용자의 미추적 파일을 덮어쓰게 되는 경우
- 사용자 최종 확인 없이 예약 확정 버튼을 눌러야 하는 경우
