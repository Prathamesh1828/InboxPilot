from app.schemas.classification import EmailCategory, EmailClassification
from app.services.classification_gate import evaluate_classification


def test_classification_gate():
    print("Testing classification confidence gate")
    print("=" * 60)

    # High-confidence classification
    high_confidence = EmailClassification(
        category=EmailCategory.BILL,
        confidence=0.90,
        reasoning="The email clearly contains a payment request.",
    )

    high_status = evaluate_classification(high_confidence)

    print(f"High confidence: {high_confidence.confidence}")
    print(f"Expected: CLASSIFIED")
    print(f"Actual:   {high_status}")

    assert high_status == "CLASSIFIED"

    print("✅ High-confidence test passed")
    print()

    # Low-confidence classification
    low_confidence = EmailClassification(
        category=EmailCategory.BILL,
        confidence=0.60,
        reasoning="The email might be related to a payment.",
    )

    low_status = evaluate_classification(low_confidence)

    print(f"Low confidence: {low_confidence.confidence}")
    print(f"Expected: REVIEW")
    print(f"Actual:   {low_status}")

    assert low_status == "REVIEW"

    print("✅ Low-confidence test passed")
    print()

    print("=" * 60)
    print("✅ Classification gate test passed")


if __name__ == "__main__":
    test_classification_gate()