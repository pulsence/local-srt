# System Overview

Local SRT is a local-first subtitle generator: it takes audio/video files and produces subtitle files using offline speech recognition. No internet connection or API keys are required.

## Design Principles

1. **Local-first** — All transcription runs on the user's machine via faster-whisper. No external AI API calls.
2. **Library + CLI** — `local_srt` is a usable Python library; the CLI is a thin wrapper on top of the library API.
3. **Decoupled logging** — The library never prints directly. It emits typed events; consumers (e.g., the CLI) subscribe and format output.
4. **Flat config** — A single `ResolvedConfig` dataclass holds all settings. No nested config sections.
5. **Preset system** — Three built-in modes (`yt`, `shorts`, `podcast`) cover common use cases with sensible defaults.
6. **Batch efficiency** — The whisper model is loaded once and reused across all files in a batch run.

## High-Level Architecture

```text
User Input (files / dirs / globs)
        │
        ▼
   [CLI / api.py]
        │
        ├─ load model once (whisper_wrapper.py)
        │
        └─ for each file:
               │
               ▼
         [core.py] ──── to_wav_16k_mono() ──── [audio.py]
               │
               ├─ detect_silences()            [audio.py]
               │
               ├─ model.transcribe()           [faster-whisper]
               │
               ├─ chunk_*_to_subtitles()      [subtitle_generation.py]
               │
               ├─ apply_silence_alignment()    [subtitle_generation.py]
               │
               ├─ hygiene_and_polish()         [subtitle_generation.py]
               │
               └─ write_[fmt]()               [output_writers.py]
```

## Core Subsystems

| Subsystem | Module(s) | Role |
| --- | --- | --- |
| **Config** | `config.py`, `models.py` | Load and resolve run configuration |
| **Audio** | `audio.py`, `system.py` | Convert media and detect silences |
| **Transcription** | `whisper_wrapper.py`, `core.py` | Load model and run speech recognition |
| **Subtitle Generation** | `subtitle_generation.py`, `text_processing.py` | Chunk and time subtitle blocks |
| **Output** | `output_writers.py` | Write subtitle files in requested format |
| **Batch** | `batch.py` | Expand inputs and manage batch runs |
| **Events** | `events.py` | Decouple library from logging/UI |
| **CLI** | `cli.py` | User-facing command and option parsing |
| **API** | `api.py` | Stable library interface |
| **Models** | `model_management.py` | Download, list, and delete model cache |

## Data Flow Summary

See [PIPELINE.md](./PIPELINE.md) for the detailed step-by-step data flow.

## Package Location

Source lives under `src/local_srt/` (PEP 517 src layout). Installed with `pip install -e ".[dev]"`.
