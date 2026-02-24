# Local SRT Development Plan

Implementation plan derived from [PLAN_RESEARCH.md](./PLAN_RESEARCH.md). Each phase represents a major feature or architectural milestone. Phases must be completed in order — later phases depend on earlier ones.

## Completion Checklist

Apply after every task block:

1. Run `pytest tests/ -v` — all tests must pass before committing
2. Update `tests/` with tests for new or modified behaviour
3. Update `USER_GUIDE.md` to reflect any new or changed flags, behaviours, or workflows
4. Update Architecture and Key Files sections in `CLAUDE.md` as needed
5. Run `git add` on all modified files and `git commit` with a message following the format in `COMMIT_MESSAGE.md`

---

## Phase 1: Initial Documentation (COMPLETED)

Establish a user-facing guide that reflects the current state of the tool before any new features are added. Every subsequent phase updates this guide as its features ship. `CHANGELOG.md` is used exclusively for version-tagged changelog entries — not general documentation.

### 1.1: Create USER_GUIDE.md (COMPLETED)

Document the current tool as-is: installation, all CLI flags, presets, batch processing, and config file usage. This becomes the canonical user reference and is updated incrementally in every later phase.

**Tasks**:

- Create `USER_GUIDE.md` in the project root with the following sections:
  - **Installation** — `pip install local-srt`, ffmpeg requirement, model download on first run
  - **Basic Usage** — `srtgen input.mp4 output.srt`, supported input formats, supported output formats (`--format srt/vtt/ass/txt/json`)
  - **Models** — `--model tiny/base/small/medium/large-v3`, trade-offs, default
  - **Language** — `--language` flag, auto-detect default
  - **Presets** — `--preset shorts/yt/podcast` with a table of what each preset changes
  - **Formatting Options** — `--max-chars`, `--max-lines`, `--target-cps`, `--min-dur`, `--max-dur`, and other formatting flags, with defaults
  - **Silence Settings** — `--silence-min-dur`, `--silence-threshold-db`
  - **Transcription Options** — `--vad-filter / --no-vad-filter`, `--word-timestamps`
  - **Batch Processing** — directory input, `--recursive`, output directory, naming conventions
  - **Config File** — `--config path/to/config.json`, JSON structure, which keys are accepted
  - **Diagnostics** — `srtgen --diagnose` output explained
  - **Dry Run** — `--dry-run` flag
- Create `CHANGELOG.md` in the project root with a version 0.2.x section summarising what the current codebase does (based on recent git commits)
- Run `pytest tests/ -v` to confirm documentation work did not affect the codebase

**Files to create**:

- `USER_GUIDE.md`
- `CHANGELOG.md`

**Success criteria**: `USER_GUIDE.md` exists and documents every current CLI flag accurately. `CHANGELOG.md` exists with at least one version entry. No production source files are modified.

---

### 1.2: Code Review — Phase 1 (COMPLETED)

**Tasks**:

- Verify all currently implemented flags are documented in `USER_GUIDE.md`
- Verify `CHANGELOG.md` entries are accurate against the codebase
- Verify no production source files were modified in this phase

---

## Phase 2: Test Infrastructure (COMPLETED)

Implement before any other code changes. All subsequent changes are only safe once regression coverage exists.

### 2.1: Track A — Deterministic Pipeline Tests (COMPLETED)

Create the foundational test suite using mocked whisper output. Tests the full post-transcription pipeline (chunking, silence alignment, polishing) with no audio files and no model calls — fully deterministic on every machine.

**Tasks**:

- Create `tests/conftest.py` with shared fixtures:
  - `mock_word_items(words: List[Tuple[str, float, float]]) -> List[WordItem]` — builds a `WordItem` list from `(text, start, end)` tuples
  - `mock_segments(data: List[dict]) -> List[Segment]` — builds mock whisper `Segment` namedtuples
  - `mock_silence_intervals() -> List[Tuple[float, float]]` — returns a fixed silence list for reuse
- Create `tests/helpers.py`:
  - `compare_srt(actual_path, expected_path, time_tol=0.05)` — asserts text lines match exactly and timestamps match within ±0.05s; prints a unified diff on failure
- Create `tests/test_pipeline.py` with at minimum these scenarios:
  - Single sentence, no silences: words chunk into one block, correct text and timing
  - Multi-sentence with silence gap: `split_words_on_silence()` splits before chunking, blocks do not straddle the silence
  - Max-chars boundary: a word list that forces a line wrap at the `max_chars` limit
  - Full chain for each scenario: words → `chunk_words_to_subtitles()` → `apply_silence_alignment()` → `hygiene_and_polish()` → compare against expected `List[SubtitleBlock]`
- Run `pytest tests/ -v` — all tests must pass

**Files to create**:

- `tests/conftest.py`
- `tests/helpers.py`
- `tests/test_pipeline.py`

**Success criteria**: `pytest tests/ -v` passes with all Track A tests included. At least 3 full-pipeline test cases: single sentence, silence-split, and line-wrap. No audio files or model calls in any Track A test.

