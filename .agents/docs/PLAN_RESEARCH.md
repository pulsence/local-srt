# PLAN_RESEARCH.md — Feature & Change Research

Research and analysis for each planned feature and architectural change, assessed against the current codebase. Source: project [TODO](../../TODO) file.

---

## Test Infrastructure

**Implement this before any other new features** to ensure all subsequent changes can be validated.

### Current Test State

- 11 test files, all unit tests with mocked dependencies
- No integration or end-to-end tests
- No real audio files used in any test
- No baseline SRT files to compare against
- Strong individual module coverage; zero full-pipeline coverage

### Key Insight: Deterministic Whisper Output

faster-whisper with `temperature=0` enables pure greedy decoding with no stochastic fallback. With the same model version on CPU, output is **fully deterministic** across runs. This unlocks real-audio + real-whisper regression testing without flakiness.

### Three-Track Approach

#### Track A — Deterministic Pipeline Tests

Create `tests/test_pipeline.py`:

- Define a fixed list of mock `Segment` namedtuples mimicking whisper output
- Run the full post-transcription pipeline: `chunk_words_to_subtitles()` → `apply_silence_alignment()` → `hygiene_and_polish()`
- Pass known silence intervals as test input
- Compare the resulting `List[SubtitleBlock]` against hardcoded expected values exactly

Fully deterministic. No audio files required. Tests the entire subtitle-generation pipeline end-to-end.

#### Track B — Integration Tests with Real Audio

- 4–5 short (5–30s) voice audio samples committed to `tests/fixtures/audio/` (~320KB per 10s, ~1.5MB total — acceptable for git, since these are a smoke test that will not change frequently)
- Run with `temperature=0` on CPU for determinism
- Compare output SRT against baseline files in `tests/fixtures/baselines/`
- `--update-baselines` flag regenerates baselines when changes are intentional
- Track B tests require an explicit marker: `pytest -m integration`

Recommended audio fixtures:

| File | Duration | Content | Tests |
| --- | --- | --- | --- |
| `single_sentence.wav` | ~5s | One clear spoken sentence | Basic transcription + chunking |
| `paused_speech.wav` | ~15s | Speech with 2–3 clear pauses | Silence detection + alignment |
| `continuous_speech.wav` | ~20s | Flowing speech, no significant pauses | Chunking without silence splits |
| `multi_sentence.wav` | ~25s | 4–5 sentences with natural rhythm | Full pipeline stress test |

These should be recorded by the user (own voice). No copyright concerns.

#### Track C — Manual Pre-Release Tests

Full transcription of longer files with human review of output quality. Not automated. Run manually before releases to catch quality regressions not captured by deterministic tests.

### Dev Process Integration

```text
1. Record audio fixture files → commit to tests/fixtures/audio/
2. pytest tests/test_integration.py --update-baselines
     → generates tests/fixtures/baselines/*.srt
3. Review generated SRTs — correct if needed → commit baselines

On each code change:
4. pytest
     → Track A: deterministic pipeline tests (fast, default run)
5. pytest -m integration
     → Track B: real audio + real whisper (temperature=0) vs baselines
6. If test fails: shows unified diff of actual vs. expected SRT
7. If change is intentional: run --update-baselines, review diff, commit

Pre-release:
8. pytest -m slow
     → Track C: human review tests on longer files
```

### New Files Required

| File | Purpose |
| --- | --- |
| `tests/conftest.py` | Shared fixtures: `mock_segments()`, `fixture_audio_path()`, `baseline_path()`, `--update-baselines` pytest option |
| `tests/helpers.py` | `compare_srt(actual, expected, time_tol=0.05)` — unified diff on mismatch |
| `tests/test_pipeline.py` | Track A: deterministic mocked pipeline tests |
| `tests/test_integration.py` | Track B: real audio + real whisper (`temperature=0`) vs baselines |
| `tests/fixtures/audio/` | 4–5 voice WAV recordings |
| `tests/fixtures/baselines/` | Expected SRT output files (committed, updated intentionally) |

`compare_srt()` checks text lines exactly and timestamps within ±0.05s tolerance. On failure it outputs a unified diff so regressions are immediately visible.

