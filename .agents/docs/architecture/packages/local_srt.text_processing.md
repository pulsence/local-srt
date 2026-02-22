# local_srt.text_processing

Text normalization, word wrapping, block splitting, and timing utilities.

## Text Normalization

### `normalize_spaces`

Replaces non-breaking and other Unicode spaces with ASCII space; collapses multiple consecutive spaces to one.

## Text Layout

### `wrap_text_lines`

```python
def wrap_text_lines(text: str, max_chars_per_line: int) -> list[str]
```

Word-wraps a string to fit `max_chars_per_line`, returning a list of lines.

### `block_fits`

```python
def block_fits(text: str, max_chars: int, max_lines: int) -> bool
```

Returns `True` if the text fits within the given char/line constraints.

### `wrap_fallback_blocks`

Creates multi-line blocks when text exceeds constraints and simpler wrapping fails.

## Splitting

### `split_on_delims`

```python
def split_on_delims(text: str, delims: str) -> list[str]
```

Splits text on any character in `delims`, preserving delimiters at split boundaries.

### `preferred_split_index`

```python
def preferred_split_index(text: str, delims: str) -> int | None
```

Finds the best split point by scanning for preferred delimiter positions.

### `split_text_into_blocks`

```python
def split_text_into_blocks(text: str, cfg: ResolvedConfig) -> list[str]
```

Intelligent text chunker that respects punctuation hierarchy (strong → medium → weak) and character limits from `cfg`.

## Timing

### `distribute_time`

```python
def distribute_time(start: float, end: float, count: int) -> list[tuple[float, float]]
```

Evenly distributes a time range across `count` items. Used for word-level timing when whisper provides only segment-level timing.

### `enforce_timing`

```python
def enforce_timing(
    start: float,
    end: float,
    min_dur: float,
    max_dur: float,
) -> tuple[float, float]
```

Adjusts `(start, end)` to satisfy duration constraints.
