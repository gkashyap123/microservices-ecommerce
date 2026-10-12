
import pytest

from unittest.mock import AsyncMock, patch

from graph.nodes import intent_node


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_message, expected_intent",
    [
        ("Where is my order 123?", "ORDER_STATUS"),
        ("What is your refund policy?", "REFUND_POLICY"),
        ("Show me smartphones under 20000", "PRODUCT_SEARCH"),
        ("Please cancel order 123", "ORDER_CANCEL"),
    ],
)
async def test_intent_node_returns_classified_intent(
    user_message,
    expected_intent,
):
    state = {
        "user_message": user_message,
        "conversation_history": [],
    }

    with patch(
        "graph.nodes.classify_intent",
        new_callable=AsyncMock,
    ) as mock_classifier:
        mock_classifier.return_value = expected_intent

        result = await intent_node(state)

    assert result["intent"] == expected_intent
    mock_classifier.assert_awaited_once()


@pytest.mark.asyncio
async def test_intent_node_preserves_existing_state():
    state = {
        "user_message": "Where is my order?",
        "conversation_history": [],
        "response": "Previous response",
    }

    with patch(
        "graph.nodes.classify_intent",
        new_callable=AsyncMock,
    ) as mock_classifier:
        mock_classifier.return_value = "ORDER_STATUS"

        result = await intent_node(state)

    assert result["intent"] == "ORDER_STATUS"
    assert result["response"] == "Previous response"
