from typing import List
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import (
    AIMessage,
    SystemMessage,
)

from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.agents import load_tools

from utils.debate.DialogueAgent import DialogueAgent


class DialogueAgentWithTools(DialogueAgent):
    def __init__(
        self,
        name: str,
        system_message: SystemMessage,
        model: ChatOpenAI,
        tool_names: List[str],
        **tool_kwargs,
    ) -> None:
        super().__init__(name, system_message, model)
        self.tools = load_tools(tool_names, **tool_kwargs)

    def send(self) -> str:
        """
        Applies the chatmodel to the message history
        and returns the message string
        """
        error_text = "Überprüfe den Output uns stelle sicher dass er konform ist (Parsing error)!"

        agent_chain = initialize_agent(
            self.tools,
            self.model,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=error_text,
            memory=ConversationBufferMemory(
                memory_key="chat_history", return_messages=True
            ),
        )
        message = AIMessage(
            content=agent_chain.run(
                input="\n".join(
                    [self.system_message.content] + self.message_history + [self.prefix]
                )
            )
        )

        return message.content
