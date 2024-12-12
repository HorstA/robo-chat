from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.config import RunnableConfig
from langfuse.callback import CallbackHandler

from utils.aiutils import get_chatmodel

model = get_chatmodel()
_prompt = ChatPromptTemplate.from_template("Question: {text}")

_chain = _prompt | model | StrOutputParser()
chain = _chain.with_config(RunnableConfig(callbacks=[CallbackHandler()]))
breakpoint = "here"
