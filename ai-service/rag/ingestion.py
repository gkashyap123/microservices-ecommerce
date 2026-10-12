from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.loader import load_policy_documents
from rag.vector_store import get_vector_store


def ingest_documents():

    documents = load_policy_documents()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    chunks = splitter.split_documents(
        documents
    )

    vector_store = get_vector_store()

    vector_store.add_documents(
        chunks
    )

    return {
        "documents": len(documents),
        "chunks": len(chunks),
    }