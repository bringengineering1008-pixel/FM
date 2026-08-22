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
        for post in posts:
            self.assertTrue(post["draft_title"])
            self.assertEqual(len(post["thumbnail_text"]), 2)
            self.assertTrue(all(len(line) <= 18 for line in post["thumbnail_text"]))


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
            self.assertIn("ko-orig,ko,en-orig,en", subtitles)
            self.assertNotIn("ko.*,ko,en.*", subtitles)

            video = video_command(post)
            self.assertIn("--js-runtimes", video)
            js_runtime = video[video.index("--js-runtimes") + 1]
            self.assertTrue(js_runtime.startswith("node:"))
            self.assertIn("--remote-components", video)
            self.assertIn("ejs:github", video)
            self.assertIn("--ffmpeg-location", video)
            format_value = video[video.index("-f") + 1]
            self.assertTrue(format_value.startswith("bestvideo[height<=1080]"))
            self.assertNotIn("bestvideo[height<=2160]", format_value)
            self.assertNotIn("--merge-output-format", video)

    def test_batch_collection_records_a_failed_video_and_continues(self):
        from scripts.prepare_bringissue_twenty_post_batch import (
            collect_posts,
            load_registry,
        )

        posts = load_registry()["posts"][:2]
        calls = []

        def fake_runner(command, **kwargs):
            calls.append(command[-1])
            if len(calls) == 1:
                raise RuntimeError("HTTP Error 429")

        failures = collect_posts("subtitles", posts, runner=fake_runner)

        self.assertEqual(len(calls), 2)
        self.assertEqual(failures, [{"slug": posts[0]["slug"], "error": "HTTP Error 429"}])

    def test_video_collection_skips_posts_with_verified_existing_assets(self):
        from unittest.mock import patch
        from scripts.prepare_bringissue_twenty_post_batch import collect_posts, load_registry

        calls = []

        def fake_runner(command, **kwargs):
            calls.append(command)

        with patch(
            "scripts.prepare_bringissue_twenty_post_batch.video_complete",
            return_value=True,
        ):
            failures = collect_posts(
                "video", load_registry()["posts"][:1], runner=fake_runner
            )

        self.assertEqual(calls, [])
        self.assertEqual(failures, [])


class BringIssueTranscriptTests(unittest.TestCase):
    def test_vtt_parser_removes_markup_timestamps_and_rolling_duplicates(self):
        from scripts.prepare_bringissue_twenty_post_batch import parse_vtt_cues

        vtt = """WEBVTT

00:00:01.000 --> 00:00:03.000
<c>첫 번째 문장</c>

00:00:03.000 --> 00:00:05.000
첫 번째 문장

00:00:21.000 --> 00:00:24.000
두 번째 &amp; 중요한 문장
"""
        self.assertEqual(
            parse_vtt_cues(vtt),
            [
                {"seconds": 1.0, "text": "첫 번째 문장"},
                {"seconds": 21.0, "text": "두 번째 & 중요한 문장"},
            ],
        )

    def test_sampler_keeps_one_representative_cue_per_twenty_seconds(self):
        from scripts.prepare_bringissue_twenty_post_batch import sample_cues

        cues = [
            {"seconds": 1.0, "text": "도입"},
            {"seconds": 8.0, "text": "반복 구간"},
            {"seconds": 21.0, "text": "변화"},
            {"seconds": 44.0, "text": "결과"},
        ]
        self.assertEqual(
            sample_cues(cues, interval_seconds=20),
            [cues[0], cues[2], cues[3]],
        )


class BringIssueScenePlanTests(unittest.TestCase):
    def test_scene_plan_has_nine_unique_in_range_editorial_beats(self):
        from scripts.prepare_bringissue_twenty_post_batch import (
            build_scene_plan,
            load_registry,
        )

        post = load_registry()["posts"][0]
        plan = build_scene_plan(post, duration=100)
        scenes = plan["scenes"]
        timestamps = [scene["timestamp_seconds"] for scene in scenes]
        self.assertEqual(len(scenes), 9)
        self.assertEqual(len(set(timestamps)), 9)
        self.assertTrue(all(0 <= timestamp < 100 for timestamp in timestamps))
        self.assertTrue(all(len(scene["caption"]) <= 20 for scene in scenes))
        self.assertTrue(all(scene["body_purpose"] for scene in scenes))


class BringIssueTwentyPostImageTests(unittest.TestCase):
    def test_thumbnail_copy_uses_editorially_approved_two_lines(self):
        from scripts.prepare_bringissue_twenty_post_batch import (
            load_registry,
            thumbnail_lines,
        )

        post = load_registry()["posts"][0]
        self.assertEqual(thumbnail_lines(post), tuple(post["thumbnail_text"]))

    def test_scenes_are_native_wide_and_thumbnails_have_safe_size(self):
        from PIL import Image
        from scripts.prepare_bringissue_twenty_post_batch import asset_dir, load_registry

        for post in load_registry()["posts"]:
            folder = asset_dir(post)
            scenes = sorted(folder.glob("scene-*.jpg"))
            self.assertGreaterEqual(len(scenes), 8, post["slug"])
            self.assertLessEqual(len(scenes), 11, post["slug"])
            for scene in scenes:
                with Image.open(scene) as image:
                    self.assertGreaterEqual(image.width, 1280)
                    self.assertAlmostEqual(image.width / image.height, 16 / 9, places=2)
            with Image.open(folder / "thumbnail.jpg") as thumb:
                self.assertEqual(thumb.size, (1600, 900))


if __name__ == "__main__":
    unittest.main()
