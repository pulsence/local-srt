# Changelog

All notable changes to this project are documented in this file.

## Unreleased

### Added

- Added deterministic pipeline tests with shared fixtures and SRT comparison helper.
- Added opt-in integration tests with real audio fixtures and baseline SRTs.
- Added reference transcript comparison with WER-based tolerance for minor transcription drift.
- Added integration test tooling: `--update-baselines` flag and pytest markers.
- Audio fixtures live in `tests/fixtures/audio/`; baselines in `tests/fixtures/baselines/`.

### Changed

### Fixed

## 0.2.0 - 2026-02-01

- Local transcription using faster-whisper with ffmpeg-based media decoding.
- CLI `srtgen` supports SRT, VTT, ASS, TXT, and JSON outputs.
- Preset modes for `yt`, `shorts`, and `podcast` to tune chunking and pacing.
- Silence-aware splitting and alignment with optional word-level subtitle output.
- Batch processing with directory scanning, `--outdir`, and `--keep-structure`.
- Model management commands: list, download, and delete cached models.
- Diagnostic output via `--diagnose` and progress/event logging in the CLI.
