#!/usr/bin/env python3
"""Shared pytest fixtures for Local SRT tests."""
from __future__ import annotations

from collections import namedtuple
from typing import Any, Callable, Dict, List, Tuple

import pytest

from local_srt.models import WordItem


Segment = namedtuple("Segment", ["start", "end", "text", "words"])


@pytest.fixture
def mock_word_items() -> Callable[[List[Tuple[str, float, float]]], List[WordItem]]:
    """Build a WordItem list from (text, start, end) tuples."""

    def _make(words: List[Tuple[str, float, float]]) -> List[WordItem]:
        return [WordItem(float(start), float(end), text) for text, start, end in words]

    return _make


@pytest.fixture
def mock_segments() -> Callable[[List[Dict[str, Any]]], List[Segment]]:
    """Build mock whisper segments from dicts."""

    def _make(data: List[Dict[str, Any]]) -> List[Segment]:
        segments: List[Segment] = []
        for item in data:
            segments.append(
                Segment(
                    start=float(item.get("start", 0.0)),
                    end=float(item.get("end", 0.0)),
                    text=item.get("text", ""),
                    words=item.get("words"),
                )
            )
        return segments

    return _make


@pytest.fixture
def mock_silence_intervals() -> List[Tuple[float, float]]:
    """Return a fixed silence interval list for reuse."""
    return [(1.0, 1.4), (3.0, 3.6)]
