from llm.client import get_llm
from rag.retriever import retrieve_policy

from graph.state import AgentState


async def rag_agent_node(
    state: AgentState,
) -> AgentState:

    documents = retrieve_policy(
        state["user_message"]
    )

    if not documents:

        return {
            **state,
            "response": (
                "I couldn't find information about "
                "that policy."
            ),
        }

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    llm = get_llm()

    prompt = f"""
You are an e-commerce customer support assistant.

Answer the customer's question using ONLY
the policy information provided below.

Policy information:
-------------------
{context}
-------------------

Customer question:
{state["user_message"]}

Rules:

1. Do not invent policy information.
2. If the answer is not present in the policy,
   say that the information is not available.
3. Give a concise and helpful answer.
"""

    result = await llm.ainvoke(prompt)

    return {
        **state,
        "response": result.content,
    }