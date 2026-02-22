# local_srt.cli

CLI entry point. Provides the `srtgen` command installed via `pyproject.toml`.

**Entry point:** `srtgen = "local_srt.cli:main"`

## Responsibilities

- Argument parsing (40+ flags via `argparse`)
- Config loading and override application
- Input expansion (files, directories, glob patterns)
- Model lifecycle (load once, reuse for batch)
- Event handler for rich terminal output (progress bars, colored output)
- Batch orchestration with `continue_on_error` support
- Model management subcommands (`--list-models`, `--download-model`, `--delete-model`, `--diagnose`)

## Key Argument Groups

| Group | Flags | Description |
| --- | --- | --- |
| Input | positional `inputs` | Files, directories, or glob patterns |
| Output | `-o`, `--outdir`, `--keep-structure` | Output path and directory layout |
| Format | `--format` | `srt` (default), `vtt`, `ass`, `txt`, `json` |
| Model | `--model`, `--device`, `--language` | Model size, device selection, language hint |
| Config | `--config`, `--mode` | JSON config file and preset name |
| Overrides | `--max-chars`, `--max-lines`, `--target-cps`, etc. | Per-run config overrides |
| Batch | `--continue-on-error`, `--dry-run`, `--overwrite` | Batch control |
| Management | `--list-models`, `--download-model`, `--delete-model`, `--diagnose` | Model cache operations |

## Event Handler

The CLI creates a local event handler function (closure) that subscribes to the `EventEmitter`. It translates library events to terminal output:

- `LogEvent` → print to stdout/stderr
- `ProgressEvent` → inline progress bar with ETA
- `StageEvent` → stage banner
- `FileStartEvent` / `FileCompleteEvent` → file start/end messages
- `ModelLoadEvent` → model loading notice with device info
