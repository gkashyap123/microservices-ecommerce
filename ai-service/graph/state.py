from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    user_message: str
    intent: str
    response: str
    order: Any
    products: Any
    conversation_history: list[dict[str, str]]   