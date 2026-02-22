# Output Formats

Local SRT supports five output formats. The format is selected via `--format` (CLI) or the `fmt` argument to `transcribe_file`.

## Format Reference

| Format | Extension | Description |
| --- | --- | --- |
| `srt` | `.srt` | SubRip — widely supported, standard subtitle format |
| `vtt` | `.vtt` | WebVTT — web-native, used in HTML5 `<video>` elements |
| `ass` | `.ass` | Advanced SubStation Alpha — supports advanced styling |
| `txt` | `.txt` | Plain text transcript (no timing) |
| `json` | `.json` | Full metadata bundle (subtitles + segments + config) |

## SRT Format

```text
1
00:00:01,000 --> 00:00:04,500
Hello, world.

2
00:00:05,000 --> 00:00:08,000
This is the second subtitle.
```

- Sequential 1-based index
- Timestamp format: `HH:MM:SS,mmm` (comma decimal separator)
- Blank line between cues

## WebVTT Format

```text
WEBVTT

00:00:01.000 --> 00:00:04.500
Hello, world.

00:00:05.000 --> 00:00:08.000
This is the second subtitle.
```

- `WEBVTT` header on first line
- Timestamp format: `HH:MM:SS.mmm` (period decimal separator)
- No cue index

## ASS Format

```text
[Script Info]
ScriptType: v4.00+
...

[V4+ Styles]
Format: Name, ...
Style: Default,...

[Events]
Format: Layer, Start, End, Style, Name, MarginV, MarginR, MarginL, Effect, Text
Dialogue: 0,0:00:01.00,0:00:04.50,Default,,0,0,0,,Hello, world.
```

- Full script header and style section
- Timestamp format: `H:MM:SS.cc` (centiseconds)
- Style derived from `ResolvedConfig` (font size proportional to `max_chars`)

## TXT Format

Plain transcript text, one line per whisper segment. No timing information. Uses raw segment text rather than processed subtitle blocks.

## JSON Format

```json
{
  "subtitles": [
    {"start": 1.0, "end": 4.5, "lines": ["Hello, world."]}
  ],
  "segments": [
    {"start": 1.0, "end": 4.5, "text": "Hello, world."}
  ],
  "config": {
    "max_chars": 42,
    "max_lines": 2
  }
}
```

Full metadata bundle. Useful for downstream processing or debugging.
