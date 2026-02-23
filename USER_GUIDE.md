# Local SRT User Guide

This guide documents the current CLI behavior for Local SRT 0.2.x.

## Installation

Install from PyPI:

```bash
python -m pip install local-srt
```

Requirements:

- Python 3.10+
- `ffmpeg` available on `PATH` (required)
- `ffprobe` available on `PATH` (recommended)

Models are downloaded automatically on first use when a model is not present in the local cache.

## Basic Usage

Transcribe a single file to SRT:

```bash
srtgen input.mp4 -o output.srt
```

Choose a different output format:

```bash
srtgen input.mp4 --format vtt
```

Generate word-level cues (per-word subtitles):

```bash
srtgen input.mp4 --word-level
```

Notes:

- `--output` is only valid when a single input expands to a single file.
- For directory or multi-file input, use `--outdir`.

## Supported Inputs

Directory inputs are scanned recursively for these extensions:

- `.mp3`, `.wav`, `.m4a`, `.aac`, `.flac`, `.ogg`
- `.mp4`, `.mkv`, `.mov`, `.webm`, `.m4v`

If you pass an explicit file path or glob, other formats may work if ffmpeg can decode them.

## Supported Outputs

Primary output formats (via `--format`):

- `srt`, `vtt`, `ass`, `txt`, `json`

Additional outputs:

- `--emit-transcript PATH` writes a plain-text transcript (`.txt`)
- `--emit-segments PATH` writes a segments JSON file (`.segments.json`)
- `--emit-bundle PATH` writes a full JSON bundle (`.bundle.json`)

If an `--emit-*` path is a directory or ends with a trailing slash, a per-input file is created inside that directory.

## Models

Select a faster-whisper model:

```bash
srtgen input.mp4 --model small
```

Common model names:

- `tiny`, `base`, `small`, `medium`, `large-v3`

Defaults and related flags:

- `--model` default: `medium`
- `--device` choices: `auto`, `cpu`, `cuda` (default: `auto`)
- `--strict-cuda` fails instead of falling back to CPU if CUDA init fails

Model management (run without input files):

- `--list-models`
- `--list-available-models`
- `--download-model NAME`
- `--delete-model NAME`

## Language

Use `--language` to force a language code (example: `en`). If omitted, faster-whisper auto-detects the language.

```bash
srtgen input.mp4 --language en
```

## Presets

Use `--preset` to apply preset tuning:

```bash
srtgen input.mp4 --preset shorts
srtgen input.mp4 --preset yt
srtgen input.mp4 --preset podcast
```

Preset values (defaults are from the base config):

| Setting | Default | shorts | yt | podcast |
| --- | --- | --- | --- | --- |
| `max_chars` | 42 | 18 | 42 | 40 |
| `max_lines` | 2 | 1 | 2 | 2 |
| `target_cps` | 17.0 | 18.0 | 17.0 | 16.0 |
| `min_dur` | 1.0 | 0.7 | 1.0 | 0.9 |
| `max_dur` | 6.0 | 3.0 | 6.0 | 5.0 |
| `prefer_punct_splits` | False | False | False | True |
| `allow_commas` | True | True | True | True |
| `allow_medium` | True | True | True | True |
| `min_gap` | 0.08 | 0.08 | 0.08 | 0.08 |
| `pad` | 0.00 | 0.00 | 0.00 | 0.05 |

These values map to `formatting.*` in the config file.

## Pipeline Modes

Use `--mode` to select the pipeline mode (default: `general`):

```bash
srtgen input.mp4 --mode general
srtgen input.mp4 --mode shorts
srtgen input.mp4 --mode transcript
```

Notes:

- `general` is the default pipeline.
- `shorts` and `transcript` currently follow the general pipeline path; their specialized behavior arrives in Phase 4.

## Formatting Options

These flags control chunking and readability. Defaults are shown in parentheses.

