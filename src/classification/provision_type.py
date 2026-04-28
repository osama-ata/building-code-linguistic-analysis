"""
Categorizes provisions by Quantitative or Qualitative nature.
"""

import re


class ProvisionClassifier:
    def __init__(self):
        # Require a physical unit after the number to avoid false positives on
        # section references like "2.2.3.2" or bare numerals in body text.
        self.number_pattern = re.compile(
            r"\b\d+(?:\.\d+)?\s*"
            r"(?:mm|m\b|cm|km|lux|N\b|rpm|%|percent|degrees?|"
            r"m2|m\s*2|sq\s*ft|ft\b|in\b|kJ/g|ml|kPa|psi|"
            r"°C|liters|litres|kilograms|microns|kg\b|hours?\b|minutes?\b)\b",
            re.IGNORECASE,
        )

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
