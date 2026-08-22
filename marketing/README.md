# BRING Marketing Automation

This folder contains the evidence-led YouTube Shorts production pipeline used by BringIssue.

## Hyundai 500-won shipyard episode

- Production script: `automation/hyundai_500won_shipyard_short.py`
- Evidence and rights ledger: `production/domestic_cases/hyundai_500won_shipyard_evidence_v1.json`
- Production manual: `docs/AI_SHORTS_AUTOMATION_MANUAL.md`
- QC record: `output/hyundai_500won_shipyard_evidence_v1/qc/report.json`
- Publication receipt: `output/hyundai_500won_shipyard_evidence_v1/publish/youtube_result.json`

Run the focused validation suite from this directory:

```powershell
python -m pytest tests/test_open_asset_library.py tests/test_hyundai_500won_shipyard_short.py -q
```

The final published video is referenced by its YouTube receipt rather than stored as a large Git binary.
