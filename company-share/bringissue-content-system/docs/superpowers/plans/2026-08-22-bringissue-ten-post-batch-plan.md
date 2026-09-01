# BringIssue Ten-Post Batch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 2026-08-22 기준 화제성 유튜브 영상 10편을 검증하고, 각 영상의 대표 이미지 1장·본문 장면 10장·예쁜 네이버 서식 원고를 제작해 브링이슈 편집기에서 발행 직전까지 준비한다.

**Architecture:** 고정된 JSON 배치 원장이 영상 ID, 출처, 각도, 수익 연결 후보를 관리한다. Python/yt-dlp로 공개 메타데이터·자막·저해상도 작업 영상을 확보하고, OpenCV/Pillow 파이프라인이 타임코드 기반 장면·대표 이미지·접촉시트를 재현 가능하게 만든다. 원고는 원본 자막 검증 후 사람 중심 화제글과 상품 중심 정보글을 같은 모바일 에디토리얼 서식으로 작성하며, 브라우저에서는 공개 발행을 누르지 않는다.

**Tech Stack:** Python 3.11, `python -m yt_dlp` 2026.03.17, OpenCV 4.13, Pillow 12.2, `unittest`, Naver SmartEditor, Chrome browser control

---

## 파일 구조

- Create: `blog/batches/2026-08-22-bringissue-ten-posts.json` — 10편 영상·각도·수익 연결 계약
- Create: `blog/batches/2026-08-22-bringissue-ten-posts.md` — 선정 근거와 제작·입력 원장
- Create: `scripts/prepare_bringissue_ten_post_batch.py` — 메타데이터, 자막, 영상, 장면, 대표 이미지, 접촉시트 생성기
- Create: `tests/test_bringissue_ten_post_batch.py` — 배치 계약과 결과물 검증
- Create: `blog-assets/2026-08-22-jipdaesung-bigbang-camping/`
- Create: `blog-assets/2026-08-22-yanghongwon-heatwave/`
- Create: `blog-assets/2026-08-22-parkgane-fold8-japan/`
- Create: `blog-assets/2026-08-22-kimjiyu-bbq-parttime/`
- Create: `blog-assets/2026-08-22-itsub-trifold-repair/`
- Create: `blog-assets/2026-08-22-mocar-gv90/`
- Create: `blog-assets/2026-08-22-congbeen-korea-return/`
- Create: `blog-assets/2026-08-22-lijulike-goodbye/`
- Create: `blog-assets/2026-08-22-wonmin-carrot-scam/`
- Create: `blog-assets/2026-08-22-yenmad-blog-income/`

각 영상 폴더는 `info.json`, `source.ko.vtt`, `transcript-sampled.txt`, `scene-plan.json`, `scene-01.jpg`~`scene-10.jpg`, `thumbnail.jpg`, `thumbnail-text.txt`, `contact-sheet.jpg`, `post-draft.md`를 가진다.

### Task 1: 10편 배치 계약 고정

**Files:**
- Create: `blog/batches/2026-08-22-bringissue-ten-posts.json`
- Create: `tests/test_bringissue_ten_post_batch.py`

- [ ] **Step 1: 계약이 없어서 실패하는 테스트 작성**

