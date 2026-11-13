
import pytest
from fastapi import HTTPException

from core.guardrails import (
    validate_user_message,
    validate_assistant_response,
)


def test_accepts_normal_user_message():
    assert validate_user_message("Where is my order?") == (
        "Where is my order?"
    )


def test_rejects_empty_user_message():
    with pytest.raises(HTTPException) as exc:
        validate_user_message("   ")

    assert exc.value.status_code == 422


def test_rejects_oversized_user_message():
    with pytest.raises(HTTPException) as exc:
        validate_user_message("a" * 4001)

    assert exc.value.status_code == 413


def test_accepts_valid_assistant_response():
    assert validate_assistant_response("Your order is shipped.") == (
        "Your order is shipped."
    )


def test_rejects_empty_assistant_response():
    with pytest.raises(HTTPException) as exc:
        validate_assistant_response("  ")

    assert exc.value.status_code == 502


def test_rejects_oversized_assistant_response():
    with pytest.raises(HTTPException) as exc:
        validate_assistant_response("a" * 8001)

    assert exc.value.status_code == 502
