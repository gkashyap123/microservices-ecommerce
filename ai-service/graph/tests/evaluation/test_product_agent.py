
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agents.product_agent import (
    ProductSearchCriteria,
    product_agent_node,
)


@pytest.mark.asyncio
async def test_product_agent_passes_correct_search_parameters():
    state = {
        "user_message": "Show smartphones under 20000",
        "conversation_history": [],
    }

    criteria = ProductSearchCriteria(
        search="smartphones",
        max_price=20000,
    )

    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_structured_llm.ainvoke = AsyncMock(
        return_value=criteria
    )
    mock_llm.with_structured_output.return_value = (
        mock_structured_llm
    )

    expected_products = [
        {"id": 1, "name": "Smartphone A", "price": 15000}
    ]

    with (
        patch(
            "agents.product_agent.get_llm",
            return_value=mock_llm,
        ),
        patch(
            "agents.product_agent.search_products",
            new_callable=AsyncMock,
        ) as mock_search,
    ):
        mock_search.return_value = expected_products

        result = await product_agent_node(state)

    mock_llm.with_structured_output.assert_called_once_with(
        ProductSearchCriteria
    )

    mock_search.assert_awaited_once_with(
        search="smartphones",
        min_price=None,
        max_price=20000,
    )

    assert result["products"] == expected_products


@pytest.mark.asyncio
async def test_product_agent_preserves_conversation_context():
    state = {
        "user_message": "Show those under 15000",
        "conversation_history": [
            {
                "role": "user",
                "content": "Show me smartphones",
            }
        ],
    }

    criteria = ProductSearchCriteria(
        search="smartphones",
        max_price=15000,
    )

    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_structured_llm.ainvoke = AsyncMock(
        return_value=criteria
    )
    mock_llm.with_structured_output.return_value = (
        mock_structured_llm
    )

    with (
        patch(
            "agents.product_agent.get_llm",
            return_value=mock_llm,
        ),
        patch(
            "agents.product_agent.search_products",
            new_callable=AsyncMock,
        ) as mock_search,
    ):
        mock_search.return_value = []

        await product_agent_node(state)

    prompt = mock_structured_llm.ainvoke.await_args.args[0]

    assert "Show me smartphones" in prompt
    assert "Show those under 15000" in prompt

    mock_search.assert_awaited_once_with(
        search="smartphones",
        min_price=None,
        max_price=15000,
    )

@pytest.mark.asyncio
async def test_product_agent_does_not_silently_hide_tool_failure():
    state = {
        "user_message": "Show smartphones under 20000",
        "conversation_history": [],
    }

    criteria = ProductSearchCriteria(
        search="smartphones",
        max_price=20000,
    )

    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_structured_llm.ainvoke = AsyncMock(
        return_value=criteria
    )
    mock_llm.with_structured_output.return_value = (
        mock_structured_llm
    )

    with (
        patch(
            "agents.product_agent.get_llm",
            return_value=mock_llm,
        ),
        patch(
            "agents.product_agent.search_products",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Database unavailable"),
        ) as mock_search,
    ):
        with pytest.raises(RuntimeError, match="Database unavailable"):
            await product_agent_node(state)

    mock_search.assert_awaited_once_with(
        search="smartphones",
        min_price=None,
        max_price=20000,
    )