---

### 2.2: Track B — Integration Tests with Real Audio (COMPLETED)

Extend the test suite with end-to-end tests using real voice audio run through actual faster-whisper with `temperature=0` (deterministic). Output is compared against committed baseline SRT files. Track B tests are opt-in (`pytest -m integration`) so they do not slow the default run.

**Tasks**:

- Add to `tests/conftest.py`:
  - `pytest_addoption`: register `--update-baselines` flag
  - `pytest_configure`: register `integration` and `slow` markers
  - `update_baselines(request)` fixture: returns `True` when `--update-baselines` is passed
- Create `tests/fixtures/audio/` directory and commit placeholder `.gitkeep`
- **User action required**: record and commit 4 WAV audio fixtures (16kHz, mono, 16-bit):
  - `tests/fixtures/audio/single_sentence.wav` (~5s, one clear sentence)
  - `tests/fixtures/audio/paused_speech.wav` (~15s, speech with 2–3 clear pauses)
  - `tests/fixtures/audio/continuous_speech.wav` (~20s, flowing speech, no significant pauses)
  - `tests/fixtures/audio/multi_sentence.wav` (~25s, 4–5 sentences with natural rhythm)
- Create `tests/fixtures/baselines/` directory
- Create `tests/test_integration.py`:
  - Mark all tests with `@pytest.mark.integration`
  - For each audio fixture: run full pipeline with `temperature=0` on CPU, load model once per session
  - If `--update-baselines`: write actual SRT output to `tests/fixtures/baselines/<name>.srt`
  - Otherwise: call `compare_srt(actual, baseline)` — fail with diff if output differs
- Generate initial baselines: `pytest tests/test_integration.py --update-baselines`
- Review all generated baseline SRT files — correct any transcription errors if needed
- Commit `tests/fixtures/audio/`, `tests/fixtures/baselines/`, and `tests/test_integration.py`
- Run `pytest -m integration` to confirm tests pass against baselines

**Files to create**:

- `tests/test_integration.py`
- `tests/fixtures/audio/` (user provides WAV recordings)
- `tests/fixtures/baselines/` (generated, then committed)

**Files to modify**:

- `tests/conftest.py`

**Success criteria**: `pytest -m integration` passes against all baselines. `--update-baselines` regenerates baseline files without asserting. Track B tests are absent from the default `pytest` run. Fixture WAVs and baselines are committed to the repository.

---

### 2.3: Code Review — Phase 2 (COMPLETED)

**Tasks**:

- Verify no production source files were modified in this phase
- Verify Track A tests are fully independent of audio files and model calls
- Verify Track B tests are excluded from the default `pytest` run
- Verify `compare_srt()` handles edge cases: empty SRT, single cue, mismatched cue counts
- Run `pytest tests/ -v && pytest -m integration`

---

### 2.4: Changelog — Phase 2 (COMPLETED)

**Tasks**:

- Write Phase 2 entry to `CHANGELOG.md` (unreleased): new test infrastructure, track descriptions, fixture file locations
- No `USER_GUIDE.md` update needed — no user-facing changes in this phase

---

## Phase 3: Architecture Refactoring (COMPLETED)

All changes in this phase are intentionally breaking. No backwards compatibility shims, aliases, or migration helpers are added anywhere.

### 3.1: Config Class Restructuring (COMPLETED)

Replace the flat `ResolvedConfig` dataclass with three nested sub-configs (`FormattingConfig`, `TranscriptionConfig`, `SilenceConfig`). Rewrite `apply_overrides` to accept nested dicts. Update `PRESETS` to the new nested structure. All callers are updated in the same change — no transition period.

**Tasks**:

- In `src/local_srt/models.py`:
  - Add `FormattingConfig` dataclass: `max_chars`, `max_lines`, `target_cps`, `min_dur`, `max_dur`, `allow_commas`, `allow_medium`, `prefer_punct_splits`, `min_gap`, `pad`
  - Add `TranscriptionConfig` dataclass: `vad_filter`, `condition_on_previous_text`, `no_speech_threshold`, `log_prob_threshold`, `compression_ratio_threshold`, `initial_prompt` (all with fw defaults — see Parameter Exposure in 3.4)
  - Add `SilenceConfig` dataclass: `silence_min_dur`, `silence_threshold_db`
  - Rewrite `ResolvedConfig` as a container: `formatting: FormattingConfig`, `transcription: TranscriptionConfig`, `silence: SilenceConfig` — each using `field(default_factory=...)`
  - Remove `use_silence_split` and `word_timestamps` from the flat struct (coordinate with 3.3)
- In `src/local_srt/config.py`:
  - Rewrite `PRESETS` to nested dict format: `{"shorts": {"formatting": {"max_chars": 18, ...}, "transcription": {...}, "silence": {...}}}`
  - Rewrite `apply_overrides(base: ResolvedConfig, overrides: dict) -> ResolvedConfig` to accept nested dicts and recursively merge into sub-config dataclasses using `dataclasses.replace()`
  - Remove `MODE_ALIASES` (replaced by `PipelineMode` in 3.2)
