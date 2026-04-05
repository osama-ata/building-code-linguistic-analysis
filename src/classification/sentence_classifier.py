"""
Classifies the sentence into functional legal categories: 
Prescriptive, Constitutive, or Informative.
"""

from .deontic_detector import DeonticDetector

class SentenceClassifier:
    def __init__(self, deontic_detector: DeonticDetector):
        """
        Using a heuristic wrapper acting as a stopgap until the 
        primary HuggingFace models are trained in notebooks/.
        """
        self.detector = deontic_detector

    def classify(self, text: str) -> str:
        """Heuristic categorization based on operators and root constraints."""
        operator = self.detector.extract_operator(text)
        
        if operator != "NONE":
            # If the user is obligated, permitted, or prohibited, it's prescriptive.
            return "Prescriptive"
            
        text_lower = text.lower()
        if "means" in text_lower or "defined as" in text_lower or "refers to" in text_lower:
            return "Constitutive"
            
        return "Informative"
