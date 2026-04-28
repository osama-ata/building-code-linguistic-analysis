"""
test_preprocessing.py — Tests for all preprocessing components.

Covers:
  - Normalizer (8 tests)
  - MarkdownParser (3 tests)
  - ChapterSplitter (2 tests)
  - CrossRefResolver (3 tests)
"""

from __future__ import annotations

import pytest

from src.preprocessing.normalizer import Normalizer
from src.preprocessing.md_parser import MarkdownParser
from src.preprocessing.section_splitter import ChapterSplitter
from src.preprocessing.cross_ref_resolver import CrossRefResolver


# ─────────────────────────────────────────────────────────────────────────────
# TestNormalizer
# ─────────────────────────────────────────────────────────────────────────────


class TestNormalizer:
    """Unit tests for src.preprocessing.normalizer.Normalizer."""

    @pytest.fixture(autouse=True)
    def _norm(self):
        self.norm = Normalizer()

    # 1 ── Strips list-item prefix and inline section number
    def test_strips_list_prefix_and_section_number(self):
        raw = "- 1.1.3 Terms  defined  in  other  codes."
        result = self.norm.normalize(raw)
        assert result.startswith("Terms"), repr(result)
        assert "1.1.3" not in result

    # 2 ── Strips heading hashes
    def test_strips_heading_hash(self):
        raw = "## 3.2.1 Educational Occupancies"
        result = self.norm.normalize(raw)
        assert not result.startswith("#"), repr(result)
        assert "Educational Occupancies" in result

    # 3 ── Collapses multiple spaces to one
    def test_collapses_multi_spaces(self):
        raw = "The  door  shall  be  fire-rated."
        result = self.norm.normalize(raw)
        assert "  " not in result
        assert "door shall be fire-rated" in result

    # 4 ── Fixes Â° mis-encoding
    def test_fixes_degree_encoding(self):
        raw = "Slope shall not exceed 20\u00c2\u00b0."
        result = self.norm.normalize(raw)
        assert "\u00c2" not in result
        assert "\u00b0" in result  # real degree sign

    # 5 ── Removes table references by default
    def test_removes_table_refs_by_default(self):
        raw = "Occupancy loads are listed in Table 9.2."
        result = self.norm.normalize(raw)
        assert "Table 9.2" not in result

    # 6 ── Preserves table refs when strip_table_refs=False
    def test_preserves_table_refs_when_disabled(self):
        norm = Normalizer(strip_table_refs=False)
        raw = "Occupancy loads are listed in Table 9.2."
        result = norm.normalize(raw)
        assert "Table 9.2" in result

    # 7 ── normalize_batch discards empty results
    def test_batch_discards_empties(self):
        texts = ["", "  ", "## ", "- 1.1 Valid clause.", ""]
        results = self.norm.normalize_batch(texts)
        assert all(r for r in results), f"Empty string in results: {results}"
        assert any("Valid clause" in r for r in results)

    # 8 ── Strips bare leading section number (no bullet prefix)
    def test_strips_leading_section_number(self):
        raw = "2.5.1 Measurement of Travel Distance."
        result = self.norm.normalize(raw)
        assert not result[0].isdigit(), repr(result)
        assert "Measurement" in result


# ─────────────────────────────────────────────────────────────────────────────
# TestMarkdownParser
# ─────────────────────────────────────────────────────────────────────────────


class TestMarkdownParser:
    """Tests for MarkdownParser using the sample_md_content fixture."""

    def test_parses_multiple_sections(self, sample_md_content):
        parser = MarkdownParser()
        result = parser.parse_file(sample_md_content)
        sections = result.get("sections", [])
        assert len(sections) >= 2, f"Expected ≥2 sections, got {len(sections)}"

    def test_captures_section_titles(self, sample_md_content):
        parser = MarkdownParser()
        result = parser.parse_file(sample_md_content)
        sections = result.get("sections", [])
        titles = [s.get("title", "") for s in sections]
        # At least one section should have a non-empty title
        assert any(t for t in titles), f"No titles found: {titles}"

    def test_clauses_contain_measurement(self, sample_md_content):
        parser = MarkdownParser()
        result = parser.parse_file(sample_md_content)
        sections = result.get("sections", [])
        all_clauses: list[str] = []
        for section in sections:
            all_clauses.extend(section.get("clauses", []))
        combined = " ".join(all_clauses)
        assert "900" in combined or "2000" in combined, (
            f"No measurement found in clauses: {combined[:200]}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# TestChapterSplitter
# ─────────────────────────────────────────────────────────────────────────────


class TestChapterSplitter:
    """Tests for ChapterSplitter using the sample_md_content fixture."""

    def test_splits_two_chapters(self, sample_md_content):
        splitter = ChapterSplitter()
        chapters = splitter.split_into_chapters(sample_md_content)
        assert len(chapters) >= 2, f"Expected ≥2 chapters, got {len(chapters)}"

    def test_chapter_body_contains_content(self, sample_md_content):
        splitter = ChapterSplitter()
        chapters = splitter.split_into_chapters(sample_md_content)
        for ch in chapters:
            body = ch.get("body", ch.get("content", ch.get("text", "")))
            assert body, f"Empty body in chapter: {ch}"


# ─────────────────────────────────────────────────────────────────────────────
# TestCrossRefResolver
# ─────────────────────────────────────────────────────────────────────────────


class TestCrossRefResolver:
    """Tests for CrossRefResolver."""

    @pytest.fixture(autouse=True)
    def _resolver(self):
        self.resolver = CrossRefResolver()
        # Manually seed the index to avoid depending on MarkdownParser
        self.resolver._section_index = {
            "2.2.3.2": "Measurement of Travel Distance",
            "9.1": "Sprinkler Systems",
        }

    def test_resolves_known_section(self):
        result = self.resolver.resolve("Section 2.2.3.2")
        assert result["resolved"] is True
        assert result["section_id"] == "2.2.3.2"
        assert "Travel Distance" in result["title"]

    def test_returns_unresolved_for_unknown(self):
        result = self.resolver.resolve("Section 99.99.99")
        assert result["resolved"] is False
        assert result["title"] == ""

    def test_resolve_batch(self):
        refs = ["Section 9.1", "Section 99.99"]
        results = self.resolver.resolve_batch(refs)
        assert len(results) == 2
        assert results[0]["resolved"] is True
        assert results[1]["resolved"] is False
