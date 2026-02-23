#!/usr/bin/env python3
"""Deterministic pipeline tests (word-level)."""
from __future__ import annotations

from typing import List, Tuple

from local_srt.models import FormattingConfig, ResolvedConfig, SubtitleBlock
from local_srt.subtitle_generation import (
    apply_silence_alignment,
    chunk_words_to_subtitles,
    hygiene_and_polish,
)


def run_pipeline(
    *,
    words,
    cfg: ResolvedConfig,
    silences: List[Tuple[float, float]],
) -> List[SubtitleBlock]:
    subs = chunk_words_to_subtitles(words, cfg, silences)
    subs = apply_silence_alignment(subs, silences)
    subs = hygiene_and_polish(
        subs,
        min_gap=cfg.formatting.min_gap,
        pad=cfg.formatting.pad,
        silence_intervals=silences,
    )
    return subs


def assert_blocks_close(
    actual: List[SubtitleBlock],
    expected: List[SubtitleBlock],
    tol: float = 0.05,
) -> None:
    assert len(actual) == len(expected)
    for a, e in zip(actual, expected):
        assert abs(a.start - e.start) <= tol
        assert abs(a.end - e.end) <= tol
        assert a.lines == e.lines


def test_pipeline_single_sentence_no_silence(mock_word_items):
    cfg = ResolvedConfig()
    words = mock_word_items(
        [
            ("Hello", 0.0, 0.4),
            ("world", 0.5, 1.0),
        ]
    )
    silences: List[Tuple[float, float]] = []

    subs = run_pipeline(words=words, cfg=cfg, silences=silences)

    expected = [SubtitleBlock(0.0, 1.0, ["Hello world"])]
    assert_blocks_close(subs, expected)


def test_pipeline_silence_split(mock_word_items):
    cfg = ResolvedConfig()
    words = mock_word_items(
        [
            ("Hello", 0.0, 0.4),
            ("there", 0.5, 0.9),
            ("General", 3.0, 3.4),
            ("Kenobi", 3.5, 4.0),
        ]
    )
    silences = [(1.0, 2.5)]

    pre_subs = chunk_words_to_subtitles(words, cfg, silences)
    assert len(pre_subs) == 2
    assert pre_subs[0].end <= silences[0][0]
    assert pre_subs[1].start >= silences[0][1]

    subs = run_pipeline(words=words, cfg=cfg, silences=silences)
    expected = [
        SubtitleBlock(0.0, 0.9, ["Hello there"]),
        SubtitleBlock(3.0, 4.0, ["General Kenobi"]),
    ]
    assert_blocks_close(subs, expected)


def test_pipeline_max_chars_wrap(mock_word_items):
    cfg = ResolvedConfig(formatting=FormattingConfig(max_chars=10, max_lines=3))
    words = mock_word_items(
        [
            ("one", 0.0, 0.4),
            ("two", 0.4, 0.8),
            ("three", 0.8, 1.4),
            ("four", 1.4, 2.0),
            ("five", 2.0, 2.5),
        ]
    )
    silences: List[Tuple[float, float]] = []

    pre_subs = chunk_words_to_subtitles(words, cfg, silences)
    assert len(pre_subs) == 1
    assert pre_subs[0].lines == ["one two", "three four", "five"]

    subs = run_pipeline(words=words, cfg=cfg, silences=silences)
    expected = [SubtitleBlock(0.0, 2.5, ["one two three four five"])]
    assert_blocks_close(subs, expected)
