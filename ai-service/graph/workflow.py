from langgraph.graph import StateGraph, START, END

from graph.state import AgentState

from graph.nodes import (
    intent_node,
    response_node,
)

from agents.order_agent import order_agent_node
from agents.order_response import order_response_node

from agents.rag_agent import rag_agent_node

from agents.product_agent import product_agent_node
from agents.product_response import product_response_node

from agents.cancel_agent import cancel_agent_node
from langgraph.checkpoint.memory import MemorySaver

def route_after_intent(state: AgentState):

    intent = state["intent"]

    if intent == "ORDER_STATUS":
        return "order_agent"

    if intent == "REFUND_POLICY":
        return "rag_agent"

    if intent == "PRODUCT_SEARCH":
        return "product_agent"

    if intent == "ORDER_CANCEL":
       return "cancel_agent"

    return "response"


def build_graph():

    graph = StateGraph(AgentState)

    # Nodes

    graph.add_node(
        "intent",
        intent_node,
    )

    graph.add_node(
        "order_agent",
        order_agent_node,
    )

    graph.add_node(
        "order_response",
        order_response_node,
    )

    graph.add_node(
        "rag_agent",
        rag_agent_node,
    )

    graph.add_node(
        "product_agent",
        product_agent_node,
    )

    graph.add_node(
        "product_response",
        product_response_node,
    )

    graph.add_node(
        "response",
        response_node,
    )

    graph.add_node(
       "cancel_agent",
        cancel_agent_node,
    )

    graph.add_edge(
        "cancel_agent",
        END,
    )

    # START

    graph.add_edge(
        START,
        "intent",
    )

    # Intent routing

    graph.add_conditional_edges(
        "intent",
        route_after_intent,
        {
            "order_agent": "order_agent",
            "rag_agent": "rag_agent",
            "product_agent": "product_agent",
            "cancel_agent": "cancel_agent",
            "response": "response",
        },
    )

    # Order

    graph.add_edge(
        "order_agent",
        "order_response",
    )

    graph.add_edge(
        "order_response",
        END,
    )

    # RAG

    graph.add_edge(
        "rag_agent",
        END,
    )

    # Product

    graph.add_edge(
        "product_agent",
        "product_response",
    )

    graph.add_edge(
        "product_response",
        END,
    )

    # General

    graph.add_edge(
        "response",
        END,
    )

    return graph.compile(checkpointer=MemorySaver())