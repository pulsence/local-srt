# Configuration System

## Overview

All configuration is held in a single flat `ResolvedConfig` dataclass. There are no nested config sections.

## Resolution Order

Settings are applied in order (later values win):

1. `ResolvedConfig()` defaults (hardcoded in `models.py`)
2. JSON config file (`--config path/to/file.json`)
3. Mode preset (`--mode yt|shorts|podcast`)
4. Individual CLI flags (`--max-chars 30`, etc.)

CLI flags always win over preset and file values.

## Presets

Three built-in presets cover common use cases:

### `yt` (YouTube)

Standard two-line subtitles for landscape video.

```json
{
  "max_chars": 42,
  "max_lines": 2,
  "target_cps": 17.0,
  "min_dur": 1.0,
  "max_dur": 6.0,
  "allow_commas": true,
  "allow_medium": true,
  "prefer_punct_splits": false,
  "min_gap": 0.08,
  "pad": 0.0
}
```

### `shorts`

Single-line, fast-paced for vertical short-form content.

```json
{
  "max_chars": 18,
  "max_lines": 1,
  "target_cps": 18.0,
  "min_dur": 0.7,
  "max_dur": 3.0
}
```

### `podcast`

Two-line, slower pacing, prefers punctuation splits, slight padding.

```json
{
  "max_chars": 40,
  "max_lines": 2,
  "target_cps": 16.0,
  "min_dur": 0.9,
  "max_dur": 5.0,
  "prefer_punct_splits": true,
  "pad": 0.05
}
```

## JSON Config File Format

A config file is a flat JSON object. Only fields that differ from defaults need to be included:

```json
{
  "max_chars": 35,
  "target_cps": 16.0,
  "prefer_punct_splits": true
}
```

Unknown keys are silently ignored by `apply_overrides()`.

## Mode Aliases

| Alias | Resolves to |
| --- | --- |
| `youtube` | `yt` |
| `pod` | `podcast` |

## Adding a New Preset

1. Add an entry to `PRESETS` dict in `config.py`
2. Optionally add aliases to `MODE_ALIASES`
3. Add test coverage in `tests/test_config.py`
