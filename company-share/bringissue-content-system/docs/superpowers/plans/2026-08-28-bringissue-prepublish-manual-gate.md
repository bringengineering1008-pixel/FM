# BringIssue Prepublish Manual Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 브링이슈 글을 발행하기 직전에 확정된 모든 매뉴얼을 다시 읽고 대조하지 않으면 발행하지 못하도록 영구 규칙과 게시물 체크리스트에 고정한다.

**Architecture:** 전역 행동 규칙은 `C:/Users/user/.codex/AGENTS.md`에 두고, 실제 게시물 검수 항목은 브링이슈 행동 안내형 템플릿과 현재 24편 발행 관리표에 함께 둔다. 세 위치에 같은 의미의 강제 게이트를 배치하고, 문자열 검증으로 누락 여부를 확인한다.

**Tech Stack:** Markdown 운영 문서, PowerShell 문자열 검증, Git

---

### Task 1: 영구 운영 명령 추가

**Files:**
- Modify: `C:/Users/user/.codex/AGENTS.md`

- [x] **Step 1: 기존 명령 확인**

Run: `Get-Content -Raw C:/Users/user/.codex/AGENTS.md`

Expected: 현재 브라우저 계정 운영 규칙이 출력된다.

- [x] **Step 2: 발행 직전 매뉴얼 재확인 강제 규칙 추가**

추가할 내용:

```markdown
# 브링이슈 발행 직전 강제 확인 규칙

- 브링이슈 글을 예약발행하거나 즉시발행하기 직전에, 지금까지 사용자와 확정한 모든 브링이슈 작성·시각자료·네이버 편집·검수 매뉴얼을 현재 파일에서 다시 읽고 해당 원고·이미지·서식과 대조한다.
- 이전에 읽었다는 기억이나 과거 검수 결과로 재확인을 대신하지 않는다.
- 한 항목이라도 불일치하거나 재확인 근거가 없으면 발행 버튼을 누르지 않고 먼저 수정한다.
- 공식 사이트·앱의 실제 화면은 공식 근거로 유지하며, AI·Google Flow 이미지는 공식 증거를 대체하지 않는다.
- 발행 결과 보고에는 매뉴얼 재확인 여부와 수정한 불일치 항목을 포함한다.
```

- [x] **Step 3: 영구 명령 검증**

Run: `Select-String -Path C:/Users/user/.codex/AGENTS.md -Pattern '브링이슈 발행 직전 강제 확인 규칙','이전 검수 결과로 재확인을 대신하지 않는다','발행 버튼을 누르지 않고 먼저 수정한다'`

Expected: 세 문구가 모두 한 번 이상 출력된다.

### Task 2: 게시물 템플릿과 현재 발행표에 게이트 반영

**Files:**
- Modify: `blog/templates/bringissue-action-guide-template.md`
- Modify: `blog/batches/2026-08-27-bringissue-24-posts.md`

- [x] **Step 1: 템플릿 공개 전 QA에 강제 게이트 추가**

추가할 내용:

```markdown
## 발행 직전 강제 게이트

- [ ] 발행 버튼을 누르기 직전에 확정된 모든 브링이슈 매뉴얼을 현재 파일에서 다시 읽었다.
- [ ] 해당 원고·공식 캡처·네이버 표·정렬·여백·구분선·형광펜·밑줄·이모티콘을 매뉴얼과 다시 대조했다.
- [ ] 불일치 항목을 먼저 수정했고 재검수 결과를 발행 관리표 또는 브리프에 기록했다.
- [ ] 위 세 항목 중 하나라도 완료되지 않으면 예약발행·즉시발행 버튼을 누르지 않는다.
```

- [x] **Step 2: 24편 발행 규칙에 같은 게이트 추가**

추가할 내용:

```markdown
- 각 글의 발행 버튼을 누르기 직전에 확정된 브링이슈 매뉴얼 전체를 다시 읽고 원고·이미지·서식을 대조한다.
- 재확인 기록이 없거나 불일치가 남아 있으면 발행하지 않는다.
```

- [x] **Step 3: 두 파일 검증**

Run: `Select-String -Path blog/templates/bringissue-action-guide-template.md,blog/batches/2026-08-27-bringissue-24-posts.md -Pattern '발행 직전 강제 게이트','발행 버튼을 누르기 직전에','재확인 기록이 없거나 불일치가 남아 있으면 발행하지 않는다'`

Expected: 템플릿과 발행표에서 강제 게이트 문구가 출력된다.

- [x] **Step 4: 변경 범위 확인**

Run: `git diff -- blog/templates/bringissue-action-guide-template.md blog/batches/2026-08-27-bringissue-24-posts.md`

Expected: 기존 콘텐츠를 삭제하지 않고 강제 게이트 문구만 추가된다.
