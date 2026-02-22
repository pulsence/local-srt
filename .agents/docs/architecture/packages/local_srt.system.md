# local_srt.system

System utilities: external dependency checks and command execution.

## Dependency Checks

| Function | Description |
| --- | --- |
| `ffmpeg_ok() -> bool` | Returns `True` if ffmpeg is on PATH |
| `ffprobe_ok() -> bool` | Returns `True` if ffprobe is on PATH |
| `ffmpeg_version() -> str` | Returns ffmpeg version string |
| `ffprobe_version() -> str` | Returns ffprobe version string |
| `which_or_none(name: str) -> str \| None` | Finds executable on PATH or returns `None` |

## Command Execution

### `run_cmd_text`

```python
def run_cmd_text(cmd: list[str]) -> tuple[int, str, str]
```

Executes a command and returns `(returncode, stdout, stderr)`.

## File Utilities

### `ensure_parent_dir`

```python
def ensure_parent_dir(path: Path) -> None
```

Creates the parent directory of `path` if it does not exist.

## Media Probing

### `probe_duration_seconds`

```python
def probe_duration_seconds(path: Path) -> float | None
```

Returns the media file duration in seconds via ffprobe JSON output. Returns `None` if ffprobe is unavailable or the probe fails.
