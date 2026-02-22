# Architecture Overview

This document provides a module-level map of Local SRT. See [INDEX.md](./INDEX.md) for the quick-start guide.

## Package Details

See individual package documentation in the [architecture/packages/](./architecture/packages/) folder:

- [local_srt](./architecture/packages/local_srt.md) - Root package: lazy-loading exports, `__main__.py`.
- [local_srt.api](./architecture/packages/local_srt.api.md) - Public library API: `transcribe_file`, `transcribe_batch`, `load_model`, result types.
- [local_srt.cli](./architecture/packages/local_srt.cli.md) - CLI entry point: argparse setup, event handler, batch orchestration.
- [local_srt.core](./architecture/packages/local_srt.core.md) - Core transcription orchestration: pipeline coordination, temp file management.
- [local_srt.models](./architecture/packages/local_srt.models.md) - Data models: `ResolvedConfig`, `SubtitleBlock`, `WordItem`.
- [local_srt.config](./architecture/packages/local_srt.config.md) - Config loading, presets, overrides, and aliases.
- [local_srt.events](./architecture/packages/local_srt.events.md) - Event dataclasses, `EventEmitter`, `EventLevel`.
- [local_srt.batch](./architecture/packages/local_srt.batch.md) - Batch file expansion, output path calculation, preflight validation.
- [local_srt.audio](./architecture/packages/local_srt.audio.md) - WAV conversion, silence detection via ffmpeg.
- [local_srt.subtitle_generation](./architecture/packages/local_srt.subtitle_generation.md) - Chunking algorithms, silence alignment, timing polish.
- [local_srt.text_processing](./architecture/packages/local_srt.text_processing.md) - Text normalization, word wrapping, block splitting, timing distribution.
- [local_srt.output_writers](./architecture/packages/local_srt.output_writers.md) - Format-specific writers: SRT, VTT, ASS, TXT, JSON.
- [local_srt.system](./architecture/packages/local_srt.system.md) - ffmpeg/ffprobe checks, command execution, media probing.
- [local_srt.whisper_wrapper](./architecture/packages/local_srt.whisper_wrapper.md) - faster-whisper model init, device and compute-type selection.
- [local_srt.model_management](./architecture/packages/local_srt.model_management.md) - Model cache: list, download, delete, diagnose.

## Development Overviews

Developer-focused architecture notes:

- [Overview](./architecture/development/OVERVIEW.md) - High-level system architecture and design principles.
- [Pipeline](./architecture/development/PIPELINE.md) - Full transcription pipeline data flow.
- [Config](./architecture/development/CONFIG.md) - Configuration schema, presets, and override hierarchy.
- [Formats](./architecture/development/FORMATS.md) - Output format specifications and writer contracts.
- [Events](./architecture/development/EVENTS.md) - Event system design and event type catalogue.
- [Testing](./architecture/development/TESTING.md) - Test strategy, organization, and running commands.
