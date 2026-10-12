
from typing import Optional

from pydantic import BaseModel, Field

from llm.client import get_llm
from tools.product_tool import search_products
from graph.state import AgentState


class ProductSearchCriteria(BaseModel):
    search: Optional[str] = Field(
        default=None,
        description="Product name or keyword to search for",
    )
    min_price: Optional[float] = Field(
        default=None,
        description="Minimum product price",
    )
    max_price: Optional[float] = Field(
        default=None,
        description="Maximum product price",
    )


def get_recent_context(state: AgentState) -> str:
    history = state.get("conversation_history", [])

    return "\n".join(
        f'{item.get("role", "user")}: {item.get("content", "")}'
        for item in history[-10:]
    )


async def product_agent_node(state: AgentState) -> AgentState:
    llm = get_llm()
    history_context = get_recent_context(state)
    user_message = state["user_message"]

    structured_llm = llm.with_structured_output(
        ProductSearchCriteria
    )

    criteria = await structured_llm.ainvoke(
        f"""
Extract product search criteria for an e-commerce catalogue.

Recent conversation:
{history_context or "No previous conversation."}

Latest customer message:
{user_message}

Rules:
- Resolve references such as "those", "which one", and "it"
  using the recent conversation.
- If the latest message is a follow-up about a previous search,
  preserve the previous product keyword and price constraints.
- For example, if the previous request was "smartphones under
  50000" and the latest request is "which one has the highest
  stock?", search for smartphones with max_price 50000.
- Do not invent keywords or price values.
- If the latest request introduces a new product category or
  new price constraint, follow the latest request.
"""
    )

    products = await search_products(
        search=criteria.search,
        min_price=criteria.min_price,
        max_price=criteria.max_price,
    )

    return {
        **state,
        "products": products,
    }
