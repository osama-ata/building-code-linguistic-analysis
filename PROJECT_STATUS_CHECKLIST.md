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

## 🚀 Phase D: Rule Extraction & Export

- [ ] Finalize semantic roles modeling (`semantic_roles.py`).
- [x] Parse explicitly conditional clauses (`condition_parser.py`).
- [x] Construct JSON representation (`to_json.py`) and XML model for `LegalRuleML` (`to_legalruleml.py`).
- [x] Implement `semantic_roles.py` — rule-based SRL (agent / action / patient / instrument / location / quantities / cross-refs).
- [x] Implement `constraint_builder.py` — orchestrates all Phase D extractors into unified `Constraint` objects.
- [x] Implement `confidence_scorer.py` — additive 0–1 confidence scoring rubric.
- [x] Implement `ambiguity_flagger.py` — 8 human-review flag codes (UNRESOLVED_PRONOUN, MISSING_AGENT, etc.).
- [ ] Run robust end-to-end integration tests over the full model logic.

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
