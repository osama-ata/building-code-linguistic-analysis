"""
semantic_roles.py — Shallow semantic role labelling for building-code sentences.

Extracts a single semantic Frame per sentence using spaCy dependency parsing.
This is a rule-based approximation of SRL targeted at the construction domain;
it does not require a trained SRL model.

Frame fields
------------
agent       : grammatical subject (nsubj / nsubjpass)
action      : root verb phrase including deontic auxiliaries
patient     : direct / indirect object or attribute complement
instrument  : prepositional "by means of" / "using" phrase
location    : prepositional "in" / "at" / "throughout" phrase
quantities  : list of {value, unit, span} numeric measurements
cross_refs  : list of "Section X.Y.Z" references found in the sentence
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import spacy
from spacy.tokens import Span, Token

_SECTION_RE = re.compile(r"Section\s+[\d\.]+", re.IGNORECASE)
_QUANTITY_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(mm|m\b|cm|km|m2|m\s*2|sq\s*ft|ft|in|lux|N\b|kPa|psi"
    r"|kg|liters|ml|kJ/g|%|percent|degrees?|rpm)",
    re.IGNORECASE,
)
_INSTRUMENT_PREPS = {"by", "using", "via", "with", "through"}
_LOCATION_PREPS = {
    "in",
    "at",
    "on",
    "throughout",
    "within",
    "along",
    "across",
    "inside",
}


@dataclass
class Frame:
    agent: str = ""
    action: str = ""
    patient: str = ""
    instrument: str = ""
    location: str = ""
    quantities: list[dict[str, Any]] = field(default_factory=list)
    cross_refs: list[str] = field(default_factory=list)


class SemanticRoleLabeller:
    """
    Rule-based semantic role labeller built on spaCy dependency trees.

    Usage::

        srl = SemanticRoleLabeller()
        frames = srl.label("Exit doors shall be provided throughout the building.")
        if frames:
            print(frames[0].agent, frames[0].action, frames[0].patient)
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        self._nlp = spacy.load(model_name, disable=["ner"])

    def label(self, text: str) -> list[Frame]:
        doc = self._nlp(text)
        frames: list[Frame] = []
        for sent in doc.sents:
            frame = self._label_sentence(sent)
            frames.append(frame)
        return frames

    # ── Internal ──────────────────────────────────────────────────────────────

    def _label_sentence(self, sent: Span) -> Frame:
        f = Frame()

        # Quantities and cross-references are extracted from raw text
        f.quantities = _extract_quantities(sent.text)
        f.cross_refs = _SECTION_RE.findall(sent.text)

        # Find root verb
        root: Token | None = next(
            (t for t in sent if t.dep_ == "ROOT" and t.pos_ in ("VERB", "AUX")), None
        )
        if root is None:
            root = next((t for t in sent if t.dep_ == "ROOT"), None)
        if root is None:
            return f

        # Action: aux chain + root verb
        aux_tokens = [t.text for t in root.lefts if t.dep_ in ("aux", "auxpass", "neg")]
        f.action = " ".join(aux_tokens + [root.text])

        # Agent
        subjects = [t for t in root.lefts if t.dep_ in ("nsubj", "nsubjpass")]
        if subjects:
            f.agent = _subtree_text(subjects[0])

        # Patient
        objects = [
            t
            for t in root.rights
            if t.dep_ in ("dobj", "pobj", "attr", "acomp", "oprd", "xcomp")
        ]
        if objects:
            f.patient = _subtree_text(objects[0])

        # Instrument & location from prepositional phrases hanging off root
        for prep in (t for t in root.rights if t.dep_ == "prep"):
            prep_lower = prep.text.lower()
            pobj = next((t for t in prep.rights if t.dep_ == "pobj"), None)
            if pobj is None:
                continue
            phrase = prep.text + " " + _subtree_text(pobj)
            if prep_lower in _INSTRUMENT_PREPS and not f.instrument:
                f.instrument = phrase
            elif prep_lower in _LOCATION_PREPS and not f.location:
                f.location = phrase

        return f


# ── Helpers ───────────────────────────────────────────────────────────────────


def _subtree_text(token: Token) -> str:
    """Return the full subtree text for a token (left + self + right)."""
    return " ".join(t.text for t in token.subtree)


def _extract_quantities(text: str) -> list[dict[str, Any]]:
    results = []
    for m in _QUANTITY_RE.finditer(text):
        results.append(
            {
                "value": float(m.group(1)),
                "unit": m.group(2).strip(),
                "span": m.group(0).strip(),
            }
        )
    return results
