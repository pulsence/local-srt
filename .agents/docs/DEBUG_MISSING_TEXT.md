# Debugging: Missing Text at End of Segments

## Problem Description

Whole sections of text are absent from transcription output. The missing content is always at the **trailing end** of a segment — the beginning transcribes correctly, then the text cuts off mid-sentence or mid-thought with no error reported.

## Prerequisites

**Phase 3.4 (Transcription Parameter Exposure) must be complete** before this debugging process can run efficiently. That phase exposes `--no-vad-filter`, `--no-condition-on-previous-text`, `--no-speech-threshold`, `--log-prob-threshold`, and `--compression-ratio-threshold` as CLI flags.

## Step 0: Confirm and Record the Bug

Before starting, establish a clear baseline:

1. Run the file normally and capture the output:
   ```
   srtgen input.mp4 baseline.srt
   ```
2. Note the timestamp range where text goes missing
3. Note what the correct text should say (from the actual audio)
4. Keep `baseline.srt` for comparison throughout the process

## Step 1: Isolate VAD

**Most likely cause.** `vad_filter=True` pre-screens audio before it reaches the model. Whisper's VAD is tuned for speech onset — it detects where speech begins well, but can cut trailing syllables with falling intonation before they reach the model. The model never sees them and cannot transcribe them.

Run:

```
srtgen --no-vad-filter input.mp4 output_no_vad.srt
```

- **Missing text appears** → VAD is the cause. Go to [VAD Fix Path](#vad-fix-path).
- **Text still missing** → VAD is not the cause. Go to Step 2.

## Step 2: Isolate Decoder Drift

`condition_on_previous_text=True` feeds the prior output back to the decoder as context. This can cause drift: the model predicts what is likely to come next based on what it already transcribed and skips ahead, halting mid-sentence when its prediction confidence drops.

Run:

```
srtgen --no-condition-on-previous-text input.mp4 output_no_cond.srt
```

- **Missing text appears** → Decoder drift is the cause. Go to [Decoder Drift Fix Path](#decoder-drift-fix-path).
- **Text still missing** → Go to Step 3.

## Step 3: Isolate Threshold Parameters

One of the probability thresholds may be silently discarding the segment that contains the missing text. Test each independently:

```
srtgen --no-speech-threshold 0.9 input.mp4 output_nst.srt
```

Raises the bar for a segment to be called "no speech" — reduces how aggressively silent segments are dropped.

```
srtgen --log-prob-threshold -2.0 input.mp4 output_lpt.srt
```

Lowers the floor for log-probability — accepts segments the model is less confident about.

```
srtgen --compression-ratio-threshold 3.0 input.mp4 output_crt.srt
```

Raises the repetition threshold — less likely to discard a segment as a "hallucination loop."

Test each change individually. If one of them restores the missing text, that parameter is the culprit.

- **One parameter restores the text** → Go to the corresponding fix path below.
- **No parameter restores the text** → The problem is likely in audio preprocessing or a model version issue. See [If Nothing Works](#if-nothing-works).

## Step 4: Combine Fixes

Once the culprit is identified, test the minimal change that fixes the bug:

```
srtgen --no-vad-filter input.mp4 output_combined.srt
```

or

```
srtgen --no-condition-on-previous-text --no-speech-threshold 0.8 input.mp4 output_combined.srt
```

Confirm the fix with `diff baseline.srt output_combined.srt` and verify the restored text is correct.

---

## Fix Paths

### VAD Fix Path

**Immediate fix** — disable VAD for this file:

```
srtgen --no-vad-filter input.mp4 output.srt
```

This is safe for clean audio (studio recording, minimal background noise). For noisier audio it may produce hallucinated transcription in silent regions.

**Better fix** — replace whisper's VAD with pyannote VAD (Phase 6: Speaker Diarization):

Once Phase 6 is implemented, `pyannote.audio`'s VAD pipeline is significantly more accurate than whisper's built-in filter, especially for trailing speech with falling intonation. Running pyannote VAD to pre-segment the audio before passing it to whisper eliminates this problem without disabling VAD entirely.

**Record the finding**: note the file, the time range, and that `--no-vad-filter` fixed it. This informs the decision about whether to change the default `vad_filter` setting or invest in pyannote VAD.

### Decoder Drift Fix Path

**Fix** — disable prior-context conditioning:

```
srtgen --no-condition-on-previous-text input.mp4 output.srt
```

Trade-off: whisper's punctuation and capitalization consistency may be slightly worse without this context. For most content this is an acceptable trade.

**Record the finding**: note the file and segment range. If decoder drift is a recurring problem across multiple files, consider setting `condition_on_previous_text = False` as the default in the config.

### Threshold Fix Path

Adjust the specific parameter that restored the text and use a config file to set it as a per-project default:

```json
{
  "transcription": {
    "no_speech_threshold": 0.9
  }
}
```

```
srtgen --config my_config.json input.mp4 output.srt
```

---

## If Nothing Works

If none of the above steps restore the missing text:

1. **Check the raw segment dump**: run with `--segments segments.json` and inspect the JSON — look for whether the segment exists with empty text, or is absent entirely
2. **Check the audio**: open the WAV in Audacity and look at the time range where text is missing — is there actual speech there, or is the audio quiet/corrupted?
3. **Try a different model**: a larger model (e.g., `medium` instead of `small`) may decode the segment successfully where a smaller model fails
4. **Try a smaller chunk**: if the file is long, the missing segment may be affected by the model's finite context window — try transcribing just a 30–60s clip that includes the missing section

---

## Cross-References

| Reference | Location |
| --- | --- |
| Missing text bug analysis | [PLAN_RESEARCH.md — Missing Text Bug](./PLAN_RESEARCH.md) |
| Parameter exposure implementation | [PLAN.md — Phase 3.4](./PLAN.md) |
| pyannote VAD as a VAD replacement | [PLAN.md — Phase 6](./PLAN.md) |
| faster-whisper transcribe() docs | [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper) |