`--update-baselines` is implemented via `pytest_addoption` in `conftest.py` — when set, writes actual output to baseline paths instead of asserting equality.

---

## Architecture Refactoring

### Pipeline Mode Separation

The codebase currently has no concept of pipeline mode — only formatting presets. Adding modes (General, Shorts, Transcript) requires a clean separation between:

- **`PipelineMode`** — controls which chunking function is called and which pipeline defaults are forced
- **`ResolvedConfig`** — contains formatting and transcription parameters only

Introduce `PipelineMode` as an enum passed independently through the pipeline, not stored in `ResolvedConfig`. The codebase is young enough that API breaks should happen now.

Changes required:

- Add `PipelineMode` enum to [models.py](../../src/local_srt/models.py): `GENERAL`, `SHORTS`, `TRANSCRIPT`
- `transcribe_file_internal()` in [core.py](../../src/local_srt/core.py) gains a `mode: PipelineMode` parameter
- Public API in [api.py](../../src/local_srt/api.py) gains `mode: PipelineMode`
- Add `--mode` flag to [cli.py](../../src/local_srt/cli.py) that resolves to a `PipelineMode`
- Add `MODE_PIPELINE_DEFAULTS` in [config.py](../../src/local_srt/config.py): maps each mode to forced parameter overrides
- In [core.py](../../src/local_srt/core.py), dispatch the chunking function based on `mode`

### Config Class Restructuring

`ResolvedConfig` currently mixes three distinct concerns in one flat dataclass with 16 fields. Restructuring into nested classes should happen at the same time as the pipeline mode separation, since `apply_overrides` will require changes regardless.

Current groupings in the flat struct:

1. **Formatting** — `max_chars`, `max_lines`, `target_cps`, `min_dur`, `max_dur`, `allow_commas`, `allow_medium`, `prefer_punct_splits`, `min_gap`, `pad`
2. **Transcription** — `vad_filter`, `word_timestamps` (becoming internal), `condition_on_previous_text` (to add), `no_speech_threshold` (to add), `log_prob_threshold` (to add), `compression_ratio_threshold` (to add), `initial_prompt` (to add)
3. **Silence** — `silence_min_dur`, `silence_threshold_db`

Proposed nested structure in [models.py](../../src/local_srt/models.py):

```python
@dataclass
class FormattingConfig:
    max_chars: int = 42
    max_lines: int = 2
    target_cps: float = 17.0
    min_dur: float = 1.0
    max_dur: float = 6.0
    allow_commas: bool = True
    allow_medium: bool = True
    prefer_punct_splits: bool = False
    min_gap: float = 0.08
    pad: float = 0.00

@dataclass
class TranscriptionConfig:
    vad_filter: bool = True
    condition_on_previous_text: bool = True
    no_speech_threshold: float = 0.6
    log_prob_threshold: float = -1.0
    compression_ratio_threshold: float = 2.4
    initial_prompt: str = ""

@dataclass
class SilenceConfig:
    silence_min_dur: float = 0.2
    silence_threshold_db: float = -35.0

@dataclass
class ResolvedConfig:
    formatting: FormattingConfig = field(default_factory=FormattingConfig)
    transcription: TranscriptionConfig = field(default_factory=TranscriptionConfig)
    silence: SilenceConfig = field(default_factory=SilenceConfig)
```

`apply_overrides` in [config.py](../../src/local_srt/config.py) will be rewritten to accept nested dicts (e.g., `{"formatting": {"max_chars": 18}}`). Dot-notation is not used. The `PRESETS` dict will be updated to the new nested structure at the same time. All of these changes are fully breaking — no backwards compatibility shims or aliases are left behind.

---

## Transcription Engine

### Always-On Silence Alignment

`use_silence_split` is currently a configurable `bool` in `ResolvedConfig`. There is no valid use case where disabling silence splitting produces better output — even in Transcript mode, splitting into silence-bounded chunks before merging into large blocks is correct behavior. The flag adds complexity for no benefit.

Changes required:

