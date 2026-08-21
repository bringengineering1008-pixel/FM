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


class BringIssueCollectorCommandTests(unittest.TestCase):
    def test_commands_are_reproducible_and_do_not_require_ffmpeg_merge(self):
        from scripts.prepare_bringissue_ten_post_batch import (
            asset_dir,
            load_registry,
            metadata_command,
            subtitle_command,
            video_command,
        )

        for post in load_registry()["posts"]:
            dest = asset_dir(post)
            self.assertTrue(dest.name.startswith("2026-08-22-"))
            metadata = metadata_command(post, dest)
            subtitles = subtitle_command(post, dest)
            video = video_command(post, dest)
            self.assertIn("--write-info-json", metadata)
            self.assertIn("--write-auto-subs", subtitles)
            language_index = subtitles.index("--sub-langs") + 1
            self.assertEqual(subtitles[language_index], "ko")
            self.assertIn(
                "best[height<=480][ext=mp4]/best[height<=480]/worst", video
            )
            self.assertNotIn("--merge-output-format", video)

    def test_vtt_sampling_removes_tags_duplicates_and_keeps_thirty_second_marks(self):
        from scripts.prepare_bringissue_ten_post_batch import vtt_to_samples

        source = """WEBVTT

00:00:00.000 --> 00:00:02.000
<c>첫 장면입니다</c>

00:00:01.000 --> 00:00:03.000
<c>첫 장면입니다</c>

00:00:14.000 --> 00:00:16.000
중간 대사

00:00:31.000 --> 00:00:34.000
<c.colorCCCCCC>다음 장면입니다</c>
"""

        self.assertEqual(
            vtt_to_samples(source),
            ["[00:00] 첫 장면입니다", "[00:31] 다음 장면입니다"],
        )


if __name__ == "__main__":
    unittest.main()
