# BringIssue Action Guide Template Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 현재 연금저축·IRP 글을 행동 안내형으로 재편집하고 같은 품질을 반복할 수 있는 브링이슈 템플릿을 만든다.

**Architecture:** 로컬 원고·브리프·공식 캡처를 기준 데이터로 삼고, 템플릿은 내용 구조와 네이버 편집 규칙을 분리해 기록한다. 공개 글에서는 관련 없는 이미지를 제거하고 국세청 핵심 화면과 네이버 자체 표를 중심으로 독자의 확인 동선을 구성한다.

**Tech Stack:** Markdown, YAML, 네이버 스마트에디터, Chrome 브라우저

---

### Task 1: 재사용 템플릿 작성

**Files:**
- Create: `blog/templates/bringissue-action-guide-template.md`

- [ ] **Step 1:** 제목·도입·결론·실제 화면·네이버 표·상황별 판단·예외·체크리스트·CTA의 10개 블록을 작성한다.
- [ ] **Step 2:** 각 블록에 필수·조건부·금지 규칙을 명시한다.
- [ ] **Step 3:** 이미지 수를 고정하지 않고 각 이미지의 역할·확인 포인트·캡션을 기록하는 표를 추가한다.
- [ ] **Step 4:** PC·모바일 공개 화면 QA 체크리스트를 추가한다.

### Task 2: 연금저축·IRP 원고 정리

**Files:**
- Modify: `blog/2026-08-26-pension-savings-irp-tax-credit.md`
- Modify: `blog/briefs/2026-08-26-pension-savings-irp-tax-credit.yaml`

- [ ] **Step 1:** 독자의 질문과 한 문장 결론을 도입 20% 안에 배치한다.
- [ ] **Step 2:** 연금저축·IRP 조합과 공제액 표를 네이버 자체 표로 옮길 수 있게 단순화한다.
- [ ] **Step 3:** DB·DC·퇴직연금 수령 등 이번 질문과 직접 관계없는 자료를 제거한다.
- [ ] **Step 4:** 국세청 핵심 표와 행동 문장만 사진 계획에 남긴다.
- [ ] **Step 5:** 저장 CTA 하나만 남긴다.

### Task 3: 로컬 검증

**Files:**
- Test: `blog/briefs/2026-08-26-pension-savings-irp-tax-credit.yaml`
- Test: `blog/2026-08-26-pension-savings-irp-tax-credit.md`

- [ ] **Step 1:** `validate_brief.py`를 실행해 승인 상태와 경고를 확인한다.
- [ ] **Step 2:** `validate_draft.py --keyword "연금저축 IRP 세액공제"`를 실행한다.
- [ ] **Step 3:** 원고에서 문자 구분선, 기계적인 이미지 설명, 관련 없는 이미지 참조, 미해결 확인 필요를 검색한다.

### Task 4: 네이버 공개 글 재편집

**Files:**
- Browser target: `https://blog.naver.com/bringissue/224391350168`

- [ ] **Step 1:** 공개 글의 기존 카테고리·주제·태그·공개 범위를 기록한다.
- [ ] **Step 2:** 관련 없는 고용노동부·법령 이미지 세 장을 제거한다.
- [ ] **Step 3:** 국세청 핵심 화면 한 장을 공제율 설명 뒤에 배치한다.
- [ ] **Step 4:** 네이버 자체 표 두 개, 구분선, 소제목 이모티콘, 형광펜 2~3곳, 밑줄 2~3곳을 적용한다.
- [ ] **Step 5:** 도입만 가운데 정렬하고 긴 설명·표·체크리스트는 왼쪽 정렬한다.
- [ ] **Step 6:** 사용자 승인 범위에 따라 수정본을 발행한다.

### Task 5: 공개 화면 검수

**Files:**
- Browser target: `https://blog.naver.com/bringissue/224391350168`

- [ ] **Step 1:** 제목, 표 두 개, 이미지, 형광펜, 밑줄, 구분선을 확인한다.
- [ ] **Step 2:** 이미지가 문장을 끊거나 글자가 잘리지 않는지 확인한다.
- [ ] **Step 3:** 중복문장, 문자 구분선, 출처 덤프, 관련 없는 이미지가 없는지 확인한다.
- [ ] **Step 4:** 공개 URL을 결과와 함께 보고한다.
