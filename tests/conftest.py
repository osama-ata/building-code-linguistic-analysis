"""
conftest.py — Shared pytest fixtures for building-code-linguistic-analysis.

All fixtures are session-scoped (computed once per test run) to keep the
test suite fast even when spaCy models are loaded inside helpers.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DOMAIN_DIR = ROOT / "domain"


# ── Text fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def sample_sentences() -> dict[str, str]:
    """One canonical sentence per deontic / informational category."""
    return {
        "obligation": (
            "The sprinkler system shall be provided throughout the building."
        ),
        "permission": (
            "Automatic sprinkler systems are permitted in lieu of a 1-hour "
            "fire-resistance rating."
        ),
        "prohibition": (
            "Combustible materials shall not be stored in the exit enclosure."
        ),
        "exemption": (
            "Exit signs are not required in rooms or areas that require only one exit."
        ),
        "conditional": (
            "Where the floor area exceeds 500 m2, an automatic sprinkler system "
            "shall be installed."
        ),
        "informative": (
            "This section describes the general requirements for means of egress."
        ),
    }


# ── Domain file fixtures ──────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def deontic_patterns_path() -> Path:
    """Absolute path to domain/deontic_patterns.yaml."""
    path = DOMAIN_DIR / "deontic_patterns.yaml"
    assert path.exists(), f"deontic_patterns.yaml not found: {path}"
    return path


@pytest.fixture(scope="session")
def entity_types_path() -> Path:
    """Absolute path to domain/entity_types.yaml."""
    path = DOMAIN_DIR / "entity_types.yaml"
    assert path.exists(), f"entity_types.yaml not found: {path}"
    return path


# ── Markdown fixture ──────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def sample_md_content() -> str:
    """Minimal markdown document with two chapters, two sections and measurements."""
    return (
        "## CHAPTER 9 FIRE PROTECTION\n\n"
        "### 9.1 Sprinkler Systems\n\n"
        "9.1.1 The sprinkler system shall be provided where the floor area "
        "exceeds 900 mm from any wall.\n\n"
        "9.1.2 The minimum clearance shall be 2000 mm.\n\n"
        "## CHAPTER 10 MEANS OF EGRESS\n\n"
        "### 10.1 General\n\n"
        "10.1.1 All exit doors shall comply with Section 10.2.\n\n"
    )


# ── Export fixtures ───────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def minimal_constraints() -> list[dict]:
    """
    Two synthetic constraint dicts suitable for export tests.

    These are plain dicts (not Constraint dataclass instances) so the export
    tests can be run without loading spaCy.
    """
    return [
        {
            "clause_id": "TEST.0001",
            "sentence": "The handrail shall be graspable.",
            "deontic_operator": "OBLIGATION",
            "agent": "handrail",
            "action": "shall be",
            "patient": "graspable",
            "instrument": "",
            "location": "",
            "condition": None,
            "numeric_values": [],
            "cross_refs": [],
            "confidence": 0.75,
            "flags": [],
        },
        {
            "clause_id": "TEST.0002",
            "sentence": "Automatic sprinkler systems are permitted in lieu of a 1-hour rating.",
            "deontic_operator": "PERMISSION",
            "agent": "automatic sprinkler systems",
            "action": "are permitted",
            "patient": "",
            "instrument": "",
            "location": "",
            "condition": None,
            "numeric_values": [],
            "cross_refs": [],
            "confidence": 0.60,
            "flags": [],
        },
    ]
