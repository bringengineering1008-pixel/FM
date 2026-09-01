# BringIssue 24-Post Series Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce, validate, visually prepare, and schedule 24 evidence-backed BringIssue Naver Blog posts across a five-calendar-day publishing window.

**Architecture:** A single schedule manifest controls topic order, publish times, source evidence, and draft paths. Each post has an independent brief, draft, and asset folder so official screenshots and validation results cannot leak across topics. Publishing happens only after draft validation, visual QA, account verification, and action-time confirmation.

**Tech Stack:** Markdown, YAML, CSV, Naver SmartEditor, official Korean government/service websites, `validate_brief.py`, `validate_draft.py`, Chrome browser control.

---

## File Map

- Create: `blog/batches/2026-08-27-bringissue-24-posts.md` — canonical 24-post schedule and status board.
- Create: `blog/batches/2026-08-27-bringissue-24-source-matrix.md` — official sources and required screenshots.
- Create: `blog/briefs/2026-08-27-pension-vs-irp-order.yaml`
- Create: `blog/briefs/2026-08-27-irp-300-tax-saving.yaml`
- Create: `blog/briefs/2026-08-27-pension-monthly-payment.yaml`
- Create: `blog/briefs/2026-08-27-pension-refund-difference.yaml`
- Create: `blog/briefs/2026-08-27-irp-early-withdrawal.yaml`
- Create: `blog/briefs/2026-08-27-pension-early-cancellation-tax.yaml`
- Create: `blog/briefs/2026-08-27-pension-fund-vs-insurance.yaml`
- Create: `blog/briefs/2026-08-27-irp-provider-transfer.yaml`
- Create: `blog/briefs/2026-08-27-isa-to-pension.yaml`
- Create: `blog/briefs/2026-08-27-pension-deduction-missing.yaml`
- Create: `blog/briefs/2026-08-27-pension-irp-investments.yaml`
- Create: `blog/briefs/2026-08-27-pension-plan-in-50s.yaml`
- Create: `blog/briefs/2026-08-27-voice-phishing-freeze.yaml`
- Create: `blog/briefs/2026-08-27-health-screening-fasting.yaml`
- Create: `blog/briefs/2026-08-27-dormant-deposit.yaml`
- Create: `blog/briefs/2026-08-27-telecom-refund.yaml`
- Create: `blog/briefs/2026-08-27-naverpay-refund.yaml`
- Create: `blog/briefs/2026-08-27-srt-refund.yaml`
- Create: `blog/briefs/2026-08-27-travel-insurance-baggage.yaml`
- Create: `blog/briefs/2026-08-27-early-old-age-pension.yaml`
- Create: `blog/briefs/2026-08-27-passport-renewal.yaml`
- Create: `blog/briefs/2026-08-27-kakaotalk-backup.yaml`
- Create: `blog/briefs/2026-08-27-travel-card-roaming-esim.yaml`
- Create: `blog/briefs/2026-08-27-health-screening-results.yaml`
- Create corresponding drafts at `blog/2026-08-27-<slug>.md`.
- Create corresponding screenshot folders at `blog/assets/2026-08-27-<slug>/`.

### Task 1: Build the Canonical Schedule

- [ ] **Step 1: Create the 24-row schedule board**

Record for every row: sequence, date, time, title, primary keyword, topic axis, brief path, draft path, source status, screenshot status, validation status, publish status, and public URL.

- [ ] **Step 2: Assign the dates and times**

Use this exact distribution:

```text
2026-08-27: 13:00, 17:00, 19:00, 21:00
2026-08-28: 09:00, 11:00, 13:00, 17:00, 19:00, 21:00
2026-08-29: 09:00, 11:00, 13:00, 17:00, 19:00, 21:00
2026-08-30: 09:00, 11:00, 13:00, 17:00, 19:00, 21:00
2026-08-31: 09:00, 11:00
```

- [ ] **Step 3: Verify no adjacent rows share the same topic axis**

Run:

```powershell
rg -n "연금|건강|여행|디지털|보안|환불" blog/batches/2026-08-27-bringissue-24-posts.md
```

Expected: adjacent rows alternate between pension/finance and life-problem axes.

- [ ] **Step 4: Commit the schedule**

```powershell
git add blog/batches/2026-08-27-bringissue-24-posts.md
git commit -m "Plan BringIssue 24-post publishing schedule"
```

### Task 2: Verify Official Sources and Screenshot Requirements

- [ ] **Step 1: Verify pension and tax sources**

