# Transcript Batch Kit

Transcript Batch Kit is a small command-line toolkit for people who process
many local audio or video files and need to keep transcript files organized.

It helps you:

- scan a media folder
- check whether each media file has a matching `.txt` transcript
- create a CSV manifest
- merge transcript files into one clean Markdown document

The project is intentionally lightweight. It uses only the Python standard
library, so it works well on a fresh machine.

## Install

Clone the repository, then install it in editable mode:

```powershell
python -m pip install -e .
```

Then run the CLI:

```powershell
python -m transcript_batch_kit --help
```

## Usage

Scan a folder of media files:

```powershell
python -m transcript_batch_kit scan "C:\path\to\videos"
```

Write a CSV manifest:

```powershell
python -m transcript_batch_kit scan "C:\path\to\videos" --transcripts "C:\path\to\txt" --csv manifest.csv
```

Merge transcript files into one Markdown file:

```powershell
python -m transcript_batch_kit merge "C:\path\to\txt" --output merged.md
```

Validate that every media file has a matching transcript:

```powershell
python -m transcript_batch_kit validate "C:\path\to\videos" --transcripts "C:\path\to\txt"
```

## Matching Rule

The toolkit matches files by stem:

- `video-001.mp4`
- `video-001.txt`

Those two files are treated as a pair.

## Supported Media Extensions

By default, the scanner recognizes:

`.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`, `.mp3`, `.wav`, `.m4a`, `.aac`, `.flac`

## Why This Exists

Batch transcription work often creates many small files. Without a manifest and
a validation step, it is easy to miss empty transcripts, skipped videos, or
files that were named differently.

This project focuses on the boring but important part: making the batch easy to
audit before you use the transcripts for writing, research, or AI workflows.

## License

MIT
