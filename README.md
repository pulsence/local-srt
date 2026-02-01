# Local SRT

Local SRT generator using **faster-whisper** (offline transcription) and **ffmpeg** (media decoding).

This tool converts audio or video files into readable `.srt` subtitle files with intelligent
punctuation-aware chunking, pacing heuristics, and presets for YouTube, Shorts, and Podcasts.

## Caveat Emptor
This project was primarily created for my personal use. I will not be responding to pull requests
or issues unless they directly impact my use cases. Feel free to fork and make whatever changes
you would like. I was frustrated that a "turn key" local SRT generator was not easily 
available; now there is.

I generated this tool primarily using an AI code assistant. The codebase has test coverage,
but not every path is exhaustively validated.

## Features
- Fully local transcription (no remote API calls)
- Uses `faster-whisper` for high-quality speech recognition
- Intelligent subtitle chunking:
  - Punctuation-aware splitting (strong -> medium -> weak)
  - Reading-speed constraints (characters per second)
  - Minimum and maximum subtitle durations
- Preset modes:
  - `yt` - standard YouTube captions
  - `shorts` - fast-paced, compact captions
  - `podcast` - slower pacing, longer phrasing
- CUDA support with automatic CPU fallback
- Progress indicators with segment-based timing
- Supports batch processing of files
- Works on Windows, macOS, and Linux
- Output formats: SRT, VTT, ASS, TXT, JSON
- Word-level cue output (optional)

## Requirements
- **Python**: 3.10 or newer
- **ffmpeg** (required)
- **ffprobe** (recommended; usually included with ffmpeg)
- Optional:
  - NVIDIA GPU + CUDA drivers for `--device cuda`

## Installation

Install the current release from PyPI:

```bash
python -m pip install local-srt
```

Install from a GitHub download:

1) Download the repository (zip) from GitHub and extract it.
2) From the extracted folder, run:

```bash
python -m pip install .
```


## Installing ffmpeg
### Windows
```powershell
winget install Gyan.FFmpeg
```

or

```powershell
choco install ffmpeg
```

---

### macOS

```bash
brew install ffmpeg
```

---

### Linux

```bash
sudo apt install ffmpeg
```

---

## Usage

Basic:

```bash
srtgen input.mp4 -o output.srt
```

ASS output:

```bash
srtgen input.mp4 --format ass
```

Word-level output (requires word timestamps):

```bash
srtgen input.mp4 --word-level --word-timestamps
```

Preset modes:

```bash
srtgen input.mp4 --mode yt
srtgen input.mp4 --mode shorts
srtgen input.mp4 --mode podcast
```

CUDA (with fallback):

```bash
srtgen input.mp4 --device cuda
```

---

## Library Usage

Minimal usage:

```python
from pathlib import Path
from local_srt import ResolvedConfig, load_model, transcribe_file

model, device_used, compute_type = load_model(
    model_name="small",
    device="auto",
    strict_cuda=False,
)

result = transcribe_file(
    input_path=Path("input.mp3"),
    output_path=Path("output.srt"),
    fmt="srt",
    cfg=ResolvedConfig(),
    model=model,
    device_used=device_used,
    compute_type_used=compute_type,
)

print(result.success, result.output_path)
```

With event handling:

```python
from local_srt import EventEmitter, LogEvent, ProgressEvent

emitter = EventEmitter()

def handler(event):
    if isinstance(event, LogEvent):
        print(event.message)
    elif isinstance(event, ProgressEvent):
        print(f"{event.percent:5.1f}%")

emitter.subscribe(handler)
```

Pass the handler into API calls:

```python
model, device_used, compute_type = load_model(
    model_name="small",
    device="auto",
    strict_cuda=False,
    event_handler=emitter,
)

result = transcribe_file(
    input_path=Path("input.mp3"),
    output_path=Path("output.srt"),
    fmt="srt",
    cfg=ResolvedConfig(),
    model=model,
    device_used=device_used,
    compute_type_used=compute_type,
    event_handler=emitter,
)
```

Batch usage (single model load):

```python
from local_srt import transcribe_batch

inputs = [Path("a.mp3"), Path("b.mp3")]
batch = transcribe_batch(
    input_paths=inputs,
    outdir=Path("out"),
    fmt="srt",
    cfg=ResolvedConfig(),
    model=model,
    device_used=device_used,
    compute_type_used=compute_type,
    event_handler=emitter,
)

print(batch.successful, batch.failed)
```

---

## CLI Commands and Options

Inputs:

```bash
srtgen <inputs...>
```

