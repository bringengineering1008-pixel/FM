# 브링이슈 하이브리드 이미지 체계 실행 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 첫 추석 기차표 글에 제미나이 이해 이미지 세 장을 추가하고 브링이슈 Word 매뉴얼을 하이브리드 이미지 체계로 최신화한다.

**Architecture:** 제미나이에서 16:9 에디토리얼 일러스트를 생성해 글별 자산 폴더에 저장하고 이미지 원장과 본문 배치를 함께 갱신한다. 매뉴얼 생성 원본을 수정해 DOCX를 재생성한 뒤 페이지 이미지로 렌더링하여 전 페이지를 검수한다.

**Tech Stack:** Google Gemini 웹, Markdown, Python DOCX 생성기, LibreOffice 렌더러

---

### Task 1: 제미나이 이미지 생성

**Files:**
- Create: `blog/assets/2026-08-23-chuseok-train-ticket/gemini-family-planning.png`
- Create: `blog/assets/2026-08-23-chuseok-train-ticket/gemini-countdown.png`
- Create: `blog/assets/2026-08-23-chuseok-train-ticket/gemini-payment-calendar.png`

- [ ] 제미나이 웹에서 한국 매거진형 16:9 이미지 3장을 각각 생성한다.
- [ ] 글자·로고·워터마크·실제 UI·실존 인물 얼굴이 없는지 육안으로 확인한다.
- [ ] 이미지가 1200×675 이상인지 확인하고 글별 자산 폴더에 저장한다.

### Task 2: 첫 글과 이미지 원장 갱신

**Files:**
- Modify: `blog/2026-08-23-chuseok-train-ticket.md`
- Modify: `blog/assets/2026-08-23-chuseok-train-ticket/image-ledger.md`
- Modify: `blog/briefs/2026-08-23-chuseok-train-ticket.yaml`

- [ ] 실제 자료와 제미나이 이미지가 교차하도록 본문 위치를 지정한다.
- [ ] 모든 제미나이 이미지에 AI 고지 캡션을 넣는다.
- [ ] 이미지 원장에 생성 도구, 프롬프트 요약, 역할과 금지사항 검수 결과를 기록한다.
- [ ] 브리프 사진 항목에 AI 이미지 세 장을 추가하고 다시 검증한다.

### Task 3: Word 매뉴얼 최신화

**Files:**
- Modify: `scripts/create_bringissue_manual.py`
- Modify: `blog/manuals/브링이슈_유튜브_콘텐츠_운영_매뉴얼_v1.0.docx`

- [ ] 이미지 체계 항목에 50·30·20 기본 비율을 추가한다.
- [ ] 실제 자료와 AI 이미지의 고정 교차 순서를 일반 정보형까지 확장한다.
- [ ] 추석 기차표 글의 이미지 배치 예시를 추가한다.
- [ ] DOCX를 재생성하고 전 페이지를 PNG로 렌더링한다.
- [ ] 모든 페이지에서 글자 깨짐, 잘림, 겹침과 빈 페이지를 확인하고 수정한다.

### Task 4: 최종 검수

**Files:**
- Verify: `blog/2026-08-23-chuseok-train-ticket.md`
- Verify: `blog/manuals/브링이슈_유튜브_콘텐츠_운영_매뉴얼_v1.0.docx`

- [ ] 실제 자료와 AI 이미지 역할이 혼동되지 않는지 확인한다.
- [ ] 생성 이미지 세 장과 대표 이미지를 사용자에게 보여준다.
- [ ] 사용자의 발행 승인을 받기 전에는 네이버 공개 발행을 진행하지 않는다.
