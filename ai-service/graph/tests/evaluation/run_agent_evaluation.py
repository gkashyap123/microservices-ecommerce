
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
import sys



BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "agent_evaluation_dataset.json"
REPORT_PATH = BASE_DIR / "agent_evaluation_results.csv"

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from graph.workflow import route_after_intent


def evaluate_case(case: dict) -> dict:
    expected_node = case["expected_node"]
    actual_node = route_after_intent(
        {"intent": case["intent"]}
    )

    passed = actual_node == expected_node

    return {
        "case_id": case["case_id"],
        "category": case["category"],
        "input": case["input"],
        "expected_node": expected_node,
        "actual_node": actual_node,
        "passed": passed,
        "failure_reason": (
            "" if passed
            else f"Expected {expected_node}, got {actual_node}"
        ),
    }


def main():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    results = [evaluate_case(case) for case in dataset]

    fieldnames = [
        "case_id",
        "category",
        "input",
        "expected_node",
        "actual_node",
        "passed",
        "failure_reason",
    ]

    with REPORT_PATH.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    total = len(results)
    passed = sum(result["passed"] for result in results)
    failed = total - passed
    accuracy = passed / total if total else 0.0

    print(f"Evaluation time: {datetime.now(timezone.utc).isoformat()}")
    print(f"Total cases: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Routing accuracy: {accuracy:.2%}")
    print(f"Report: {REPORT_PATH}")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
