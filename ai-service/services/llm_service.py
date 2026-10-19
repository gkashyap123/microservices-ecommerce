from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

def ask_llm(question: str) -> str:
    response = llm.invoke([
        HumanMessage(content=question)
    ])
    return str(response.content)