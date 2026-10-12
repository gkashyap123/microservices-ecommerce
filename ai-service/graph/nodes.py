
from agents.router import classify_intent
from llm.client import get_llm
from graph.state import AgentState


async def intent_node(state: AgentState) -> AgentState:
    history = state.get("conversation_history", [])

    # Include recent context so follow-up messages can be classified.
    context = "\n".join(
        f'{item["role"]}: {item["content"]}'
        for item in history[-6:]
    )

    message_for_classification = state["user_message"]

    if context:
        message_for_classification = (
            f"Recent conversation:\n{context}\n\n"
            f"Latest user message: {state['user_message']}"
        )

    intent = await classify_intent(message_for_classification)

    return {
        **state,
        "intent": intent,
    }


async def response_node(state: AgentState) -> AgentState:
    llm = get_llm()
    history = state.get("conversation_history", [])

    context = "\n".join(
        f'{item["role"]}: {item["content"]}'
        for item in history[-6:]
    )

    prompt = f"""
You are an e-commerce customer assistant.

Use the conversation history to understand follow-up questions.
Do not invent product, order, stock, or policy information.
If the available context is insufficient, ask a clarifying question.

Recent conversation:
{context or "No previous conversation."}

Latest user message:
{state["user_message"]}

Detected intent:
{state["intent"]}

Provide a helpful, concise response.
"""

    result = await llm.ainvoke(prompt)

    return {
        **state,
        "response": result.content,
    }
