from typing import Annotated
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import InjectedState, create_react_agent
from chains.rag.graph import graph as rag_graph
from utils.aiutils import get_chatmodel


# this is the agent function that will be called as tool
# notice that you can pass the state to the tool via InjectedState annotation
def agent_archive(state: Annotated[dict, InjectedState]):
    # you can pass relevant parts of the state to the LLM (e.g., state["messages"])
    # and add any additional logic (different models, custom prompts, structured output, etc.)
    response = rag_graph.invoke(state)
    # return the LLM response as a string (expected tool response format)
    # this will be automatically turned to ToolMessage
    # by the prebuilt create_react_agent (supervisor)
    return response.content


def agent_2(state: Annotated[dict, InjectedState]):
    # response = model.invoke(...)
    return {"generation": "das ist alles nur gefaket"}


tools = [agent_archive, agent_2]
# the simplest way to build a supervisor w/ tool-calling is to use prebuilt ReAct agent graph
# that consists of a tool-calling LLM node (i.e. supervisor) and a tool-executing node
supervisor = create_react_agent(get_chatmodel(), tools)
