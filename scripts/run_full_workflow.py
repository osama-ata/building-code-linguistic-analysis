"""
run_full_workflow.py — End-to-end linguistic analysis workflow runner.

Phases:
  A  Preprocessing  — split raw MD into chapters, parse sections
  B  NLP            — tokenise, NER, dependency parsing (SVO)
  C  Classification — deontic detection, provision typing
  D  Rule Extraction — constraint building, condition parsing, scoring
  Export            — JSON Lines + LegalRuleML XML
"""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

RAW_FILE = ROOT / "data" / "01_raw" / "SBC-201-2007.md"
RULES_OUT = ROOT / "data" / "04_processed" / "rules.jsonl"
XML_OUT = ROOT / "data" / "04_processed" / "rules_legalruleml.xml"
STATS_OUT = ROOT / "data" / "04_processed" / "workflow_stats.json"

SEP = "=" * 70


def banner(title):
    print(f"\n{SEP}\n  {title}\n{SEP}")


# ── Phase A: Preprocessing ─────────────────────────────────────────────────
banner("PHASE A — PREPROCESSING")
t0 = time.time()

from src.preprocessing.section_splitter import ChapterSplitter
from src.preprocessing.md_parser import MarkdownParser
from src.preprocessing.normalizer import Normalizer

raw_text = RAW_FILE.read_text(encoding="utf-8")
print(f"  Raw file loaded: {len(raw_text):,} chars")

splitter = ChapterSplitter()
chapters = splitter.split_into_chapters(raw_text)
meaningful = [c for c in chapters if len(c["body"].split()) > 20]
print(f"  Chapters extracted : {len(chapters)}")
print(f"  Meaningful chapters: {len(meaningful)}")

md_parser = MarkdownParser()
total_sections = 0
all_clauses = []
for ch in meaningful:
    struct = md_parser.parse_file(ch["body"])
    for sec in struct.get("sections", []):
        total_sections += 1
        all_clauses.extend(sec.get("clauses", []))

print(f"  Total sections     : {total_sections}")
print(f"  Total clauses (raw): {len(all_clauses)}")
normalizer = Normalizer()
all_clauses = normalizer.normalize_batch(all_clauses)
print(f"  Total clauses (normalised): {len(all_clauses)}")
phase_a_time = time.time() - t0
print(f"  Time: {phase_a_time:.1f}s")

# Sample sentences for downstream phases (cap at 500 for speed)
sample_clauses = [c for c in all_clauses if len(c.split()) >= 5][:500]
print(f"  Sample clauses for NLP (>=5 words): {len(sample_clauses)}")

# ── Phase B: NLP Pipeline ──────────────────────────────────────────────────
banner("PHASE B — NLP PIPELINE")
t0 = time.time()

from src.nlp_pipeline.tokenizer import Tokenizer
from src.nlp_pipeline.ner import ConstructionNER
from src.nlp_pipeline.dependency_parser import DependencyParser

tokenizer = Tokenizer()
ner_model = ConstructionNER(patterns_path=str(ROOT / "domain" / "entity_types.yaml"))
dep_parser = DependencyParser()

# Run on first 100 clauses for detailed stats
nlp_sample = sample_clauses[:100]
total_sents, total_entities, total_svo = 0, 0, 0
entity_label_counts = {}
for clause in nlp_sample:
    sents = tokenizer.get_sentences(clause)
    total_sents += len(sents)
    ents = ner_model.extract_entities(clause)
    total_entities += len(ents)
    for e in ents:
        lbl = e.get("label", "OTHER")
        entity_label_counts[lbl] = entity_label_counts.get(lbl, 0) + 1
    svos = dep_parser.extract_svo(clause)
    total_svo += len(svos)

phase_b_time = time.time() - t0
print(f"  Sample size        : {len(nlp_sample)} clauses")
print(f"  Sentences detected : {total_sents}")
print(f"  Entities detected  : {total_entities}")
print(f"  SVO triplets       : {total_svo}")
print(f"  Entity breakdown   : {json.dumps(entity_label_counts, indent=4)}")
print(f"  Time: {phase_b_time:.1f}s")

# ── Phase C: Classification ────────────────────────────────────────────────
banner("PHASE C — CLASSIFICATION & DEONTIC LOGIC")
t0 = time.time()

from src.classification.deontic_detector import DeonticDetector
from src.classification.provision_type import ProvisionClassifier

deontic_det = DeonticDetector(str(ROOT / "domain" / "deontic_patterns.yaml"))
prov_clf = ProvisionClassifier()

deontic_counts = {}
provision_counts = {}
for clause in sample_clauses:
    op = deontic_det.extract_operator(clause) or "NONE"
    pt = prov_clf.classify(clause)
    deontic_counts[op] = deontic_counts.get(op, 0) + 1
    provision_counts[pt] = provision_counts.get(pt, 0) + 1

prescriptive_n = sum(v for k, v in deontic_counts.items() if k != "NONE")
phase_c_time = time.time() - t0
print(f"  Sample size           : {len(sample_clauses)} clauses")
print(
    f"  Prescriptive clauses  : {prescriptive_n} ({prescriptive_n / len(sample_clauses) * 100:.1f}%)"
)
print(f"  Deontic distribution  : {json.dumps(deontic_counts, indent=4)}")
print(f"  Provision types       : {json.dumps(provision_counts, indent=4)}")
print(f"  Time: {phase_c_time:.1f}s")