- Update all attribute access throughout the codebase from flat (`cfg.max_chars`) to nested (`cfg.formatting.max_chars`):
  - `src/local_srt/core.py`
  - `src/local_srt/api.py`
  - `src/local_srt/cli.py`
  - `src/local_srt/batch.py`
  - `src/local_srt/subtitle_generation.py`
  - `src/local_srt/output_writers.py`
- Update all test files that access config fields directly
- Run `pytest tests/ -v` — fix all failures before proceeding

**Files to modify**:

- `src/local_srt/models.py`
- `src/local_srt/config.py`
- `src/local_srt/core.py`
- `src/local_srt/api.py`
- `src/local_srt/cli.py`
- `src/local_srt/batch.py`
- `src/local_srt/subtitle_generation.py`
- `src/local_srt/output_writers.py`
- All test files that reference config fields

**Success criteria**: `cfg.formatting.max_chars` is the access pattern throughout. No flat `ResolvedConfig` field accesses remain. `apply_overrides` accepts `{"formatting": {"max_chars": 18}}`. No backwards compatibility shims exist anywhere. `pytest tests/ -v` passes.

---

### 3.2: Pipeline Mode Separation (COMPLETED)

Introduce `PipelineMode` as an enum that travels through the pipeline independently of `ResolvedConfig`. Presets control formatting parameters; modes control which pipeline path runs.

**Tasks**:

- In `src/local_srt/models.py`:
  - Add `import enum`
  - Add `class PipelineMode(enum.Enum): GENERAL = "general"; SHORTS = "shorts"; TRANSCRIPT = "transcript"`
- In `src/local_srt/config.py`:
  - Add `MODE_PIPELINE_DEFAULTS: Dict[PipelineMode, Dict]` — maps each mode to forced parameter overrides applied on top of the chosen preset
- In `src/local_srt/core.py`:
  - Add `mode: PipelineMode = PipelineMode.GENERAL` parameter to `transcribe_file_internal()`
  - Add dispatch stubs (full implementation in Phase 4): `if mode == PipelineMode.SHORTS: ...` and `if mode == PipelineMode.TRANSCRIPT: ...` — both fall through to the existing General path for now
- In `src/local_srt/api.py`:
  - Add `mode: PipelineMode = PipelineMode.GENERAL` to `transcribe_file()` and `transcribe_batch()`
- In `src/local_srt/cli.py`:
  - Add `--mode [general|shorts|transcript]` flag
  - Resolve the string to a `PipelineMode` enum value
  - Apply `MODE_PIPELINE_DEFAULTS[mode]` on top of the resolved preset before passing `cfg` to core
- Run `pytest tests/ -v` — fix all failures

**Files to modify**:

- `src/local_srt/models.py`
- `src/local_srt/config.py`
- `src/local_srt/core.py`
- `src/local_srt/api.py`
- `src/local_srt/cli.py`

**Success criteria**: `srtgen --mode general input.mp4 output.srt` works end-to-end. `PipelineMode` is accepted at every level: CLI → api → core. `pytest tests/ -v` passes.

---

### 3.3: Always-On Silence Alignment (COMPLETED)

Remove `use_silence_split` and user-facing `word_timestamps` as configurable flags. Silence detection, word-level timestamps, silence alignment, and silence-aware polishing become unconditional internal behavior in every pipeline mode.

**Tasks**:

- In `src/local_srt/models.py`: confirm `use_silence_split` is absent from `ResolvedConfig` (handled in 3.1); confirm `word_timestamps` is absent from `TranscriptionConfig` (it was never added — verify it is not present)
- In `src/local_srt/core.py`:
  - Remove all `if cfg.use_silence_split:` conditional guards
  - Make `detect_silences()` call unconditional
  - Make `apply_silence_alignment()` call unconditional
  - Make `hygiene_and_polish(silence_intervals=...)` call unconditional
  - Set `word_timestamps=True` unconditionally in `model.transcribe()`
- In `src/local_srt/config.py`: remove `use_silence_split` and `word_timestamps` from all preset definitions if present
- In `src/local_srt/api.py` and `src/local_srt/cli.py`: remove any `--word-timestamps` or `use_silence_split` parameters if they were exposed
- Update any test fixtures or mocks that set these flags
- Run `pytest tests/ -v` — fix all failures

**Files to modify**:

- `src/local_srt/core.py`
- `src/local_srt/config.py`
- `src/local_srt/api.py`
- `src/local_srt/cli.py`
- Test files that mock `use_silence_split` or `word_timestamps`

**Success criteria**: Zero references to `use_silence_split` or user-facing `word_timestamps` remain in the codebase. Silence alignment always runs regardless of mode. `pytest tests/ -v` passes.

---

