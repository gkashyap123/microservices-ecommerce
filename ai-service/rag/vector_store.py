import os

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


PERSIST_DIRECTORY = os.path.join(
    os.path.dirname(__file__),
    "chroma_db",
)


def get_embeddings():
    return OpenAIEmbeddings(
        model="text-embedding-3-small"
    )


def get_vector_store():

    return Chroma(
        collection_name="ecommerce_policies",
        embedding_function=get_embeddings(),
        persist_directory=PERSIST_DIRECTORY,
    )