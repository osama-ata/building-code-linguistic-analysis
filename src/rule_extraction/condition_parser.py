"""
condition_parser.py — Extracts conditional clauses from regulatory sentences.

Identifies if/where/when/unless triggers and parses the condition text,
numeric thresholds, and any referenced code sections.

Condition shape::

  {
    "trigger":           "where",
    "condition_text":    "the floor area exceeds 500 m2",
    "threshold_value":   500.0,
    "threshold_unit":    "m2",
    "referenced_sections": ["Section 903.2.1"]
  }
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import spacy

_TRIGGER_RE = re.compile(
    r"\b(if|where|when|unless|except(?:\s+where)?|provided\s+that"
    r"|subject\s+to|in\s+cases?\s+where|in\s+lieu\s+of)\b",
    re.IGNORECASE,
)
_SECTION_RE = re.compile(r"Section\s+[\d\.]+", re.IGNORECASE)
_NUMERIC_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(mm|m\b|cm|km|m2|m\s*2|sq\s*ft|ft|in|lux|N\b|kPa|psi"
    r"|kg|liters|ml|kJ/g|%|percent|degrees?|rpm)",
    re.IGNORECASE,
)


@dataclass
class Condition:
    trigger: str = ""
    condition_text: str = ""
    threshold_value: float | None = None
    threshold_unit: str = ""
    referenced_sections: list[str] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not self.trigger

    def to_dict(self) -> dict[str, Any]:
        return {
            "trigger": self.trigger,
            "condition_text": self.condition_text,
            "threshold_value": self.threshold_value,
            "threshold_unit": self.threshold_unit,
            "referenced_sections": self.referenced_sections,
        }


class ConditionParser:
    """
    Parses conditional clauses from building-code sentences.

    Usage::

        parser = ConditionParser()
        cond = parser.parse("Sprinklers shall be provided where the floor area exceeds 500 m2.")
        if not cond.is_empty:
            print(cond.trigger, cond.condition_text, cond.threshold_value)
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        self._nlp = spacy.load(model_name, disable=["ner"])

    def parse(self, sentence: str) -> Condition:
        cond = Condition()

        trigger_match = _TRIGGER_RE.search(sentence)
        if not trigger_match:
            return cond

        cond.trigger = trigger_match.group(0).strip()

        # Condition text: everything after the trigger keyword
        after_trigger = sentence[trigger_match.end() :].strip()
        # Truncate at sentence-ending punctuation or a second clause marker
        clause_end = re.search(r"\.\s*$|\band\b|\bor\b", after_trigger)
        cond.condition_text = (
            after_trigger[: clause_end.start()].strip()
            if clause_end
            else after_trigger.strip()
        )

        # Threshold numeric value
        num_match = _NUMERIC_RE.search(cond.condition_text) or _NUMERIC_RE.search(
            after_trigger
        )
        if num_match:
            try:
                cond.threshold_value = float(num_match.group(1))
                cond.threshold_unit = num_match.group(2).strip()
            except ValueError:
                pass

        # Section cross-references within the condition clause
        cond.referenced_sections = _SECTION_RE.findall(after_trigger)

        return cond

    def parse_batch(self, sentences: list[str]) -> list[Condition]:
        return [self.parse(s) for s in sentences]