```python
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "blog" / "batches" / "2026-08-22-bringissue-ten-posts.json"


class BringIssueTenPostContractTests(unittest.TestCase):
    def test_registry_contains_ten_unique_public_youtube_videos(self):
        self.assertTrue(REGISTRY.exists())
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        posts = data["posts"]
        self.assertEqual(len(posts), 10)
        self.assertEqual(len({post["video_id"] for post in posts}), 10)
        self.assertEqual(len({post["slug"] for post in posts}), 10)
        self.assertTrue(all(post["url"] == f"https://www.youtube.com/watch?v={post['video_id']}" for post in posts))
        self.assertTrue(all(post["editorial_angle"] for post in posts))
        self.assertTrue(all(post["monetization_bridge"] for post in posts))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 예상 실패 확인**

Run: `python -m unittest tests.test_bringissue_ten_post_batch.BringIssueTenPostContractTests -v`

Expected: `FAIL` because the registry does not exist.

- [ ] **Step 3: 아래 10편을 정확히 등록**

```json
{
  "checked_at": "2026-08-22T00:00:00+09:00",
  "trend_source": "https://pikk.co.kr/youtube-trends?category=0",
  "posts": [
    {
      "order": 1,
      "slug": "jipdaesung-bigbang-camping",
      "video_id": "C8bnSlLCh8g",
      "url": "https://www.youtube.com/watch?v=C8bnSlLCh8g",
      "channel": "집대성",
      "source_title": "[SUB] 우리 캠핑 갈고야 | 집대성 ep.120 빅뱅 (BIGBANG)",
      "editorial_angle": "빅뱅 멤버들이 캠핑 준비 과정에서 보여준 예상 밖 역할 분담과 관계성",
      "monetization_bridge": "캠핑 의자·랜턴·휴대용 조리도구"
    },
    {
      "order": 2,
      "slug": "yanghongwon-heatwave",
      "video_id": "ko3IP-WTB2Q",
      "url": "https://www.youtube.com/watch?v=ko3IP-WTB2Q",
      "channel": "양홍원의 육아일기",
      "source_title": "폭염에서 살아남기",
      "editorial_angle": "폭염 속 육아에서 계획보다 먼저 바뀐 현실적인 선택",
      "monetization_bridge": "휴대용 선풍기·쿨링용품·유아 여름용품"
    },
    {
      "order": 3,
      "slug": "parkgane-fold8-japan",
      "video_id": "6JOhl0WhRxw",
      "url": "https://www.youtube.com/watch?v=6JOhl0WhRxw",
      "channel": "ぱく家(박가네)",
      "source_title": "일본에서 갤럭시 폴드8은 얼마나 인기일까?",
      "editorial_angle": "한국에서 보는 인기와 일본 현장 반응이 달랐던 이유",
      "monetization_bridge": "폴더블 케이스·보호필름·충전 액세서리"
    },
    {
      "order": 4,
      "slug": "kimjiyu-bbq-parttime",
      "video_id": "IPWva69hO7w",
      "url": "https://www.youtube.com/watch?v=IPWva69hO7w",
      "channel": "천상여자 김지유",
      "source_title": "불판을 또 닦아요..?🔥 고깃집 막내 알바생으로 잠입한 37세 천상여자 | 김지유의 알바",
      "editorial_angle": "손님이 보지 못하는 고깃집 막내의 반복 노동과 김지유의 반응 변화",
      "monetization_bridge": "주방 장갑·냄새 제거제·세척용품"
    },
    {
      "order": 5,
      "slug": "itsub-trifold-repair",
      "video_id": "48JWie_aMxI",
      "url": "https://www.youtube.com/watch?v=48JWie_aMxI",
      "channel": "ITSub잇섭",
      "source_title": "359만원짜리 갤럭시 Z 트라이폴드 깨먹으면 수리비 얼마나 나올까?",
      "editorial_angle": "359만원 기기의 파손 이후 실제 수리 과정과 예상 밖 비용",
      "monetization_bridge": "파손보험·보호필름·힌지 케이스"
    },
    {
      "order": 6,
      "slug": "mocar-gv90",
      "video_id": "gB7CRaVAi4U",
      "url": "https://www.youtube.com/watch?v=gB7CRaVAi4U",
      "channel": "김한용의 MOCAR",
      "source_title": "제네시스 GV90 세계 최초 공개! 이제야 감동의 현대차가 시작됐다!",
      "editorial_angle": "GV90 최초 공개에서 외관보다 더 반응이 컸던 실제 기능",
      "monetization_bridge": "차량용 충전기·수납용품·세차용품"
    },
    {
      "order": 7,
      "slug": "congbeen-korea-return",
      "video_id": "7OP9yBcLeO4",
      "url": "https://www.youtube.com/watch?v=7OP9yBcLeO4",
      "channel": "콩빈Cong Been",
      "source_title": "1년 만에 한국 돌아와서 하고 싶었던 거 원없이 하는 브이로그",
      "editorial_angle": "1년 만에 돌아온 사람이 가장 먼저 챙긴 평범하지만 구체적인 한국 생활",
      "monetization_bridge": "베개·올리브영 뷰티·장보기 아이템"
    },
    {
      "order": 8,
      "slug": "lijulike-goodbye",
      "video_id": "RzYOAwZ2rrE",
      "url": "https://www.youtube.com/watch?v=RzYOAwZ2rrE",
      "channel": "리쥬라이크 LIJULIKE",
      "source_title": "[VLOG] 잠깐봤는데 또 헤어져야 한다구요..?🥺",
      "editorial_angle": "짧은 만남 뒤 다시 헤어져야 했던 가족의 실제 준비와 마지막 반응",
      "monetization_bridge": "여행 파우치·휴대용 육아용품·기내용 정리용품"
    },
    {
      "order": 9,
      "slug": "wonmin-carrot-scam",
      "video_id": "JuK_D77HWpg",
      "url": "https://www.youtube.com/watch?v=JuK_D77HWpg",
      "channel": "원민커플",
      "source_title": "당근거래 처음하는 와이프 상대로 사기쳐봤습니다ㅋㅋㅋㅋㅋ",
      "editorial_angle": "처음 중고거래에 나선 사람을 속인 장난이 예상 밖 반응으로 돌아온 순간",
      "monetization_bridge": "중고거래 체크리스트·휴대용 보안용품·택배 포장재"
    },
    {
      "order": 10,
      "slug": "yenmad-blog-income",
      "video_id": "BWVGEhf17P8",
      "url": "https://www.youtube.com/watch?v=BWVGEhf17P8",
      "channel": "옌마드Yenmad",
      "source_title": "퇴근하고 하루 10분, 블로그로 돈버는 방법 총정리💰",
      "editorial_angle": "하루 10분이라는 주장 안에서 실제로 필요한 작업과 자동화의 한계",
      "monetization_bridge": "블로그 템플릿·AI 도구·디지털 가이드"
    }
  ]
}
```

- [ ] **Step 4: 계약 테스트 통과 확인**

Run: `python -m unittest tests.test_bringissue_ten_post_batch.BringIssueTenPostContractTests -v`

Expected: `OK`, 1 test passed.

- [ ] **Step 5: 커밋**

```bash
git add blog/batches/2026-08-22-bringissue-ten-posts.json tests/test_bringissue_ten_post_batch.py
git commit -m "test: define bringissue ten-post batch"
```

### Task 2: 메타데이터·자막·작업 영상 수집기

**Files:**
- Create: `scripts/prepare_bringissue_ten_post_batch.py`
- Modify: `tests/test_bringissue_ten_post_batch.py`

- [ ] **Step 1: 수집기 공개 함수와 폴더 계약 테스트 추가**

```python
class BringIssueCollectorCommandTests(unittest.TestCase):
    def test_commands_are_reproducible_and_do_not_require_ffmpeg_merge(self):
        from scripts.prepare_bringissue_ten_post_batch import (
            asset_dir,
            load_registry,
            metadata_command,
            subtitle_command,
            video_command,
        )

        for post in load_registry()["posts"]:
            dest = asset_dir(post)
            self.assertTrue(dest.name.startswith("2026-08-22-"))
            metadata = metadata_command(post, dest)
            subtitles = subtitle_command(post, dest)
            video = video_command(post, dest)
            self.assertIn("--write-info-json", metadata)
            self.assertIn("--write-auto-subs", subtitles)
            self.assertIn("best[height<=480][ext=mp4]/best[height<=480]/worst", video)
            self.assertNotIn("--merge-output-format", video)
