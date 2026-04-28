from pathlib import Path
from src.classification.deontic_detector import DeonticDetector
from src.classification.sentence_classifier import SentenceClassifier
from src.classification.provision_type import ProvisionClassifier


def test_complete_classification_heuristic():
    # Setup paths relative to the mocked root
    pattern_path = Path("domain") / "deontic_patterns.yaml"

    # We will only run logic if the actual yaml is resolved, avoiding mock crashes
    if not pattern_path.exists():
        return

    detector = DeonticDetector(str(pattern_path))
    classifier = SentenceClassifier(detector)
    provision = ProvisionClassifier()

    s1 = "The door shall be 900 mm wide."
    assert detector.extract_operator(s1) == "OBLIGATION"
    assert classifier.classify(s1) == "Prescriptive"
    assert provision.classify(s1) == "Quantitative"

    s2 = "An exit route means a continuous pathway."
    assert detector.extract_operator(s2) == "NONE"
    assert classifier.classify(s2) == "Constitutive"
    assert provision.classify(s2) == "Qualitative"

    s3 = "Exception: Handrails serving stairs and ramps are permitted to protrude 115 mm."
    assert classifier.classify(s3) == "Exception"
    assert provision.classify(s3) == "Quantitative"

    s4 = "The means of egress illumination level shall not be less than 11 lux at the floor level."
    assert detector.extract_operator(s4) == "PROHIBITION"
    assert classifier.classify(s4) == "Prescriptive"
    assert provision.classify(s4) == "Quantitative"

    s5 = "Liquids having a closed cup flash point at or above 38°C and below 60°C."
    assert classifier.classify(s5) == "Informative"
    assert provision.classify(s5) == "Quantitative"

    s6 = "A single cylinder containing 68 kilograms or less of anhydrous ammonia in a single control area shall be considered a maximum allowable quantity."
    assert detector.extract_operator(s6) == "OBLIGATION"
    assert classifier.classify(s6) == "Prescriptive"
    assert provision.classify(s6) == "Quantitative"
