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

**Workflow run results (latest — Phase F fixes applied):**

| Metric | Before Phase E | After Phase E | After Phase F (current) |
|---|---|---|---|
| Total constraints | 59 | 60 | **113** |
| Avg confidence | 0.542 | 0.536 | **0.565** |
| Max confidence | 0.75 | 0.75 | **0.95** |
| 0.8–1.0 confidence | 0 | 0 | **6** |
| PROHIBITION detected | 0 | 0 | **5** |
| UNRESOLVED_PRONOUN flags | — | 45 | **8** |
| Flag rate | — | 98.3% | **75.2%** |
| With numeric value | — | 1 | **6** |
| With cross-reference | — | 4 | **11** |
| SVO triplets (100 clauses) | — | 11 | **21** |
| Pipeline time | 7.2 s | 4.7 s | 5.5 s |
| Tests passing | 0 / 0 | 41 / 41 | **41 / 41** |

**Completed Phase E enhancements:**

- [x] Implement `src/preprocessing/normalizer.py` — strips list-item prefixes, heading hashes, multi-space runs, mis-encoded Unicode.
- [x] Fix `src/classification/provision_type.py` — require physical unit after number to avoid false-positive Quantitative (80.8% → 13.0%).
- [x] Expand `domain/entity_types.yaml` — BUILDING_ELEMENT 14 → ~85 patterns; added FIRE_RESISTANCE, MATERIAL categories.
- [x] Implement `src/preprocessing/cross_ref_resolver.py` — index section titles, resolve Section X.Y.Z with progressive fallback.
- [x] Populate `tests/conftest.py`, `tests/test_preprocessing.py` (16), `tests/test_rule_extraction.py` (14), `tests/test_export.py` (8) — 41/41 pass.
- [x] Updated `scripts/run_full_workflow.py` to normalise clauses in Phase A using Normalizer.

**Completed Phase F enhancements (this session):**

- [x] Fix `DeonticDetector.extract_operator()` — check PROHIBITION/EXEMPTION before OBLIGATION/PERMISSION to prevent `\bshall\b` shadowing `\bshall not\b` (PROHIBITION was 0 → now 5).
- [x] Fix `scripts/run_full_workflow.py` Phase D — pre-split each clause block into individual sentences via spaCy before calling `ConstraintBuilder.build_from_sentences()`, fixing MISSING_AGENT from 78% → 32%.
- [x] Tune `src/rule_extraction/ambiguity_flagger.py` `_PRONOUN_RE` — removed `this/that/these/those/such/the above/the following` (legal cross-reference language) from UNRESOLVED_PRONOUN detection (45 → 8 flags).
- [x] Remove `"in"` false-positive MEASUREMENT pattern from `domain/entity_types.yaml` (matched every English preposition).
- [x] Add passive voice SVO extraction to `src/nlp_pipeline/dependency_parser.py` — handles `nsubjpass + auxpass` pattern; SVO triplets 11 → 21.
- [x] Integrate `CrossRefResolver` in workflow Phase A — annotate sections with IDs extracted from title prefix, build index (16 entries), resolve cross-refs to human-readable titles in Phase D.
- [x] Fix `scripts/run_full_workflow.py` CrossRefResolver usage — correctly handle dict return value from `resolve()`.
- [x] Fix `tests/test_classification.py` — updated `s4` expected deontic operator from OBLIGATION → PROHIBITION.
- [x] Full end-to-end run verified: 113 constraints, 41/41 tests, XML export working.

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
