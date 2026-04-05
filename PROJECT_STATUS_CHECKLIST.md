# Project Status & Workflow Checklist

This document tracks the progress of the `building-code-linguistic-analysis` pipeline implementation.

## ✅ Phase A: Preprocessing & Repository Initialization
- [x] Establish base `pyproject.toml`, `.gitignore`, and `Makefile` structure.
- [x] Create project module skeleton (`src/`, `data/`, `tests/`, `configs/`, etc.).
- [x] Draft initial parser architectures (`md_parser.py`, `section_splitter.py`).
- [x] Scaffold domain artifacts (`deontic_patterns.yaml`).
- [x] Segment raw input string `SBC-201-2007.md` into individual curated chapter files.
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
- [ ] Parse explicitly conditional clauses (`condition_parser.py`).
- [ ] Construct JSON representation (`to_json.py`) and XML model for `LegalRuleML`.
- [ ] Run robust end-to-end integration tests over the full model logic.

## 📓 Machine Learning & Notebooks TODOs
- [x] Create `01_md_exploration.ipynb` for RAW to processed text visualization.
- [x] Create `02_ner_prototyping.ipynb` for NLP model execution.
- [ ] Implement `03_classifier_training.ipynb` for fine-tuning `spaCy TextCategorizer`.
- [ ] Build `04_rule_extraction_demo.ipynb` for JSON rule debugging.
- [ ] Build pipeline evaluation dataset (`gold_standard.jsonl`).
