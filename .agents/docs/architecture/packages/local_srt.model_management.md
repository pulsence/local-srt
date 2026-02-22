# local_srt.model_management

Model cache management: listing, downloading, deleting, and system diagnostics.

## Available Models

| Name | Description |
| --- | --- |
| `tiny` | Fastest, lowest accuracy |
| `base` | Fast, acceptable accuracy |
| `small` | Balanced (recommended default) |
| `medium` | Higher accuracy, slower |
| `large-v3` | Best accuracy, slowest |

## Functions

### `list_available_models() -> list[str]`

Returns the list of known model names.

### `list_downloaded_models() -> list[str]`

Returns model names found in the faster-whisper model cache directory.

### `download_model(name: str) -> None`

Downloads the named model to the cache.

### `delete_model(name: str) -> None`

Removes the named model from the cache.

### `diagnose() -> DiagnoseResult`

Returns a `DiagnoseResult` with:

- Python version and platform
- ffmpeg and ffprobe paths and versions
- faster-whisper version
- Available vs downloaded models

Used by `srtgen --diagnose` to help users troubleshoot their environment.

## `DiagnoseResult`

| Field | Type | Description |
| --- | --- | --- |
| `python_version` | `str` | Python version string |
| `platform` | `str` | OS platform |
| `ffmpeg_path` | `str \| None` | Path to ffmpeg executable |
| `ffprobe_path` | `str \| None` | Path to ffprobe executable |
| `ffmpeg_version` | `str \| None` | ffmpeg version |
| `ffprobe_version` | `str \| None` | ffprobe version |
| `faster_whisper_version` | `str \| None` | faster-whisper package version |