### 3.4: Transcription Parameter Exposure (COMPLETED)

Wire all `TranscriptionConfig` fields into the `model.transcribe()` call and expose them in the CLI. These parameters are the primary diagnostic tools for the missing-text bug.

**Tasks**:

- Confirm `TranscriptionConfig` (added in 3.1) contains all of these fields with the listed faster-whisper defaults:
  - `condition_on_previous_text: bool = True`
  - `no_speech_threshold: float = 0.6`
  - `log_prob_threshold: float = -1.0`
  - `compression_ratio_threshold: float = 2.4`
  - `initial_prompt: str = ""`
- In `src/local_srt/core.py`: update `model.transcribe()` call to pass all `TranscriptionConfig` fields: `vad_filter`, `condition_on_previous_text`, `no_speech_threshold`, `log_prob_threshold`, `compression_ratio_threshold`, and `initial_prompt or None`
- In `src/local_srt/cli.py`: add flags for each tunable parameter:
  - `--no-condition-on-previous-text` (boolean flag, sets to False)
  - `--no-speech-threshold FLOAT`
  - `--log-prob-threshold FLOAT`
  - `--compression-ratio-threshold FLOAT`
  - `--vad-filter / --no-vad-filter`
- Run `pytest tests/ -v`

**Files to modify**:

- `src/local_srt/core.py`
- `src/local_srt/cli.py`

**Success criteria**: `srtgen --no-speech-threshold 0.4 --no-condition-on-previous-text input.mp4 output.srt` runs without error. All `TranscriptionConfig` fields are forwarded to `model.transcribe()`. `pytest tests/ -v` passes.

---

### 3.5: Code Review — Phase 3 (COMPLETED)

**Tasks**:

- Search codebase for flat `cfg.max_chars`, `cfg.vad_filter`, etc. — must find zero results
- Search for `use_silence_split` and user-facing `word_timestamps` — must find zero results
- Verify `PipelineMode` flows correctly: CLI flag → enum → api → core parameter
- Verify `apply_overrides` correctly merges nested dicts into sub-config dataclasses
- Verify no backwards compatibility layers, aliases, or deprecated shims were added anywhere
- Run `pytest tests/ -v && pytest -m integration`

---

### 3.6: Changelog — Phase 3 (COMPLETED)

**Tasks**:

- Write Phase 3 entry to `CHANGELOG.md`: all breaking API changes — new nested config structure, `PipelineMode` enum, removed `use_silence_split` flag, new `--mode` and diagnostic flags
- Update `USER_GUIDE.md`:
  - Replace the flat config flags section with the new nested structure
  - Add `--mode` flag documentation (General as default, Shorts and Transcript as coming in Phase 4)
  - Add the new diagnostic flags: `--no-condition-on-previous-text`, `--no-speech-threshold`, `--log-prob-threshold`, `--compression-ratio-threshold`
  - Remove `--word-timestamps` and `--use-silence-split` from the guide
- Update `README.md` with the latest usage information.

---

## Phase 4: Output Modes

### 4.1: Shorts Mode

Implement `PipelineMode.SHORTS` dispatch. Shorts mode produces two output files: a sentence-level SRT for editing and a word-level SRT for dynamic animation. Both outputs are derived from the same whisper word-timestamp run.

**Tasks**:

- Review `words_to_subtitles()` in `src/local_srt/subtitle_generation.py` — confirm it produces one `SubtitleBlock` per word with correct start/end
- In `src/local_srt/core.py`:
  - When `mode == PipelineMode.SHORTS`:
    - Sentence-level: call `chunk_words_to_subtitles(words, cfg, silences)` as normal → write to `output_path`
    - Word-level: call `words_to_subtitles(words)` → write to `word_output_path`
  - Add `word_output_path: Optional[Path] = None` parameter to `transcribe_file_internal()`
- In `src/local_srt/api.py`: add `word_output_path: Optional[Path] = None` to `transcribe_file()`
- In `src/local_srt/cli.py`:
  - When `--mode shorts`: derive default word-level output path as `<stem>.words.srt` in the same directory as `output_path`
  - Add `--word-srt PATH` flag to override the word-level output path
- Add tests to `tests/test_pipeline.py`:
  - Shorts pipeline produces two `SubtitleBlock` lists: one chunked (sentence-level), one per-word (word-level)
  - Word-level blocks have single-word text and correct timestamps
- Run `pytest tests/ -v`
- Run `git add` on all modified files and `git commit` with a message following the format in `COMMIT_MESSAGE.md`

**Files to modify**:

- `src/local_srt/core.py`
- `src/local_srt/api.py`
- `src/local_srt/cli.py`
- `tests/test_pipeline.py`

**Success criteria**: `srtgen --mode shorts input.mp4 output.srt` produces `output.srt` (sentence-level) and `output.words.srt` (word-level). Both are valid SRT files. `pytest tests/ -v` passes.

---

### 4.2: Transcript Mode

