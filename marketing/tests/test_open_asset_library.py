from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automation"))


def asset(**overrides):
    from open_asset_library import OpenAsset

    values = {
        "asset_id": "shocked_face",
        "provider": "OpenMoji",
        "canonical_page_url": "https://openmoji.org/library/emoji-1F631/",
        "download_url": "https://openmoji.org/data/color/svg/1F631.svg",
        "license_id": "CC-BY-SA-4.0",
        "attribution": "OpenMoji – CC BY-SA 4.0",
    }
    values.update(overrides)
    return OpenAsset(**values)


def test_only_approved_provider_license_pairs_are_accepted() -> None:
    from open_asset_library import validate_asset

    pairs = (
        ("Openclipart", "CC0-1.0", "https://openclipart.org/", "Openclipart – CC0"),
        ("OpenMoji", "CC-BY-SA-4.0", "https://openmoji.org/", "OpenMoji – CC BY-SA 4.0"),
        ("Twemoji", "CC-BY-4.0", "https://github.com/twitter/twemoji", "Twemoji – CC BY 4.0"),
    )
    for provider, license_id, page_url, attribution in pairs:
        assert validate_asset(
            asset(
                provider=provider,
                license_id=license_id,
                canonical_page_url=page_url,
                attribution=attribution,
            )
        ) is None


def test_wrong_provider_license_pair_is_rejected() -> None:
    from open_asset_library import validate_asset

    with pytest.raises(ValueError, match="license"):
        validate_asset(asset(license_id="CC0-1.0"))


def test_unknown_or_meme_site_license_is_rejected() -> None:
    from open_asset_library import validate_asset

    with pytest.raises(ValueError, match="provider"):
        validate_asset(
            asset(
                provider="random-meme-site",
                canonical_page_url="https://example.com/frog",
                download_url="https://example.com/frog.png",
                license_id="UNKNOWN",
                attribution="unknown",
            )
        )


def test_missing_attribution_is_rejected() -> None:
    from open_asset_library import validate_asset

    with pytest.raises(ValueError, match="attribution"):
        validate_asset(asset(attribution=""))


def test_download_writes_exact_bytes_and_sha256_receipt(tmp_path: Path, monkeypatch) -> None:
    import open_asset_library as library

    payload = b"<svg>licensed</svg>"

    class Response:
        content = payload

        @staticmethod
        def raise_for_status() -> None:
            return None

    monkeypatch.setattr(library.requests, "get", lambda *args, **kwargs: Response())
    target = tmp_path / "asset.svg"
    receipt_path = tmp_path / "asset.receipt.json"
    receipt = library.download_asset(asset(), target, receipt_path)

    assert target.read_bytes() == payload
    assert receipt["sha256"] == sha256(payload).hexdigest()
    assert json.loads(receipt_path.read_text(encoding="utf-8")) == receipt
