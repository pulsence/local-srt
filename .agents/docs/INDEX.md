# Agent Documentation Index

This document is the entry point for Claude/Codex agents working on Local SRT. For detailed architecture and file documentation, see [ARCHITECTURE.md](./ARCHITECTURE.md).

## Project Overview

Local-first subtitle generator. Uses faster-whisper (offline speech recognition) and ffmpeg to produce SRT, VTT, ASS, TXT, and JSON subtitle files from audio/video content.

- **Language:** Python 3.10+
- **Package:** `local_srt` (installed as `local-srt`)
- **Entry:** `srtgen` CLI command or `python -m local_srt`
- **Config:** JSON config file or CLI flags; mode presets (`yt`, `shorts`, `podcast`)
- **Version:** 0.2.0

## Architecture Overview

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed package structure and key file references.

### Package Docs

- [local_srt](./architecture/packages/local_srt.md) - Root package index and lazy-loading exports.
- [local_srt.api](./architecture/packages/local_srt.api.md) - Public library API (`transcribe_file`, `transcribe_batch`, `load_model`).
- [local_srt.cli](./architecture/packages/local_srt.cli.md) - CLI entry point (`srtgen` command).
- [local_srt.core](./architecture/packages/local_srt.core.md) - Core transcription orchestration.
- [local_srt.models](./architecture/packages/local_srt.models.md) - Data models (`ResolvedConfig`, `SubtitleBlock`, `WordItem`).
- [local_srt.config](./architecture/packages/local_srt.config.md) - Configuration loading, presets, and overrides.
- [local_srt.events](./architecture/packages/local_srt.events.md) - Event system for decoupled logging and progress.
- [local_srt.batch](./architecture/packages/local_srt.batch.md) - Batch processing and file discovery.
- [local_srt.audio](./architecture/packages/local_srt.audio.md) - Audio conversion and silence detection.
- [local_srt.subtitle_generation](./architecture/packages/local_srt.subtitle_generation.md) - Subtitle chunking and timing algorithms.
- [local_srt.text_processing](./architecture/packages/local_srt.text_processing.md) - Text normalization, wrapping, and splitting utilities.
- [local_srt.output_writers](./architecture/packages/local_srt.output_writers.md) - SRT/VTT/ASS/TXT/JSON output writers.
- [local_srt.system](./architecture/packages/local_srt.system.md) - System utilities (ffmpeg checks, command execution).
- [local_srt.whisper_wrapper](./architecture/packages/local_srt.whisper_wrapper.md) - faster-whisper model initialization.
- [local_srt.model_management](./architecture/packages/local_srt.model_management.md) - Model listing, downloading, and deletion.

### Architecture Overviews

- [Overview](./architecture/development/OVERVIEW.md) - System map and design principles.
- [Pipeline](./architecture/development/PIPELINE.md) - Transcription pipeline data flow.
- [Config](./architecture/development/CONFIG.md) - Configuration system and presets.
- [Formats](./architecture/development/FORMATS.md) - Output format specifications.
- [Events](./architecture/development/EVENTS.md) - Event system architecture.
- [Testing](./architecture/development/TESTING.md) - Test strategy and organization.

## Developer Guides

- When asked to create a plan read for how to do so: [CREATE_PLAN.md](./CREATE_PLAN.md).
- Always use the commit message format in [COMMIT_MESSAGE.md](./COMMIT_MESSAGE.md).
- [CODING_PATTERNS.md](./CODING_PATTERNS.md) - Coding conventions
- When asked to create a research plan, research the requested task in details and in depth. You should explore and document
  all the considerations needed implement the assigned task taking into considering the current code base. At the end of the
  document you should include a `Clarifications Required:` section with a list of questions for the user so he can clarify
  and answer questions in one place. This research plan should be saved in a file: .agents/docs/RESEARCH_PLAN.md. This
  document will be used by the user to iteratively fleshout ideas and design considerations before producings an
  implementation plan.

## Commands

```bash
# WLS: use the project venv
source .venv-wls/bin/activate

# Install (dev)
pip install -e ".[dev]"

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=local_srt --cov-report=html

# CLI
srtgen --help
srtgen input.mp4 -o output.srt
srtgen input.mp4 --mode yt --format vtt
srtgen videos/ --outdir processed/ --keep-structure
srtgen --list-models
srtgen --download-model small
srtgen --diagnose
```

## Environment Variables

No API keys required — fully local. System dependencies:

- **ffmpeg** (required) — audio/video decoding and silence detection
- **ffprobe** (optional) — media duration probing

## Key Implementation Notes

- **WLS Environment:** Whenver running in WLS all python and pytests need to be run using the .venv-wls venv. If python is not found no the system, you probably need to run in the WLS venv.
- **Entry point:** `srtgen = "local_srt.cli:main"` in `pyproject.toml`.
- **Package root:** `src/local_srt/` (src layout).
- **Lazy loading:** `__init__.py` uses `__getattr__` for on-demand imports; improves CLI startup time.
- **Event system:** Library emits typed events (`LogEvent`, `ProgressEvent`, `StageEvent`, etc.) rather than printing directly. The CLI subscribes and formats output.
- **Config hierarchy:** Defaults → JSON file → mode preset → CLI overrides (highest priority).
- **Presets:** `yt`, `shorts`, `podcast` with aliases (`youtube`, `pod`). Defined in `config.py:PRESETS`.
- **Model reuse:** In batch mode, the WhisperModel is loaded once and reused across all files.
- **Device selection:** `auto` tries CUDA, falls back to CPU. `strict_cuda=True` raises instead of falling back.
- **Audio pipeline:** All input is converted to 16kHz mono WAV via ffmpeg before passing to faster-whisper.
- **Silence detection:** Uses ffmpeg `silencedetect` filter; results used to align subtitle boundaries.
- **Word-level mode:** `word_timestamps=True` produces per-word subtitle cues rather than segment-level groupings.
- **Chunking:** `chunk_segments_to_subtitles()` for segment-level; `words_to_subtitles()` for word-level.
- **Output formats:** SRT, VTT, ASS, TXT (plain transcript), JSON (full metadata bundle).
- **Transcription result:** `TranscriptionResult(success, input_path, output_path, subtitles, segments, device_used, compute_type_used, error)`.
- **Batch result:** `BatchResult(total, successful, failed, results)`.
- **Config model:** All config in `ResolvedConfig` dataclass — flat field layout, no nested sections.
