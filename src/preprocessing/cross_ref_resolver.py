"""
cross_ref_resolver.py — Resolves inline section cross-references.

Builds an index of ``{section_id: title}`` from parsed chapter/section
dictionaries, then resolves strings like "Section 2.2.3.2" to the
corresponding section title using progressively shorter ID fallbacks.

Usage::

    from src.preprocessing.cross_ref_resolver import CrossRefResolver
    from src.preprocessing.md_parser import MarkdownParser

    parser = MarkdownParser()
    sections = parser.parse(raw_md_text)

    resolver = CrossRefResolver()
    resolver.build_index(sections, parser)

    result = resolver.resolve("Section 2.2.3.2")
    # {"ref": "Section 2.2.3.2", "section_id": "2.2.3.2",
    #  "title": "Measurement of Travel Distance", "resolved": True}
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.preprocessing.md_parser import MarkdownParser

# Matches "Section X.Y.Z" or "Article X.Y.Z" (case-insensitive)
_SECTION_ID_RE = re.compile(
    r"\b(?:Section|Article|Clause)\s+([\d]+(?:\.[\d]+)*)", re.IGNORECASE
)


class CrossRefResolver:
    """
    Resolves inline ``Section X.Y.Z`` references to section titles.

    The resolver must be populated via :meth:`build_index` before use.
    Unresolved references are returned with ``"resolved": False`` and an
    empty ``title``.
    """

    def __init__(self) -> None:
        # Primary index: section_id (str) -> title (str)
        self._section_index: dict[str, str] = {}
        # Chapter index: chapter_id (str) -> title (str)
        self._chapter_index: dict[str, str] = {}

    # ── Index construction ────────────────────────────────────────────────────

    def build_index(
        self,
        chapters: list[dict],
        md_parser: "MarkdownParser | None" = None,
    ) -> None:
        """
        Populate the internal index from a list of chapter/section dicts.

        Each dict is expected to contain at least ``"id"`` and ``"title"`` keys
        and optionally a ``"sections"`` list of sub-section dicts with the same
        structure.  If *chapters* already contains flat section dicts (no
        ``"sections"`` child key), those are indexed directly.

        Parameters
        ----------
        chapters :
            List of chapter or section dictionaries, typically returned by
            ``MarkdownParser.parse()`` or ``ChapterSplitter.split()``.
        md_parser :
            Unused; kept for API compatibility with callers that pass the
            parser instance.
        """
        for item in chapters:
            self._index_item(item)

    def _index_item(self, item: dict) -> None:
        """Recursively index an item and its children."""
        section_id = str(item.get("id", "")).strip()
        title = str(item.get("title", "")).strip()

        if section_id:
            self._section_index[section_id] = title

        # Recurse into nested sections / sub-sections
        for child in item.get("sections", []):
            self._index_item(child)
        for child in item.get("clauses", []):
            if isinstance(child, dict):
                self._index_item(child)

    def size(self) -> int:
        """Return the number of indexed section IDs."""
        return len(self._section_index)

    # ── Resolution API ────────────────────────────────────────────────────────

    def resolve(self, ref_string: str) -> dict:
        """
        Resolve a cross-reference string such as ``"Section 2.2.3.2"``.

        Falls back to progressively shorter IDs (``2.2.3.2`` → ``2.2.3``
        → ``2.2`` → ``2``) before giving up.

        Returns
        -------
        dict
            ``{"ref": str, "section_id": str, "title": str, "resolved": bool}``
        """
        match = _SECTION_ID_RE.search(ref_string)
        if match is None:
            return {
                "ref": ref_string,
                "section_id": "",
                "title": "",
                "resolved": False,
            }

        raw_id = match.group(1)
        parts = raw_id.split(".")

        # Try progressively shorter section IDs
        for depth in range(len(parts), 0, -1):
            candidate = ".".join(parts[:depth])
            if candidate in self._section_index:
                return {
                    "ref": ref_string,
                    "section_id": raw_id,
                    "title": self._section_index[candidate],
                    "resolved": True,
                }

        return {
            "ref": ref_string,
            "section_id": raw_id,
            "title": "",
            "resolved": False,
        }

    def resolve_batch(self, refs: list[str]) -> list[dict]:
        """Resolve a list of cross-reference strings."""
        return [self.resolve(r) for r in refs]
