import os

from langchain_community.document_loaders import TextLoader


DOCUMENT_DIRECTORY = os.path.join(
    os.path.dirname(__file__),
    "documents",
)


def load_policy_documents():

    documents = []

    for filename in os.listdir(DOCUMENT_DIRECTORY):

        if not filename.endswith(".txt"):
            continue

        path = os.path.join(
            DOCUMENT_DIRECTORY,
            filename,
        )

        loader = TextLoader(
            path,
            encoding="utf-8",
        )

        documents.extend(
            loader.load()
        )

    return documents