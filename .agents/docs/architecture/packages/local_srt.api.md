# local_srt.api

Public library API. The stable interface for consumers of `local_srt` as a library (not via CLI).

## Key Functions

### `load_model`

```python
def load_model(
    model_name: str,
    device: str,
    strict_cuda: bool,
    event_handler: EventHandler | None,
) -> tuple[WhisperModel, str, str]
```

Loads a faster-whisper model. Returns `(model, device_used, compute_type_used)`.

- `device`: `"auto"`, `"cpu"`, or `"cuda"`
- `strict_cuda=True`: raises if CUDA unavailable instead of falling back to CPU

### `transcribe_file`

```python
def transcribe_file(
    input_path: Path,
    output_path: Path,
    fmt: str,
    cfg: ResolvedConfig,
    model: WhisperModel,
    device_used: str,
    compute_type_used: str,
    event_handler: EventHandler | None,
    language: str | None,
    word_level: bool,
    overwrite: bool,
) -> TranscriptionResult
```

Transcribes a single media file and writes the output.

### `transcribe_batch`

```python
def transcribe_batch(
    input_paths: list[Path],
    outdir: Path | None,
    fmt: str,
    cfg: ResolvedConfig,
    model: WhisperModel,
    device_used: str,
    compute_type_used: str,
    event_handler: EventHandler | None,
    language: str | None,
    word_level: bool,
    overwrite: bool,
    continue_on_error: bool,
) -> BatchResult
```

Transcribes multiple files using a shared model instance.

## Result Types

### `TranscriptionResult`

| Field | Type | Description |
| --- | --- | --- |
| `success` | `bool` | Whether transcription succeeded |
| `input_path` | `Path` | Source media file |
| `output_path` | `Path` | Written output file |
| `subtitles` | `list[SubtitleBlock]` | Generated subtitle blocks |
| `segments` | `list` | Raw whisper segments |
| `device_used` | `str` | Actual device (`"cpu"` or `"cuda"`) |
| `compute_type_used` | `str` | Compute type (`"int8"`, `"float16"`) |
| `error` | `Exception \| None` | Set if `success=False` |

### `BatchResult`

| Field | Type | Description |
| --- | --- | --- |
| `total` | `int` | Total files attempted |
| `successful` | `int` | Files that succeeded |
| `failed` | `int` | Files that failed |
| `results` | `list[TranscriptionResult]` | Per-file results |

## Type Alias

```python
EventHandler = Callable[[BaseEvent], None]
```

Accepts any callable or object with an `.emit()` method.
