# Testing Guide

## Test Strategy

Local SRT uses pytest with a fast, isolated test suite. All tests should run in under 5 seconds on a standard machine. Tests mock external processes (ffmpeg, whisper model) so no GPU, CUDA, or media files are required.

## Test Structure

```text
tests/
├── __init__.py
├── test_models.py               # ResolvedConfig, SubtitleBlock, WordItem dataclasses
├── test_config.py               # Preset loading, config file loading, override application
├── test_text_processing.py      # Text normalization, wrapping, splitting, timing distribution
├── test_subtitle_generation.py  # Chunking, silence alignment, timing polish
├── test_output_writers.py       # SRT/VTT/ASS/TXT/JSON format correctness
├── test_audio.py                # Silence detection, WAV conversion (mocked ffmpeg)
├── test_batch.py                # Input expansion, output path calculation, preflight
├── test_system.py               # Dependency checks, command execution (mocked)
├── test_logging_utils.py        # Duration formatting
├── test_events.py               # Event dataclasses, EventEmitter pub/sub
└── test_api.py                  # Public API (mocked model + ffmpeg)
```

## Running Tests

```bash
# All tests with coverage
python -m pytest tests/ -v --cov=local_srt --cov-report=html

# Specific file
python -m pytest tests/test_subtitle_generation.py -v

# Fail fast
python -m pytest tests/ -x
```

## Coverage Targets

| Module group | Target |
| --- | --- |
| Core logic (`subtitle_generation`, `text_processing`) | >90% |
| Config, models, events, batch | >90% |
| System utilities, output writers | >80% |
| CLI (`cli.py`) | >70% |

## Test Configuration

Defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
  "-v",
  "--cov=local_srt",
  "--cov-report=term-missing",
  "--cov-report=html",
  "--html=report.html",
  "--self-contained-html",
]
```

## Mocking Approach

Tests use `pytest-mock` to mock:

- `faster_whisper.WhisperModel` — avoid loading actual models
- `subprocess.run` / `run_cmd_text` — avoid running ffmpeg
- File system operations where needed

Tests do **not** require:

- GPU or CUDA
- ffmpeg installed
- Any audio/video files
- Internet access

## Key Test Patterns

Most fixtures are inline within test modules rather than in a shared `conftest.py`.

Common patterns:

- `ResolvedConfig()` with default settings for baseline
- Manually constructed `SubtitleBlock` and `WordItem` lists as inputs to subtitle generation tests
- `mocker.patch("local_srt.system.run_cmd_text")` to stub ffmpeg calls
