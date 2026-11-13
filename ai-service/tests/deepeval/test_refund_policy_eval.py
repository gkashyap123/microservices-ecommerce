
from deepeval import assert_test
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase


def test_refund_policy_answer_is_grounded():
    question = "What is the refund policy?"

    # Illustrative context and answer for the first smoke test.
    # Replace these with your real policy and actual RAG output later.
    retrieved_context = [
        "Eligible products can be returned within 30 days "
        "of delivery, subject to the return policy."
    ]

    actual_answer = (
        "Eligible products can be returned within 30 days "
        "of delivery, subject to the return policy."
    )

    test_case = LLMTestCase(
        input=question,
        actual_output=actual_answer,
        retrieval_context=retrieved_context,
    )

    metrics = [
        FaithfulnessMetric(threshold=0.8),
        AnswerRelevancyMetric(threshold=0.8),
    ]

    assert_test(test_case=test_case, metrics=metrics)
