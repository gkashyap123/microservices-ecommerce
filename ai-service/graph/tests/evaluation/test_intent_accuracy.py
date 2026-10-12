
import pytest

from agents.router import classify_intent
from graph.tests.evaluation.intent_dataset import INTENT_DATASET


@pytest.mark.asyncio
async def test_real_classifier_accuracy():
    results = []

    for item in INTENT_DATASET:
        predicted = await classify_intent(item["query"])

        passed = predicted == item["expected_intent"]

        results.append({
            "query": item["query"],
            "expected": item["expected_intent"],
            "predicted": predicted,
            "passed": passed,
        })

    correct = sum(result["passed"] for result in results)
    accuracy = correct / len(results)

    for result in results:
        print(result)

    print(f"\nIntent classification accuracy: {accuracy:.1%}")

    assert accuracy >= 0.80, (
        f"Intent accuracy {accuracy:.1%} is below the 80% threshold"
    )
