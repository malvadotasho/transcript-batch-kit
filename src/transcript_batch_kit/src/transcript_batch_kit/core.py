from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

DEFAULT_MEDIA_EXTENSIONS = (
    ".mp4",
    ".mov",
    ".mkv",
    ".avi",
    ".webm",
    ".mp3",
    ".wav",
    ".m4a",
    ".aac",
    ".flac",
)


@dataclass(frozen=True)
class TranscriptItem:
    media_path: Path
    transcript_path: Path | None
    transcript_exists: bool
    transcript_empty: bool

    @property
    def stem(self) -> str:
        return self.media_path.stem


def normalize_extensions(extensions: Iterable[str]) -> tuple[str, ...]:
    normalized: list[str] = []
    for extension in extensions:
        value = extension.strip().lower()
        if not value:
            continue
        if not value.startswith("."):
            value = "." + value
        normalized.append(value)
    return tuple(dict.fromkeys(normalized))


def list_media_files(
    media_dir: Path,
    extensions: Sequence[str] = DEFAULT_MEDIA_EXTENSIONS,
) -> list[Path]:
    media_dir = media_dir.expanduser().resolve()
    extension_set = set(normalize_extensions(extensions))
    if not media_dir.exists():
        raise FileNotFoundError(f"Media directory does not exist: {media_dir}")
    if not media_dir.is_dir():
        raise NotADirectoryError(f"Media path is not a directory: {media_dir}")

    return sorted(
        (
            path
            for path in media_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in extension_set
        ),
        key=lambda path: path.as_posix().lower(),
    )


def scan_batch(
    media_dir: Path,
    transcript_dir: Path | None = None,
    extensions: Sequence[str] = DEFAULT_MEDIA_EXTENSIONS,
) -> list[TranscriptItem]:
    media_files = list_media_files(media_dir, extensions)
    transcript_root = (
        transcript_dir.expanduser().resolve()
        if transcript_dir is not None
        else media_dir.expanduser().resolve()
    )

    items: list[TranscriptItem] = []
    for media_path in media_files:
        transcript_path = transcript_root / f"{media_path.stem}.txt"
        exists = transcript_path.exists()
        empty = exists and transcript_path.stat().st_size == 0
        items.append(
            TranscriptItem(
                media_path=media_path,
                transcript_path=transcript_path if exists else None,
                transcript_exists=exists,
                transcript_empty=empty,
            )
        )
    return items


def write_manifest(items: Sequence[TranscriptItem], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "stem",
                "media_path",
                "transcript_path",
                "transcript_exists",
                "transcript_empty",
            ],
        )
        writer.writeheader()
        for item in items:
            writer.writerow(
                {
                    "stem": item.stem,
                    "media_path": str(item.media_path),
                    "transcript_path": str(item.transcript_path or ""),
                    "transcript_exists": item.transcript_exists,
                    "transcript_empty": item.transcript_empty,
                }
            )


def list_transcript_files(transcript_dir: Path) -> list[Path]:
    transcript_dir = transcript_dir.expanduser().resolve()
    if not transcript_dir.exists():
        raise FileNotFoundError(f"Transcript directory does not exist: {transcript_dir}")
    if not transcript_dir.is_dir():
        raise NotADirectoryError(f"Transcript path is not a directory: {transcript_dir}")
    return sorted(transcript_dir.glob("*.txt"), key=lambda path: path.name.lower())


def merge_transcripts(transcript_dir: Path, output_path: Path, title: str) -> int:
    files = list_transcript_files(transcript_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(f"# {title}\n\n")
        for index, path in enumerate(files, start=1):
            text = path.read_text(encoding="utf-8", errors="replace").strip()
            handle.write(f"## {index}. {path.stem}\n\n")
            if text:
                handle.write(text)
                handle.write("\n\n")
            else:
                handle.write("_Empty transcript._\n\n")
    return len(files)


def summarize(items: Sequence[TranscriptItem]) -> dict[str, int]:
    total = len(items)
    missing = sum(1 for item in items if not item.transcript_exists)
    empty = sum(1 for item in items if item.transcript_empty)
    complete = total - missing - empty
    return {
        "media": total,
        "complete": complete,
        "missing": missing,
        "empty": empty,
    }
