# Event System

## Design Goal

The `local_srt` library never calls `print()` or writes to a logger directly. Instead it emits typed event objects via an `EventEmitter`. This decouples the library from any specific output mechanism and allows consumers to handle events as they see fit.

## Architecture

```text
Library code
    │
    │  emitter.emit(LogEvent(...))
    │  emitter.emit(ProgressEvent(...))
    │
    ▼
EventEmitter ──── subscriber 1 (CLI formatter)
             ──── subscriber 2 (logging handler)
             ──── subscriber 3 (test spy)
```

The emitter is passed into every library function that may produce output. If `event_handler=None`, events are silently discarded.

## EventEmitter API

```python
class EventEmitter:
    def subscribe(self, handler: Callable[[BaseEvent], None]) -> None: ...
    def emit(self, event: BaseEvent) -> None: ...
```

`emit()` calls all subscribers synchronously in subscription order.

## Event Hierarchy

```text
BaseEvent (timestamp: float)
├── LogEvent (message, level: EventLevel)
├── WarnEvent (message)
├── ErrorEvent (message, exc: Exception | None)
├── ProgressEvent (percent, segment_count, media_time, elapsed, eta)
├── StageEvent (stage, stage_number, total_stages)
├── FileStartEvent (input_path)
├── FileCompleteEvent (input_path, output_path, success)
└── ModelLoadEvent (model_name, device, compute_type)
```

## EventLevel

```python
class EventLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
```

## CLI Event Handler

The CLI creates a closure that subscribes to the emitter and formats events for the terminal:

| Event | CLI Output |
| --- | --- |
| `LogEvent(level=INFO)` | Plain print |
| `LogEvent(level=WARNING)` | Yellow warning prefix |
| `ErrorEvent` | Red error prefix |
| `ProgressEvent` | Inline progress bar with `percent`, `eta` |
| `StageEvent` | Stage banner line |
| `FileStartEvent` | Processing `<filename>...` |
| `FileCompleteEvent` | Checkmark or ✗ with filename |
| `ModelLoadEvent` | Loading model `<name>` on `<device>`... |

## Custom Event Handlers

Library consumers can implement any handler:

```python
def my_handler(event: BaseEvent) -> None:
    if isinstance(event, ProgressEvent):
        update_progress_bar(event.percent)
    elif isinstance(event, ErrorEvent):
        logger.error(event.message, exc_info=event.exc)

emitter = EventEmitter()
emitter.subscribe(my_handler)
result = transcribe_file(..., event_handler=emitter)
```

Pass a plain callable or an object with an `.emit()` method.
