from __future__ import annotations

import argparse
from pathlib import Path

from .core import (
    DEFAULT_MEDIA_EXTENSIONS,
    merge_transcripts,
    normalize_extensions,
    scan_batch,
    summarize,
    write_manifest,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="transcript-batch-kit",
        description="Scan, validate, and merge transcript batches.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Scan media files and transcript status.")
    add_scan_arguments(scan)
    scan.add_argument("--csv", type=Path, help="Optional CSV manifest output path.")

    validate = subparsers.add_parser(
        "validate",
        help="Exit with an error when transcripts are missing or empty.",
    )
    add_scan_arguments(validate)

    merge = subparsers.add_parser("merge", help="Merge .txt transcripts into Markdown.")
    merge.add_argument("transcripts", type=Path, help="Directory containing .txt files.")
    merge.add_argument(
        "--output",
        type=Path,
        default=Path("merged.md"),
        help="Markdown output path. Defaults to merged.md.",
    )
    merge.add_argument(
        "--title",
        default="Merged Transcripts",
        help="Document title. Defaults to 'Merged Transcripts'.",
    )

    return parser


def add_scan_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("media", type=Path, help="Directory containing media files.")
    parser.add_argument(
        "--transcripts",
        type=Path,
        help="Directory containing matching .txt transcripts. Defaults to media folder.",
    )
    parser.add_argument(
        "--extensions",
        nargs="*",
        default=list(DEFAULT_MEDIA_EXTENSIONS),
        help="Media extensions to include, for example mp4 mp3 wav.",
    )


def print_summary(summary: dict[str, int]) -> None:
    print(f"Media files: {summary['media']}")
    print(f"Complete transcripts: {summary['complete']}")
    print(f"Missing transcripts: {summary['missing']}")
    print(f"Empty transcripts: {summary['empty']}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command in {"scan", "validate"}:
        extensions = normalize_extensions(args.extensions)
        items = scan_batch(args.media, args.transcripts, extensions)
        summary = summarize(items)
        print_summary(summary)

        if args.command == "scan" and args.csv:
            write_manifest(items, args.csv)
            print(f"Manifest written: {args.csv}")

        if args.command == "validate":
            if summary["missing"] or summary["empty"]:
                print("Validation failed: missing or empty transcripts found.")
                return 1
            print("Validation passed.")
        return 0

    if args.command == "merge":
        count = merge_transcripts(args.transcripts, args.output, args.title)
        print(f"Merged {count} transcript files into {args.output}")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2