Implement `PipelineMode.TRANSCRIPT` with a new chunking strategy that merges segments into large, paragraph-like blocks.

**Tasks**:

- In `src/local_srt/subtitle_generation.py`: implement `chunk_segments_to_transcript_blocks(segments, cfg, silences) -> List[SubtitleBlock]`:
  - Merge consecutive segments into accumulating blocks
  - Split at silence boundaries (any silence gap from `silences` that falls within the accumulated block)
  - Split when accumulated duration exceeds `cfg.formatting.max_dur`
  - Apply line-wrapping within each block using `cfg.formatting.max_chars` and `cfg.formatting.max_lines`
  - Return a `List[SubtitleBlock]`
- In `src/local_srt/config.py`: add `"transcript"` preset with nested structure:
  - `formatting`: `max_chars=80`, `max_lines=4`, `max_dur=30.0`, `min_dur=2.0`, `prefer_punct_splits=True`
  - `transcription` and `silence`: use defaults
- In `src/local_srt/core.py`: when `mode == PipelineMode.TRANSCRIPT`, dispatch to `chunk_segments_to_transcript_blocks()` instead of the standard path
- Add `speaker: Optional[str] = None` field to `SubtitleBlock` in `src/local_srt/models.py`
- In `src/local_srt/output_writers.py`: when `block.speaker` is not None, prepend `"{block.speaker}: "` to the block text in `write_srt()`, `write_vtt()`, and `write_ass()`
- Add tests to `tests/test_pipeline.py`:
  - Transcript chunker produces larger blocks than General mode given the same segment list
  - Blocks split at silence boundaries
  - Speaker prefix rendered correctly when `block.speaker` is set
- Run `pytest tests/ -v`
- Run `git add` on all modified files and `git commit` with a message following the format in `COMMIT_MESSAGE.md`

**Files to modify**:

- `src/local_srt/subtitle_generation.py`
- `src/local_srt/config.py`
- `src/local_srt/core.py`
- `src/local_srt/models.py`
- `src/local_srt/output_writers.py`
- `tests/test_pipeline.py`

**Success criteria**: `srtgen --mode transcript input.mp4 output.srt` produces valid SRT with large, multi-sentence blocks. Blocks split at silence boundaries and at the `max_dur` limit. Speaker prefix renders when `block.speaker` is set. `pytest tests/ -v` passes.

---

### 4.3: Code Review — Phase 4

**Tasks**:

- Manually verify all three modes produce valid SRT on a real file: `srtgen --mode general`, `--mode shorts`, `--mode transcript`
- Verify Shorts produces two output files with correct naming
- Verify Transcript blocks are larger than General blocks on the same input
- Verify `speaker` field plumbs through `SubtitleBlock` → output writers correctly
- Run `pytest tests/ -v && pytest -m integration`
- Run `git add` on all modified files and `git commit` with a message following the format in `COMMIT_MESSAGE.md`

---

### 4.4: Changelog — Phase 4

**Tasks**:

- Write Phase 4 entry to `CHANGELOG.md`: `--mode shorts` (dual-output), `--mode transcript` (large blocks), new `transcript` preset
- Update `USER_GUIDE.md`:
  - Complete the `--mode` section with full Shorts and Transcript documentation
  - Shorts: explain dual-output (sentence SRT + word SRT), `--word-srt` override, animation workflow use case
  - Transcript: explain large-block format, silence-based splitting, speaker prefix format
- Run `pytest tests/ -v`
- Run `git add` on all modified files and `git commit` with a message following the format in `COMMIT_MESSAGE.md`

---

## Phase 5: Text Accuracy

### 5.1: Script Input Tier 1 — Initial Prompt

Parse `.docx` Word documents and pass their text as `initial_prompt` to `model.transcribe()`. This biases whisper toward the script's vocabulary, punctuation style, and capitalization with no additional ML dependencies.

**Tasks**:

- Add `python-docx` to project dependencies in `pyproject.toml`
- Create `src/local_srt/script_reader.py`:
  - `read_docx(path: Path) -> str`: open `.docx` with `python-docx`, iterate `doc.paragraphs`, join non-empty paragraphs with a single space; handle list items (those with `style.name` starting with `"List"`) as individual sentence units
  - Truncate output to approximately 900 characters (~224 whisper tokens) — return the truncated string
- In `src/local_srt/core.py`: pass `cfg.transcription.initial_prompt or None` to `model.transcribe(initial_prompt=...)`
- In `src/local_srt/cli.py`:
  - Add `--prompt TEXT` flag: sets `cfg.transcription.initial_prompt` directly
  - Add `--prompt-file PATH` flag: if `.docx`, call `read_docx()`; if plain text, read as UTF-8 string; set on `cfg.transcription.initial_prompt`
- In `src/local_srt/api.py`: add `initial_prompt: str = ""` parameter; set on the `TranscriptionConfig` before passing to core
- Create `tests/test_script_reader.py`:
  - Test `read_docx()` with a minimal `.docx` fixture containing paragraphs and a bulleted list
  - Test truncation behaviour at the character limit
