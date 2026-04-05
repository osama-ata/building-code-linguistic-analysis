# Enhanced Repository Structure & Implementation Guide

## building-code-linguistic-analysis

> Tailored for your context: building codes already available as `.md` files — Phase 1 (Data Acquisition) is bypassed.

---

## 1. Revised Repository Structure

```
building-code-linguistic-analysis/
├── .gitignore
├── README.md
├── LICENSE
├── pyproject.toml                    # Single source for deps, metadata, tool config
├── Makefile                          # Common commands: lint, test, run-pipeline
│
├── configs/                          # All configuration in one place
│   ├── pipeline.yaml                 # End-to-end pipeline settings
│   ├── spacy_config.cfg              # spaCy training config for custom NER
│   └── logging.yaml                  # Centralized logging config
│
├── data/
│   ├── 01_raw/                       # Your .md building code files go here
│   │   ├── sbc_chapter_03.md         # e.g., Saudi Building Code chapters
│   │   ├── sbc_chapter_04.md
│   │   └── ...
│   ├── 02_curated/                   # Cleaned & section-split markdown
│   │   └── sbc_ch03/
│   │       ├── 3.1_general.md
│   │       └── 3.2_structural.md
│   ├── 03_annotated/                 # Gold-standard human annotations
│   │   ├── annotations.jsonl         # One JSON object per clause
│   │   └── annotation_guide.md       # Codebook for annotators
│   └── 04_processed/                 # Pipeline outputs (structured rules)
│       ├── rules.jsonl               # Extracted rules in JSON Lines
│       └── rules_legalruleml.xml     # LegalRuleML export
│
├── src/
│   ├── __init__.py
│   ├── config.py                     # Loads configs/, defines paths & constants
│   │
│   ├── preprocessing/                # Phase 2 replacement: .md → structured sections
│   │   ├── __init__.py
│   │   ├── md_parser.py              # Parse .md headers, lists, tables, cross-refs
│   │   ├── section_splitter.py       # Split into clause-level units
│   │   ├── normalizer.py             # Normalize numbering, units, abbreviations
│   │   └── cross_ref_resolver.py     # Resolve "see Section 3.2.1" references
│   │
│   ├── nlp_pipeline/                 # Core linguistic analysis
│   │   ├── __init__.py
│   │   ├── tokenizer.py              # Sentence splitting & tokenization
│   │   ├── pos_tagger.py             # POS tagging with construction domain rules
│   │   ├── dependency_parser.py      # Syntactic dependency parsing
│   │   ├── ner.py                    # Custom NER: building elements & constraints
│   │   └── coreference.py            # Resolve "it", "such", "the same" references
│   │
│   ├── classification/               # Sentence-level classification
│   │   ├── __init__.py
│   │   ├── sentence_classifier.py    # Prescriptive vs. Constitutive vs. Informative
│   │   ├── deontic_detector.py       # Detect shall/may/must/shall-not patterns
│   │   └── provision_type.py         # Quantitative vs. qualitative provisions
│   │
│   ├── rule_extraction/              # Semantic role → structured rule
│   │   ├── __init__.py
│   │   ├── semantic_roles.py         # Extract Subject, Object, Operator, Value
│   │   ├── condition_parser.py       # Parse if/when/where/unless clauses
│   │   ├── constraint_builder.py     # Build structured constraint objects
│   │   ├── confidence_scorer.py      # Assign interpretability confidence
│   │   └── ambiguity_flagger.py      # Flag vague terms for human review
│   │
│   ├── export/                       # Output formatters
│   │   ├── __init__.py
│   │   ├── to_json.py                # Export to JSON / JSON Lines
│   │   ├── to_legalruleml.py         # Export to LegalRuleML XML
│   │   ├── to_sparql.py              # Optional: generate SPARQL queries for BIM
│   │   └── to_ifc_mvd.py            # Optional: map to IFC MVD concepts
│   │
│   ├── pipeline.py                   # Orchestrates the full pipeline end-to-end
│   │
│   └── utils/
│       ├── __init__.py
│       ├── text_cleaning.py          # Strip markdown artifacts, normalize whitespace
│       ├── unit_converter.py         # Handle metric/imperial, Arabic numerals
│       └── logger.py                 # Structured logging setup
│
├── domain/                           # Domain knowledge & lexicons
│   ├── construction_lexicon.jsonl    # Domain terms: door, lintel, rebar, مخرج
│   ├── deontic_patterns.yaml         # Regex/dependency patterns for shall/may/must
│   ├── unit_aliases.yaml             # "m" → meters, "mm" → millimeters, etc.
│   └── entity_types.yaml             # NER label definitions & examples
│
├── models/                           # Trained model artifacts (git-ignored, DVC-tracked)
│   ├── ner/                          # Custom spaCy NER model
│   ├── classifier/                   # Fine-tuned sentence classifier
│   └── embeddings/                   # Cached word/sentence embeddings
│
├── notebooks/
│   ├── 01_md_exploration.ipynb       # Explore .md structure & edge cases
│   ├── 02_ner_prototyping.ipynb      # Prototype NER on sample clauses
│   ├── 03_classifier_training.ipynb  # Train & evaluate sentence classifier
│   ├── 04_rule_extraction_demo.ipynb # End-to-end extraction demo
│   └── 05_error_analysis.ipynb       # Analyze pipeline failure modes
│
├── tests/
│   ├── conftest.py                   # Shared fixtures: sample clauses, expected outputs
│   ├── test_preprocessing.py
│   ├── test_nlp_pipeline.py
│   ├── test_classification.py
│   ├── test_rule_extraction.py
│   ├── test_export.py
│   └── test_integration.py           # End-to-end pipeline test
│
├── evaluation/                       # Evaluation framework
│   ├── gold_standard.jsonl           # 150–200 manually annotated clauses
│   ├── evaluate.py                   # Compute P/R/F1 per component
│   ├── confusion_matrix.py           # Visualize classification errors
│   └── reports/                      # Generated evaluation reports
│
├── scripts/                          # One-off & utility scripts
│   ├── run_pipeline.py               # CLI entry point
│   ├── annotate_helper.py            # Interactive annotation tool
│   └── export_rules.py               # Batch export script
│
├── docs/                             # Project documentation
│   ├── architecture.md               # System design & data flow
│   ├── annotation_codebook.md        # How to annotate clauses
│   ├── api_reference.md              # Module-level API docs
│   └── decisions/                    # Architecture Decision Records (ADRs)
│       ├── 001_why_spacy.md
│       └── 002_rule_schema.md
│
└── docker/                           # Reproducible environment
    ├── Dockerfile
    └── docker-compose.yaml
```

