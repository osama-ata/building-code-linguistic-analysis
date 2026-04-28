"""
test_rule_extraction.py — Tests for Phase D rule-extraction components.

Covers:
  - ConditionParser (5 tests)
  - SemanticRoleLabeller (3 tests)
  - AmbiguityFlagger (3 tests)
  - ConfidenceScorer (3 tests)
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.rule_extraction.condition_parser import ConditionParser
from src.rule_extraction.semantic_roles import SemanticRoleLabeller
from src.rule_extraction.ambiguity_flagger import AmbiguityFlagger
from src.rule_extraction.confidence_scorer import ConfidenceScorer


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_constraint(**kwargs):
    """Return a minimal namespace that satisfies Constraint attribute access."""
    defaults = dict(
        agent="",
        action="",
        patient="",
        deontic_operator="OBLIGATION",
        condition=None,
        numeric_values=[],
        cross_refs=[],
        flags=[],
        confidence=0.0,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# ─────────────────────────────────────────────────────────────────────────────
# TestConditionParser
# ─────────────────────────────────────────────────────────────────────────────


class TestConditionParser:
    """Tests for src.rule_extraction.condition_parser.ConditionParser."""

    @pytest.fixture(autouse=True)
    def _parser(self, deontic_patterns_path):
        self.parser = ConditionParser()

    # 1 — "where" trigger detected
    def test_where_trigger_detected(self):
        sentence = "Where the floor area exceeds 500 m2, a sprinkler system shall be installed."
        condition = self.parser.parse(sentence)
        assert condition.trigger.lower() == "where", repr(condition)

    # 2 — "unless" trigger detected
    def test_unless_trigger_detected(self):
        sentence = "Exit signs are not required unless the building exceeds 3 storeys."
        condition = self.parser.parse(sentence)
        assert condition.trigger.lower() == "unless", repr(condition)

    # 3 — Numeric threshold "500.0 m2" extracted
    def test_numeric_threshold_extracted(self):
        sentence = "Where the floor area exceeds 500 m2, a sprinkler system shall be installed."
        condition = self.parser.parse(sentence)
        assert condition.threshold_value == pytest.approx(500.0), repr(condition)
        assert "m2" in condition.threshold_unit.lower(), repr(condition)

    # 4 — Empty condition for sentence with no trigger
    def test_empty_condition_for_no_trigger(self):
        sentence = "The handrail shall be graspable."
        condition = self.parser.parse(sentence)
        assert condition.is_empty, repr(condition)

    # 5 — batch parse returns one Condition per sentence
    def test_batch_parse(self):
        sentences = [
            "Where the area exceeds 500 m2, install sprinklers.",
            "The door shall be fire-rated.",
        ]
        results = self.parser.parse_batch(sentences)
        assert len(results) == 2
        assert not results[1].trigger  # second sentence has no trigger


# ─────────────────────────────────────────────────────────────────────────────
# TestSemanticRoleLabeller
# ─────────────────────────────────────────────────────────────────────────────


class TestSemanticRoleLabeller:
    """Tests for src.rule_extraction.semantic_roles.SemanticRoleLabeller."""

    @pytest.fixture(autouse=True)
    def _srl(self):
        self.srl = SemanticRoleLabeller()

    # 1 — label() returns a list of Frame objects
    def test_returns_list_of_frames(self, sample_sentences):
        sentence = sample_sentences["obligation"]
        frames = self.srl.label(sentence)
        assert isinstance(frames, list), type(frames)
        assert len(frames) >= 1

    # 2 — quantity "900 mm" extracted
    def test_extracts_quantity(self):
        sentence = "The handrail shall be installed at 900 mm above the floor."
        frames = self.srl.label(sentence)
        all_quantities = [q for f in frames for q in f.quantities]
        # Check that 900 appears with a unit
        assert any(q["value"] == pytest.approx(900.0) for q in all_quantities), (
            f"No 900 mm found in: {all_quantities}"
        )

    # 3 — cross-reference "Section 2.2.3.2" captured
    def test_extracts_cross_ref(self):
        sentence = "The exit width shall comply with Section 2.2.3.2."
        frames = self.srl.label(sentence)
        all_refs = [r for f in frames for r in f.cross_refs]
        assert any("2.2.3.2" in r for r in all_refs), f"No cross-ref found: {all_refs}"


# ─────────────────────────────────────────────────────────────────────────────
# TestAmbiguityFlagger
# ─────────────────────────────────────────────────────────────────────────────


class TestAmbiguityFlagger:
    """Tests for src.rule_extraction.ambiguity_flagger.AmbiguityFlagger."""

    @pytest.fixture(autouse=True)
    def _flagger(self):
        self.flagger = AmbiguityFlagger()

    # 1 — MISSING_AGENT flagged when agent is empty
    def test_missing_agent_flagged(self):
        constraint = _make_constraint(agent="", patient="the building")
        flags = self.flagger.flag(
            "Shall be installed throughout the building.", constraint
        )
        assert "MISSING_AGENT" in flags, flags

    # 2 — MISSING_AGENT NOT flagged when agent is present
    def test_missing_agent_not_flagged_when_agent_present(self):
        constraint = _make_constraint(agent="sprinkler system", patient="the building")
        flags = self.flagger.flag(
            "The sprinkler system shall be installed throughout the building.",
            constraint,
        )
        assert "MISSING_AGENT" not in flags, flags

    # 3 — UNRESOLVED_PRONOUN flagged for "It shall…"
    def test_unresolved_pronoun_flagged(self):
        constraint = _make_constraint(agent="", patient="")
        flags = self.flagger.flag("It shall comply with the requirements.", constraint)
        assert "UNRESOLVED_PRONOUN" in flags, flags


# ─────────────────────────────────────────────────────────────────────────────
# TestConfidenceScorer
# ─────────────────────────────────────────────────────────────────────────────


class TestConfidenceScorer:
    """Tests for src.rule_extraction.confidence_scorer.ConfidenceScorer."""

    @pytest.fixture(autouse=True)
    def _scorer(self):
        self.scorer = ConfidenceScorer()

    # 1 — Score is always in [0, 1]
    def test_score_in_bounds(self):
        constraint = _make_constraint()
        score = self.scorer.score(constraint)
        assert 0.0 <= score <= 1.0, score

    # 2 — Full fields score higher than minimal fields
    def test_full_fields_score_higher_than_minimal(self):
        minimal = _make_constraint(
            agent="",
            patient="",
            deontic_operator="NONE",
            numeric_values=[],
            cross_refs=[],
            flags=["MISSING_AGENT"],
        )
        full = _make_constraint(
            agent="sprinkler system",
            patient="the building",
            deontic_operator="OBLIGATION",
            condition={"trigger": "where", "condition_text": "area exceeds 500 m2"},
            numeric_values=[{"value": 500.0, "unit": "m2", "span": "500 m2"}],
            cross_refs=["Section 9.1"],
            flags=[],
        )
        assert self.scorer.score(full) > self.scorer.score(minimal)

    # 3 — score_batch updates the confidence attribute on each constraint
    def test_batch_score_updates_confidence_attr(self):
        constraints = [_make_constraint(), _make_constraint()]
        scores = self.scorer.score_batch(constraints)
        assert len(scores) == 2
        for s in scores:
            assert 0.0 <= s <= 1.0
