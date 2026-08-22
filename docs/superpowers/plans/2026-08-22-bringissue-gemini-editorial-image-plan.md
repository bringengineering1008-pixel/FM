# Bringissue Gemini Editorial Image Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace text-only editorial cards with disclosed Gemini-created magazine illustrations and encode the workflow in the Bringissue Word manual and current Go Youn-jung/RESCENE article package.

**Architecture:** Keep verified source captures as evidence and add Gemini illustrations only for context, emotion, and explanatory transitions. The manual builder remains the single source of truth for the DOCX; a separate prompt pack controls the five generated illustrations for the current article.

**Tech Stack:** Python 3, python-docx, Pillow, pytest, Gemini web image generation, LibreOffice DOCX rendering

---

### Task 1: Add regression coverage for the manual rule

**Files:**
- Create: `tests/test_bringissue_gemini_editorial_manual.py`
- Modify: `scripts/create_bringissue_manual.py`

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run: `pytest tests/test_bringissue_gemini_editorial_manual.py -q`

Expected: FAIL because the Gemini editorial phrases are not yet in the builder.

- [ ] **Step 3: Add the manual content**

Add a new `6.3 제미나이 매거진 일러스트` section after the clean-capture section. Include role separation, 16:9/1200×675 requirements, prohibited styles, the disclosure caption, and the full reusable prompt template. Update the body template, copyright section, and final checklist with the same terms.

- [ ] **Step 4: Run the focused test and verify it passes**

Run: `pytest tests/test_bringissue_gemini_editorial_manual.py -q`

Expected: `1 passed`.

### Task 2: Create the current article's Gemini prompt pack

**Files:**
- Create: `blog-assets/2026-08-24-goyounjung-rescene-gift/gemini-prompts.md`
- Modify: `blog-assets/2026-08-24-goyounjung-rescene-gift/post-draft.md`

- [ ] **Step 1: Write five production prompts**

Create exact 16:9 magazine-illustration prompts for:

1. A large mysterious delivery arriving at a new idol dorm entrance.
2. A full-length mirror and stool placed naturally in a bright new dorm.
3. A junior idol reacting warmly to a thoughtful senior's gift, shown from behind.
4. Two non-identifiable female entertainers becoming closer through a warm phone conversation.
5. Fan admiration growing into a supportive senior-junior relationship, expressed symbolically.

Every prompt must forbid text, logos, watermarks, YouTube UI, photorealistic news imagery, and direct copying of a real person's face.

- [ ] **Step 2: Replace the card references in the article**

Remove `card-02.jpg` through `card-10.jpg` references. Insert `gemini-01.jpg` through `gemini-05.jpg` only in interpretation or context sections and add the caption `AI로 제작한 이해용 이미지입니다.` below every generated image.

- [ ] **Step 3: Verify the draft structure**

Run a script that asserts there are no `card-` references, exactly five `gemini-` references, five disclosure captions, four `<mark>` tags, and valid source links.

Expected: all assertions pass.

### Task 3: Generate and inspect the five illustrations

**Files:**
- Create: `blog-assets/2026-08-24-goyounjung-rescene-gift/gemini-01.jpg`
- Create: `blog-assets/2026-08-24-goyounjung-rescene-gift/gemini-02.jpg`
- Create: `blog-assets/2026-08-24-goyounjung-rescene-gift/gemini-03.jpg`
- Create: `blog-assets/2026-08-24-goyounjung-rescene-gift/gemini-04.jpg`
- Create: `blog-assets/2026-08-24-goyounjung-rescene-gift/gemini-05.jpg`

- [ ] **Step 1: Generate each image from its locked prompt**

Use Gemini image generation without adding any names or reference portraits. Download each result to the exact path above.

- [ ] **Step 2: Normalize delivery dimensions**

Crop or letterbox each output to 1200×675 or larger while preserving the focal subject and keeping all images free from text.

- [ ] **Step 3: Visually inspect all five images**

Reject and regenerate any image with text artifacts, logos, malformed hands/furniture, copied-looking celebrity faces, repeated composition, or weak 16:9 framing.

### Task 4: Rebuild and visually verify the Word manual

**Files:**
- Modify: `blog/manuals/브링이슈_유튜브_콘텐츠_운영_매뉴얼_v1.0.docx`
- Create/refresh QA: `blog/manuals/_qa_gemini/`

- [ ] **Step 1: Mark the document edit operation**

Run the bundled `mark_artifact_operation_started.mjs` with `--operation-kind edit --expected-output-count 1 --output-format docx`.

- [ ] **Step 2: Rebuild the DOCX**

Run: `python scripts/create_bringissue_manual.py`

Expected: the manual DOCX is regenerated successfully.

- [ ] **Step 3: Render the DOCX to page PNGs**

Run the bundled `render_docx.py` into `blog/manuals/_qa_gemini/`.

Expected: one PNG for every Word page and no conversion error.

- [ ] **Step 4: Inspect every rendered page**

Check 100% zoom for clipped text, broken tables, missing Korean glyphs, crowded callouts, and page-break gaps. Fix the builder and rerender if any defect appears.

### Task 5: Run final verification

**Files:**
- Test: `tests/test_bringissue_gemini_editorial_manual.py`
- Test: existing Bringissue tests under `tests/`

- [ ] **Step 1: Run the new regression test**

Run: `pytest tests/test_bringissue_gemini_editorial_manual.py -q`

Expected: PASS.

- [ ] **Step 2: Run existing Bringissue tests**

Run: `pytest tests/test_bringissue_* -q`

Expected: all tests pass with zero failures.

- [ ] **Step 3: Audit the article assets**

Verify `cover.jpg`, `community-original.jpg`, and `gemini-01.jpg` through `gemini-05.jpg` exist; each generated image is at least 1200×675; the draft contains exactly four highlights and five AI disclosures.

- [ ] **Step 4: Commit only scoped files**

Stage the new test, builder changes, prompt pack, draft, five generated images, and regenerated DOCX. Preserve unrelated dirty-worktree changes.