- Run `pytest tests/ -v`
- Run `git add` on all modified files and `git commit` with a message following the format in `COMMIT_MESSAGE.md`

**Files to create**:

- `src/local_srt/script_reader.py`
- `tests/test_script_reader.py`
- `tests/fixtures/script_reader/sample.docx` (minimal fixture for unit tests)

**Files to modify**:

- `pyproject.toml`
- `src/local_srt/core.py`
- `src/local_srt/cli.py`
- `src/local_srt/api.py`

**Success criteria**: `srtgen --prompt-file script.docx input.mp4 output.srt` runs without error. `read_docx()` correctly extracts text from paragraphs and list items. `pytest tests/ -v` passes.

---

### 5.2: Corrected SRT Alignment

Accept a corrected sentence-level SRT and derive a word-level SRT by aligning corrected words to whisper word timestamps via `difflib.SequenceMatcher`. This is the core workflow for Shorts: correct the sentence SRT, re-derive the word SRT.

**Tasks**:

- Create `src/local_srt/alignment.py`:
  - `parse_srt_to_words(srt_path: Path) -> List[str]`: parse all cue text from an SRT file, split on whitespace, normalize (lowercase, strip punctuation) for matching — return normalized word list alongside original word list as a `(normalized, original)` pair list
  - `align_corrected_srt(corrected_srt: Path, words: List[WordItem]) -> List[WordItem]`:
    - Parse corrected SRT to normalized word list
    - Normalize whisper `WordItem` text for matching
    - Run `difflib.SequenceMatcher(None, whisper_normalized, corrected_normalized)`
    - For `equal` and `replace` opcodes: keep whisper start/end, use corrected original text
    - For `insert` opcodes (words in corrected but not whisper): distribute time proportionally between the surrounding whisper timestamps
    - For `delete` opcodes (words in whisper but not corrected): drop the word
    - Return corrected `List[WordItem]`
- In `src/local_srt/core.py`:
  - After `collect_words()`: if `correction_srt` is provided, call `align_corrected_srt(correction_srt, words)` and replace `words` with the result
- In `src/local_srt/api.py`: add `correction_srt: Optional[Path] = None` parameter
- In `src/local_srt/cli.py`: add `--correction-srt PATH` flag
- Create `tests/test_alignment.py` with cases:
  - Exact match: corrected text equals whisper output → timestamps unchanged
  - One word changed: timestamps preserved, corrected text used
  - One word inserted in corrected: time distributed
  - One word deleted from corrected: word dropped
- Run `pytest tests/ -v`
- Run `git add` on all modified files and `git commit` with a message following the format in `COMMIT_MESSAGE.md`

**Files to create**:

- `src/local_srt/alignment.py`
- `tests/test_alignment.py`

**Files to modify**:

- `src/local_srt/core.py`
- `src/local_srt/api.py`
- `src/local_srt/cli.py`

**Success criteria**: `srtgen --mode shorts --correction-srt corrected.srt input.mp4 output.srt` produces a corrected word-level SRT. Alignment handles minor corrections (1–5 word changes) with correct timestamps. `pytest tests/ -v` passes.

---

### 5.3: Script Input Tier 2 — Script-Guided Text Substitution

Use the `.docx` script as the authoritative text source at the sentence level. Script sentences replace matched whisper segment text while preserving whisper timestamps. Unmatched audio (ad-libs, skipped sections) retains whisper text.

**Tasks**:

- In `src/local_srt/alignment.py`: add `align_script_to_segments(script_sentences: List[str], segments: List[Any]) -> List[Any]`:
  - Tokenize script into sentence list: split on `.`, `!`, `?`, `;`; each list item from `.docx` is already a sentence unit (from `read_docx()`)
  - Build flat normalized text from whisper segments
  - Run `difflib.SequenceMatcher` at the sentence level (match script sentences to segment text spans)
  - For matched pairs: replace segment group text with script sentence, keep whisper start/end
  - For unmatched whisper segments: keep whisper text unchanged
  - Return updated segment list
- In `src/local_srt/core.py`: after transcription, if `script_path` is provided:
  - Call `read_docx(script_path)` to get script text
  - Tokenize into sentences
  - Call `align_script_to_segments()` to substitute matched segments
  - Continue to chunking with the updated segment list
- In `src/local_srt/api.py`: add `script_path: Optional[Path] = None` parameter
- In `src/local_srt/cli.py`: add `--script PATH` flag; load via `read_docx()` for `.docx`, plain text read for `.txt`
- Add sentence-level alignment tests to `tests/test_alignment.py`:
  - Script matches all segments: all text replaced with script version
  - Script has one extra sentence (user skipped it in recording): extra sentence dropped, surrounding segments preserved
  - Script is missing one sentence (user ad-libbed): ad-lib kept as whisper text
