# 2026 추석 기차표 블로그 글 제작 실행 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 코레일 공식 자료와 실제 예매 화면을 기반으로 2026 추석 기차표 예매 준비 글 한 편을 네이버 발행 직전 상태로 만든다.

**Architecture:** 공식 출처에서 일정과 절차를 검증하고, 재사용 가능한 공식 화면과 자체 설명 카드를 구분해 자산 원장을 만든다. 검증된 사실만 브리프와 본문에 넣고 자동 검수 후 사용자에게 원고와 이미지 배치를 보여준다.

**Tech Stack:** 웹 공식자료, Markdown, YAML, 네이버 블로그 편집 매뉴얼, 브링이슈 원고 검증 스크립트

---

### Task 1: 공식 일정과 절차 검증

**Files:**
- Create: `blog/briefs/2026-08-23-chuseok-train-ticket.yaml`

- [x] 코레일·정부·철도 운영기관 공식 페이지에서 2026 추석 승차권 예매 일정, 대상 열차, 예매 방법과 결제 기한을 확인한다.
- [x] 공식 발표가 없는 항목은 `확인 필요`로 기록하고 제목에서 숫자나 확정 표현을 제거한다.
- [x] 브리프에 확인일, 공식 URL, 독자, 검색 의도, 단일 CTA와 이미지 역할을 기록한다.
- [x] `validate_brief.py`를 실행해 승인 상태를 확인한다.

### Task 2: 실제 화면 기반 이미지 자산 구성

**Files:**
- Create: `blog/assets/2026-08-23-chuseok-train-ticket/`
- Create: `blog/assets/2026-08-23-chuseok-train-ticket/image-ledger.md`

- [x] 코레일 공식 안내와 예매 시작 화면 중 본문 설명에 필요한 화면만 확보한다.
- [x] 뉴스·블로그 사진은 재사용 권리가 확인되는 경우에만 저장하고, 불명확하면 링크 참고로만 기록한다.
- [x] 실제 화면으로 설명할 수 없는 비교 정보는 출처가 적힌 자체 설명 카드로 제작한다.
- [x] 모든 로컬 이미지를 직접 열어 보이는 사실, 출처, AI 여부, 가림 필요 여부를 원장에 기록한다.

### Task 3: 네이버용 최종 원고 작성

**Files:**
- Create: `blog/2026-08-23-chuseok-train-ticket.md`

- [x] 제목 후보 12개를 만든 뒤 약속을 실제로 해결하는 상위 3개와 추천 1개를 선정한다.
- [x] `그림 → 설명 → 해설` 흐름, 의미 단위 여백, 굵게·밑줄·이모티콘·노란 형광펜 표시를 적용한다.
- [x] 예매 전 준비, 실제 예매 순서, 실패하기 쉬운 지점, 결제 확인까지 독자의 행동 순서로 작성한다.
- [x] 썸네일 문구 3개, 이미지 순서와 캡션, 태그, 공식 출처, 확인 필요 항목을 포함한 15개 발행 묶음을 완성한다.

### Task 4: 사실·형식 검수

**Files:**
- Modify: `blog/2026-08-23-chuseok-train-ticket.md`

- [x] `validate_draft.py`를 기본 키워드 `2026 추석 기차표 예매`로 실행한다.
- [x] 제목의 숫자, 일정, 요금과 본문 출처를 대조한다.
- [x] 이미지 중복, 불필요한 UI, 개인정보, 저작권 오인, 과도한 키워드 반복을 확인한다.
- [ ] 오류가 0개인 원고와 이미지 미리보기를 사용자에게 전달하고 공개 발행 승인을 기다린다.