---

## 2. Key Changes from the Original Proposal

### What was removed
- **`src/data_ingestion/`** — You already have `.md` files; no PDF/OCR pipeline needed.
- **`requirements.txt`** — Replaced by `pyproject.toml` for modern Python packaging.

### What was added

| Addition | Rationale |
|---|---|
| **`src/preprocessing/`** | Your `.md` files still need parsing: extract headers as section IDs, handle markdown tables, resolve cross-references between sections, and normalize units/abbreviations. |
| **`src/rule_extraction/condition_parser.py`** | Building codes are full of conditional logic ("if the building exceeds 3 stories, then..."). This needs a dedicated parser, not just deontic detection. |
| **`src/rule_extraction/ambiguity_flagger.py`** | Implements the "confidence score" concept. Flags terms like "adequate", "sufficient", "as required" for human review. |
| **`src/export/`** | Separated from rule_extraction. Export is its own concern — you'll want multiple output formats. |
| **`domain/`** | Externalizes domain knowledge. Lexicons, deontic patterns, and entity definitions should be data, not hardcoded in source. |
| **`evaluation/`** | Dedicated evaluation directory with gold standard data and metric scripts, separate from unit tests. |
| **`configs/`** | All pipeline parameters in YAML. Makes experiments reproducible and avoids magic numbers in code. |
| **`docs/decisions/`** | Architecture Decision Records track *why* you chose spaCy over Stanza, why your rule schema looks the way it does, etc. |
| **`src/nlp_pipeline/coreference.py`** | Building codes heavily use anaphoric references ("it shall be...", "the same material"). Without coreference resolution, extracted rules lose their subject. |

---

## 3. Revised Implementation Phases

### Phase A — Preprocessing (replaces Phase 1)

Since your codes are already in `.md`, the challenge shifts from extraction to **structural parsing**:

- Parse markdown headers into a hierarchical section tree (Chapter → Section → Clause)
- Split compound clauses at sentence boundaries while preserving cross-references
- Normalize measurement units, numbering schemes, and abbreviations
- Build a section index so "see Section 3.2.1" can be resolved programmatically

**Key module:** `src/preprocessing/md_parser.py`

### Phase B — Linguistic Analysis (Phase 2)

