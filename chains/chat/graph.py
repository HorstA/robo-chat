import json

# from typing_extensions import Annotated, TypedDict, List
from typing import Annotated, NotRequired, TypedDict
from tenacity import retry, stop_after_attempt, wait_fixed
from langchain_core.messages import AIMessage, HumanMessage, AnyMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph.message import add_messages
from langgraph.graph import START, END, StateGraph
from loguru import logger
from langchain.schema.runnable import RunnableLambda
from chains.core.chains import (
    further_q_prompt,
    FurtherQuestions,
    further_q_parser,
    patch_config,
)

from utils.aiutils import get_chatmodel


# TODO: creates UserWarning: typing.NotRequired is not a Python type
# because of "NotRequired", but NotRequired must be
# and pydantic.SkipValidation not working
class InputDict(TypedDict):
    input: str
    chat_history: Annotated[NotRequired[list[AnyMessage]], add_messages]


class GraphState(TypedDict):
    """
    Status des Graphen.

    Attribute:
        question: question
    """

    input: str
    chat_history: Annotated[list[AnyMessage], add_messages]
    generation: str
    further_questions: list[str]


@logger.catch(reraise=True)
@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def create_chat_history(state: InputDict):
    if not state.get("input", ""):
        raise ValueError("Aufruf ohne Key 'input' oder leer")

    if state.get("chat_history", []):
        history = state["chat_history"] + [HumanMessage(content=state["input"])]
    else:
        history = [HumanMessage(content=state["input"])]
    return {"chat_history": history}


@logger.catch(reraise=True)
@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def generate(state: GraphState, config: RunnableConfig):
    model = get_chatmodel().with_config(patch_config(config))
    output = model.invoke(state["chat_history"])
    return {"generation": output.content}


def get_further_questions(state: GraphState, config: RunnableConfig):

    if not config["metadata"].get("further_questions", False):
        return {"further_questions": []}

    logger.info("---FURTHER QUESTIONS---")
    qa_history = state["chat_history"] + [
        AIMessage(content=state["generation"]),
    ]

    model = get_chatmodel(use_ollama_json_format=True).with_config(patch_config(config))

    further_questions_chain = (
        further_q_prompt
        | model.with_structured_output(FurtherQuestions)
        | RunnableLambda(further_q_parser)
    )
    try:
        fqs = further_questions_chain.invoke({"chat_history": qa_history})
        further_questions = fqs["questions"]
    except Exception as e:
        logger.warning(f"Error in get_further_questions: {e}")
        further_questions = []
    return {"further_questions": further_questions}


workflow = StateGraph(GraphState)
workflow.add_node("create_chat_history", create_chat_history)
workflow.add_node("chatbot", generate)
workflow.add_node("get_further_questions", get_further_questions)

workflow.add_edge(START, "create_chat_history")
workflow.add_edge("create_chat_history", "chatbot")
workflow.add_edge("chatbot", "get_further_questions")
workflow.add_edge("get_further_questions", END)

graph = workflow.compile()
"""this is the chat graph with optional further questions
"""

# from langfuse.callback import CallbackHandler
# graph = graph.with_config(RunnableConfig(callbacks=[CallbackHandler()]))
# breakpoint = "here"
