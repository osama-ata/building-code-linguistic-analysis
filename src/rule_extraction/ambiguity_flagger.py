"""
ambiguity_flagger.py — Flags Constraint objects that require human review.

Flag codes
----------
UNRESOLVED_PRONOUN    sentence contains an unresolved pronoun (it/they/such/this …)
MODAL_CONFLICT        "shall" co-occurs with "may" or "need not" — conflicting obligation
MISSING_AGENT         no grammatical agent could be extracted
MISSING_PATIENT       no object / patient could be extracted
MISSING_NUMERIC       sentence has a dimension keyword but no numeric value was found
VAGUE_CONDITION       condition trigger present but condition_text < 3 words
MULTIPLE_DEONTICS     more than one distinct deontic modal detected in one sentence
EXCEPTION_UNRESOLVED  "except as provided in Section X" — X not captured in cross_refs
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.rule_extraction.constraint_builder import Constraint

_PRONOUN_RE = re.compile(
    r"\b(?:it|they|them|their|its|this|that|these|those|such"
    r"|the\s+above|the\s+following)\b",
    re.IGNORECASE,
)
_DIMENSION_RE = re.compile(
    r"\b(?:height|width|depth|length|area|distance|clearance|thickness"
    r"|separation|span|load|capacity|rating|size"
    r"|floor\s+area|occupant\s+load|travel\s+distance)\b",
    re.IGNORECASE,
)
_CONFLICT_PAIRS = [
    (re.compile(r"\bshall\b", re.I), re.compile(r"\bmay\b", re.I)),
    (re.compile(r"\bshall\b", re.I), re.compile(r"\bneed\s+not\b", re.I)),
    (re.compile(r"\bshall\b", re.I), re.compile(r"\bis\s+not\s+required\b", re.I)),
]
_DEONTIC_RE = re.compile(
    r"\b(shall|must|may|need\s+not|is\s+required|is\s+not\s+required"
    r"|is\s+permitted|is\s+prohibited)\b",
    re.IGNORECASE,
)
_EXCEPT_SECTION_RE = re.compile(
    r"\bexcept(?:\s+as)?(?:\s+provided)?(?:\s+in)?\s+(Section\s+[\d\.]+)",
    re.IGNORECASE,
)


class AmbiguityFlagger:
    """
    Generates human-review flag codes for a Constraint.

    Usage::

        flagger = AmbiguityFlagger()
        flags   = flagger.flag(sentence, constraint)
    """

    def flag(self, sentence: str, constraint: "Constraint") -> list[str]:
        flags: list[str] = []

        if _PRONOUN_RE.search(sentence):
            flags.append("UNRESOLVED_PRONOUN")

        for pat_a, pat_b in _CONFLICT_PAIRS:
            if pat_a.search(sentence) and pat_b.search(sentence):
                flags.append("MODAL_CONFLICT")
                break

        if not constraint.agent:
            flags.append("MISSING_AGENT")

        if not constraint.patient:
            flags.append("MISSING_PATIENT")

        if _DIMENSION_RE.search(sentence) and not constraint.numeric_values:
            flags.append("MISSING_NUMERIC")

        cond = constraint.condition
        if cond and cond.get("trigger"):
            if len((cond.get("condition_text") or "").split()) < 3:
                flags.append("VAGUE_CONDITION")

        deontic_words = {m.lower().split()[0] for m in _DEONTIC_RE.findall(sentence)}
        if len(deontic_words) > 1:
            flags.append("MULTIPLE_DEONTICS")

        except_m = _EXCEPT_SECTION_RE.search(sentence)
        if except_m and except_m.group(1) not in (constraint.cross_refs or []):
            flags.append("EXCEPTION_UNRESOLVED")

        return flags
