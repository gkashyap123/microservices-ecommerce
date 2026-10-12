import re

from graph.state import AgentState
from tools.order_tool import get_order


def extract_order_id(message: str) -> int | None:
    """
    Extract an order ID from messages such as:

    'Where is order 123?'
    'What is the status of order #123?'
    """

    match = re.search(
        r"(?:order\s*#?\s*)(\d+)",
        message,
        re.IGNORECASE,
    )

    if not match:
        return None

    return int(match.group(1))


async def order_agent_node(
    state: AgentState,
) -> AgentState:

    order_id = extract_order_id(
        state["user_message"]
    )

    if not order_id:
        return {
            **state,
            "response": (
                "Please provide your order ID so I can "
                "check the order status."
            ),
        }

    try:

        order = await get_order(order_id)

        return {
            **state,
            "order": order,
        }

    except Exception:
        return {
            **state,
            "response": (
                f"I couldn't retrieve order #{order_id} "
                "right now. Please try again."
            ),
        }