# Changelog

All notable changes to this project are documented in this file.

## [0.2.0] - Current

- Local transcription using faster-whisper with ffmpeg-based media decoding.
- CLI `srtgen` supports SRT, VTT, ASS, TXT, and JSON outputs.
- Preset modes for `yt`, `shorts`, and `podcast` to tune chunking and pacing.
- Silence-aware splitting and alignment with optional word-level subtitle output.
- Batch processing with directory scanning, `--outdir`, and `--keep-structure`.
- Model management commands: list, download, and delete cached models.
- Diagnostic output via `--diagnose` and progress/event logging in the CLI.

