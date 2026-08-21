import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "brand" / "bringissue" / "brand-system.json"


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


if __name__ == "__main__":
    unittest.main()
