# local_srt.subtitle_generation

Core subtitle chunking and timing algorithms. Converts raw whisper output into timed subtitle blocks.

## Functions

### Word Collection

#### `collect_words`

```python
def collect_words(segments: Iterable) -> list[WordItem]
```

Extracts `WordItem` objects from whisper word-level segment data.

#### `words_to_text`

```python
def words_to_text(words: list[WordItem]) -> str
```

Concatenates word text with space normalization.

### Chunking

#### `chunk_segments_to_subtitles`

```python
def chunk_segments_to_subtitles(
    segments: Iterable,
    cfg: ResolvedConfig,
) -> list[SubtitleBlock]
```

Groups whisper segments into subtitle blocks respecting `max_chars`, `max_lines`, `max_dur`, and punctuation split preferences. Used when `word_timestamps=False`.

#### `chunk_words_to_subtitles`

```python
def chunk_words_to_subtitles(
    words: list[WordItem],
    cfg: ResolvedConfig,
) -> list[SubtitleBlock]
```

Creates subtitle blocks at the word level, distributing timing proportionally. Used when `word_timestamps=True`.

#### `words_to_subtitles`

```python
def words_to_subtitles(
    words: list[WordItem],
    cfg: ResolvedConfig,
) -> list[SubtitleBlock]
```

High-level entry: converts word list to final subtitle blocks with proper timing.

### Alignment

#### `apply_silence_alignment`

```python
def apply_silence_alignment(
    subtitles: list[SubtitleBlock],
    silences: list[tuple[float, float]],
    cfg: ResolvedConfig,
) -> list[SubtitleBlock]
```

Shifts subtitle boundaries into detected silence regions for cleaner visual transitions.

### Polish

#### `hygiene_and_polish`

```python
def hygiene_and_polish(
    subtitles: list[SubtitleBlock],
    cfg: ResolvedConfig,
) -> list[SubtitleBlock]
```

Final pass:

- Enforces `min_gap` between consecutive cues
- Applies `pad` offset to timing
- Clamps durations to `min_dur` / `max_dur`

## Split Priority

When chunking by punctuation:

1. **Strong** — periods, question marks, exclamation marks
2. **Medium** — commas, colons, semicolons (if `allow_commas` / `allow_medium`)
3. **Weak** — space (word boundary)

`prefer_punct_splits=True` biases chunking toward boundary splits even when the text would fit without splitting.