- Run `pytest tests/ -v`
- Run `git add` on all modified files and `git commit` with a message following the format in `COMMIT_MESSAGE.md`

**Files to modify**:

- `src/local_srt/alignment.py`
- `src/local_srt/core.py`
- `src/local_srt/api.py`
- `src/local_srt/cli.py`
- `tests/test_alignment.py`

**Success criteria**: `srtgen --script script.docx input.mp4 output.srt` produces output where matched text uses script punctuation and capitalization. Ad-libbed audio retains whisper text. `pytest tests/ -v` passes.

---

### 5.4: Code Review — Phase 5

**Tasks**:

- Review `alignment.py` for edge cases: empty word list, all words deleted, all words inserted, corrected SRT with more words than whisper
- Verify `.docx` parsing handles both paragraph body text and list-item paragraphs
- Verify `--prompt-file`, `--correction-srt`, and `--script` flags operate independently and do not interfere when combined
- Verify `initial_prompt` is passed as `None` (not empty string) when unset — faster-whisper treats `None` and `""` differently
- Run `pytest tests/ -v && pytest -m integration`
- Run `git add` on all modified files and `git commit` with a message following the format in `COMMIT_MESSAGE.md`

---

### 5.5: Changelog — Phase 5

**Tasks**:

- Write Phase 5 entry to `CHANGELOG.md`: `--prompt-file`, `--script`, and `--correction-srt` flags
- Update `USER_GUIDE.md`:
  - Add **Script Input** section: `--prompt TEXT` and `--prompt-file PATH` with `.docx` support, behaviour explanation, token limit note
  - Add **Script-Guided Substitution** section: `--script PATH`, what it does, how unmatched audio is handled
  - Add **Corrected SRT Alignment** section: `--correction-srt PATH`, the Shorts correction workflow (generate sentence SRT → correct → re-derive word SRT)
- Run `pytest tests/ -v`
- Run `git add` on all modified files and `git commit` with a message following the format in `COMMIT_MESSAGE.md`

---

## Phase 6: Speaker Diarization

### 6.1: pyannote-audio Integration

Add optional pyannote-audio v3 as a separate install extra. Create a diarization module that wraps the pyannote pipeline and assigns speaker labels to segments.

**Tasks**:

- In `pyproject.toml`: add `[project.optional-dependencies]` entry: `diarize = ["pyannote.audio>=3.0"]`
- Create `src/local_srt/diarization.py`:
  - `is_diarization_available() -> bool`: try `import pyannote.audio`; return True/False without raising
  - `load_diarization_pipeline(hf_token: str) -> Any`: load `pyannote/speaker-diarization-3.1` from HuggingFace with the provided token; return the pipeline object
  - `run_diarization(pipeline: Any, audio_path: str) -> List[Tuple[float, float, str]]`: run the pipeline on the WAV file; return sorted list of `(start, end, speaker_label)` tuples
  - `assign_speakers(segments: List[Any], diarization: List[Tuple[float, float, str]]) -> List[Any]`: for each segment, find the diarization interval with the greatest overlap and assign its speaker label as a new attribute `segment.speaker`; return the updated segment list
- In `src/local_srt/cli.py`:
  - Add `--diarize` boolean flag
  - Add `--hf-token TOKEN` flag (fallback: read from `HF_TOKEN` environment variable)
  - Raise a clear error if `--diarize` is set but `pyannote.audio` is not installed (use `is_diarization_available()`)
- In `src/local_srt/api.py`: add `diarize: bool = False` and `hf_token: Optional[str] = None` parameters
- In `src/local_srt/core.py`: add `diarize: bool = False` and `hf_token: Optional[str] = None` parameters; wire to `load_diarization_pipeline()` and `assign_speakers()` (actual Transcript integration in 6.2)
- Add unit tests to a new `tests/test_diarization.py`:
  - `assign_speakers()` correctly labels segments given a mock diarization list
  - `is_diarization_available()` returns a bool without raising
- Run `pytest tests/ -v`
- Run `git add` on all modified files and `git commit` with a message following the format in `COMMIT_MESSAGE.md`

**Files to create**:

- `src/local_srt/diarization.py`
- `tests/test_diarization.py`

**Files to modify**:

- `pyproject.toml`
- `src/local_srt/core.py`
- `src/local_srt/api.py`
- `src/local_srt/cli.py`

**Success criteria**: `pip install local-srt[diarize]` installs pyannote without errors. `is_diarization_available()` returns `False` when pyannote is not installed and `True` when it is. `assign_speakers()` correctly maps mock diarization intervals to segments. `pytest tests/ -v` passes.

---

### 6.2: Transcript Mode Integration

Wire speaker diarization into the Transcript mode pipeline. Each `SubtitleBlock` receives the dominant speaker label from its time range. SRT output includes a speaker prefix.

**Tasks**:

