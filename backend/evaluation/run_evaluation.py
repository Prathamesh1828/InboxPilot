import json
import logging
from pathlib import Path

from app.services.classifier import EmailClassifier
from app.services.planner import EmailPlanner
from app.schemas.classification import EmailCategory
from app.schemas.action_plan import ActionType

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def main():
    print("Starting InboxPilot Evaluation...")
    print("=" * 60)

    dataset_path = Path(__file__).parent / "eval_dataset.json"
    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    classifier = EmailClassifier()
    planner = EmailPlanner()

    total = len(dataset)
    classification_correct = 0
    action_correct = 0

    print(f"Loaded {total} evaluation examples.\n")

    for item in dataset:
        print(f"Evaluating {item['id']} - {item['subject']}")
        
        # 1. Classification
        classification = classifier.classify(
            sender="test@example.com",
            recipients=["user@inboxpilot.com"],
            subject=item["subject"],
            body=item["body"],
        )
        
        is_category_correct = classification.category.value == item["expected_category"]
        if is_category_correct:
            classification_correct += 1
            print(f"  [PASS] Category: {classification.category.value}")
        else:
            print(f"  [FAIL] Category: Got {classification.category.value}, expected {item['expected_category']}")
            
        # 2. Planning
        plan = planner.create_plan(
            category=classification.category.value,
            classification_reasoning=classification.reasoning,
            subject=item["subject"],
            body=item["body"],
        )
        
        is_action_correct = plan.action.value == item["expected_action"]
        if is_action_correct:
            action_correct += 1
            print(f"  [PASS] Action: {plan.action.value}")
        else:
            print(f"  [FAIL] Action: Got {plan.action.value}, expected {item['expected_action']}")
            
        print("-" * 40)

    print("\n" + "=" * 60)
    print("Evaluation Results")
    print("=" * 60)
    print(f"Total Examples: {total}")
    print(f"Classification Accuracy: {classification_correct}/{total} ({classification_correct/total*100:.1f}%)")
    print(f"Action Planning Accuracy: {action_correct}/{total} ({action_correct/total*100:.1f}%)")


if __name__ == "__main__":
    main()
