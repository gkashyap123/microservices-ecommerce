
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
from langchain_openai import ChatOpenAI


def test_llm_answers_refund_question_relevantly():
    question = "What information should I check before requesting a refund?"

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
    )

    response = llm.invoke(question)
    actual_answer = response.content

    test_case = LLMTestCase(
        input=question,
        actual_output=actual_answer,
    )

    metric = AnswerRelevancyMetric(threshold=0.8)

    assert_test(
        test_case=test_case,
        metrics=[metric],
    )