# ── Phase D: Rule Extraction ───────────────────────────────────────────────
banner("PHASE D — RULE EXTRACTION & CONSTRAINT BUILDING")
t0 = time.time()

from src.rule_extraction.constraint_builder import ConstraintBuilder
from src.export.to_json import JsonExporter
from src.export.to_legalruleml import LegalRuleMLExporter

# Only run constraint builder on prescriptive clauses (has deontic op) for quality
prescriptive_clauses = [
    c for c in sample_clauses if (deontic_det.extract_operator(c) or "NONE") != "NONE"
]
print(f"  Prescriptive clauses to process: {len(prescriptive_clauses)}")

builder = ConstraintBuilder(
    patterns_path=ROOT / "domain" / "deontic_patterns.yaml",
)
sentence_pairs = [
    (f"SBC201.{i + 1:04d}", s) for i, s in enumerate(prescriptive_clauses)
]
constraints = builder.build_from_sentences(sentence_pairs)

# Stats
flag_counts = {}
confidence_bins = {"0.0-0.2": 0, "0.2-0.4": 0, "0.4-0.6": 0, "0.6-0.8": 0, "0.8-1.0": 0}
with_condition = with_numeric = with_crossref = flagged = 0
for c in constraints:
    if c.flags:
        flagged += 1
    for fl in c.flags:
        flag_counts[fl] = flag_counts.get(fl, 0) + 1
    if c.condition:
        with_condition += 1
    if c.numeric_values:
        with_numeric += 1
    if c.cross_refs:
        with_crossref += 1
    conf = c.confidence
    if conf < 0.2:
        confidence_bins["0.0-0.2"] += 1
    elif conf < 0.4:
        confidence_bins["0.2-0.4"] += 1
    elif conf < 0.6:
        confidence_bins["0.4-0.6"] += 1
    elif conf < 0.8:
        confidence_bins["0.6-0.8"] += 1
    else:
        confidence_bins["0.8-1.0"] += 1

avg_conf = (
    sum(c.confidence for c in constraints) / len(constraints) if constraints else 0
)
phase_d_time = time.time() - t0
print(f"  Constraints built      : {len(constraints)}")
print(f"  Avg confidence         : {avg_conf:.3f}")
print(f"  Confidence distribution: {json.dumps(confidence_bins, indent=4)}")
print(f"  With condition clause  : {with_condition}")
print(f"  With numeric value     : {with_numeric}")
print(f"  With cross-reference   : {with_crossref}")
print(f"  Flagged for review     : {flagged} ({flagged / len(constraints) * 100:.1f}%)")
print(f"  Flag breakdown         : {json.dumps(flag_counts, indent=4)}")
print(f"  Time: {phase_d_time:.1f}s")

# ── Export ─────────────────────────────────────────────────────────────────
banner("EXPORT")
json_exp = JsonExporter()
written = json_exp.export(constraints, RULES_OUT)
print(f"  JSON Lines written : {written} records → {RULES_OUT.name}")

xml_exp = LegalRuleMLExporter()
xml_exp.export(constraints, XML_OUT)
print(f"  LegalRuleML written: {XML_OUT.name}")

# Sample output
print("\n  Sample constraint (first record):")
print(
    "  "
    + json.dumps(constraints[0].to_dict(), indent=4, ensure_ascii=False)[:800]
    + "..."
)

# ── Tests ──────────────────────────────────────────────────────────────────
banner("PYTEST SUITE")
import subprocess

result = subprocess.run(
    [".venv\\Scripts\\python.exe", "-m", "pytest", "tests/", "-v", "--tb=short", "-q"],
    capture_output=True,
    text=True,
    cwd=str(ROOT),
)
print(result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[-1000:])

# ── Summary stats JSON ─────────────────────────────────────────────────────
stats = {
    "phase_a": {
        "chapters": len(chapters),
        "meaningful_chapters": len(meaningful),
        "total_sections": total_sections,
        "total_clauses": len(all_clauses),
        "time_s": round(phase_a_time, 2),
    },
    "phase_b": {
        "nlp_sample_size": len(nlp_sample),
        "sentences": total_sents,
        "entities": total_entities,
        "svo_triplets": total_svo,
        "entity_breakdown": entity_label_counts,
        "time_s": round(phase_b_time, 2),
    },
    "phase_c": {
        "sample_size": len(sample_clauses),
        "prescriptive_count": prescriptive_n,
        "prescriptive_pct": round(prescriptive_n / len(sample_clauses) * 100, 1),
        "deontic_distribution": deontic_counts,
        "provision_types": provision_counts,
        "time_s": round(phase_c_time, 2),
    },
    "phase_d": {
        "constraints": len(constraints),
        "avg_confidence": round(avg_conf, 3),
        "confidence_distribution": confidence_bins,
        "with_condition": with_condition,
        "with_numeric": with_numeric,
        "with_cross_ref": with_crossref,
        "flagged": flagged,
        "flag_breakdown": flag_counts,
        "time_s": round(phase_d_time, 2),
    },
}
STATS_OUT.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")

banner("COMPLETE")
total_time = phase_a_time + phase_b_time + phase_c_time + phase_d_time
print(f"  Total pipeline time: {total_time:.1f}s")
print(f"  Stats saved to    : {STATS_OUT.name}")