Use the National Tax Service, Ministry of Employment and Labor, Financial Supervisory Service, National Pension Service, and official financial-company disclosure pages. Record the page title, URL, visible fact, verification date, and screenshot role in the source matrix.

- [ ] **Step 2: Verify life-problem sources**

Use the Financial Supervisory Service or police guidance for voice phishing, National Health Insurance Service or examination provider guidance for screening, Korea Federation of Banks/Seomin Finance resources for dormant deposits, SmartChoice for telecom refunds, Naver Pay Help, SR official refund rules, insurance policy wording, Ministry of Foreign Affairs for passports, and Kakao Help for backups.

- [ ] **Step 3: Reject weak evidence**

Do not use search snippets, reposted news summaries, unofficial blog screenshots, cropped pages without the relevant label, or YouTube frames from unofficial creators.

- [ ] **Step 4: Define each screenshot**

For every post, record the full-page context capture and any detail capture required for legibility. Specify the exact label, table row, button, or warning the reader must see.

- [ ] **Step 5: Commit the source matrix**

```powershell
git add blog/batches/2026-08-27-bringissue-24-source-matrix.md
git commit -m "Document official sources for BringIssue series"
```

### Task 3: Create and Validate 24 Briefs

- [ ] **Step 1: Write the pension-series briefs**

Set `request_mode: 키워드발굴`, `distribution_goal: 검색`, `content_role.primary: 유입`, `post_type: 검색정보`, `content_engine: traffic`, and `one_cta: 저장`. Each brief must contain at least one publishable official fact and one actual screenshot entry.

- [ ] **Step 2: Write the life-problem briefs**

Use the same traffic-post contract. Medical posts must state that they explain preparation or document-reading steps and do not diagnose or prescribe treatment.

- [ ] **Step 3: Validate every brief**

Run from `C:\Users\user\.codex\skills\writing-bringcare-naver-blog`:

```powershell
Get-ChildItem 'C:\Users\user\.codex\worktrees\7129\마케팅\blog\briefs\2026-08-27-*.yaml' | ForEach-Object { python scripts/validate_brief.py $_.FullName }
```

Expected: every result is `작성승인` or an explicitly justified traffic-post `수정후승인` caused only by the generic consultation-banner rule. No factual, safety, image, or privacy errors may remain.

- [ ] **Step 4: Commit the briefs**

```powershell
git add blog/briefs/2026-08-27-*.yaml
git commit -m "Add BringIssue 24-post briefs"
```

### Task 4: Draft Posts 1-6

- [ ] **Step 1: Write the six drafts scheduled first**

Create complete posts for pension-vs-IRP order, voice-phishing account freeze, IRP 300 tax saving, health-screening fasting, pension monthly payment, and dormant deposit claim.

- [ ] **Step 2: Apply the approved visual structure**

Use centered paragraphs, meaningful blank lines, 3-6 native separators, 2-3 yellow highlights, 2-3 underlines, emoji section headings, and native Naver table specifications.

- [ ] **Step 3: Validate the six drafts**

```powershell
python C:\Users\user\.codex\skills\writing-bringcare-naver-blog\scripts\validate_draft.py blog\2026-08-27-pension-vs-irp-order.md --keyword "연금저축 IRP 무엇부터"
python C:\Users\user\.codex\skills\writing-bringcare-naver-blog\scripts\validate_draft.py blog\2026-08-27-voice-phishing-freeze.md --keyword "보이스피싱 지급정지"
```

Repeat with the matching primary keyword for the remaining four drafts. Expected: no unresolved factual, privacy, image, or keyword errors.

- [ ] **Step 4: Commit posts 1-6**

```powershell
git add blog/2026-08-27-*.md blog/assets/2026-08-27-*
git commit -m "Draft first BringIssue series batch"
```

### Task 5: Draft Posts 7-12

- [ ] **Step 1: Write the next six drafts**

Cover pension refund difference, telecom refund, IRP early withdrawal, Naver Pay refund, pension cancellation tax, and SRT refund.

- [ ] **Step 2: Check cross-post duplication**

Each post must contain a unique lead question, unique comparison table, unique official screen, and a distinct final action. The hub post may be linked but not copied.

- [ ] **Step 3: Validate and commit**

Run `validate_draft.py` for each matching keyword, resolve every substantive warning, then commit as `Draft second BringIssue series batch`.

### Task 6: Draft Posts 13-18

- [ ] **Step 1: Write the next six drafts**

