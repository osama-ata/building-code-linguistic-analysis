"""
Categorizes provisions by Quantitative or Qualitative nature.
"""
import re

class ProvisionClassifier:
    def __init__(self):
        # A simple fallback check for physical numeric traits.
        # Ideally, this listens to the 'MEASUREMENT' parameter emitted from spaCy NER.
        self.number_pattern = re.compile(r'\b\d+(\.\d+)?\b')

    def classify(self, text: str, entities: list = None) -> str:
        """
        Determines provision typology. If entities exist and contain MEASUREMENT tags,
        it evaluates as Quantitative.
        """
        if entities:
            for ent in entities:
                if ent.get("label") == "MEASUREMENT":
                    return "Quantitative"
                    
        # Fallback to regex testing if NER wasn't passed down.
        if self.number_pattern.search(text):
            return "Quantitative"
            
        return "Qualitative"
