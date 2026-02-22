# local_srt.output_writers

Format-specific subtitle writers and time formatters.

## Time Formatting

| Function | Format | Example |
| --- | --- | --- |
| `format_srt_time(s)` | `HH:MM:SS,mmm` | `00:01:23,456` |
| `format_vtt_time(s)` | `HH:MM:SS.mmm` | `00:01:23.456` |
| `format_ass_time(s)` | `H:MM:SS.cc` | `0:01:23.45` (centiseconds) |

## Writers

### `write_srt`

```python
def write_srt(subtitles: list[SubtitleBlock], path: Path) -> None
```

Writes SubRip format with sequential 1-based numbering.

### `write_vtt`

```python
def write_vtt(subtitles: list[SubtitleBlock], path: Path) -> None
```

Writes WebVTT format with `WEBVTT` header.

### `write_ass`

```python
def write_ass(subtitles: list[SubtitleBlock], path: Path, cfg: ResolvedConfig) -> None
```

Writes Advanced SubStation Alpha format with script header and style block derived from `cfg`.

### `write_txt`

```python
def write_txt(segments: Iterable, path: Path) -> None
```

Writes a plain text transcript from raw whisper segments (no timing).

### `write_json_bundle`

```python
def write_json_bundle(
    subtitles: list[SubtitleBlock],
    segments: Iterable,
    cfg: ResolvedConfig,
    path: Path,
) -> None
```

Writes a JSON file containing:

- `subtitles` — serialized `SubtitleBlock` list
- `segments` — raw whisper segments via `segments_to_jsonable()`
- `config` — the `ResolvedConfig` that produced this output

### `segments_to_jsonable`

Converts faster-whisper segment objects to JSON-serializable dicts.