```

- [ ] **Step 2: 수집기가 없어서 실패하는지 확인**

Run: `python -m unittest tests.test_bringissue_ten_post_batch -v`

Expected: `ModuleNotFoundError: scripts.prepare_bringissue_ten_post_batch`.

- [ ] **Step 3: 수집기 구현**

Implement these exact behaviors:

```python
def asset_dir(post):
    return ROOT / "blog-assets" / f"2026-08-22-{post['slug']}"

def metadata_command(post, dest):
    return [sys.executable, "-m", "yt_dlp", "--skip-download", "--write-info-json", "-o", str(dest / "source.%(ext)s"), post["url"]]

def subtitle_command(post, dest):
    return [sys.executable, "-m", "yt_dlp", "--skip-download", "--write-auto-subs", "--write-subs", "--sub-langs", "ko.*,ko,en.*", "--sub-format", "vtt", "-o", str(dest / "source.%(ext)s"), post["url"]]

def video_command(post, dest):
    return [sys.executable, "-m", "yt_dlp", "-f", "best[height<=480][ext=mp4]/best[height<=480]/worst", "-o", str(dest / "source-video.%(ext)s"), post["url"]]
```

The CLI supports `metadata`, `subtitles`, `video`, `scenes`, `thumbnail`, and `all` stages and accepts `--slug` to limit work to one post.

- [ ] **Step 4: 수집기 테스트 통과 확인**

Run: `python -m unittest tests.test_bringissue_ten_post_batch -v`

Expected: all contract and command tests pass.

- [ ] **Step 5: 커밋**

```bash
git add scripts/prepare_bringissue_ten_post_batch.py tests/test_bringissue_ten_post_batch.py
git commit -m "feat: add bringissue batch collector"
```

### Task 3: 원본 10편 검증과 자막 확보

**Files:**
- Create: ten `info.json` files
- Create: ten `source.*.vtt` files
- Create: ten `transcript-sampled.txt` files
- Create: `blog/batches/2026-08-22-bringissue-ten-posts.md`

- [ ] **Step 1: 메타데이터와 자막 수집**

Run:

```bash
python scripts/prepare_bringissue_ten_post_batch.py metadata
python scripts/prepare_bringissue_ten_post_batch.py subtitles
```

Expected: 10 folders exist; each has metadata and at least one usable Korean or English VTT. If a video has no usable subtitle, stop that slug and use YouTube transcript export from the original video instead of inventing dialogue.

- [ ] **Step 2: 공개 상태와 중복 검증**

Verify every `info.json` has matching `id`, `title`, `channel`, `upload_date`, `view_count`, and duration over 180 seconds. Compare IDs against `blog/batches/2026-08-21-bringissue-five-posts.md`; no duplicate is allowed.

- [ ] **Step 3: 대사 표본 생성**

Strip VTT cue metadata and repeated rolling-caption lines. Save chronological transcript text with time markers at least every 30 seconds to `transcript-sampled.txt`.

- [ ] **Step 4: 선정 원장 작성**

Record exact observed upload date, view count, duration, title, channel, URL, chosen angle, likely scene range, and monetization bridge for all 10 posts. Mark any factual uncertainty explicitly as excluded from the draft.

- [ ] **Step 5: 커밋**

```bash
git add blog/batches/2026-08-22-bringissue-ten-posts.md blog-assets/2026-08-22-*/info.json blog-assets/2026-08-22-*/source*.vtt blog-assets/2026-08-22-*/transcript-sampled.txt
git commit -m "docs: verify ten bringissue source videos"
```

### Task 4: 장면 계획과 깨끗한 캡처 100장

**Files:**
- Create: ten `scene-plan.json` files
- Create: `scene-01.jpg` through `scene-10.jpg` in each asset folder
- Create: ten `contact-sheet.jpg` files
- Modify: `scripts/prepare_bringissue_ten_post_batch.py`
- Modify: `tests/test_bringissue_ten_post_batch.py`

- [ ] **Step 1: 장면 결과 테스트 추가**

```python
from PIL import Image


