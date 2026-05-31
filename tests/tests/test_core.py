import tempfile
import unittest
from pathlib import Path

from transcript_batch_kit.core import merge_transcripts, scan_batch, summarize, write_manifest


class CoreTests(unittest.TestCase):
    def test_scan_batch_matches_transcripts_by_stem(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            media = root / "media"
            transcripts = root / "transcripts"
            media.mkdir()
            transcripts.mkdir()

            (media / "clip-1.mp4").write_bytes(b"video")
            (media / "clip-2.mp3").write_bytes(b"audio")
            (transcripts / "clip-1.txt").write_text("hello", encoding="utf-8")
            (transcripts / "clip-2.txt").write_text("", encoding="utf-8")

            items = scan_batch(media, transcripts)
            summary = summarize(items)

            self.assertEqual(
                summary,
                {"media": 2, "complete": 1, "missing": 0, "empty": 1},
            )

    def test_write_manifest_creates_csv(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            media = root / "media"
            media.mkdir()
            (media / "clip.mp4").write_bytes(b"video")

            output = root / "manifest.csv"
            write_manifest(scan_batch(media), output)

            text = output.read_text(encoding="utf-8")
            self.assertIn(
                "stem,media_path,transcript_path,transcript_exists,transcript_empty",
                text,
            )
            self.assertIn("clip", text)

    def test_merge_transcripts_writes_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            transcripts = root / "txt"
            transcripts.mkdir()
            (transcripts / "a.txt").write_text("first", encoding="utf-8")
            (transcripts / "b.txt").write_text("second", encoding="utf-8")

            output = root / "merged.md"
            count = merge_transcripts(transcripts, output, "Batch")

            self.assertEqual(count, 2)
            self.assertEqual(
                output.read_text(encoding="utf-8"),
                "# Batch\n\n"
                "## 1. a\n\n"
                "first\n\n"
                "## 2. b\n\n"
                "second\n\n",
            )


if __name__ == "__main__":
    unittest.main()
