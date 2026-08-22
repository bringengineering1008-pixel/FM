from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path

import requests


PROVIDER_LICENSES = {
    "Openclipart": "CC0-1.0",
    "OpenMoji": "CC-BY-SA-4.0",
    "Twemoji": "CC-BY-4.0",
}


@dataclass(frozen=True)
class OpenAsset:
    asset_id: str
    provider: str
    canonical_page_url: str
    download_url: str
    license_id: str
    attribution: str


def validate_asset(asset: OpenAsset) -> None:
    if asset.provider not in PROVIDER_LICENSES:
        raise ValueError(f"unapproved provider: {asset.provider}")
    if asset.license_id != PROVIDER_LICENSES[asset.provider]:
        raise ValueError(f"unapproved license for {asset.provider}: {asset.license_id}")
    if not asset.attribution.strip():
        raise ValueError("attribution is required")
    if not asset.canonical_page_url.startswith("https://"):
        raise ValueError("canonical page URL is required")
    if not asset.download_url.startswith("https://"):
        raise ValueError("HTTPS download URL is required")


def download_asset(asset: OpenAsset, target: Path, receipt_path: Path) -> dict[str, str]:
    validate_asset(asset)
    response = requests.get(asset.download_url, timeout=30)
    response.raise_for_status()
    target.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(response.content)
    receipt = {**asdict(asset), "sha256": sha256(response.content).hexdigest()}
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return receipt
