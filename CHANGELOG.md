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

- **Breaking:** Replaced flat `ResolvedConfig` fields with nested `formatting`, `transcription`, and `silence` sections.
- **Breaking:** Added `PipelineMode` (`general`, `shorts`, `transcript`) and new `--mode` flag; presets now use `--preset`.
- **Breaking:** Removed `use_silence_split` and user-facing `--word-timestamps`; silence alignment and word timestamps are always on.
- Added diagnostic transcription flags: `--no-condition-on-previous-text`, `--no-speech-threshold`, `--log-prob-threshold`, `--compression-ratio-threshold`, `--vad-filter/--no-vad-filter`.

### Fixed

## 0.2.0 - 2026-02-01

- Local transcription using faster-whisper with ffmpeg-based media decoding.
- CLI `srtgen` supports SRT, VTT, ASS, TXT, and JSON outputs.
- Preset modes for `yt`, `shorts`, and `podcast` to tune chunking and pacing.
- Silence-aware splitting and alignment with optional word-level subtitle output.
- Batch processing with directory scanning, `--outdir`, and `--keep-structure`.
- Model management commands: list, download, and delete cached models.
- Diagnostic output via `--diagnose` and progress/event logging in the CLI.
