# local_srt.events

Event system for decoupled logging, progress reporting, and lifecycle notifications.

## `EventLevel`

```python
class EventLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
```

## Event Types

All events extend `BaseEvent` which carries a `timestamp: float` (Unix time).

| Class | Fields | Purpose |
| --- | --- | --- |
| `BaseEvent` | `timestamp` | Abstract base |
| `LogEvent` | `message`, `level: EventLevel` | Info/debug messages |
| `WarnEvent` | `message` | Warnings |
| `ErrorEvent` | `message`, `exc: Exception \| None` | Errors with optional exception |
| `ProgressEvent` | `percent`, `segment_count`, `media_time`, `elapsed`, `eta` | Transcription progress |
| `StageEvent` | `stage`, `stage_number`, `total_stages` | Pipeline stage transitions |
| `FileStartEvent` | `input_path` | A file is about to be processed |
| `FileCompleteEvent` | `input_path`, `output_path`, `success` | A file finished processing |
| `ModelLoadEvent` | `model_name`, `device`, `compute_type` | Model loaded |

## `EventEmitter`

Simple pub/sub mechanism.

```python
emitter = EventEmitter()
emitter.subscribe(handler)   # handler: Callable[[BaseEvent], None]
emitter.emit(event)          # Calls all subscribers
```

Subscribers receive every emitted event. Filtering is the subscriber's responsibility.

## Usage Pattern

```python
def my_handler(event: BaseEvent) -> None:
    if isinstance(event, LogEvent):
        print(event.message)
    elif isinstance(event, ProgressEvent):
        print(f"{event.percent:.0f}%")

emitter = EventEmitter()
emitter.subscribe(my_handler)
result = transcribe_file(..., event_handler=emitter)
```
