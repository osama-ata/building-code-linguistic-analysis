"""
Custom Named Entity Recognition (NER) for the building code domain.
"""
import spacy
from spacy.pipeline import EntityRuler
import yaml
from pathlib import Path

class ConstructionNER:
    def __init__(self, model_name: str = "en_core_web_sm", patterns_path: str = None):
        self.nlp = spacy.load(model_name)
        
        # Add ruler before the default NER overrides us
        self.ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        
        if patterns_path and Path(patterns_path).exists():
            self._load_patterns(patterns_path)

    def _load_patterns(self, path: str):
        """Parse the yaml dictionary into spacy rule formats."""
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        spacy_patterns = []
        for label, terms in data.get("patterns", {}).items():
            for term in terms:
                # Basic string match
                spacy_patterns.append({"label": label, "pattern": term})
                
        self.ruler.add_patterns(spacy_patterns)

    def extract_entities(self, text: str) -> list[dict]:
        """Returns the detected elements & custom entities."""
        doc = self.nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        return entities