- Remove `use_silence_split: bool` from `ResolvedConfig` in [models.py](../../src/local_srt/models.py)
- Remove all `if cfg.use_silence_split:` guards in [core.py](../../src/local_srt/core.py) — silence detection, `apply_silence_alignment()`, and `hygiene_and_polish(silence_intervals=...)` become unconditional
- `word_timestamps` also becomes always-on — it is an internal implementation detail, not a user-facing flag; remove from `ResolvedConfig` and set unconditionally in [core.py](../../src/local_srt/core.py)
- Update any tests that mock `use_silence_split` or `word_timestamps`

### Missing Text Bug

A separate and undiagnosed problem: whole sections of text are absent from transcription output. The missing content is always at the **trailing end** of a segment, with the beginning correctly transcribed.

The `model.transcribe()` call in [core.py:117](../../src/local_srt/core.py) currently exposes only `vad_filter`, `language`, and `word_timestamps`. Many faster-whisper parameters that affect transcription completeness are not exposed:

| Parameter | fw Default | Effect |
| --- | --- | --- |
| `vad_filter` | `True` (we set this) | **Most likely cause.** VAD pre-screens audio and can aggressively cut trailing speech that is quieter than onset. Falling intonation on trailing syllables often drops below the VAD threshold. |
| `condition_on_previous_text` | `True` | Can cause decoder drift: the model predicts what comes next based on prior output and may skip ahead, stopping mid-sentence. |
| `no_speech_threshold` | `0.6` | Segments where the model's no-speech probability exceeds this are dropped entirely. |
| `compression_ratio_threshold` | `2.4` | Segments with repetitive text are discarded as hallucinations — can incorrectly drop valid speech. |
| `log_prob_threshold` | `-1.0` | Low-probability segments are dropped. |

Most likely culprits in order: `vad_filter=True` cutting quiet trailing speech, then `condition_on_previous_text=True` causing decoder drift, then threshold parameters discarding valid speech.

The diagnostic infrastructure must exist before a reproducing file is found. Once a problem file is identified, rapid iteration requires these parameters to already be tunable.

Diagnostic path (once a reproducing file is identified):

1. Test with `vad_filter=False` — if missing text appears, VAD is the cause; consider replacing with pyannote VAD (see Speaker Diarization)
2. Test with `condition_on_previous_text=False` — if that fixes it, decoder drift is the cause
3. Tune threshold parameters until behavior is correct

### Parameter Exposure

The `TranscriptionConfig` nested class (see Architecture Refactoring) handles parameter grouping cleanly. Parameters to add:

- `condition_on_previous_text: bool = True`
- `no_speech_threshold: float = 0.6`
- `log_prob_threshold: float = -1.0`
- `compression_ratio_threshold: float = 2.4`
- `initial_prompt: str = ""` (also used by Script Input)

All are passed directly to `model.transcribe()` in [core.py](../../src/local_srt/core.py).

---

## Output Modes

Mode controls pipeline dispatch (which chunking function runs and what defaults apply). Formatting parameters are set independently via presets. `PipelineMode` is passed separately from `ResolvedConfig` (see Architecture Refactoring).

### General Mode

Current default behavior. The `yt` preset (42 chars, 2 lines) is the effective General configuration. No pipeline changes required beyond the mode dispatch infrastructure.

### Shorts Mode

The `shorts` preset (18 chars, 1 line) already covers the formatting parameters. Additional Shorts-specific behavior:

- `word_timestamps` is always-on (per the Transcription Engine section), so the word-level path is automatically used
- `PipelineMode.SHORTS` dispatches to `chunk_words_to_subtitles()` with tight formatting
- Optional: single-word-per-block output via `words_to_subtitles()` (already implemented in [subtitle_generation.py](../../src/local_srt/subtitle_generation.py))
- Shorts produces **two outputs**: a sentence-level SRT and a word-level SRT, both needed for dynamic animation workflows (see Corrected SRT Alignment for the correction workflow)

### Transcript Mode

Not currently implemented. Produces standard SRT output with large blocks — the opposite of Shorts.

Changes required:

