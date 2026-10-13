
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.rag_agent import rag_agent_node


@pytest.mark.asyncio
async def test_rag_agent_returns_fallback_when_no_documents():
    state = {"user_message": "What is the refund policy?"}

    with patch(
        "agents.rag_agent.retrieve_policy",
        return_value=[],
    ):
        result = await rag_agent_node(state)

    assert "couldn't find information" in result["response"]


@pytest.mark.asyncio
async def test_rag_agent_uses_retrieved_policy_context():
    state = {"user_message": "Can I return a damaged item?"}

    documents = [
        SimpleNamespace(
            page_content=(
                "Damaged items can be returned within 7 days "
                "of delivery."
            )
        )
    ]

    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(
        return_value=SimpleNamespace(
            content="Damaged items can be returned within 7 days."
        )
    )

    with (
        patch(
            "agents.rag_agent.retrieve_policy",
            return_value=documents,
        ),
        patch(
            "agents.rag_agent.get_llm",
            return_value=mock_llm,
        ),
    ):
        result = await rag_agent_node(state)

    prompt = mock_llm.ainvoke.await_args.args[0]

    assert "Damaged items can be returned within 7 days" in prompt
    assert result["response"] == (
        "Damaged items can be returned within 7 days."
    )


@pytest.mark.asyncio
async def test_rag_agent_preserves_existing_state():
    state = {
        "user_message": "What is the return policy?",
        "intent": "REFUND_POLICY",
    }

    documents = [
        SimpleNamespace(page_content="Returns are allowed within 7 days.")
    ]

    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(
        return_value=SimpleNamespace(
            content="Returns are allowed within 7 days."
        )
    )

    with (
        patch(
            "agents.rag_agent.retrieve_policy",
            return_value=documents,
        ),
        patch(
            "agents.rag_agent.get_llm",
            return_value=mock_llm,
        ),
    ):
        result = await rag_agent_node(state)

    assert result["intent"] == "REFUND_POLICY"
    assert "response" in result
