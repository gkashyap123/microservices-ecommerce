from rag.vector_store import get_vector_store


def retrieve_policy(query: str):

    vector_store = get_vector_store()

    results = vector_store.similarity_search(
        query,
        k=4,
    )

    return results