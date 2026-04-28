"""
constraint_builder.py — Assembles all Phase B/C outputs into unified Constraint objects.

Orchestrates:
  - DeonticDetector (Phase C)       → deontic_operator
  - SemanticRoleLabeller (Phase D)  → agent, action, patient, instrument, location
  - ConditionParser (Phase D)       → condition struct
  - ConfidenceScorer (Phase D)      → confidence float  [0–1]
  - AmbiguityFlagger (Phase D)      → flags list

Output Constraint shape (also written to data/05_rules/ as .jsonl)::

  {
    "clause_id":        "SBC201.0903.0001",
    "sentence":         "...",
    "deontic_operator": "OBLIGATION",
    "agent":            "sprinkler system",
    "action":           "shall be provided",
    "patient":          "throughout the building",
    "instrument":       "",
    "location":         "throughout the building",
    "condition":        { "trigger": "where", "threshold_value": 23.0, ... },
    "numeric_values":   [{"value": 23.0, "unit": "m", "span": "23 m"}],
    "cross_refs":       ["Section 903.2.1"],
    "confidence":       0.87,
    "flags":            []
  }
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import spacy

from src.classification.deontic_detector import DeonticDetector
from src.rule_extraction.condition_parser import ConditionParser
from src.rule_extraction.semantic_roles import SemanticRoleLabeller
from src.rule_extraction.confidence_scorer import ConfidenceScorer
from src.rule_extraction.ambiguity_flagger import AmbiguityFlagger

logger = logging.getLogger(__name__)

_DEFAULT_PATTERNS = Path("domain/deontic_patterns.yaml")


@dataclass
class Constraint:
    clause_id: str
    sentence: str
    deontic_operator: str = "NONE"
    agent: str = ""
    action: str = ""
    patient: str = ""
    instrument: str = ""
    location: str = ""
    condition: dict[str, Any] = field(default_factory=dict)
    numeric_values: list[dict[str, Any]] = field(default_factory=list)
    cross_refs: list[str] = field(default_factory=list)
    confidence: float = 0.0
    flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class ConstraintBuilder:
    """
    Orchestrates all Phase D extractors to produce Constraint objects.

    Usage::

        builder = ConstraintBuilder()
        constraints = builder.build_from_text(
            text="...",
            clause_id_prefix="SBC201.0903"
        )
        builder.save_jsonl(constraints, Path("data/05_rules/sbc201_903.jsonl"))
    """

    def __init__(
        self,
        patterns_path: str | Path = _DEFAULT_PATTERNS,
        model_name: str = "en_core_web_sm",
    ):
        self._nlp = spacy.load(model_name, disable=["ner"])
        self._deontic = DeonticDetector(str(patterns_path))
        self._srl = SemanticRoleLabeller(model_name)
        self._cond = ConditionParser(model_name)
        self._scorer = ConfidenceScorer()
        self._flagger = AmbiguityFlagger()

    # ── Public API ────────────────────────────────────────────────────────────

    def build_from_text(
        self,
        text: str,
        clause_id_prefix: str = "SBC201",
    ) -> list[Constraint]:
        """Segment *text* into sentences and build one Constraint per sentence."""
        doc = self._nlp(text)
        constraints: list[Constraint] = []
        for idx, sent in enumerate(doc.sents):
            sentence = sent.text.strip()
            if len(sentence.split()) < 3:
                continue
            clause_id = f"{clause_id_prefix}.{idx + 1:04d}"
            constraints.append(self._build_one(clause_id, sentence))
        return constraints

    def build_from_sentences(
        self,
        sentences: list[tuple[str, str]],
    ) -> list[Constraint]:
        """Build constraints from (clause_id, sentence) pairs."""
        return [self._build_one(cid, sent) for cid, sent in sentences]

    def save_jsonl(self, constraints: list[Constraint], output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as fh:
            for c in constraints:
                fh.write(c.to_json() + "\n")
        logger.info("Saved %d constraints → %s", len(constraints), output_path)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _build_one(self, clause_id: str, sentence: str) -> Constraint:
        c = Constraint(clause_id=clause_id, sentence=sentence)

        # Deontic operator
        c.deontic_operator = self._deontic.extract_operator(sentence)

        # Semantic roles (one sentence → one frame)
        frames = self._srl.label(sentence)
        if frames:
            f = frames[0]
            c.agent = f.agent
            c.action = f.action
            c.patient = f.patient
            c.instrument = f.instrument
            c.location = f.location
            c.numeric_values = f.quantities
            c.cross_refs = f.cross_refs

        # Condition
        cond = self._cond.parse(sentence)
        if not cond.is_empty:
            c.condition = cond.to_dict()
            for ref in cond.referenced_sections:
                if ref not in c.cross_refs:
                    c.cross_refs.append(ref)

        # Confidence + flags (flagger populates first, scorer uses result)
        c.flags = self._flagger.flag(sentence, c)
        c.confidence = self._scorer.score(c)

        return c
