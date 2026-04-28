"""
test_export.py — Tests for Phase D export components.

Covers:
  - JsonExporter (5 tests)
  - LegalRuleMLExporter (3 tests)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.export.to_json import JsonExporter
from src.export.to_legalruleml import LegalRuleMLExporter
from src.rule_extraction.constraint_builder import Constraint


# ── Helpers ───────────────────────────────────────────────────────────────────


def _dicts_to_constraints(records: list[dict]) -> list[Constraint]:
    """Convert minimal_constraints dicts to Constraint dataclass instances."""
    constraints = []
    for r in records:
        c = Constraint(
            clause_id=r["clause_id"],
            sentence=r["sentence"],
            deontic_operator=r["deontic_operator"],
            agent=r["agent"],
            action=r["action"],
            patient=r["patient"],
            instrument=r.get("instrument", ""),
            location=r.get("location", ""),
            condition=r.get("condition") or {},
            numeric_values=r.get("numeric_values", []),
            cross_refs=r.get("cross_refs", []),
            confidence=r.get("confidence", 0.0),
            flags=r.get("flags", []),
        )
        constraints.append(c)
    return constraints


# ─────────────────────────────────────────────────────────────────────────────
# TestJsonExporter
# ─────────────────────────────────────────────────────────────────────────────


class TestJsonExporter:
    """Tests for src.export.to_json.JsonExporter."""

    @pytest.fixture(autouse=True)
    def _setup(self, tmp_path, minimal_constraints):
        self.exporter = JsonExporter()
        self.constraints = _dicts_to_constraints(minimal_constraints)
        self.output_path = tmp_path / "test_output.jsonl"

    # 1 — Exports the correct number of records
    def test_exports_n_records(self):
        n = self.exporter.export(self.constraints, self.output_path)
        assert n == len(self.constraints)

    # 2 — Output file is valid JSONL (each line is parseable JSON)
    def test_valid_jsonl_output(self):
        self.exporter.export(self.constraints, self.output_path)
        lines = self.output_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == len(self.constraints)
        for line in lines:
            obj = json.loads(line)
            assert "clause_id" in obj

    # 3 — only_prescribed=True filters out non-prescribed records
    def test_only_prescribed_filter(self):
        # Add a NONE-operator constraint
        constraints = self.constraints + _dicts_to_constraints(
            [
                {
                    "clause_id": "TEST.NONE",
                    "sentence": "This section describes general requirements.",
                    "deontic_operator": "NONE",
                    "agent": "",
                    "action": "",
                    "patient": "",
                    "confidence": 0.0,
                }
            ]
        )
        n = self.exporter.export(constraints, self.output_path, only_prescribed=True)
        assert n == 2  # only the two OBLIGATION/PERMISSION records

    # 4 — min_confidence filter removes low-confidence records
    def test_min_confidence_filter(self):
        # One constraint has confidence 0.75, other has 0.60
        n = self.exporter.export(
            self.constraints, self.output_path, min_confidence=0.70
        )
        assert n == 1  # only confidence=0.75 passes

    # 5 — load() round-trips the exported data
    def test_load_roundtrip(self):
        self.exporter.export(self.constraints, self.output_path)
        records = JsonExporter.load(self.output_path)
        assert len(records) == len(self.constraints)
        assert records[0]["clause_id"] == self.constraints[0].clause_id


# ─────────────────────────────────────────────────────────────────────────────
# TestLegalRuleMLExporter
# ─────────────────────────────────────────────────────────────────────────────


class TestLegalRuleMLExporter:
    """Tests for src.export.to_legalruleml.LegalRuleMLExporter."""

    @pytest.fixture(autouse=True)
    def _setup(self, tmp_path, minimal_constraints):
        self.exporter = LegalRuleMLExporter()
        self.constraints = _dicts_to_constraints(minimal_constraints)
        self.output_path = tmp_path / "test_output.xml"
        self.exporter.export(self.constraints, self.output_path)
        self.xml_text = self.output_path.read_text(encoding="utf-8")

    # 1 — XML file is produced
    def test_xml_file_produced(self):
        assert self.output_path.exists()
        assert self.output_path.stat().st_size > 0

    # 2 — XML contains "Obligation"
    def test_contains_obligation(self):
        assert "Obligation" in self.xml_text, (
            f"'Obligation' not found in XML output:\n{self.xml_text[:500]}"
        )

    # 3 — XML contains "Permission"
    def test_contains_permission(self):
        assert "Permission" in self.xml_text, (
            f"'Permission' not found in XML output:\n{self.xml_text[:500]}"
        )
