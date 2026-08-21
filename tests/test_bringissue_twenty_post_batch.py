import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "blog" / "batches" / "2026-08-22-bringissue-twenty-posts.json"
EXPECTED_SLOTS = [
    *(
        f"2026-08-23T{time}:00+09:00"
        for time in (
            "07:30",
            "09:00",
            "10:30",
            "12:00",
            "13:30",
            "15:00",
            "16:30",
            "18:00",
            "20:00",
            "22:00",
        )
    ),
    *(
        f"2026-08-24T{time}:00+09:00"
        for time in (
            "07:30",
            "09:00",
            "10:30",
            "12:00",
            "13:30",
            "15:00",
            "16:30",
            "18:00",
            "20:00",
            "22:00",
        )
    ),
]


class BringIssueTwentyPostContractTests(unittest.TestCase):
    def test_registry_has_twenty_unique_posts_and_exact_portfolio(self):
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        posts = data["posts"]
        self.assertEqual(len(posts), 20)
        self.assertEqual(len({post["slug"] for post in posts}), 20)
        self.assertEqual(len({post["video_id"] for post in posts}), 20)
        self.assertEqual(
            Counter(post["engine"] for post in posts),
            Counter({"entertainment": 12, "product": 5, "money": 3}),
        )
        self.assertEqual([post["scheduled_at"] for post in posts], EXPECTED_SLOTS)
        self.assertEqual(posts[0]["slug"], "avengers-doomsday-doctor-doom")


class BringIssueHighResolutionCollectorTests(unittest.TestCase):
    def test_commands_preserve_metadata_subtitles_and_native_video_quality(self):
        from scripts.prepare_bringissue_twenty_post_batch import (
            asset_dir,
            load_registry,
            metadata_command,
            subtitle_command,
            video_command,
        )

        for post in load_registry()["posts"]:
            dest = asset_dir(post)
            self.assertTrue(dest.name.startswith(post["scheduled_at"][:10]))

            metadata = metadata_command(post)
            self.assertIn("--write-info-json", metadata)
            self.assertIn(str(dest / "source.%(ext)s"), metadata)

            subtitles = subtitle_command(post)
            self.assertIn("--write-auto-subs", subtitles)
            self.assertIn("ko.*,ko,en.*", subtitles)

            video = video_command(post)
            self.assertIn("--js-runtimes", video)
            format_value = video[video.index("-f") + 1]
            self.assertIn("bestvideo[height<=2160]", format_value)
            self.assertNotIn("--merge-output-format", video)


if __name__ == "__main__":
    unittest.main()
