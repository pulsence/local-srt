# local_srt.whisper_wrapper

faster-whisper model initialization with device selection and compute-type selection.

## Function

### `init_whisper_model_internal`

```python
def init_whisper_model_internal(
    model_name: str,
    device: str,
    strict_cuda: bool,
    event_handler: EventHandler | None,
) -> tuple[WhisperModel, str, str]
```

Returns `(model, device_used, compute_type_used)`.

## Device Selection Logic

| Input `device` | Behavior |
| --- | --- |
| `"cpu"` | Always use CPU, `int8` compute type |
| `"cuda"` | Attempt CUDA with `float16`; if `strict_cuda=False` fall back to CPU on error |
| `"auto"` | Try CUDA first, fall back to CPU |

## Compute Types

| Device | Compute Type |
| --- | --- |
| CPU | `int8` |
| CUDA | `float16` |

## Events Emitted

Emits a `ModelLoadEvent` with `model_name`, `device_used`, and `compute_type_used` after the model is loaded.
