# Bringissue Validated 40·40·20 Content Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 검증된 수익형 블로그의 40·40·20 구조를 브링이슈 신규 글 10편에 적용하고, 공식 출처와 실제 화면을 갖춘 발행 묶음 및 성과 측정 체계를 만든다.

**Architecture:** 주제 원장, 개별 브리프, 원고·자산 폴더, 성과 원장을 분리한다. 후보는 실제 검색 수요와 공식 자료 존재 여부를 통과해야 하며, 각 글은 브리프 검증 후 원고를 만들고 최종 승인 이후에만 발행한다.

**Tech Stack:** Markdown, YAML, CSV, 네이버 블로그 편집기, 공식 웹사이트 실제 캡처, `validate_brief.py`, `validate_draft.py`

---

## 파일 구조

- Create: `blog/batches/2026-08-26-bringissue-40-40-20-pilot.md` — 10편의 비율, 우선순위, 검색 의도, 출처와 캡처 계획 원장
- Create: `blog/briefs/2026-08-26-voice-phishing-account-freeze.yaml` — 첫 글의 검증 사실과 이미지 계획; 후속 글도 날짜와 영문 주제명을 사용
- Create: `blog/2026-08-26-voice-phishing-account-freeze.md` — 첫 번째 승인 가능 원고; 후속 글도 같은 명명 규칙을 사용
- Create: `blog/assets/2026-08-26-voice-phishing-account-freeze/` — 첫 글의 실제 공식 화면과 검수 이미지
- Modify: `blog/automation/topic-cooldown.csv` — 중복 주제와 재발행 가능 시점
- Modify: `blog/automation/performance-ledger.csv` — 공개 후 72시간·7일 성과

### Task 1: 첫 10편 후보 조사와 비율 확정

**Files:**
- Create: `blog/batches/2026-08-26-bringissue-40-40-20-pilot.md`
- Read: `blog/automation/performance-ledger.csv`
- Read: `blog/automation/topic-cooldown.csv`
- Read: `blog/automation/alerts.md`

- [ ] **Step 1: 기존 공개 글과 예약 글의 중복 주제를 확인한다**

최근 글의 핵심 검색어, 주제 축, 공개 여부를 정리하고 동일 검색 의도의 후보를 제외한다.

- [ ] **Step 2: 고단가 후보를 실제 조사한다**

퇴직금·연금·보험·금융 피해에서 8개 이상을 수집하고 검색 의도, 공식 출처, 독자 행동, 정확성 위험을 기록한다.

- [ ] **Step 3: 생활 문제 후보를 실제 조사한다**

환불·고객센터·앱 오류·은행 이용에서 8개 이상을 수집하고 동일 항목을 기록한다.

- [ ] **Step 4: 실시간 이슈 후보를 실제 조사한다**

당일 관심 소재 5개 이상을 확인하고 사생활·단순 기사 요약·자료 부족 후보를 제외한다.

- [ ] **Step 5: 4·4·2 최종 후보를 확정한다**

각 후보를 현재 관심 20, 검색 의도 15, 독자 가치 15, 클릭 15, 근거·이미지 10, 차별성 10, 확장성 5, 비율 보정 10으로 평가하고 75점 이상만 남긴다.

- [ ] **Step 6: 파일을 검수한다**

Run: `rg -n "확인 필요" blog/batches/2026-08-26-bringissue-40-40-20-pilot.md`

Expected: 결과 없음

- [ ] **Step 7: 커밋한다**

```powershell
git add blog/batches/2026-08-26-bringissue-40-40-20-pilot.md
git commit -m "content: select bringissue 40-40-20 pilot topics"
```

### Task 2: 제목·검색 의도·캡처 동선 설계

**Files:**
- Modify: `blog/batches/2026-08-26-bringissue-40-40-20-pilot.md`
- Modify: `blog/automation/topic-cooldown.csv`

- [ ] **Step 1: 글별 제목 후보 3개를 작성한다**

`대상 키워드 + 독자가 처한 문제 + 바로 얻는 답`을 사용하고 과장 수익, 근거 없는 숫자와 순위 보장을 제외한다.

- [ ] **Step 2: 글별 한 문장 약속을 확정한다**

독자가 검색 직후 해야 할 행동이나 판단을 한 문장으로 적는다.

- [ ] **Step 3: 글별 공식 출처를 지정한다**

기관명, 실제 페이지 URL, 확인할 사실, 발행 당일 재확인 항목을 기록한다.

- [ ] **Step 4: 글별 실제 캡처 순서를 지정한다**

첫 화면부터 결과 확인 화면까지 사용자 동선 순서로 5~10개 화면을 적고, 개인정보 가림 대상을 표시한다.

- [ ] **Step 5: 쿨다운 원장에 10개 핵심 키워드를 추가한다**

동일 검색 의도 글이 연달아 발행되지 않도록 재사용 가능 시점을 기록한다.

- [ ] **Step 6: 변경 내용을 검수한다**

Run: `git diff --check -- blog/batches/2026-08-26-bringissue-40-40-20-pilot.md blog/automation/topic-cooldown.csv`

Expected: 출력 없음

- [ ] **Step 7: 커밋한다**

```powershell
git add blog/batches/2026-08-26-bringissue-40-40-20-pilot.md blog/automation/topic-cooldown.csv
git commit -m "content: define pilot titles sources and capture routes"
```

### Task 3: 우선순위 1번 보이스피싱 지급정지 브리프 작성과 검증

**Files:**
- Create: `blog/briefs/2026-08-26-voice-phishing-account-freeze.yaml`
- Read: `C:/Users/user/.codex/skills/writing-bringcare-naver-blog/assets/naver-post-template.md`
- Test: `C:/Users/user/.codex/skills/writing-bringcare-naver-blog/scripts/validate_brief.py`

