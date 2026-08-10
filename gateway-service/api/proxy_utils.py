import json
from fastapi import Request


EXCLUDED_REQUEST_HEADERS = {
    "host",
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "content-length",
    "upgrade",
    "proxy-connection",
}


def make_proxy_headers(request: Request, payload: dict | None) -> dict[str, str]:
    headers = {k: v for k, v in request.headers.items() if k.lower() not in EXCLUDED_REQUEST_HEADERS}
    if payload is not None and "content-type" not in {k.lower() for k in headers.keys()}:
        headers["content-type"] = "application/json"
    return headers


async def build_proxy_content(request: Request, payload: dict | None) -> bytes | None:
    if payload is not None:
        return json.dumps(payload).encode("utf-8")

    body = await request.body()
    return body if body else None
