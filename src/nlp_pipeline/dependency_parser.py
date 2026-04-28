"""
Dependency Parser isolating Subject-Verb-Object (SVO) constraints.
"""

import spacy


class DependencyParser:
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.nlp = spacy.load(model_name)

    def extract_svo(self, text: str) -> list[dict]:
        """
        Extract Subject-Verb-Object mappings from a sentence.

        Handles both active voice (nsubj) and passive voice (nsubjpass /
        auxpass) constructions, which are dominant in regulatory text.
        For passive sentences the logical subject is the syntactic object
        (pobj of the "by" prepositional phrase when present).
        """
        doc = self.nlp(text)
        svo_triplets = []

        for token in doc:
            if token.pos_ not in ("VERB", "AUX"):
                continue

            subjects = [w for w in token.lefts if w.dep_ in ("nsubj", "nsubjpass")]
            objects = [
                w for w in token.rights if w.dep_ in ("dobj", "pobj", "attr", "acomp")
            ]

            # --- Active voice triplet ---
            if subjects and objects:
                svo_triplets.append(
                    {
                        "subject": " ".join(t.text for t in subjects[0].subtree),
                        "verb": token.text,
                        "object": " ".join(t.text for t in objects[0].subtree),
                        "voice": "active",
                    }
                )
                continue

            # --- Passive voice: verb root without active subject/object ---
            # Pattern: <ROOT:VERB> with auxpass + nsubjpass
            # e.g.  "Handrails shall be provided at all stairways."
            #         nsubjpass=Handrails, auxpass=be, ROOT=provided
            passive_subj = [w for w in token.lefts if w.dep_ == "nsubjpass"]
            is_passive = any(w.dep_ == "auxpass" for w in token.children)
            if passive_subj and is_passive:
                # The logical "object" is the nsubjpass (the thing acted upon)
                logical_obj = " ".join(t.text for t in passive_subj[0].subtree)
                # Look for a "by <agent>" prepositional phrase
                by_agents = [
                    w
                    for w in token.rights
                    if w.dep_ == "prep" and w.text.lower() == "by"
                ]
                logical_subj = ""
                if by_agents:
                    by_children = [c for c in by_agents[0].children if c.dep_ == "pobj"]
                    if by_children:
                        logical_subj = " ".join(t.text for t in by_children[0].subtree)
                svo_triplets.append(
                    {
                        "subject": logical_subj,
                        "verb": token.text,
                        "object": logical_obj,
                        "voice": "passive",
                    }
                )

        return svo_triplets
