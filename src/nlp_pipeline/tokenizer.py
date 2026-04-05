"""
Tokenizer module for standardizing sentence boundaries and splitting.
"""
import spacy

class Tokenizer:
    def __init__(self, model_name: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            # If the model isn't downloaded, attempt fallback or download
            from spacy.cli import download
            download(model_name)
            self.nlp = spacy.load(model_name)
            
    def get_sentences(self, text: str) -> list[str]:
        """Split text into sentences logic via Dependency Parser."""
        doc = self.nlp(text)
        return [sent.text.strip() for sent in doc.sents]