- [ ] **Step 1: 공식 페이지를 발행일 기준으로 확인한다**

확인한 사실마다 URL, 확인일, 게시 가능 여부를 기록한다. 결론을 바꾸는 정보가 확인되지 않으면 브리프를 `검증대기`로 둔다.

- [ ] **Step 2: 실제 화면을 사용자 동선에 따라 캡처한다**

불필요한 탭과 브라우저 영역을 줄이고 메뉴명과 버튼이 읽히도록 저장한다.

- [ ] **Step 3: 모든 캡처를 직접 검사한다**

이미지마다 보이는 사실, 본문 역할, 캡션, 가림 대상을 브리프에 기록한다.

- [ ] **Step 4: 브리프를 작성한다**

`request_mode: 키워드발굴`, `distribution_goal: 혼합`, `content_role.primary: 유입`, `post_type: 검색정보`, `content_engine: traffic`을 기본으로 하되 실제 주제에 따라 근거 있게 조정한다.

- [ ] **Step 5: 브리프 검증을 실행한다**

Run: `python C:/Users/user/.codex/skills/writing-bringcare-naver-blog/scripts/validate_brief.py blog/briefs/2026-08-26-voice-phishing-account-freeze.yaml`

Expected: JSON 상태가 `작성승인`이고 오류가 0개

- [ ] **Step 6: 커밋한다**

```powershell
git add blog/briefs/2026-08-26-voice-phishing-account-freeze.yaml blog/assets/2026-08-26-voice-phishing-account-freeze
git commit -m "content: verify first 40-40-20 pilot brief"
```

### Task 4: 우선순위 1번 보이스피싱 지급정지 원고와 편집 묶음 제작

**Files:**
- Create: `blog/2026-08-26-voice-phishing-account-freeze.md`
- Read: `docs/superpowers/specs/2026-08-26-bringissue-balanced-editorial-format-design.md`
- Test: `C:/Users/user/.codex/skills/writing-bringcare-naver-blog/scripts/validate_draft.py`

- [ ] **Step 1: 검증된 사실만으로 원고를 작성한다**

도입 상황, 결론, 공식 화면, 단계별 절차, 예외, 체크리스트, 관련 글 행동 순서를 사용한다.

- [ ] **Step 2: B 균형형 편집 지시를 넣는다**

의미 단위 빈 문단, 소제목 이모티콘 한 개, 구분선 3~5개, 형광펜 2~3개, 행동 문장 밑줄을 표시한다.

- [ ] **Step 3: 이미지 배치를 확정한다**

각 이미지 앞에는 확인할 내용을, 뒤에는 사용자가 다음에 할 행동을 작성한다. 자동 생성형 그림 설명은 넣지 않는다.

- [ ] **Step 4: 원고 검증을 실행한다**

Run: `python C:/Users/user/.codex/skills/writing-bringcare-naver-blog/scripts/validate_draft.py blog/2026-08-26-voice-phishing-account-freeze.md --keyword "보이스피싱 지급정지"`

Expected: 오류 0개, 미해결 `확인 필요` 0개

- [ ] **Step 5: 모바일 읽기 흐름과 캡처 가독성을 확인한다**

제목 약속이 본문에서 답변됐는지, 화면의 메뉴와 글자가 읽히는지, 개인정보가 남지 않았는지 검사한다.

- [ ] **Step 6: 커밋한다**

```powershell
git add blog/2026-08-26-voice-phishing-account-freeze.md blog/assets/2026-08-26-voice-phishing-account-freeze
git commit -m "content: draft first validated 40-40-20 post"
```

### Task 5: 승인 후 발행과 성과 기록

**Files:**
- Modify: `blog/automation/performance-ledger.csv`
- Modify: `blog/automation/topic-cooldown.csv`

- [ ] **Step 1: 사용자에게 최종 원고와 캡처를 보여준다**

제목, 본문, 이미지 순서, 공식 출처, 공개 시각을 한 번에 검토할 수 있게 제시한다.

- [ ] **Step 2: 명시적 최종 승인을 확인한다**

승인 전에는 네이버의 공개 또는 예약 버튼을 누르지 않는다.

- [ ] **Step 3: 네이버 블로그에 편집·발행한다**

카테고리, 공개 범위, 검색 허용, 태그, 발행 시각을 확인한 뒤 최종 버튼을 누른다.

- [ ] **Step 4: 공개 URL을 직접 확인한다**

공개 페이지에서 제목, 소제목, 이미지, 강조, 공식 출처와 공개 상태를 검사한다.

- [ ] **Step 5: 공개 글만 텔레그램으로 전송한다**

예약·비공개 글은 보내지 않고 공개 `logNo`를 post-id로 사용한다.

- [ ] **Step 6: 성과 측정 행을 추가한다**

72시간·7일 수집 예정 시각과 실험 분류를 `performance-ledger.csv`에 기록한다.

- [ ] **Step 7: 커밋한다**

```powershell
git add blog/automation/performance-ledger.csv blog/automation/topic-cooldown.csv
git commit -m "content: register first pilot publication metrics"
```

## 완료 검증

- 10개 후보가 정확히 고단가 4, 생활 문제 4, 실시간 이슈 2인지 확인한다.
- 10개 모두 제목, 한 문장 약속, 공식 URL, 캡처 순서, 가림 대상이 있는지 확인한다.
- 우선순위 1번 브리프 검증 결과가 작성승인인지 확인한다.
- 우선순위 1번 원고 검증 결과에 오류와 미해결 항목이 없는지 확인한다.
- 발행한 경우 실제 공개 URL과 텔레그램 전송 결과를 확인한다.
