# Building atlas company release

Goal: publish the existing local atlas on a new branch of bringengineering1008-pixel/FM, preserving the fork's default branch and existing FM functionality. Add the user-approved name/address-only building transfer.

Architecture: FM presents a user-selected building preview from data already loaded under its existing login. A small allowlisted JSON download contains only version, kind, name and address. Atlas imports this file after preview and confirmation into a new empty building. It never queries Firebase directly and never writes back to FM. Duplicate imports select the existing building without overwriting coordinates or records. Model dimensions are explicitly placeholders until entered by the user.

Files: `building-operations/crm-transfer.mjs` owns validation and pure mapping; `crm-transfer-ui.mjs` owns atlas import; `fm-transfer-entry.mjs` owns the parent FM chooser; `index.html` adds the entry only. Existing module files are carried unchanged except initialization and documentation. Runtime assets use local Three.js with its license.

Execution checklist:
- [ ] Run baseline atlas tests in isolated worktree.
- [ ] Write failing tests for allowlisting, archived/deleted exclusion, bad input, empty preview, duplicate handling, and preservation.
- [ ] Implement small transfer payload and user-confirmed import without invented equipment.
- [ ] Test both parent chooser and atlas import using synthetic data; block production database access in tests.
- [ ] Re-run unit and browser suites against isolated worktree, inspect screenshots and staged diff.
- [ ] Exclude generated screenshots, real documents, customer data, unrelated marketing/workflow changes.
- [ ] Commit and push only a new codex branch; create a review PR targeting the company default branch, without merging or production deployment.

Acceptance: remote commit and PR contain atlas module plus minimal entry; company default branch untouched; source allowlist tested; JSON preview confirms only name/address; existing atlas buildings unchanged. Limits: no company server sync, private data, live sensors, AI analysis, or verified site geometry. Repo security rules remain unchanged and require separate review before expanded server integration.
