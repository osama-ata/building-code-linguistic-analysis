"""
normalizer.py — Text normalisation for raw building-code clauses.

Removes PDF-to-Markdown conversion artefacts, strips markdown syntax noise,
collapses whitespace, and decodes mis-encoded Unicode characters so that
downstream NLP (tokeniser, NER, dependency parser, SRL) receives clean prose.

Usage::

    from src.preprocessing.normalizer import Normalizer

    norm = Normalizer()
    clean = norm.normalize("- 1.1.3 Terms  defined  in  other  codes.")
    # -> "Terms defined in other codes."

    cleaned = norm.normalize_batch(raw_clauses)
"""

from __future__ import annotations

import re
import unicodedata

# ── Compiled patterns ─────────────────────────────────────────────────────────

# Leading markdown list-item bullets (-, *, bullet) optionally followed by a
# section-number token like "1.1.3" or "2.28.3.2.1"
_LIST_PREFIX_RE = re.compile(r"^[-*\u2022]\s+(?:\d+(?:\.\d+)*\.?\s+)?")

# Standalone section-number at the very start of a string ("2.5.1 Educational...")
_LEADING_SECTION_NUM_RE = re.compile(r"^\d+(?:\.\d+)+\.?\s+")

# Markdown heading hashes (### 3.2.1 Title)
_HEADING_HASH_RE = re.compile(r"^#{1,6}\s+")

# Multi-whitespace (spaces/tabs) -> single space
_MULTI_SPACE_RE = re.compile(r"[ \t]{2,}")

# Known mis-encoding pairs produced by naive UTF-8->Latin-1->UTF-8 round-trips.
# Each tuple is (broken_sequence, correct_character).
_ENCODING_FIXES: list[tuple[str, str]] = [
    # Degree / superscript / middle-dot
    ("\u00c2\u00b0", "\u00b0"),  # Â° -> °
    ("\u00c2\u00b2", "\u00b2"),  # Â² -> ²
    ("\u00c2\u00b3", "\u00b3"),  # Â³ -> ³
    ("\u00c2\u00b7", "\u00b7"),  # Â· -> ·
    # French / accented letters
    ("\u00c3\u00a9", "\u00e9"),  # Ã© -> é
    ("\u00c3\u00a8", "\u00e8"),  # Ã¨ -> è
    ("\u00c3\u00a0", "\u00e0"),  # Ã  -> à
    ("\u00c3\u00a2", "\u00e2"),  # Ã¢ -> â
    ("\u00c3\u00ae", "\u00ee"),  # Ã® -> î
    ("\u00c3\u00b4", "\u00f4"),  # Ã´ -> ô
    ("\u00c3\u00bb", "\u00fb"),  # Ã» -> û
    ("\u00c3\u00a7", "\u00e7"),  # Ã§ -> ç
    ("\u00c3\u00bc", "\u00fc"),  # Ã¼ -> ü
    ("\u00c3\u00b6", "\u00f6"),  # Ã¶ -> ö
    ("\u00c3\u00a4", "\u00e4"),  # Ã¤ -> ä
    ("\u00c3\u00a1", "\u00e1"),  # Ã¡ -> á
    ("\u00c3\u00ad", "\u00ed"),  # Ã­ -> í
    ("\u00c3\u00b3", "\u00f3"),  # Ã³ -> ó
    ("\u00c3\u00ba", "\u00fa"),  # Ãº -> ú
    # Typographic quotes / dashes
    ("\u00e2\u0080\u0099", "\u2019"),  # â€™ -> right single quote
    ("\u00e2\u0080\u009c", "\u201c"),  # â€œ -> left double quote
    ("\u00e2\u0080\u009d", "\u201d"),  # â€ -> right double quote
    ("\u00e2\u0080\u0093", "\u2013"),  # â€" -> en dash
    ("\u00e2\u0080\u0094", "\u2014"),  # â€" -> em dash
    # Fractions
    ("\u00c2\u00bd", "\u00bd"),  # Â½ -> ½
    ("\u00c2\u00bc", "\u00bc"),  # Â¼ -> ¼
    ("\u00c2\u00be", "\u00be"),  # Â¾ -> ¾
]

# Stray non-printable control characters (keep newline \n and tab \t)
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# Parenthetical table/figure references that add no semantic content to a clause
_TABLE_FIG_REF_RE = re.compile(
    r"\b(?:see\s+)?(?:Table|Figure|Appendix)\s+[\d.A-Z]+", re.IGNORECASE
)

# Trailing punctuation artefacts: trailing colons, pipes, lone dashes
_TRAILING_NOISE_RE = re.compile(r"[|:;\-]+\s*$")


class Normalizer:
    """
    Cleans raw clause text extracted by ``MarkdownParser`` or ``ChapterSplitter``.

    Parameters
    ----------
    strip_table_refs : bool
        Whether to remove inline "Table X.Y" / "Figure X.Y" references.
        Default ``True``.  Set ``False`` to preserve them for cross-reference
        resolution.
    """

    def __init__(self, strip_table_refs: bool = True):
        self._strip_table_refs = strip_table_refs

    # ── Public API ────────────────────────────────────────────────────────────

    def normalize(self, text: str) -> str:
        """Return a single normalised string from *text*."""
        t = self._fix_encoding(text)
        t = self._strip_markdown_noise(t)
        t = self._collapse_whitespace(t)
        if self._strip_table_refs:
            t = _TABLE_FIG_REF_RE.sub("", t)
        t = _TRAILING_NOISE_RE.sub("", t)
        return t.strip()

    def normalize_batch(self, texts: list[str]) -> list[str]:
        """Normalise a list of clause strings, discarding empty results."""
        return [clean for t in texts if (clean := self.normalize(t))]

    # ── Internal steps ────────────────────────────────────────────────────────

    @staticmethod
    def _fix_encoding(text: str) -> str:
        """Apply known mis-encoding fixes, then NFC-normalise Unicode."""
        for broken, correct in _ENCODING_FIXES:
            text = text.replace(broken, correct)
        text = _CONTROL_CHARS_RE.sub("", text)
        return unicodedata.normalize("NFC", text)

    @staticmethod
    def _strip_markdown_noise(text: str) -> str:
        """Remove markdown structural markers and leading section numbers."""
        text = _HEADING_HASH_RE.sub("", text)
        text = _LIST_PREFIX_RE.sub("", text)
        text = _LEADING_SECTION_NUM_RE.sub("", text)
        return text

    @staticmethod
    def _collapse_whitespace(text: str) -> str:
        """Replace runs of spaces/tabs with a single space."""
        return _MULTI_SPACE_RE.sub(" ", text)
