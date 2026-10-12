from llm.client import get_llm

from graph.state import AgentState


async def order_response_node(
    state: AgentState,
) -> AgentState:

    order = state.get("order")

    if not order:

        return {
            **state,
            "response": state.get(
                "response",
                "I couldn't find the requested order.",
            ),
        }

    llm = get_llm()

    prompt = f"""
You are an e-commerce customer support assistant.

The customer asked:

{state["user_message"]}

Here is the order information retrieved from the
Order Service:

{order}

Answer the customer naturally.

Include:
- order number
- current status
- total amount
- relevant product information

Do not invent information that is not present
in the order data.
"""

    result = await llm.ainvoke(prompt)

    return {
        **state,
        "response": result.content,
    }