
from uuid import uuid4
from collections import defaultdict
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langgraph.types import Command

from graph.workflow import build_graph
from tools.order_tool import get_order


router = APIRouter(prefix="/api/chat", tags=["Chat"])
logger = logging.getLogger(__name__)

# Build once to preserve LangGraph checkpoints.
graph = build_graph()

# Step 12: In-memory conversation history
conversation_histories: dict[
    str, list[dict[str, str]]
] = defaultdict(list)

MAX_HISTORY = 20


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


class ChatResponse(BaseModel):
    intent: str
    response: str
    thread_id: str
    requires_confirmation: bool = False


class ConfirmationRequest(BaseModel):
    thread_id: str
    confirmed: bool


def get_interrupt_value(result):
    interruptions = result.get("__interrupt__", ())
    if not interruptions:
        return None
    return interruptions[0].value


def save_history(
    thread_id: str,
    user_message: str,
    assistant_response: str,
):
    """Store the latest conversation messages."""
    history = conversation_histories[thread_id]

    history.extend([
        {
            "role": "user",
            "content": user_message,
        },
        {
            "role": "assistant",
            "content": assistant_response,
        },
    ])

    conversation_histories[thread_id] = history[-MAX_HISTORY:]


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    thread_id = request.thread_id or str(uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    try:
        # Prevent starting a new request while confirmation
        # is pending for this conversation.
        snapshot = await graph.aget_state(config)

        if snapshot.interrupts:
            raise HTTPException(
                status_code=409,
                detail=(
                    "This conversation is awaiting confirmation. "
                    "Use /api/chat/confirm first."
                ),
            )

        # Load previous messages for this conversation.
        history = conversation_histories[thread_id].copy()

        initial_state = {
            "user_message": request.message,
            "intent": "",
            "response": "",
            "order": None,
            "products": None,
            "conversation_history": history,
        }

        result = await graph.ainvoke(
            initial_state,
            config=config,
        )

        interrupt_value = get_interrupt_value(result)

        if interrupt_value:
            return ChatResponse(
                intent=result.get("intent", ""),
                response=interrupt_value.get(
                    "question",
                    "Please confirm this action.",
                ),
                thread_id=thread_id,
                requires_confirmation=True,
            )

        response_text = result.get("response", "")

        # Save completed conversation turns.
        save_history(
            thread_id=thread_id,
            user_message=request.message,
            assistant_response=response_text,
        )

        return ChatResponse(
            intent=result.get("intent", ""),
            response=response_text,
            thread_id=thread_id,
            requires_confirmation=False,
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception("Chat request failed")
        raise HTTPException(
            status_code=500,
            detail="Chat request failed.",
        )


@router.post("/confirm", response_model=ChatResponse)
async def confirm_cancellation(
    request: ConfirmationRequest,
):
    config = {
        "configurable": {
            "thread_id": request.thread_id,
        }
    }

    try:
        # Only resume an existing, interrupted workflow.
        snapshot = await graph.aget_state(config)

        if not snapshot.interrupts:
            raise HTTPException(
                status_code=409,
                detail="No pending confirmation for this thread.",
            )

        result = await graph.ainvoke(
            Command(resume=request.confirmed),
            config=config,
        )

        interrupt_value = get_interrupt_value(result)

        if interrupt_value:
            return ChatResponse(
                intent=result.get("intent", ""),
                response=interrupt_value.get(
                    "question",
                    "Please confirm this action.",
                ),
                thread_id=request.thread_id,
                requires_confirmation=True,
            )

        response_text = result.get("response", "")

        # Save the completed cancellation conversation.
        original_message = snapshot.values.get(
            "user_message",
            "Order cancellation request",
        )

        save_history(
            thread_id=request.thread_id,
            user_message=original_message,
            assistant_response=response_text,
        )

        return ChatResponse(
            intent=result.get("intent", ""),
            response=response_text,
            thread_id=request.thread_id,
            requires_confirmation=False,
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception("Confirmation request failed")
        raise HTTPException(
            status_code=500,
            detail="Confirmation request failed.",
        )


@router.get("/test-order/{order_id}")
async def test_order(order_id: int):
    try:
        order = await get_order(order_id)
        return {
            "success": True,
            "order": order,
        }
    except Exception:
        logger.exception("Order lookup failed")
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve order.",
        )


# Step 12: Development-only history inspection
@router.get("/history/{thread_id}")
async def get_chat_history(thread_id: str):
    return {
        "thread_id": thread_id,
        "messages": conversation_histories.get(
            thread_id, []
        ),
    }
