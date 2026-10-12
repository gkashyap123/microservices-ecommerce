
import re
import logging

from langgraph.types import interrupt
from graph.state import AgentState
from tools.order_tool import get_order, cancel_order

logger = logging.getLogger(__name__)


def extract_order_id(message: str) -> int | None:
    match = re.search(
        r"\border\s*#?\s*(\d+)\b",
        message,
        re.IGNORECASE,
    )
    return int(match.group(1)) if match else None


async def cancel_agent_node(state: AgentState) -> AgentState:
    order_id = extract_order_id(state["user_message"])

    if order_id is None:
        return {
            **state,
            "response": "Please provide your order ID.",
        }

    # Step 1: Fetch and validate the order.
    try:
        order = await get_order(order_id)
    except Exception:
        logger.exception("Failed to fetch order %s", order_id)
        return {
            **state,
            "response": f"I couldn't retrieve order #{order_id}. Please try again.",
        }

    if not isinstance(order, dict):
        logger.error("Unexpected response for order %s: %r", order_id, order)
        return {
            **state,
            "response": f"I couldn't verify order #{order_id}.",
        }

    status = str(order.get("status", "")).upper()

    if status not in {"PENDING", "CONFIRMED"}:
        return {
            **state,
            "response": (
                f"Order #{order_id} cannot be cancelled. "
                f"Current status: {status or 'UNKNOWN'}."
            ),
        }

    # Step 2: Pause here. Do NOT wrap interrupt() in try/except Exception.
    confirmed = interrupt({
        "type": "order_cancellation_confirmation",
        "order_id": order_id,
        "question": (
            f"Are you sure you want to cancel order #{order_id}?"
        ),
    })

    if confirmed is not True:
        return {
            **state,
            "response": f"Cancellation of order #{order_id} was not confirmed.",
        }

    # Step 3: Cancel only after explicit confirmation.
    try:
        cancelled_order = await cancel_order(order_id)
    except Exception:
        logger.exception("Failed to cancel order %s", order_id)
        return {
            **state,
            "response": f"I couldn't cancel order #{order_id}. Please try again.",
        }

    return {
        **state,
        "order": cancelled_order,
        "response": f"Order #{order_id} has been cancelled successfully.",
    }