class BringIssueSceneTests(unittest.TestCase):
    def test_each_post_has_ten_distinct_wide_scenes_and_contact_sheet(self):
        from scripts.prepare_bringissue_ten_post_batch import asset_dir, load_registry

        for post in load_registry()["posts"]:
            folder = asset_dir(post)
            scenes = sorted(folder.glob("scene-*.jpg"))
            self.assertEqual(len(scenes), 10, post["slug"])
            fingerprints = set()
            for scene in scenes:
                with Image.open(scene).convert("RGB") as image:
                    self.assertGreaterEqual(image.width, 854)
                    self.assertGreaterEqual(image.height, 480)
                    self.assertAlmostEqual(image.width / image.height, 16 / 9, places=2)
                    small = image.resize((16, 9)).convert("L")
                    fingerprints.add(tuple(small.getdata()))
            self.assertEqual(len(fingerprints), 10, post["slug"])
            self.assertTrue((folder / "contact-sheet.jpg").exists())
```

- [ ] **Step 2: 결과가 없어서 실패하는지 확인**

Run: `python -m unittest tests.test_bringissue_ten_post_batch.BringIssueSceneTests -v`

Expected: failure because scene plans and images do not exist.

- [ ] **Step 3: 영상과 장면 계획 작성**

Download 480p working videos. For each transcript, choose ten exact timestamps representing: introduction, trigger, first choice, reaction, question, decisive action, pre-reversal, reversal, aftermath, conclusion. Save those ten seconds and Korean captions in `scene-plan.json`.

- [ ] **Step 4: OpenCV 캡처와 Pillow 접촉시트 구현·실행**

The script seeks to each timestamp, crops only the video frame, saves JPEG quality 94, and never captures browser/player chrome. The contact sheet is a 2×5 grid labeled 01–10 without covering faces.

Run: `python scripts/prepare_bringissue_ten_post_batch.py scenes`

- [ ] **Step 5: 자동·시각 검수**

Run: `python -m unittest tests.test_bringissue_ten_post_batch.BringIssueSceneTests -v`

Open all ten contact sheets and reject: repeated frames, blurred faces, UI, irrelevant subtitles, or a face hidden by labels.

- [ ] **Step 6: 커밋**

```bash
git add scripts/prepare_bringissue_ten_post_batch.py tests/test_bringissue_ten_post_batch.py blog-assets/2026-08-22-*/scene-plan.json blog-assets/2026-08-22-*/scene-*.jpg blog-assets/2026-08-22-*/contact-sheet.jpg
git commit -m "assets: add ten bringissue scene sets"
```

### Task 5: 대표 이미지 10장

**Files:**
- Create: ten `thumbnail-text.txt` files
- Create: ten `thumbnail.jpg` files
- Modify: `scripts/prepare_bringissue_ten_post_batch.py`
- Modify: `tests/test_bringissue_ten_post_batch.py`

- [ ] **Step 1: 대표 이미지 테스트 추가**

```python
class BringIssueThumbnailTests(unittest.TestCase):
    def test_each_post_has_mobile_readable_thumbnail_contract(self):
        from scripts.prepare_bringissue_ten_post_batch import asset_dir, load_registry

        for post in load_registry()["posts"]:
            folder = asset_dir(post)
            with Image.open(folder / "thumbnail.jpg") as image:
                self.assertEqual(image.size, (1280, 720))
            lines = [
                line.strip()
                for line in (folder / "thumbnail-text.txt").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(lines), 2, post["slug"])
            self.assertTrue(all(len(line) <= 18 for line in lines), post["slug"])