- In `src/local_srt/core.py`:
  - When `diarize=True` and `mode == PipelineMode.TRANSCRIPT`:
    - After transcription, call `load_diarization_pipeline(hf_token)` (raise a clear error if `hf_token` is not set)
    - Call `run_diarization(pipeline, tmp_wav)` on the temp WAV file
    - Call `assign_speakers(seg_list, diarization_result)` to label segments
  - In `chunk_segments_to_transcript_blocks()` in `src/local_srt/subtitle_generation.py`: carry speaker label from segments to each block — if a block spans segments with different speakers, assign the speaker with the longest total duration in that block
- Verify `src/local_srt/output_writers.py` renders `"{block.speaker}: "` prefix when `block.speaker` is not None (added in 4.2)
- Add a test in `tests/test_pipeline.py` for Transcript chunking with mock speaker-labeled segments:
  - Single speaker throughout: all blocks share the same label
  - Speaker change at a silence boundary: blocks on each side have correct labels
- Run `pytest tests/ -v && pytest -m integration`
- Run `git add` on all modified files and `git commit` with a message following the format in `COMMIT_MESSAGE.md`

**Files to modify**:

- `src/local_srt/core.py`
- `src/local_srt/subtitle_generation.py`
- `tests/test_pipeline.py`

**Success criteria**: `srtgen --mode transcript --diarize --hf-token TOKEN input.mp4 output.srt` produces a speaker-labeled SRT with correct speaker prefixes. Speaker label assignment uses dominant-duration logic across multi-speaker blocks. `pytest tests/ -v` passes.

---

### 6.3: Code Review — Phase 6

**Tasks**:

- Verify `is_diarization_available()` guard prevents any `ImportError` when pyannote is not installed
- Verify diarization does not run unless `--diarize` is explicitly passed
- Verify `HF_TOKEN` environment variable is read as a fallback for `--hf-token`
- Verify speaker labels flow correctly: diarization intervals → segments → SubtitleBlocks → output file speaker prefix
- Run `pytest tests/ -v && pytest -m integration`
- Run `git add` on all modified files and `git commit` with a message following the format in `COMMIT_MESSAGE.md`

---

### 6.4: Changelog — Phase 6

**Tasks**:

- Write Phase 6 entry to `CHANGELOG.md`: `--diarize`, `--hf-token`, `pip install local-srt[diarize]`
- Update `USER_GUIDE.md`:
  - Add **Speaker Diarization** section: installation (`pip install local-srt[diarize]`), HuggingFace account and token setup, `--diarize` and `--hf-token` flags, `HF_TOKEN` environment variable, which modes support diarization, expected output format
  - Add a note in the Transcript Mode section that `--diarize` enables speaker-labeled output
- Run `pytest tests/ -v`
- Run `git add` on all modified files and `git commit` with a message following the format in `COMMIT_MESSAGE.md`

---

## Phase 7: Release Preparation

### 7.1: Final Documentation Review

Review all user-facing documentation for completeness and accuracy before tagging the release. Every flag and workflow documented in `USER_GUIDE.md` must match the actual implementation.

**Tasks**:

- Read `USER_GUIDE.md` in full and cross-check every flag and example against the current CLI implementation
- Read `README.md` and update it to reflect new features (installation extras, new flags, new modes, link to `USER_GUIDE.md`)
- Verify `CHANGELOG.md` contains entries for all five implementation phases with accurate descriptions
- Run the full test suite: `pytest tests/ -v && pytest -m integration`
- Manually run a representative command for each mode: `--mode general`, `--mode shorts`, `--mode transcript`
- Run `git add` on all modified files and `git commit` with a message following the format in `COMMIT_MESSAGE.md`

**Files to modify**:

- `USER_GUIDE.md`
- `README.md`

**Success criteria**: Every flag in the CLI is documented. `USER_GUIDE.md` has no references to removed flags (`--word-timestamps`, `--use-silence-split`). `CHANGELOG.md` covers all phases. `pytest tests/ -v && pytest -m integration` passes.

---

### 7.2: Version Bump to 0.3.0

**Tasks**:

- In `pyproject.toml`: update `version = "0.3.0"`
- In `src/local_srt/__init__.py`: update `__version__ = "0.3.0"`
- In `CHANGELOG.md`: promote the unreleased section to `## [0.3.0] — <release date>`
- Run `pytest tests/ -v` one final time
- Commit with message: `Release 0.3.0`

**Files to modify**:

- `pyproject.toml`
- `src/local_srt/__init__.py`
- `CHANGELOG.md`

**Success criteria**: `srtgen --version` outputs `0.3.0`. `pytest tests/ -v` passes. `CHANGELOG.md` `[0.3.0]` entry is dated and complete.

---

### 7.3: Code Review — Phase 7

**Tasks**:

- Verify version string is consistent across `pyproject.toml`, `__init__.py`, and `CHANGELOG.md`
- Verify no debug flags, print statements, or temporary code were left in the codebase
- Final `pytest tests/ -v && pytest -m integration` run
- Run `git add` on all modified files and `git commit` with a message following the format in `COMMIT_MESSAGE.md`