1. Add `"transcript"` preset to [config.py](../../src/local_srt/config.py): `max_chars=80`, `max_lines=4`, `max_dur=30.0`, `min_dur=2.0`, `prefer_punct_splits=True`
2. Add `chunk_segments_to_transcript_blocks()` in [subtitle_generation.py](../../src/local_srt/subtitle_generation.py): merges consecutive segments until a silence gap or duration threshold, producing large `SubtitleBlock`s
3. `PipelineMode.TRANSCRIPT` dispatches to the new function in [core.py](../../src/local_srt/core.py)
4. When diarization is enabled, each `SubtitleBlock` carries an optional `speaker: str | None` field and output includes a speaker prefix: `Speaker A: text`

---

## Speaker Diarization

Speaker diarization is a priority for the initial Transcript mode implementation, not a phase-2 addition.

### pyannote-audio v3

| Aspect | Detail |
| --- | --- |
| What it does | Labels each audio segment with a speaker identifier (SPEAKER_00, SPEAKER_01, …) |
| Accuracy | Excellent for 2–4 speakers; degrades with more speakers or heavy overlap |
| Dependencies | `pyannote.audio`, `torch`; ~1GB model download on first use |
| Access | HuggingFace account + model access approval (~1 minute) |
| Output | List of `(start, end, speaker_label)` segments |
| Integration | Run after transcription; match speaker segment to whisper segment by timestamp overlap |

### Benefits Beyond Diarization

Adding pyannote provides additional pipeline capabilities beyond speaker labeling:

#### Voice Activity Detection

pyannote's VAD pipeline is significantly more accurate than whisper's built-in `vad_filter`, particularly for trailing speech that falls below the onset volume — the most likely cause of the missing-text bug. It can replace or supplement `vad_filter=True` in `model.transcribe()`, and provides a concrete diagnostic path for the missing-text issue before a reproducing file is found.

#### Overlapped Speech Detection

Identifies segments where multiple speakers talk simultaneously. Useful for tagging or excluding cross-talk in Transcript output.

#### Speaker Change Detection

Even without full speaker labeling, pyannote can detect speaker boundaries — useful for natural segmentation in General and Transcript modes even when diarization is not explicitly requested.

#### Speaker Verification

Confirms whether two audio segments belong to the same speaker. Useful for merging consecutive segments from the same speaker in Transcript mode post-processing.

### Integration Approach

- `SubtitleBlock` gains `speaker: Optional[str] = None` in [models.py](../../src/local_srt/models.py)
- New optional module: `src/local_srt/diarization.py` — wraps the pyannote pipeline, returns `List[Tuple[float, float, str]]`
- In [core.py](../../src/local_srt/core.py): when diarization is enabled and `mode == TRANSCRIPT`, run diarization after transcription and label each segment
- Optional install: `pip install local-srt[diarize]`

---

## Text Accuracy

### Script Input

Users have Word document scripts (.docx) formatted as paragraphs or lists. These serve two purposes: improving transcription accuracy via vocabulary/style priming, and acting as an authoritative text source for punctuation and capitalization correction.

#### Tier 1 — Initial Prompt

faster-whisper's `initial_prompt` parameter feeds text to the model as ~224 tokens of prior context. The model treats this as already-transcribed audio, biasing subsequent token selection toward the same vocabulary, capitalization style, and punctuation style. It does not force specific words — it is a soft influence.

Even at Tier 1, providing the script as `initial_prompt` causes whisper to adopt the script's punctuation conventions and capitalization style.

`initial_prompt` is already planned as part of `TranscriptionConfig` (see Architecture Refactoring). Additional changes:

- New module: `src/local_srt/script_reader.py` — parses `.docx` files via `python-docx`, extracts plain text, and normalizes paragraphs and lists to a flat string suitable for `initial_prompt`
- Add `--prompt TEXT` and `--prompt-file PATH` to [cli.py](../../src/local_srt/cli.py)
- Note: `initial_prompt` is truncated to ~224 tokens; for long scripts, use only the opening portion or a representative excerpt

#### Tier 2 — Script-Guided Text Substitution

Uses the script as the authoritative text source. Maps script sentences to whisper segments via sequence matching, substituting script text while preserving whisper timestamps.

Algorithm:

