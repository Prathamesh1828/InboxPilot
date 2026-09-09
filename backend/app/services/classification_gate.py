from app.core.settings import settings
from app.schemas.classification import EmailClassification


def evaluate_classification(
    classification: EmailClassification,
) -> str:
    """
    Determine whether an LLM classification is trusted
    enough to continue automatically.
    """

    if classification.confidence >= settings.llm_confidence_threshold:
        return "CLASSIFIED"

    return "REVIEW"