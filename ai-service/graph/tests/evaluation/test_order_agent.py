
import pytest
from unittest.mock import AsyncMock, patch

from agents.order_agent import (
    extract_order_id,
    order_agent_node,
)


def test_extract_order_id():
    assert extract_order_id("Where is order 123?") == 123
    assert extract_order_id("Status of order #456?") == 456
    assert extract_order_id("Check my order") is None


@pytest.mark.asyncio
async def test_order_agent_calls_tool_with_correct_id():
    state = {"user_message": "Where is order #123?"}
    expected_order = {"id": 123, "status": "shipped"}

    with patch(
        "agents.order_agent.get_order",
        new_callable=AsyncMock,
    ) as mock_get_order:
        mock_get_order.return_value = expected_order

        result = await order_agent_node(state)

    mock_get_order.assert_awaited_once_with(123)
    assert result["order"] == expected_order


@pytest.mark.asyncio
async def test_order_agent_handles_missing_order_id():
    state = {"user_message": "Where is my order?"}

    with patch(
        "agents.order_agent.get_order",
        new_callable=AsyncMock,
    ) as mock_get_order:
        result = await order_agent_node(state)

    mock_get_order.assert_not_awaited()
    assert "order ID" in result["response"]


@pytest.mark.asyncio
async def test_order_agent_handles_tool_failure():
    state = {"user_message": "Where is order 123?"}

    with patch(
        "agents.order_agent.get_order",
        new_callable=AsyncMock,
    ) as mock_get_order:
        mock_get_order.side_effect = TimeoutError("Service timeout")

        result = await order_agent_node(state)

    mock_get_order.assert_awaited_once_with(123)
    assert "couldn't retrieve order #123" in result["response"]
