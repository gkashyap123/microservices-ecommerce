from typing import Literal

from llm.client import get_llm


Intent = Literal[
    "REFUND_POLICY",
    "ORDER_STATUS",
    "ORDER_CANCEL",
    "PRODUCT_SEARCH",
    "GENERAL",
]


async def classify_intent(message: str) -> Intent:

    llm = get_llm()

    prompt = f"""
You are an intent classification system for an e-commerce application.

Classify the user's message into exactly ONE of these intents:

REFUND_POLICY
ORDER_STATUS
ORDER_CANCEL
PRODUCT_SEARCH
GENERAL

Rules:

- REFUND_POLICY:
  Questions about refunds, return policy, refund eligibility,
  refund timelines, or return rules.

- ORDER_STATUS:
  Questions about an existing order, delivery status,
  shipment status, or tracking.

- ORDER_CANCEL:
  Requests to cancel an existing order.
  Examples:
  "Cancel my order"
  "I want to cancel order 123"
  "Can I cancel my order?"
  
- PRODUCT_SEARCH:
  Questions asking to find, search, compare, or recommend products.

- GENERAL:
  Anything else.

User message:
{message}

Return ONLY the intent name.
"""

    result = await llm.ainvoke(prompt)

    intent = result.content.strip().upper()

    valid_intents = {
        "REFUND_POLICY",
        "ORDER_STATUS",
        "ORDER_CANCEL",
        "PRODUCT_SEARCH",
        "GENERAL",
    }

    if intent not in valid_intents:
        return "GENERAL"

    return intent