# local_srt.batch

Batch processing utilities: input expansion, output path calculation, and preflight validation.

## Constants

### `MEDIA_EXTS`

Set of recognized media file extensions:

- Audio: `.mp3`, `.wav`, `.m4a`, `.aac`, `.flac`, `.ogg`
- Video: `.mp4`, `.mkv`, `.mov`, `.webm`, `.m4v`

## Functions

### `expand_inputs`

```python
def expand_inputs(inputs: list[str], glob_pat: str | None) -> list[Path]
```

Expands a list of input specifications into a flat list of media file paths:

- String paths to individual files → validated and included
- String paths to directories → recursively scanned for media files
- Glob patterns (via `glob_pat`) → expanded

### `default_output_for`

```python
def default_output_for(
    input_file: Path,
    outdir: Path | None,
    fmt: str,
    keep_structure: bool,
    base_root: Path | None,
) -> Path
```

Calculates the output path for a given input file. When `keep_structure=True` and `base_root` is set, preserves the relative directory structure under `outdir`.

### `preflight_one`

```python
def preflight_one(
    input_path: Path,
    output_path: Path,
    overwrite: bool,
) -> str | None
```

Validates a single file before processing. Returns an error string if the file should be skipped (e.g., output already exists and `overwrite=False`), or `None` if OK.

### `iter_media_files_in_dir`

```python
def iter_media_files_in_dir(d: Path) -> Iterator[Path]
```

Recursively yields media files within a directory, filtered by `MEDIA_EXTS`.
