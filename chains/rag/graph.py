from typing import List

from langchain_core.documents import Document
from langgraph.graph import END, StateGraph
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed
from typing_extensions import TypedDict

from chains.core.chains import rag_chain
from utils.retriever import get_retriever


class InputDict(TypedDict):
    question: str


@logger.catch
@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def retrieve(state: InputDict):
    """
    Retrieve documents from vectorstore
    """
    logger.info("---ABRUFEN---")
    question = state["question"]

    retriever = get_retriever()

    documents = retriever.invoke(question)
    return {"documents": documents}


@logger.catch
@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def generate(state):
    """
    Generate answer using RAG on retrieved documents
    """
    logger.info("---GENERIEREN---")
    question = state["question"]
    documents = state["documents"]

    generation = rag_chain.invoke({"context": documents, "question": question})
    return {
        "generation": generation,
    }


### State


class GraphState(TypedDict):
    """
    Status des Graphen.

    Attribute:
        question: question
    """

    question: str
    generation: str | None
    documents: List[Document] | None


workflow = StateGraph(GraphState)

workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

graph = workflow.compile()
"""this is the normal RAG graph
"""
