# local_srt.audio

Audio processing: media conversion and silence detection via ffmpeg.

## Functions

### `to_wav_16k_mono`

```python
def to_wav_16k_mono(input_path: Path, tmpdir: Path) -> Path
```

Converts any media file to a 16kHz mono WAV using ffmpeg. This is the format expected by faster-whisper.

- Output is written to `tmpdir` with the same stem as the input
- ffmpeg handles all input formats (audio and video)
- Video files are decoded to audio only

### `detect_silences`

```python
def detect_silences(
    wav_path: Path,
    min_silence_dur: float,
    silence_threshold_db: float,
) -> list[tuple[float, float]]
```

Runs ffmpeg's `silencedetect` filter on a WAV file to find silence regions.

- Returns a list of `(start_seconds, end_seconds)` tuples
- Overlapping silence regions are merged
- Used by `core.py` to align subtitle boundaries to natural pauses

**Defaults** (from `ResolvedConfig`):

- `min_silence_dur`: 0.2 seconds
- `silence_threshold_db`: -35.0 dBFS