Cover pension fund vs insurance, travel-insurance baggage claim, IRP provider transfer, early old-age pension income check, ISA-to-pension transfer, and passport renewal.

- [ ] **Step 2: Verify comparison wording**

Product comparisons must discuss structures and decision criteria without recommending a specific financial company or promising returns.

- [ ] **Step 3: Validate and commit**

Run `validate_draft.py` for each matching keyword, resolve every substantive warning, then commit as `Draft third BringIssue series batch`.

### Task 7: Draft Posts 19-24

- [ ] **Step 1: Write the final six drafts**

Cover pension deduction missing, KakaoTalk backup, pension/IRP investment choices, travel card vs roaming vs eSIM, pension planning in the 50s, and health-screening result wording.

- [ ] **Step 2: Apply safety boundaries**

The health-results post explains how to identify recommendation wording and contact the examination provider; it must not interpret a reader's individual disease status. The digital post must not expose personal chat data or account identifiers.

- [ ] **Step 3: Validate and commit**

Run `validate_draft.py` for each matching keyword, resolve every substantive warning, then commit as `Draft final BringIssue series batch`.

### Task 8: Capture and Inspect Official Visuals

- [ ] **Step 1: Capture full context screens**

Open each recorded official page and capture enough surrounding UI for the reader to identify the service and location.

- [ ] **Step 2: Capture detail screens only when needed**

Add a second or later capture when the full screen makes a row, rate, button, or warning unreadable on mobile.

- [ ] **Step 3: Inspect every local image**

Use `view_image` on every PNG/JPG. Confirm no clipped text, unrelated browser chrome, personal data, cursor obstruction, or unreadable scale.

- [ ] **Step 4: Update each draft's image table**

Record order, visible fact, caption, placement, and masking status. Do not use `그림 설명` or mechanical timestamp captions.

- [ ] **Step 5: Commit the visual assets**

```powershell
git add blog/assets/2026-08-27-* blog/2026-08-27-*.md
git commit -m "Add official visuals to BringIssue series"
```

### Task 9: Final Editorial and Mobile QA

- [ ] **Step 1: Scan prohibited text**

```powershell
rg -n "확인 기준일|공식 참고자료|그림 설명|영상의 [0-9]+%|────|확인 필요" blog/2026-08-27-*.md
```

Expected: no reader-facing matches. Internal metadata may retain verification dates outside the final-body section.

- [ ] **Step 2: Check format counts**

For each post confirm 3-6 separators, 2-3 highlights, 2-3 underlines, one native-table specification, and no fixed image-count requirement.

- [ ] **Step 3: Humanize Korean prose**

Remove repeated transitions, generic AI phrases, excessive parallel bullet structures, and identical conclusions. Preserve verified meaning.

- [ ] **Step 4: Update the schedule board**

Mark every post `draft=ready`, `source=verified`, `image=ready`, and `validation=pass` only when evidence exists.

- [ ] **Step 5: Commit final QA**

```powershell
git add blog blog/batches/2026-08-27-bringissue-24-posts.md
git commit -m "Finalize BringIssue 24-post series"
```

### Task 10: Publish and Verify

- [ ] **Step 1: Confirm the active Naver account**

Before changing Naver state, verify that the external Chrome session is the user-authorized `rancemo858` BringIssue account. Do not switch accounts or enter credentials.

- [ ] **Step 2: Obtain action-time confirmation**

Present the exact batch, dates, times, and account. Ask once immediately before the final publish/reservation clicks for the ready batch.

- [ ] **Step 3: Enter each approved post**

Use category `오늘 뜬 유튜브` unless the user has created and approved a new category. Apply centered body alignment, native tables, real separators, highlights, underlines, tags, and the assigned schedule.

- [ ] **Step 4: Verify each scheduled post**

Confirm title, scheduled date/time, category, full-public visibility, search permission, image order, and no clipped content.

- [ ] **Step 5: Record the post IDs**

Add each Naver `logNo`, scheduled status, and eventual public URL to the schedule board. Telegram notification remains gated until the URL is actually public.

## Self-Review Results

- Spec coverage: all 24 topics, official-source verification, visual capture, Naver formatting, schedule, safety, validation, account check, and publication verification are represented.
- Placeholder scan: no `TBD`, `TODO`, or deferred implementation instructions remain.
- Path consistency: every brief, draft, asset folder, schedule file, and source matrix uses the `2026-08-27` series prefix.
- Scope boundary: this plan produces one coherent 24-post publishing package; ongoing future automation is not included.
