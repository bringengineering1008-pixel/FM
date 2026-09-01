# 브링이슈 유튜브 홈피드형 5편 일괄 제작 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Execute this plan task-by-task in the current session. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 화제 유튜브 영상 5편을 무음 분석해 네이버 블로그 공개 발행 직전 상태까지 완성한다.

**Architecture:** 후보 조사, 전체 내용 분석, 이미지 자산 제작, 원고 검수, 네이버 편집기 입력을 글별 독립 단위로 반복한다. 각 글은 자체 자산 폴더와 초안 파일을 가지며 동일한 QA 기준을 통과한다.

**Tech Stack:** 웹 검색, yt-dlp, 로컬 음성 인식, ffmpeg 프레임 추출, 이미지 생성·편집, 네이버 스마트에디터

---

### Task 1: 후보 조사 및 5편 선정

**Files:**
- Create: `blog/batches/2026-08-21-bringissue-five-posts.md`

- [ ] 실시간 인기 영상 후보를 실제 검색한다.
- [ ] 화제성, 클릭 이유, 독자 가치, 이미지 준비도, 차별성을 평가한다.
- [ ] 저작권·사생활·안전 기준을 통과한 5편을 확정한다.

### Task 2: 영상 전체 무음 분석

**Files:**
- Create: `blog-assets/2026-08-21-<slug>/analysis.md`

- [ ] 영상 음원을 로컬 분석용으로 내려받되 재생하지 않는다.
- [ ] 전체 자막 또는 음성 인식 결과를 시간대별로 검토한다.
- [ ] 제목의 약속이 될 핵심 장면과 근거 시간대를 기록한다.

### Task 3: 대표 이미지와 장면 캡처 제작

**Files:**
- Create: `blog-assets/2026-08-21-<slug>/representative-thumbnail.png`
- Create: `blog-assets/2026-08-21-<slug>/scene-*.jpg`

- [ ] 핵심 인물·상황·짧은 문구가 보이는 대표 이미지를 만든다.
- [ ] 영상 UI가 없는 장면 캡처 8~10장을 추출한다.
- [ ] 모든 이미지를 직접 확인해 장면 설명과 순서를 확정한다.

### Task 4: 원고 작성 및 검수

**Files:**
- Create: `blog-assets/2026-08-21-<slug>/post-draft.md`

- [ ] 그림 다음에 해당 장면 설명이 바로 나오도록 본문을 작성한다.
- [ ] 이모지 소제목, 굵게, 밑줄, 빈 문단과 독자 질문을 적용한다.
- [ ] 원본 링크·채널·캡처 출처·태그를 넣는다.
- [ ] 제목-본문 일치, 사실성, 인용 길이, 이미지 중복을 검수한다.

### Task 5: 네이버 발행 직전 입력

**Files:**
- Create: `blog/.publish/2026-08-21-<slug>.json`

- [ ] `오늘 뜬 유튜브` 카테고리에 제목과 본문을 입력한다.
- [ ] 대표 이미지와 장면 이미지를 지정된 순서로 배치한다.
- [ ] 주제를 `스타·연예인`으로 지정하고 전체공개·검색·댓글·공감·공유 허용을 확인한다.
- [ ] 최종 공개 발행 버튼은 누르지 않고 다섯 글의 준비 상태를 기록한다.
