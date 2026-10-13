
import pytest

from graph.workflow import route_after_intent


@pytest.mark.parametrize(
    ("intent", "expected_node"),
    [
        ("ORDER_STATUS", "order_agent"),
        ("REFUND_POLICY", "rag_agent"),
        ("PRODUCT_SEARCH", "product_agent"),
        ("ORDER_CANCEL", "cancel_agent"),
        ("GENERAL", "response"),
        ("UNKNOWN", "response"),
    ],
)
def test_workflow_routes_intents_correctly(intent, expected_node):
    state = {"intent": intent}

    result = route_after_intent(state)

    assert result == expected_node
