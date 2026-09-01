import json
import unittest
from pathlib import Path

from PIL import Image


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
            storyboard_command,
            subtitle_command,
            video_command,
        )

        for post in load_registry()["posts"]:
            dest = asset_dir(post)
            self.assertTrue(dest.name.startswith("2026-08-22-"))
            metadata = metadata_command(post, dest)
            subtitles = subtitle_command(post, dest)
            video = video_command(post, dest)
            storyboard = storyboard_command(post, dest)
            self.assertIn("--write-info-json", metadata)
            self.assertIn("--write-auto-subs", subtitles)
            language_index = subtitles.index("--sub-langs") + 1
            self.assertEqual(subtitles[language_index], "ko")
            self.assertIn("--js-runtimes", video)
            self.assertIn("node", video)
            self.assertIn("--get-url", video)
            self.assertIn(
                "bestvideo[height<=480][vcodec^=avc1][ext=mp4]"
                "/bestvideo[height<=480][ext=mp4]",
                video,
            )
            self.assertNotIn("--merge-output-format", video)
            self.assertIn("sb0", storyboard)
            self.assertIn(str(dest / "storyboard.mhtml"), storyboard)

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


class BringIssueSceneTests(unittest.TestCase):
    def test_each_post_has_ten_distinct_wide_scenes_and_contact_sheet(self):
        from scripts.prepare_bringissue_ten_post_batch import asset_dir, load_registry

        for post in load_registry()["posts"]:
            folder = asset_dir(post)
            scenes = sorted(folder.glob("scene-*.jpg"))
            self.assertEqual(len(scenes), 10, post["slug"])
            fingerprints = set()
            for scene in scenes:
                with Image.open(scene).convert("RGB") as image:
                    self.assertGreaterEqual(image.width, 854)
                    self.assertGreaterEqual(image.height, 480)
                    self.assertAlmostEqual(image.width / image.height, 16 / 9, places=2)
                    small = image.resize((16, 9)).convert("L")
                    fingerprints.add(tuple(small.get_flattened_data()))
            self.assertEqual(len(fingerprints), 10, post["slug"])
            self.assertTrue((folder / "contact-sheet.jpg").exists())
            self.assertTrue((folder / "scene-plan.json").exists())


class BringIssueThumbnailTests(unittest.TestCase):
    def test_each_post_has_mobile_readable_thumbnail_contract(self):
        from scripts.prepare_bringissue_ten_post_batch import asset_dir, load_registry

        for post in load_registry()["posts"]:
            folder = asset_dir(post)
            with Image.open(folder / "thumbnail.jpg") as image:
                self.assertEqual(image.size, (1280, 720))
            lines = [
                line.strip()
                for line in (folder / "thumbnail-text.txt")
                .read_text(encoding="utf-8")
                .splitlines()
                if line.strip()
            ]
            self.assertEqual(len(lines), 2, post["slug"])
            self.assertTrue(all(len(line) <= 18 for line in lines), post["slug"])


class BringIssueDraftTests(unittest.TestCase):
    def test_each_post_matches_editorial_draft_contract(self):
        from scripts.prepare_bringissue_ten_post_batch import asset_dir, load_registry

        for post in load_registry()["posts"]:
            draft_path = asset_dir(post) / "post-draft.md"
            self.assertTrue(draft_path.exists(), post["slug"])
            draft = draft_path.read_text(encoding="utf-8")
            title = draft.splitlines()[0].removeprefix("# ")
            self.assertGreaterEqual(len(title), 40, post["slug"])
            self.assertLessEqual(len(title), 55, post["slug"])
            self.assertEqual(sum(line.startswith("## ") for line in draft.splitlines()), 3)
            self.assertEqual(draft.count("![장면 "), 10)
            self.assertEqual(draft.count("<u>"), 4)
            self.assertIn(post["url"], draft)
            self.assertIn("원본 영상을 대체하지 않는", draft)
            tags = draft.splitlines()[-1].split()
            self.assertGreaterEqual(len(tags), 8, post["slug"])
            self.assertLessEqual(len(tags), 12, post["slug"])
            compact_length = len("".join(draft.split()))
            self.assertGreaterEqual(compact_length, 1500, post["slug"])
            self.assertLessEqual(compact_length, 2200, post["slug"])


if __name__ == "__main__":
    unittest.main()
