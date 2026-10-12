from fastapi import APIRouter, HTTPException

from rag.ingestion import ingest_documents
from rag.retriever import retrieve_policy
from llm.client import get_llm


router = APIRouter(
    prefix="/api/rag",
    tags=["RAG"],
)


@router.post("/ingest")
async def ingest():

    try:

        result = ingest_documents()

        return {
            "success": True,
            **result,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/search")
async def search(query: str):

    try:

        documents = retrieve_policy(query)

        return {
            "results": [
                {
                    "content": document.page_content,
                    "metadata": document.metadata,
                }
                for document in documents
            ]
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )