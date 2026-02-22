# local_srt.config

Configuration loading, preset definitions, and override application.

## Constants

### `PRESETS`

Built-in mode presets. Keys are canonical mode names.

| Mode | `max_chars` | `max_lines` | `max_dur` | `target_cps` | Notes |
| --- | --- | --- | --- | --- | --- |
| `yt` | 42 | 2 | 6.0 | 17.0 | Standard YouTube subtitles |
| `shorts` | 18 | 1 | 3.0 | 18.0 | Vertical short-form video |
| `podcast` | 40 | 2 | 5.0 | 16.0 | Prefer punctuation splits, 0.05s padding |

### `MODE_ALIASES`

User-friendly aliases mapped to canonical preset names:

| Alias | Canonical |
| --- | --- |
| `youtube` | `yt` |
| `pod` | `podcast` |

## Functions

### `load_config_file(path: Path) -> dict`

Reads a JSON config file and returns a raw dict of override values.

### `apply_overrides(base: ResolvedConfig, overrides: dict) -> ResolvedConfig`

Creates a new `ResolvedConfig` by merging `overrides` onto `base`. Unknown keys are silently ignored.

## Config Hierarchy

Resolution order (later overrides earlier):

1. `ResolvedConfig()` defaults
2. JSON config file (`--config`)
3. Mode preset (`--mode`)
4. CLI argument overrides (individual flags)
