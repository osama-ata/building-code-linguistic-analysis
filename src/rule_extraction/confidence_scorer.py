"""
confidence_scorer.py — Scores each Constraint on a 0–1 confidence scale.

Scoring rubric (additive weights, normalised to 1.0):

  Component                    Weight   Rationale
  ─────────────────────────    ──────   ──────────────────────────────────────
  Deontic operator detected     0.25    Core requirement for any useful rule
  Agent extracted               0.20    Subject of obligation must be known
  Patient / action extracted    0.20    Object of obligation must be known
  Condition parsed              0.10    Conditional rules are more precise
  Numeric value present         0.10    Quantitative rules are verifiable
  Cross-reference present       0.10    Traceability to code sections
  No ambiguity flags            0.05    Clean extraction bonus
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.rule_extraction.constraint_builder import Constraint

_WEIGHTS: dict[str, float] = {
    "deontic": 0.25,
    "agent": 0.20,
    "patient": 0.20,
    "condition": 0.10,
    "numeric": 0.10,
    "cross_ref": 0.10,
    "no_flags": 0.05,
}


class ConfidenceScorer:
    """
    Assigns a 0–1 confidence score based on extraction completeness.

    Usage::

        scorer = ConfidenceScorer()
        score  = scorer.score(constraint)
    """

    def score(self, constraint: "Constraint") -> float:
        raw = 0.0

        if constraint.deontic_operator not in ("NONE", "", None):
            raw += _WEIGHTS["deontic"]

        if constraint.agent:
            raw += _WEIGHTS["agent"]

        if constraint.patient or constraint.action:
            raw += _WEIGHTS["patient"]

        if constraint.condition and constraint.condition.get("trigger"):
            raw += _WEIGHTS["condition"]

        if constraint.numeric_values:
            raw += _WEIGHTS["numeric"]

        if constraint.cross_refs:
            raw += _WEIGHTS["cross_ref"]

        if not constraint.flags:
            raw += _WEIGHTS["no_flags"]

        return round(min(max(raw, 0.0), 1.0), 4)

    def score_batch(self, constraints: list["Constraint"]) -> list[float]:
        return [self.score(c) for c in constraints]

    @staticmethod
    def explain(constraint: "Constraint") -> dict[str, object]:
        """Return a breakdown of which scoring components fired."""
        return {
            "deontic_detected": constraint.deontic_operator not in ("NONE", "", None),
            "agent_present": bool(constraint.agent),
            "patient_present": bool(constraint.patient or constraint.action),
            "condition_parsed": bool(
                constraint.condition and constraint.condition.get("trigger")
            ),
            "numeric_present": bool(constraint.numeric_values),
            "cross_ref_present": bool(constraint.cross_refs),
            "no_flags": not constraint.flags,
        }
