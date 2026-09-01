import json
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "brand" / "bringissue" / "brand-system.json"
OUTPUT = ROOT / "brand" / "bringissue" / "output"


class BringIssueBrandContractTests(unittest.TestCase):
    def test_contract_contains_approved_identity(self):
        self.assertTrue(CONTRACT.exists())
        data = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(data["name"], "브링이슈")
        self.assertEqual(data["tagline"], "지금 뜬 영상 속 결정적 한 장면")
        self.assertEqual(data["palette"]["navy"], "#14233B")
        self.assertEqual(data["palette"]["yellow"], "#FFCC36")
        self.assertEqual(data["categories"][0]["after"], "오늘 뜬 유튜브")
        self.assertEqual(len(data["published_posts"]), 5)


class BringIssueAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from scripts.build_bringissue_brand_assets import build_all

        build_all()

    def test_master_asset_sizes(self):
        expected = {
            "cover.png": (1600, 400),
            "background.png": (1920, 1200),
            "profile.png": (600, 600),
        }
        for name, size in expected.items():
            with self.subTest(name=name):
                with Image.open(OUTPUT / name) as image:
                    self.assertEqual(image.size, size)

    def test_five_thumbnail_outputs(self):
        files = sorted((OUTPUT / "thumbnails").glob("*.jpg"))
        self.assertEqual(len(files), 5)
        for file in files:
            with Image.open(file) as image:
                self.assertEqual(image.size, (1280, 720))

    def test_profile_uses_approved_signal_colors(self):
        with Image.open(OUTPUT / "profile.png").convert("RGB") as image:
            colors = image.getcolors(maxcolors=image.width * image.height)
        present = {rgb for _, rgb in colors}
        self.assertIn((255, 204, 54), present)
        self.assertIn((20, 35, 59), present)


if __name__ == "__main__":
    unittest.main()