1. Parse the `.docx` script into a flat list of sentences (split on strong punctuation; handle list items as individual sentences)
2. Collect whisper segments as a flat text sequence
3. Align script sentences to whisper segment groups using `difflib.SequenceMatcher` at sentence level
4. For each matched pair: use script sentence text, keep whisper segment timing
5. For unmatched segments (ad-libs, skipped sections): use whisper text — do not force script text onto audio that does not match

Result: output text matches the script's punctuation, capitalization, and proper nouns. Timing comes from whisper.

This shares implementation with the Corrected SRT Alignment module — both use `difflib.SequenceMatcher` at different granularities (sentence vs. word level).

New API parameter: `script_path: Optional[Path]` in [api.py](../../src/local_srt/api.py). New CLI flag: `--script <path>`.

### Corrected SRT Alignment

**Primary use case for Shorts**: the user needs both a sentence-level SRT and a word-level SRT to create dynamic animations. Whisper's word timing is generally accurate but whisper often mishears individual words, making word-level SRT correction impractical word by word. The practical workflow is:

1. Generate sentence-level SRT via normal transcription
2. Correct the sentence SRT manually (fix wrong words)
3. Feed the corrected SRT back to derive an accurate word-level SRT

WhisperX is not needed here — it addresses wrong timestamps, not wrong text. Word substitution via sequence matching solves this problem with no new ML dependencies.

#### Algorithm

```text
corrected_srt → flat word list
whisper words → List[WordItem]
                    ↓
          difflib.SequenceMatcher alignment
                    ↓
      matched: keep whisper timestamp, use corrected text
      inserted: distribute time proportionally
      deleted: drop word
                    ↓
          corrected List[WordItem]
```

Works well when the corrected SRT text is similar to whisper output (same approximate word count, minor corrections). Accuracy degrades for heavy rewrites where borrowed timestamps become unreliable.

#### New Files

- New module: [src/local_srt/alignment.py](../../src/local_srt/alignment.py) — houses `align_corrected_srt(corrected_srt: Path, words: List[WordItem]) -> List[WordItem]` and the sentence-level alignment for Script Input Tier 2
- New API parameter: `correction_srt: Optional[Path]` in [api.py](../../src/local_srt/api.py)
- New CLI flag: `--correction-srt <path>` in [cli.py](../../src/local_srt/cli.py)
- Applied in [core.py](../../src/local_srt/core.py) after `collect_words()`, before `chunk_words_to_subtitles()`

---

## Prioritization

| Feature / Change | Effort | Impact | Priority |
| --- | --- | --- | --- |
| **Test Infrastructure — Track A** (deterministic pipeline tests) | Low | High — enables safe work on all other items | **1** |
| **Test Infrastructure — Track B** (real audio baselines, `pytest -m integration`) | Medium | High — true regression coverage | **2** |
| **Architecture Refactoring** (`PipelineMode` enum + nested config classes) | Medium | High — API break; best done while codebase is young | **3** |
| **Transcription: Always-On Silence Alignment** (remove `use_silence_split` flag) | Low | Medium — simplifies config | **3** |
| **Transcription: Parameter Exposure** (`TranscriptionConfig` fields for diagnostics) | Low | High — enables missing-text investigation | **3** |
| **Script Input: Tier 1** (`initial_prompt` + `.docx` parsing) | Low | Medium — improves accuracy with no new ML deps | **4** |
| **Output Modes: Shorts** (`PipelineMode` dispatch + dual sentence/word-level output) | Medium | High — core use case | **5** |
| **Output Modes: Transcript** (new chunking function + preset) | High | High — new use case | **5** |
| **Corrected SRT Alignment** (`alignment.py`, word substitution) | Medium | Medium — depends on Shorts mode | **6** |
| **Script Input: Tier 2** (sentence-level substitution, `.docx` parsing) | Medium | Medium — shares code with `alignment.py` | **6** |
| **Speaker Diarization** (pyannote, VAD replacement, Transcript mode integration) | High | High | **7** |
| **Transcription: Missing Text Bug** (diagnose + fix; requires a reproducing file) | Low–Medium | High — when reproducing file is found | **ongoing** |
