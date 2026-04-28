"""
Streamlit App: Error Analysis & Corpus Statistics (Phase E)

Interactive dashboard for inspecting corpus statistics, classifier performance,
and annotation quality.
"""

import sys
import json
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

st.set_page_config(page_title="Error Analysis", layout="wide")
st.title("Error Analysis & Corpus Statistics")
st.markdown(
    "Inspect corpus-level statistics, review annotation data, and analyse "
    "classifier performance across deontic categories."
)

# ── Corpus Statistics ──────────────────────────────────────────────────────────
st.header("1. Corpus Statistics")

stats_path = ROOT / "data" / "04_processed" / "corpus_statistics.json"
if stats_path.exists() and stats_path.stat().st_size > 0:
    stats = json.loads(stats_path.read_text(encoding="utf-8"))

    cols = st.columns(4)
    cols[0].metric("Files processed", stats.get("files_processed", "—"))
    cols[1].metric("Total characters", f"{stats.get('total_characters', 0):,}")
    cols[2].metric("Total words", f"{stats.get('total_words', 0):,}")
    cols[3].metric("Total sentences", f"{stats.get('total_sentences', 0):,}")

    cols2 = st.columns(3)
    cols2[0].metric("Vocabulary size", f"{stats.get('vocab_size', 0):,}")
    cols2[1].metric(
        "Avg sentence length (words)", stats.get("average_sentence_length", "—")
    )

    top_words = stats.get("top_words", [])
    if top_words:
        st.subheader("Top Words")
        top_n = st.slider("Show top N words", 5, min(50, len(top_words)), 20)
        word_data = {w: c for w, c in top_words[:top_n]}
        st.bar_chart(word_data)
else:
    st.info(
        "`data/04_processed/corpus_statistics.json` not found or empty. "
        "Run `python scripts/corpus_statistics.py` to generate it."
    )

# ── Annotation Review ──────────────────────────────────────────────────────────
st.header("2. Annotation Review")

annot_path = ROOT / "data" / "03_annotated" / "annotations.jsonl"
gold_path = ROOT / "evaluation" / "gold_standard.jsonl"


def load_jsonl(path: Path) -> list:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


annotations = load_jsonl(annot_path)
gold = load_jsonl(gold_path)

col_a, col_g = st.columns(2)
with col_a:
    st.subheader(f"Annotations ({len(annotations)} records)")
    if annotations:
        st.dataframe(annotations[:100], use_container_width=True)
    else:
        st.info("`data/03_annotated/annotations.jsonl` is empty.")

with col_g:
    st.subheader(f"Gold Standard ({len(gold)} records)")
    if gold:
        st.dataframe(gold[:100], use_container_width=True)
    else:
        st.info("`evaluation/gold_standard.jsonl` is empty.")

# ── Live Deontic Analysis ──────────────────────────────────────────────────────
st.header("3. Live Deontic Analysis")
st.markdown(
    "Run the deontic detector and provision classifier on custom text and inspect results."
)


@st.cache_resource(show_spinner="Loading classifiers…")
def load_classifiers():
    from src.classification.deontic_detector import DeonticDetector
    from src.classification.provision_type import ProvisionClassifier

    deontic = DeonticDetector(
        patterns_path=str(ROOT / "domain" / "deontic_patterns.yaml")
    )
    provision = ProvisionClassifier()
    return deontic, provision


try:
    deontic_detector, provision_classifier = load_classifiers()
    classifiers_ok = True
except Exception as exc:
    st.warning(f"Classifiers unavailable: {exc}")
    classifiers_ok = False

if classifiers_ok:
    sample_sentences = [
        "Exit doors shall be at least 900 mm wide.",
        "The roof may be constructed of lightweight materials.",
        "Stairs shall not have open risers in high-rise buildings.",
        "Handrails need not be provided on ramps with a slope less than 1:20.",
        "All fire exits must be clearly marked.",
    ]

    raw_text = st.text_area(
        "Enter sentences (one per line)",
        value="\n".join(sample_sentences),
        height=150,
    )
    sentences = [s.strip() for s in raw_text.splitlines() if s.strip()]

    if sentences:
        results = []
        for sent in sentences:
            deontic_op = deontic_detector.extract_operator(sent)
            prov_type = provision_classifier.classify(sent)
            results.append(
                {
                    "Sentence": sent,
                    "Deontic Operator": deontic_op or "NONE",
                    "Provision Type": prov_type,
                }
            )

        st.dataframe(results, use_container_width=True)

        import collections

        st.subheader("Deontic Operator Breakdown")
        counts = collections.Counter(r["Deontic Operator"] for r in results)
        st.bar_chart(counts)

# ── Processed Rules Preview ────────────────────────────────────────────────────
st.header("4. Processed Rules Preview")

rules_path = ROOT / "data" / "04_processed" / "rules.jsonl"
rules = load_jsonl(rules_path)

if rules:
    st.metric("Total rules in pipeline output", len(rules))
    st.dataframe(rules[:50], use_container_width=True)
else:
    st.info(
        "`data/04_processed/rules.jsonl` is empty. "
        "Run `python scripts/export_rules.py` to populate it."
    )