`<inputs...>` can be one or more files, directories, or glob patterns. Directories are scanned recursively
for media files. You can also add an extra `--glob` pattern to widen a batch run.

Output control:

```bash
--outdir PATH
--keep-structure
--root PATH
-o, --output PATH
--format srt|vtt|ass|txt|json
--emit-transcript PATH
--emit-segments PATH
--emit-bundle PATH
--overwrite
```

- `--outdir`: Write outputs into a directory (batch mode). Default is next to each input file.
- `--keep-structure`: Preserve input directory structure under `--outdir`.
- `--root`: Base root used with `--keep-structure` (defaults to common parent).
- `-o/--output`: Single-file output path (only valid when one input expands to one file).
- `--format`: Primary output file format.
- `--emit-transcript`: Also write a plain-text transcript. If a directory is provided, a file is created per input.
- `--emit-segments`: Also write segments JSON (word timestamps included if requested).
- `--emit-bundle`: Also write a full JSON bundle (segments + subs + config).
- `--overwrite`: Overwrite outputs if they already exist.

Model + device:

```bash
--model tiny|base|small|medium|large-v3
--device auto|cpu|cuda
--strict-cuda
--language CODE
--word-timestamps
--word-level
```

- `--model`: faster-whisper model name.
- `--device`: `auto` picks CUDA when available, otherwise CPU.
- `--strict-cuda`: Fail instead of falling back to CPU when CUDA init fails.
- `--language`: Optional language code (e.g., `en`). If omitted, auto-detect.
- `--word-timestamps`: Request word timestamps (stored in JSON outputs).
- `--word-level`: Emit word-level subtitle cues (requires word timestamps).

Preset + config:

```bash
--mode shorts|yt|podcast
--config PATH
--dry-run
```

- `--mode`: Apply a preset (`shorts`, `yt`, `podcast`).
- `--config`: JSON config file. CLI args override config values.
- `--dry-run`: Validate inputs and show resolved settings without transcribing.

Chunking + timing:

```bash
--max_chars INT
--max_lines INT
--target_cps FLOAT
--min_dur FLOAT
--max_dur FLOAT
--no-comma-split
--no-medium-split
--prefer-punct-splits
--min-gap FLOAT
--pad FLOAT
--no-silence-split
--silence-min-dur FLOAT
--silence-threshold FLOAT
```

- `--max_chars`: Max characters per line.
- `--max_lines`: Max lines per subtitle block.
- `--target_cps`: Target characters per second for readability.
- `--min_dur`: Minimum subtitle duration (seconds).
- `--max_dur`: Maximum subtitle duration (seconds).
- `--no-comma-split`: Avoid splitting on commas.
- `--no-medium-split`: Avoid splitting on `;` or `:`.
- `--prefer-punct-splits`: Prefer punctuation splits even when text already fits.
- `--min-gap`: Minimum gap between consecutive cues (seconds).
- `--pad`: Pad cues into silence where possible (seconds).
- `--no-silence-split`: Disable silence-based splitting/alignment.
- `--silence-min-dur`: Minimum silence duration for splits (seconds).
- `--silence-threshold`: Silence threshold in dB (e.g., `-35`).

Temp files:

```bash
--keep_wav
--tmpdir PATH
```

- `--keep_wav`: Keep the temporary WAV file.
- `--tmpdir`: Directory for temporary WAV files (defaults to system temp).

Batch behavior + logging:

```bash
--continue-on-error
--quiet
--no-progress
--debug
```

- `--continue-on-error`: In batch mode, keep processing files after errors.
- `--quiet`: Minimal logging.
- `--no-progress`: Disable progress output.
- `--debug`: Show stack traces on errors.

Version + diagnostics:

```bash
--version
--diagnose
```

- `--version`: Print tool version and exit.
- `--diagnose`: Print system dependency info and exit.

Model management (run without input files):

```bash
--list-models
--list-available-models
--download-model NAME
--delete-model NAME
```

- `--list-models`: List downloaded models plus available model names.
- `--list-available-models`: List available model names only.
- `--download-model`: Download a model and exit.
- `--delete-model`: Delete a downloaded model from cache and exit.

---

## Model Management

List downloaded models:

```bash
srtgen --list-models
```

List available models:

```bash
srtgen --list-available-models
```

Download a model:

```bash
srtgen --download-model small
```

Delete a downloaded model:

```bash
srtgen --delete-model small
```

---

## Troubleshooting

**ffmpeg not found**
```bash
ffmpeg -version
```

**CUDA errors**
- Ensure NVIDIA drivers are installed
- Tool will fall back to CPU automatically

---

## License
MIT
