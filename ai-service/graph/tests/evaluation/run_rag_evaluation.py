
import asyncio
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

from rag.retriever import retrieve_policy
from agents.rag_agent import rag_agent_node


BASE_DIR = Path(__file__).parent
DATASET_PATH = BASE_DIR / "rag_dataset.json"


async def collect_results():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        test_cases = json.load(file)

    rows = []

    for case in test_cases:
        question = case["question"]

        # Retrieve real documents from your vector store.
        documents = retrieve_policy(question)
        
        print(f"\nQuestion: {question}")
        print(f"Retrieved documents: {len(documents)}")

        for index, document in enumerate(documents, start=1):
            print(f"\n--- Retrieved document {index} ---")
            print(document.page_content[:1000])
            print("Metadata:", document.metadata)

        contexts = [
            document.page_content
            for document in documents
        ]

        # Run the actual RAG agent.
        result = await rag_agent_node({
            "user_message": question,
            "intent": "REFUND_POLICY",
        })

        rows.append({
            "question": question,
            "answer": result["response"],
            "contexts": contexts,
            "ground_truth": case["ground_truth"],
        })

        print(f"\nQuestion: {question}")
        print(f"Retrieved documents: {len(contexts)}")
        print(f"Answer: {result['response']}")

    return rows


async def main():
    rows = await collect_results()

    dataset = Dataset.from_list(rows)

    scores = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ],
    )

    print("\nRAG evaluation results:")
    print(scores)

    output_path = BASE_DIR / "rag_evaluation_results.csv"
    scores.to_pandas().to_csv(output_path, index=False)

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
