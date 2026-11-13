
import re
from fastapi import HTTPException


MAX_MESSAGE_LENGTH = 4000

# Detect common direct prompt-injection attempts.
# These checks are a first layer, not a complete security solution.
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"reveal\s+(your\s+)?(system|developer)\s+prompt",
    r"show\s+(me\s+)?(your\s+)?(system|developer)\s+prompt",
    r"print\s+(your\s+)?(hidden|system)\s+instructions",
    r"bypass\s+(all\s+)?(safety|security)\s+(rules|checks|guardrails)",
    r"act\s+as\s+(the\s+)?system",
]

COMPILED_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in INJECTION_PATTERNS
]


def validate_user_message(message: str) -> str:
    """Validate incoming customer text before it reaches the graph."""

    if not isinstance(message, str):
        raise HTTPException(
            status_code=422,
            detail="Message must be text.",
        )

    cleaned_message = message.strip()

    if not cleaned_message:
        raise HTTPException(
            status_code=422,
            detail="Message cannot be empty.",
        )

    if len(cleaned_message) > MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=413,
            detail="Message exceeds the allowed length.",
        )

    for pattern in COMPILED_PATTERNS:
        if pattern.search(cleaned_message):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Your message contains instructions that "
                    "cannot be processed. Please rephrase your request."
                ),
            )

    return cleaned_message


MAX_RESPONSE_LENGTH = 8000


def validate_assistant_response(response: str) -> str:
    """Validate an assistant response before returning it to the client."""

    if not isinstance(response, str):
        raise HTTPException(
            status_code=500,
            detail="Invalid assistant response.",
        )

    cleaned_response = response.strip()

    if not cleaned_response:
        raise HTTPException(
            status_code=502,
            detail="The assistant could not generate a response.",
        )

    if len(cleaned_response) > MAX_RESPONSE_LENGTH:
        raise HTTPException(
            status_code=502,
            detail="The assistant response exceeds the allowed length.",
        )

    return cleaned_response