```

- [ ] **Step 2: 두 줄 문구 확정**

Use factual `행동/상황 → 반전/이유` wording. Avoid repeating the full blog title, and keep the person or product visible in the image.

- [ ] **Step 3: 대표 이미지 생성**

Use the strongest scene, a readable dark lower gradient, one small category label, and two large white title lines. Do not add YouTube logos, play buttons, or fake quotations.

Run: `python scripts/prepare_bringissue_ten_post_batch.py thumbnail`

- [ ] **Step 4: 테스트와 모바일 축소 검수**

Run: `python -m unittest tests.test_bringissue_ten_post_batch.BringIssueThumbnailTests -v`

Inspect thumbnails at 320px width; both lines and the main face/product must remain readable.

- [ ] **Step 5: 커밋**

```bash
git add blog-assets/2026-08-22-*/thumbnail.jpg blog-assets/2026-08-22-*/thumbnail-text.txt scripts/prepare_bringissue_ten_post_batch.py tests/test_bringissue_ten_post_batch.py
git commit -m "assets: add ten bringissue thumbnails"
```

### Task 6: 예쁜 모바일 에디토리얼 원고 10편

**Files:**
- Create: ten `post-draft.md` files
- Modify: `blog/batches/2026-08-22-bringissue-ten-posts.md`

- [ ] **Step 1: 원고별 사실 원장 작성**

Before drafting, record the exact transcript timestamps supporting every quoted phrase, number, product specification, price, or claimed result. Remove any claim that cannot be tied to the original video or an authoritative product source.

- [ ] **Step 2: 10편 초안 작성**

Each draft contains:

- 40–55 character factual curiosity title
- three-sentence hook
- exactly three emoji subheads
- `image → scene description → BringIssue interpretation` for ten images
- 1,500–2,200 Korean characters excluding spaces
- 3–5 underline markers and restrained bold markers
- one editor-view paragraph
- one easy reader question
- original channel, video title, URL, copyright notice, and 8–12 tags

Use HTML-compatible markers in Markdown: `<b>핵심</b>` and `<u>기억할 결론</u>` so Naver formatting can be reproduced exactly.

- [ ] **Step 3: 수익 연결 문단 제한**

Add a product/tool suggestion only when the video naturally creates purchase intent. Mark it `정보성 제안` in the draft. Do not insert affiliate URLs that have not been supplied and do not claim personal use. The entertainment-first posts may omit monetization if the connection would feel forced.

- [ ] **Step 4: 원고 QA**

Check title length, three subheads, ten image references, three-to-five underline markers, source URL, copyright notice, tag count, and prohibited speculation. Read each draft once without images to confirm narrative flow and once with the contact sheet to confirm scene order.

- [ ] **Step 5: 커밋**

```bash
git add blog-assets/2026-08-22-*/post-draft.md blog/batches/2026-08-22-bringissue-ten-posts.md
git commit -m "content: draft ten bringissue editorial posts"
```

### Task 7: 네이버 편집기 발행 직전 입력

**Files:**
- Modify: authenticated Naver SmartEditor drafts only
- Modify: `blog/batches/2026-08-22-bringissue-ten-posts.md`

- [ ] **Step 1: 편집기 설정 확인**

Use `blog.naver.com/bringissue`. Keep all video playback muted. For every post use category `오늘 뜬 유튜브`, topic `스타·연예인`, overall public visibility, comments, sympathy, search, and external sharing enabled.

- [ ] **Step 2: 한 편을 기준 템플릿으로 입력**

Insert thumbnail, hook, scenes 1–10, three emoji subheads, paragraphs, source, copyright notice, and tags. Apply bold and underline exactly where `<b>` and `<u>` markers appear. Verify mobile paragraph spacing and stop before the final public publish action.

- [ ] **Step 3: 기준 글 시각 QA**

Verify image/text alternation, no two images touch, no paragraph exceeds four mobile lines, three subheads stand out, and source/advertising disclosure is visible.

- [ ] **Step 4: 나머지 9편 입력**

Repeat the verified template. After each post, record editor-tab status, title, image count 11, tag count, category, topic, and settings in the batch ledger. Do not click final publish.

- [ ] **Step 5: 10편 탭 검수**

Check every editor remains open at the final publish dialog or last editable screen, has the correct title and first image, and contains 11 total images. Mark all ten as `발행 직전 / 미발행` in the ledger.

### Task 8: 최종 검증과 기록

**Files:**
- Modify: `blog/batches/2026-08-22-bringissue-ten-posts.md`

- [ ] **Step 1: 전체 자동 테스트**

Run:

```bash
python -m unittest tests.test_bringissue_ten_post_batch -v
git diff --check
git status --short
```

Expected: all batch tests pass, `git diff --check` has no output, and unrelated user files remain untouched.

- [ ] **Step 2: 최종 원장 기록**

Record ten titles, source URLs, folder paths, thumbnail/scene counts, draft character counts, bold/underline/subhead counts, Naver category/topic/settings, and `미발행` status.

- [ ] **Step 3: 최종 커밋**

```bash
git add blog/batches/2026-08-22-bringissue-ten-posts.md
git commit -m "docs: record bringissue ten-post batch readiness"
```

## 중지 조건

- 영상이 삭제·비공개·연령 제한·유료 공개로 바뀐 경우
- 자막과 실제 음성이 달라 핵심 발언을 검증할 수 없는 경우
- 영상 다운로드 또는 캡처가 원본을 대체할 수준의 재배포가 되는 경우
- 네이버 로그인·CAPTCHA·권한 경고가 나타나는 경우
- 기존 공개글이나 다른 초안을 덮어쓰려는 경우
- 실제 공개 발행 버튼을 눌러야 다음 단계로 넘어가는 경우