Unchanged in concept, but with a construction-domain focus:

- Train a **custom spaCy NER** model for entity types: `BUILDING_ELEMENT` (door, wall, staircase), `MEASUREMENT` (3m, 100mm), `MATERIAL` (concrete, steel), `SPATIAL` (corridor, exit route)
- Use dependency parsing to extract **Subject-Verb-Object** triples
- Add coreference resolution for pronoun/demonstrative references

**Key module:** `src/nlp_pipeline/`

### Phase C — Classification & Deontic Logic (Phase 3)

Two-stage classification:

1. **Sentence type:** Prescriptive (creates obligation/permission) vs. Constitutive (defines a term) vs. Informative (provides context/notes)
2. **Deontic operator:** For prescriptive sentences, map modal verbs to `OBLIGATION`, `PERMISSION`, `PROHIBITION`, `EXEMPTION`

Use pattern-based detection first (deontic_patterns.yaml), then a fine-tuned classifier for edge cases.

**Key module:** `src/classification/`

### Phase D — Rule Extraction & Export (Phase 4)

Extract structured rules with this schema:

```json
{
  "id": "SBC-3.2.1-R01",
  "source": { "chapter": 3, "section": "3.2.1", "sentence": 2 },
  "type": "OBLIGATION",
  "subject": "exit door",
  "property": "minimum width",
  "operator": ">=",
  "value": 900,
  "unit": "mm",
  "conditions": [
    { "property": "occupancy_load", "operator": ">", "value": 50 }
  ],
  "confidence": 0.92,
  "ambiguous_terms": [],
  "requires_human_review": false
}
```

**Key module:** `src/rule_extraction/`

### Phase E — Evaluation (Phase 5)

Build a **gold standard** of 150–200 manually annotated clauses covering:
- All sentence types (prescriptive, constitutive, informative)
- All deontic operators
- Quantitative and qualitative constraints
- Conditional and unconditional rules
- Ambiguous and clear clauses

Evaluate each pipeline component independently (NER F1, classification accuracy, rule extraction precision) and end-to-end.

**Key module:** `evaluation/`

---

## 4. Recommended Tech Stack

| Component | Tool | Why |
|---|---|---|
| NLP backbone | spaCy 3.x | Best dependency parser for production; trainable NER pipeline; Arabic support via `camel-tools` integration |
| Sentence classification | spaCy `TextCategorizer` or HuggingFace `bert-base-multilingual` | Start simple with spaCy; upgrade to transformer if needed |
| Configuration | Hydra or OmegaConf | Composable YAML configs for experiments |
| Data versioning | DVC | Track large model files and datasets outside git |
| Testing | pytest + pytest-cov | Standard; aim for 80%+ coverage on core modules |
| Experiment tracking | MLflow or Weights & Biases | Track NER/classifier training runs |
| Packaging | pyproject.toml + hatch | Modern Python packaging |

---

## 5. Suggested `.gitignore` Additions

```gitignore
# Data (tracked via DVC)
data/01_raw/
data/02_curated/
data/04_processed/

# Models
models/

# Evaluation reports
evaluation/reports/

# Notebook outputs
notebooks/.ipynb_checkpoints/
```

---

## 6. Quick Start Skeleton — `pyproject.toml`

```toml
[project]
name = "building-code-linguistic-analysis"
version = "0.1.0"
description = "NLP pipeline for transforming building codes into machine-processable rules"
requires-python = ">=3.10"
dependencies = [
    "spacy>=3.7",
    "pyyaml>=6.0",
    "jsonlines>=4.0",
    "click>=8.0",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = ["pytest", "pytest-cov", "ruff", "mypy", "ipykernel"]
ml = ["transformers", "torch", "scikit-learn", "mlflow"]

[project.scripts]
run-pipeline = "scripts.run_pipeline:main"
```

---

## 7. First Steps (Action Items)

1. **Set up the repo skeleton** — Create the directory structure above with empty `__init__.py` files
2. **Place your `.md` files** in `data/01_raw/`
3. **Build `md_parser.py`** — Parse one chapter end-to-end: headers → section tree → individual clauses
4. **Manually annotate 30 clauses** — This small gold set lets you iterate on NER and classification before scaling to 150+
5. **Implement deontic detection** — Start with regex patterns in `deontic_patterns.yaml`; this gives you quick wins before training ML models
6. **Write your first integration test** — One `.md` file in, structured rules out; this becomes your regression guard
