
import pytest
from graph.workflow import route_after_intent


@pytest.mark.parametrize(
    "intent, expected_node",
    [
        ("ORDER_STATUS", "order_agent"),
        ("REFUND_POLICY", "rag_agent"),
        ("PRODUCT_SEARCH", "product_agent"),
        ("ORDER_CANCEL", "cancel_agent"),
        ("GENERAL_QUERY", "response"),
        ("UNKNOWN", "response"),
    ],
)
def test_route_after_intent(intent, expected_node):
    state = {
        "user_message": "Test customer query",
        "intent": intent,
    }

    actual_node = route_after_intent(state)

    assert actual_node == expected_node
