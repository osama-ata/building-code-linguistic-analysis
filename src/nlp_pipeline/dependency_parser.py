"""
Dependency Parser isolating Subject-Verb-Object (SVO) constraints.
"""
import spacy

class DependencyParser:
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.nlp = spacy.load(model_name)

    def extract_svo(self, text: str) -> list[dict]:
        """
        Extract primary Subject-Verb-Object mappings from a sentence.
        This provides the semantic constraints required for Phase D.
        """
        doc = self.nlp(text)
        svo_triplets = []
        
        for token in doc:
            if token.pos_ in ("VERB", "AUX"):
                subject = [w for w in token.lefts if w.dep_ in ("nsubj", "nsubjpass")]
                obj = [w for w in token.rights if w.dep_ in ("dobj", "pobj", "attr", "acomp")]
                
                if subject and obj:
                    svo_triplets.append({
                        "subject": " ".join([t.text for t in subject[0].subtree]),
                        "verb": token.text,
                        "object": " ".join([t.text for t in obj[0].subtree])
                    })
                    
        return svo_triplets