- `--max_chars` (42): Max characters per line.
- `--max_lines` (2): Max lines per subtitle cue.
- `--target_cps` (17.0): Target characters per second.
- `--min_dur` (1.0): Minimum cue duration in seconds.
- `--max_dur` (6.0): Maximum cue duration in seconds.
- `--no-comma-split` (default: allow commas): Do not split on commas.
- `--no-medium-split` (default: allow): Do not split on `;` or `:`.
- `--prefer-punct-splits` (default: off): Prefer punctuation splits even if text fits.
- `--min-gap` (0.08): Minimum gap between cues in seconds.
- `--pad` (0.00): Pad cues into nearby silence in seconds.

## Silence Settings

Silence-aware splitting and alignment are always enabled.

- `--silence-min-dur` (0.2): Minimum silence duration to consider (seconds).
- `--silence-threshold` (-35.0): Silence threshold in dB (example: `-35`).

## Transcription Options

- `--word-level`: Output one subtitle per word.
- `--no-condition-on-previous-text`: Disable conditioning on previous text.
- `--no-speech-threshold`: Override the no-speech threshold.
- `--log-prob-threshold`: Override the log probability threshold.
- `--compression-ratio-threshold`: Override the compression ratio threshold.
- `--vad-filter` / `--no-vad-filter`: Enable or disable VAD filtering.

Notes:

- Word timestamps are always collected so that silence alignment can run and JSON outputs can include per-word timing.
- Voice activity detection (VAD) is controlled by the config key `vad_filter` (default: true) and can be overridden by `--vad-filter`/`--no-vad-filter`.

## Batch Processing

Directory input (recursive scan):

```bash
srtgen videos/
```

Multiple inputs with a shared output directory:

```bash
srtgen a.mp3 b.mp3 --outdir out/
```

Keep directory structure under `--outdir`:

```bash
srtgen videos/ --outdir out/ --keep-structure
```

Notes:

- Directory scanning is always recursive. There is no `--recursive` flag.
- Use `--glob` to add an extra glob pattern (example: `--glob "*.wav"`).
- Use `--root` to set the base root used with `--keep-structure`.
- Use `--overwrite` to overwrite existing outputs.
- Use `--continue-on-error` to keep processing other files after a failure.

## Config File

Use `--config path/to/config.json` to apply overrides from a JSON file. CLI args always override config values, and presets are applied after the config file.

Precedence order:

- Defaults
- `--config` JSON
- `--preset` preset
- `--mode` pipeline defaults
- CLI flags

Accepted keys (nested JSON object):

- `formatting`: `max_chars`, `max_lines`, `target_cps`, `min_dur`, `max_dur`
- `formatting`: `allow_commas`, `allow_medium`, `prefer_punct_splits`
- `formatting`: `min_gap`, `pad`
- `transcription`: `vad_filter`
- `silence`: `silence_min_dur`, `silence_threshold_db`

Example:

```json
{
  "formatting": {
    "max_chars": 40,
    "max_lines": 2,
    "target_cps": 16.0,
    "min_dur": 0.9,
    "max_dur": 5.0,
    "allow_commas": true,
    "allow_medium": true,
    "prefer_punct_splits": false,
    "min_gap": 0.08,
    "pad": 0.05
  },
  "transcription": {
    "vad_filter": true
  },
  "silence": {
    "silence_min_dur": 0.2,
    "silence_threshold_db": -35.0
  }
}
```

## Diagnostics

Use `srtgen --diagnose` to print system information and exit. Output includes:

- Tool version
- Python version
- Platform
- ffmpeg and ffprobe versions
- faster-whisper version (if installed)
- Detected `ffmpeg` and `ffprobe` paths

## Dry Run

Use `--dry-run` to validate inputs and show the resolved config without running transcription. When not combined with `--quiet`, the resolved config is printed as JSON.

## Temp Files

- `--keep_wav` keeps the temporary 16 kHz mono WAV file.
- `--tmpdir PATH` sets the directory for temporary WAV output.

## Logging and Debugging

- `--quiet` reduces output to errors only.
- `--no-progress` disables the progress line.
- `--debug` prints stack traces for errors.
- `--version` prints the tool version and exits.
