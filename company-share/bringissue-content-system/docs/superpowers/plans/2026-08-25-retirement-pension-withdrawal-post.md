# 퇴직연금 수령방법 첫 게시물 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 공식 자료와 실제 화면을 근거로 `퇴직연금 수령방법: 일시금과 연금의 차이` 네이버 블로그 완성 원고와 6~8개의 시각자료를 제작한다.

**Architecture:** 사실 원장과 게시용 원고를 분리하고, 공식 화면은 원본 증거로 보존한 뒤 개인정보 없는 관련 영역만 게시용으로 사용한다. 표지·비교표·절차도·주의 카드·체크리스트는 동일한 브링이슈 디자인 토큰으로 자체 제작하며 모든 변동 정보에 출처와 확인일을 연결한다.

**Tech Stack:** Markdown, YAML, HTML/CSS 기반 이미지 제작, 공식 기관 웹 자료, 네이버 모바일 형식 검수

---

### Task 1: 공식 근거와 글 브리프 확정

**Files:**
- Create: `blog/briefs/2026-08-25-retirement-pension-withdrawal.yaml`
- Create: `blog/assets/2026-08-25-retirement-pension-withdrawal/source-ledger.md`

- [ ] **Step 1:** 고용노동부·금융감독원·국세청 등 공식 출처에서 수령 절차, 일시금/연금 요건, 과세 차이를 확인한다.
- [ ] **Step 2:** 변동 가능 사실마다 원문 URL과 2026-08-25 확인일을 기록한다.
- [ ] **Step 3:** 개인별 판단이 필요한 항목과 일반적으로 설명 가능한 항목을 분리한다.
- [ ] **Step 4:** 독자·상황·불안·약속·CTA가 포함된 YAML 브리프를 작성한다.

### Task 2: 실제 화면과 자체 제작 시각자료 구성

**Files:**
- Create: `blog/assets/2026-08-25-retirement-pension-withdrawal/official-screen-01.png`
- Create: `blog/assets/2026-08-25-retirement-pension-withdrawal/cover.png`
- Create: `blog/assets/2026-08-25-retirement-pension-withdrawal/comparison.png`
- Create: `blog/assets/2026-08-25-retirement-pension-withdrawal/steps.png`
- Create: `blog/assets/2026-08-25-retirement-pension-withdrawal/warning.png`
- Create: `blog/assets/2026-08-25-retirement-pension-withdrawal/checklist.png`

- [ ] **Step 1:** 공식 안내 화면에서 글의 핵심 근거가 보이는 영역을 확보한다.
- [ ] **Step 2:** 개인정보와 계좌·문서 식별정보가 없는지 검사하고 필요한 부분을 가린다.
- [ ] **Step 3:** 40대 이상 모바일 독자가 읽기 쉬운 큰 글자와 높은 대비로 자체 제작 이미지 5개를 만든다.
- [ ] **Step 4:** 모든 이미지에 근거 기관 또는 `브링이슈 정리`, 확인일을 표시한다.
- [ ] **Step 5:** 각 이미지를 실제로 열어 글자 잘림, 오탈자, 출처 표시, 모바일 가독성을 확인한다.

### Task 3: 게시용 원고 작성과 검수

**Files:**
- Create: `blog/2026-08-25-retirement-pension-withdrawal.md`

- [ ] **Step 1:** 검색 상황 도입, 3줄 결론, 공식 기준, 실행 순서, 비교표, 예외, 체크리스트 순으로 초안을 작성한다.
- [ ] **Step 2:** 결론과 주의사항에만 형광펜 2~3개를 지정하고 이미지 위치와 자연스러운 캡션을 배치한다.
- [ ] **Step 3:** 제목의 약속을 본문이 직접 해결하는지, 공식 근거 없는 금액·세율·보장 표현이 없는지 검수한다.
- [ ] **Step 4:** AI식 반복 문장, 유튜브 캡처, 기계적 이미지 설명 문구를 제거한다.
- [ ] **Step 5:** 최종 제목 후보 3개, 추천 제목 1개, 태그, 관련 글 확장안과 확인 필요 항목을 함께 제공한다.

### Task 4: 사용자 검수용 결과 묶음 전달

**Files:**
- Modify: `blog/2026-08-25-retirement-pension-withdrawal.md`

- [ ] **Step 1:** 대표 이미지와 핵심 비교표를 대화에 표시한다.
- [ ] **Step 2:** 완성 원고 경로와 시각자료 폴더를 전달한다.
- [ ] **Step 3:** 사용자 최종 승인 전에는 네이버에 공개 발행하지 않는다.
- [ ] **Step 4:** 승인 후 네이버 모바일 미리보기와 공개 페이지를 다시 확인한다.
