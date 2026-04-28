"""
Streamlit App: Classifier Training & Evaluation (Phase C)

Demonstrates the deontic operator detector and provision-type classifier.
Allows batch evaluation on pasted or uploaded text.
"""

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

st.set_page_config(page_title="Classifier Training", layout="wide")
st.title("Classifier Training & Evaluation (Phase C)")
st.markdown(
    "Detect deontic operators (Obligation / Permission / Prohibition / Exemption) "
    "and classify provisions as Quantitative or Qualitative."
)


# --- Load classifiers (cached) ---
@st.cache_resource(show_spinner="Loading classifiers…")
def load_classifiers():
    from src.classification.deontic_detector import DeonticDetector
    from src.classification.provision_type import ProvisionClassifier

    patterns_path = ROOT / "domain" / "deontic_patterns.yaml"
    deontic = DeonticDetector(patterns_path=str(patterns_path))
    provision = ProvisionClassifier()
    return deontic, provision


try:
    deontic_detector, provision_classifier = load_classifiers()
    models_ok = True
except Exception as exc:
    st.error(f"Could not load classifiers: {exc}")
    models_ok = False

# --- Input ---
st.sidebar.header("Input")
input_mode = st.sidebar.radio(
    "Input mode", ["Single sentence", "Batch (one per line)", "Upload .txt file"]
)

default_sentences = [
    "Exit doors shall be at least 900 mm wide.",
    "The roof may be constructed of lightweight materials.",
    "Stairs shall not have open risers in buildings over four stories.",
    "Handrails need not be provided for ramps with a slope of less than 1:20.",
    "All fire exits must be clearly marked with illuminated signage.",
]

if input_mode == "Single sentence":
    raw_input = st.text_area(
        "Enter a regulatory sentence", value=default_sentences[0], height=80
    )
    sentences = [raw_input.strip()] if raw_input.strip() else []

elif input_mode == "Batch (one per line)":
    raw_input = st.text_area(
        "Enter sentences (one per line)",
        value="\n".join(default_sentences),
        height=200,
    )
    sentences = [s.strip() for s in raw_input.splitlines() if s.strip()]

else:
    uploaded = st.sidebar.file_uploader("Upload a .txt file", type=["txt"])
    if uploaded:
        sentences = [
            s.strip() for s in uploaded.read().decode("utf-8").splitlines() if s.strip()
        ]
    else:
        sentences = []
        st.info("Please upload a .txt file.")

if not models_ok or not sentences:
    st.stop()

# --- Run classification ---
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

# --- Results table ---
st.header("Classification Results")
st.metric("Sentences processed", len(results))
st.dataframe(results, use_container_width=True)

# --- Distribution charts ---
st.header("Distribution Analysis")

import collections

deontic_counts = collections.Counter(r["Deontic Operator"] for r in results)
prov_counts = collections.Counter(r["Provision Type"] for r in results)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Deontic Operator Distribution")
    st.bar_chart(deontic_counts)

with col2:
    st.subheader("Provision Type Distribution")
    st.bar_chart(prov_counts)

# --- Pattern reference ---
with st.expander("Deontic Pattern Reference (domain/deontic_patterns.yaml)"):
    import yaml

    patterns_path = ROOT / "domain" / "deontic_patterns.yaml"
    if patterns_path.exists():
        st.code(patterns_path.read_text(encoding="utf-8"), language="yaml")
    else:
        st.warning("deontic_patterns.yaml not found.")
