
from uuid import uuid4
from collections import defaultdict
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from langgraph.types import Command

from graph.workflow import build_graph
from tools.order_tool import get_order
from core.security import get_current_user


router = APIRouter(prefix="/api/chat", tags=["Chat"])
logger = logging.getLogger(__name__)

# Keep one graph instance so its checkpointer can retain state.
graph = build_graph()

# DEVELOPMENT ONLY:
# These mappings are lost on restart and are not shared across workers.
# Use durable storage for production.
conversation_histories: dict[
    str, list[dict[str, str]]
] = defaultdict(list)

conversation_owners: dict[str, str] = {}

MAX_HISTORY = 20


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    thread_id: str | None = Field(default=None, min_length=1, max_length=128)


class ChatResponse(BaseModel):
    intent: str
    response: str
    thread_id: str
    requires_confirmation: bool = False


class ConfirmationRequest(BaseModel):
    thread_id: str = Field(min_length=1, max_length=128)
    confirmed: bool


def get_interrupt_value(result):
    interruptions = result.get("__interrupt__", ())
    if not interruptions:
        return None
    return interruptions[0].value


def get_user_id(current_user: dict) -> str:
    user_id = current_user.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Authenticated user identifier is missing.",
        )

    return str(user_id)


def verify_thread_owner(thread_id: str, current_user: dict) -> None:
    user_id = get_user_id(current_user)
    owner_id = conversation_owners.get(thread_id)

    if owner_id is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    if owner_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this conversation.",
        )


def save_history(
    thread_id: str,
    user_message: str,
    assistant_response: str,
) -> None:
    history = conversation_histories[thread_id]
    history.extend([
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": assistant_response},
    ])
    conversation_histories[thread_id] = history[-MAX_HISTORY:]


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    user_id = get_user_id(current_user)

    if request.thread_id is None:
        thread_id = str(uuid4())
        conversation_owners[thread_id] = user_id
    else:
        thread_id = request.thread_id
        verify_thread_owner(thread_id, current_user)

    config = {"configurable": {"thread_id": thread_id}}

    try:
        snapshot = await graph.aget_state(config)

        if snapshot.interrupts:
            raise HTTPException(
                status_code=409,
                detail=(
                    "This conversation is awaiting confirmation. "
                    "Use /api/chat/confirm first."
                ),
            )

        history = conversation_histories[thread_id].copy()

        initial_state = {
            "user_message": request.message,
            "intent": "",
            "response": "",
            "order": None,
            "products": None,
            "conversation_history": history,
        }

        result = await graph.ainvoke(initial_state, config=config)
        interrupt_value = get_interrupt_value(result)

        if interrupt_value is not None:
            question = (
                interrupt_value.get("question")
                if isinstance(interrupt_value, dict)
                else None
            )

            return ChatResponse(
                intent=result.get("intent", ""),
                response=question or "Please confirm this action.",
                thread_id=thread_id,
                requires_confirmation=True,
            )

        response_text = result.get("response", "")

        save_history(thread_id, request.message, response_text)

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
    current_user: dict = Depends(get_current_user),
):
    verify_thread_owner(request.thread_id, current_user)

    config = {
        "configurable": {"thread_id": request.thread_id}
    }

    try:
        snapshot = await graph.aget_state(config)

        if not snapshot.interrupts:
            raise HTTPException(
                status_code=409,
                detail="No pending confirmation for this conversation.",
            )

        # Only allow this endpoint to resume an actual cancellation.
        # The graph state must retain the intent while interrupted.
        pending_intent = snapshot.values.get("intent")

        if pending_intent != "ORDER_CANCEL":
            raise HTTPException(
                status_code=409,
                detail="The pending action is not an order cancellation.",
            )

        result = await graph.ainvoke(
            Command(resume=request.confirmed),
            config=config,
        )

        interrupt_value = get_interrupt_value(result)

        if interrupt_value is not None:
            question = (
                interrupt_value.get("question")
                if isinstance(interrupt_value, dict)
                else None
            )

            return ChatResponse(
                intent=result.get("intent", ""),
                response=question or "Please confirm this action.",
                thread_id=request.thread_id,
                requires_confirmation=True,
            )

        response_text = result.get("response", "")
        original_message = snapshot.values.get(
            "user_message",
            "Order cancellation request",
        )

        save_history(
            request.thread_id,
            original_message,
            response_text,
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
        logger.exception("Cancellation confirmation failed")
        raise HTTPException(
            status_code=500,
            detail="Unable to process confirmation.",
        )


@router.get("/test-order/{order_id}")
async def test_order(
    order_id: int,
    current_user: dict = Depends(get_current_user),
):
    user_id = get_user_id(current_user)

    try:
        order = await get_order(order_id)

        if not isinstance(order, dict):
            raise HTTPException(
                status_code=502,
                detail="Unexpected response from Order Service.",
            )

        # Defense in depth: do not return an order unless its owner
        # matches the authenticated JWT subject.
        order_user_id = order.get("user_id")

        if order_user_id is None:
            logger.error(
                "Order Service response lacks user_id; cannot verify ownership."
            )
            raise HTTPException(
                status_code=502,
                detail="Unable to verify order ownership.",
            )

        if str(order_user_id) != user_id:
            # 404 avoids confirming another user's order exists.
            raise HTTPException(
                status_code=404,
                detail="Order not found.",
            )

        return {"success": True, "order": order}

    except HTTPException:
        raise
    except Exception:
        logger.exception("Order lookup failed")
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve order.",
        )


@router.get("/history/{thread_id}")
async def get_chat_history(
    thread_id: str,
    current_user: dict = Depends(get_current_user),
):
    verify_thread_owner(thread_id, current_user)

    return {
        "thread_id": thread_id,
        "messages": conversation_histories.get(thread_id, []),
    }
