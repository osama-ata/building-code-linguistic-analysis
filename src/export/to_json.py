"""
to_json.py — Serialises Constraint objects to JSON Lines format.

Each line in the output file is a self-contained JSON object representing
one extracted building-code rule, compatible with:
  - BIM-Guard compliance engine ingestion
  - Downstream LegalRuleML conversion
  - Jupyter notebook inspection / pandas DataFrame loading

Usage::

    from src.export.to_json import JsonExporter
    from pathlib import Path

    exporter = JsonExporter()
    exporter.export(constraints, Path("data/05_rules/sbc201_chapter09.jsonl"))

    # Or load back:
    records = JsonExporter.load(Path("data/05_rules/sbc201_chapter09.jsonl"))
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class JsonExporter:
    """Writes / reads Constraint objects as JSON Lines."""

    # ── Export ────────────────────────────────────────────────────────────────

    def export(
        self,
        constraints: list[Any],  # list[Constraint]
        output_path: Path,
        *,
        indent: int | None = None,
        only_prescribed: bool = False,
        min_confidence: float = 0.0,
    ) -> int:
        """
        Write *constraints* to *output_path* as JSON Lines.

        Parameters
        ----------
        only_prescribed : bool
            If True, skip NONE deontic / informative sentences.
        min_confidence : float
            Skip constraints whose confidence is below this threshold.

        Returns
        -------
        int — number of records written.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        count = 0
        with output_path.open("w", encoding="utf-8") as fh:
            for c in constraints:
                if only_prescribed and c.deontic_operator in ("NONE", "", None):
                    continue
                if c.confidence < min_confidence:
                    continue
                line = json.dumps(c.to_dict(), ensure_ascii=False, indent=indent)
                fh.write(line + "\n")
                count += 1
        logger.info(
            "Exported %d / %d constraints \u2192 %s",
            count,
            len(constraints),
            output_path,
        )
        return count

    # ── Import ──────────────────────────────────────────────────────────────

    @staticmethod
    def load(path: Path) -> list[dict[str, Any]]:
        """Load a .jsonl file back as a list of raw dicts."""
        records = []
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        logger.info("Loaded %d records from %s", len(records), path)
        return records

    # ── Summary ───────────────────────────────────────────────────────────

    @staticmethod
    def summarise(constraints: list[Any]) -> dict[str, Any]:
        """Return high-level stats dict for a list of Constraints."""
        from collections import Counter

        deontic_counts = Counter(c.deontic_operator for c in constraints)
        flag_counts: Counter = Counter()
        for c in constraints:
            flag_counts.update(c.flags)
        confidences = [c.confidence for c in constraints]
        return {
            "total": len(constraints),
            "deontic_distribution": dict(deontic_counts),
            "avg_confidence": round(sum(confidences) / len(confidences), 3)
            if confidences
            else 0,
            "flagged": sum(1 for c in constraints if c.flags),
            "flag_breakdown": dict(flag_counts),
            "with_condition": sum(1 for c in constraints if c.condition),
            "with_numeric": sum(1 for c in constraints if c.numeric_values),
            "with_cross_ref": sum(1 for c in constraints if c.cross_refs),
        }
