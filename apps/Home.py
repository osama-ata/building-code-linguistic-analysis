"""
Building Code Linguistic Analysis — Streamlit Home Page

Run with:
    streamlit run apps/Home.py
"""

import streamlit as st

st.set_page_config(
    page_title="Building Code Linguistic Analysis",
    page_icon="🏛️",
    layout="wide",
)

st.title("Building Code Linguistic Analysis")
st.markdown(
    "An NLP pipeline that transforms raw building-code regulations into "
    "structured, computationally accessible formats (JSON / LegalRuleML)."
)

st.markdown("---")

pages = [
    (
        "01_md_exploration",
        "Markdown Exploration",
        "Phase A — Chunk raw `.md` documents into semantic chapters and validate structural parsers.",
    ),
    (
        "02_ner_prototyping",
        "NER Prototyping",
        "Phase B — Custom NER, sentence tokenisation, and SVO dependency parsing on regulatory text.",
    ),
    (
        "03_classifier_training",
        "Classifier Training",
        "Phase C — Detect deontic operators and classify provisions as Quantitative / Qualitative.",
    ),
    (
        "04_rule_extraction_demo",
        "Rule Extraction Demo",
        "Phase D — Full extraction pipeline producing structured JSON rule objects.",
    ),
    (
        "05_error_analysis",
        "Error Analysis",
        "Phase E — Corpus statistics, annotation review, and classifier performance dashboard.",
    ),
]

cols = st.columns(len(pages))
for col, (page_id, title, desc) in zip(cols, pages):
    col.subheader(title)
    col.markdown(desc)
    col.code(f"streamlit run apps/{page_id}.py", language="bash")

st.markdown("---")
st.markdown(
    "**How to run individual apps:**\n"
    "```bash\n"
    "streamlit run apps/01_md_exploration.py\n"
    "streamlit run apps/02_ner_prototyping.py\n"
    "streamlit run apps/03_classifier_training.py\n"
    "streamlit run apps/04_rule_extraction_demo.py\n"
    "streamlit run apps/05_error_analysis.py\n"
    "```"
)
