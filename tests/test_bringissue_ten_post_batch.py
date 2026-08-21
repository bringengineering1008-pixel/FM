import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "blog" / "batches" / "2026-08-22-bringissue-ten-posts.json"


class BringIssueTenPostContractTests(unittest.TestCase):
    def test_registry_contains_ten_unique_public_youtube_videos(self):
        self.assertTrue(REGISTRY.exists())
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        posts = data["posts"]
        self.assertEqual(len(posts), 10)
        self.assertEqual(len({post["video_id"] for post in posts}), 10)
        self.assertEqual(len({post["slug"] for post in posts}), 10)
        self.assertTrue(
            all(
                post["url"]
                == f"https://www.youtube.com/watch?v={post['video_id']}"
                for post in posts
            )
        )
        self.assertTrue(all(post["editorial_angle"] for post in posts))
        self.assertTrue(all(post["monetization_bridge"] for post in posts))


if __name__ == "__main__":
    unittest.main()
