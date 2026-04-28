# Project Status & Workflow Checklist

This document tracks the progress of the `building-code-linguistic-analysis` pipeline implementation.

## ✅ Phase A: Preprocessing & Repository Initialization

- [x] Establish base `pyproject.toml`, `.gitignore`, and `Makefile` structure.
- [x] Create project module skeleton (`src/`, `data/`, `tests/`, `configs/`, etc.).
- [x] Draft initial parser architectures (`md_parser.py`, `section_splitter.py`).
- [x] Scaffold domain artifacts (`deontic_patterns.yaml`).
- [x] Segment raw input string `SBC-201-2007.md` into individual curated chapter files.
- [x] Establish corpus vocabulary & sentence data baseline via `scripts/corpus_statistics.py`.
- [x] Produce and integrate agent scaffolding (`AGENTS.md`).

## ✅ Phase B: Linguistic Analysis (Completed)

- [x] Incorporate `spaCy` to run linguistic extractions.
- [x] Build dependency parser to extract Subject-Verb-Object relationships.
- [x] Implement Custom Named Entity Recognition (NER) for construction domain terms.
- [x] Handle coreference resolution.

## ✅ Phase C: Classification & Deontic Logic (Completed)

- [x] Fine-tune classifier to identify prescriptive vs. informative sentences (Heuristic mapping active).
- [x] Build mapping system for deontic operators (Obligation, Permission, Prohibition).

## ✅ Phase D: Rule Extraction & Export (Completed)

- [x] Finalize semantic roles modeling (`semantic_roles.py`).
- [x] Parse explicitly conditional clauses (`condition_parser.py`).
- [x] Construct JSON representation (`to_json.py`) and XML model for `LegalRuleML` (`to_legalruleml.py`).
- [x] Implement `semantic_roles.py` — rule-based SRL (agent / action / patient / instrument / location / quantities / cross-refs).
- [x] Implement `constraint_builder.py` — orchestrates all Phase D extractors into unified `Constraint` objects.
- [x] Implement `confidence_scorer.py` — additive 0–1 confidence scoring rubric.
- [x] Implement `ambiguity_flagger.py` — 8 human-review flag codes (UNRESOLVED_PRONOUN, MISSING_AGENT, etc.).
- [x] Run end-to-end workflow (`scripts/run_full_workflow.py`) — 18 chapters, 370 sections, 6 890 clauses, 59 prescriptive constraints exported.

## 🚀 Phase E: Quality Enhancements (In Progress)

**Workflow run results (2026-04-28):**

- Phases A–D completed in 7.2 s on full SBC-201-2007.md (1 698 576 chars)
- 59 constraints exported to `data/04_processed/rules.jsonl` and `rules_legalruleml.xml`
- Average confidence: 0.542 (max 0.75) — blocked by missing agent/patient
- Flag rate: 98.3% — root cause: PDF-to-Markdown artefacts pollute clause text pre-NLP

**Enhancements in progress:**

- [x] Implement `src/preprocessing/normalizer.py` — strips list-item prefixes, heading hashes, multi-space runs, mis-encoded Unicode (critical — unblocks NER and SRL quality).
- [x] Fix `src/classification/provision_type.py` — require physical unit after number to avoid false-positive Quantitative on section references like `2.2.3.2`.
- [x] Expand `domain/entity_types.yaml` — grew BUILDING_ELEMENT from 14 → ~85 patterns; added FIRE_RESISTANCE and MATERIAL categories; expanded MEASUREMENT, SPATIAL, OCCUPANCY_GROUP.
- [x] Implement `src/preprocessing/cross_ref_resolver.py` — index all section titles and resolve `Section X.Y.Z` strings to their titles.
- [x] Populate `tests/conftest.py` with shared fixtures (5 session-scoped fixtures).
- [x] Populate `tests/test_preprocessing.py` (16 tests: Normalizer, MarkdownParser, ChapterSplitter, CrossRefResolver) — all pass.
- [x] Populate `tests/test_rule_extraction.py` (14 tests: ConditionParser, SemanticRoleLabeller, AmbiguityFlagger, ConfidenceScorer) — all pass.
- [x] Populate `tests/test_export.py` (8 tests: JsonExporter, LegalRuleMLExporter) — all pass.
- [x] Updated `scripts/run_full_workflow.py` to normalise clauses (Phase A) using Normalizer before NLP.
- **Test suite result: 41 / 41 passed in 3.98s**

## ✅ Interactive Apps (Streamlit)

Jupyter notebooks replaced with browser-based Streamlit apps under `apps/`.

- [x] `apps/01_md_exploration.py` — Phase A: raw markdown exploration & chapter splitting.
- [x] `apps/02_ner_prototyping.py` — Phase B: NER, tokenisation & SVO dependency parsing.
- [x] `apps/03_classifier_training.py` — Phase C: deontic detection & provision classification.
- [x] `apps/04_rule_extraction_demo.py` — Phase D: full rule extraction with JSON Lines export.
- [x] `apps/05_error_analysis.py` — Phase E: corpus statistics, annotation review & error analysis.
- [x] `apps/Home.py` — Multi-page home dashboard.
- [x] README updated with `streamlit run` usage examples.

## 📓 Machine Learning TODOs

- [ ] Fine-tune `spaCy TextCategorizer` for prescriptive vs. informative classification.
- [ ] Build pipeline evaluation dataset (`gold_standard.jsonl`).
- [ ] Populate `data/03_annotated/annotations.jsonl` with labelled examples.
