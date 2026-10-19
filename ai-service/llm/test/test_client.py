import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from llm.client import get_llm

load_dotenv()


if __name__ == "__main__":
	llm = get_llm()
	answer = llm.invoke("What is Retrieval-Augmented Generation?")
	print(answer.content)