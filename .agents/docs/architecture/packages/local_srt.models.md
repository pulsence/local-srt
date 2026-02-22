# local_srt.models

Core data models used throughout the pipeline.

## `ResolvedConfig`

Flat dataclass holding all configuration for a transcription run.

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `max_chars` | `int` | `42` | Max characters per subtitle line |
| `max_lines` | `int` | `2` | Max lines per subtitle block |
| `target_cps` | `float` | `17.0` | Target characters per second (reading speed) |
| `min_dur` | `float` | `1.0` | Minimum subtitle duration in seconds |
| `max_dur` | `float` | `6.0` | Maximum subtitle duration in seconds |
| `allow_commas` | `bool` | `True` | Allow splitting at commas |
| `allow_medium` | `bool` | `True` | Allow splitting at colons and semicolons |
| `prefer_punct_splits` | `bool` | `False` | Prefer punctuation boundaries over fill-based splits |
| `min_gap` | `float` | `0.08` | Minimum gap between consecutive subtitles (seconds) |
| `pad` | `float` | `0.0` | Padding added to subtitle timing (seconds) |
| `vad_filter` | `bool` | `True` | Enable faster-whisper VAD filter |
| `word_timestamps` | `bool` | `False` | Request word-level timestamps from whisper |
| `use_silence_split` | `bool` | `True` | Detect and align to silence regions |
| `silence_min_dur` | `float` | `0.2` | Minimum silence duration to detect (seconds) |
| `silence_threshold_db` | `float` | `-35.0` | Silence threshold in dBFS |

## `SubtitleBlock`

Represents a single subtitle cue.

| Field | Type | Description |
| --- | --- | --- |
| `start` | `float` | Start time in seconds |
| `end` | `float` | End time in seconds |
| `lines` | `list[str]` | Text lines for this cue |

## `WordItem`

Represents a transcribed word with timing, extracted from whisper word-level data.

| Field | Type | Description |
| --- | --- | --- |
| `word` | `str` | The word text |
| `start` | `float` | Word start time in seconds |
| `end` | `float` | Word end time in seconds |
