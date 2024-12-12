from typing import List
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    HumanMessage,
    SystemMessage,
)

from utils.debate.DialogueAgent import DialogueAgent


# Beschreibungen der Teilnehmer generieren
def generate_agent_description(
    conversation_description, name, word_limit, openai_api_key
):
    content = (
        "Du kannst Details zu den Beschreibungen der Gesprächsteilnehmer hinzufügen."
    )
    agent_descriptor_system_message = SystemMessage(content=content)

    content = f"""{conversation_description}
    Bitte antworte mit einer kreativen Beschreibung von {name} in {word_limit} Wörtern oder weniger.
    Spreche direkt mit {name}.
    Gib ihm eine Sicht der Dinge.
    Füge sonst nichts hinzu.
    Antworte auf Deutsch."""

    agent_specifier_prompt = [
        agent_descriptor_system_message,
        HumanMessage(content=content),
    ]
    agent_description = ChatOpenAI(temperature=1.0, openai_api_key=openai_api_key)(
        agent_specifier_prompt
    ).content
    return agent_description


def generate_agent_descriptions(
    participants: dict[str, list[str]],
    conversation_description: str,
    word_limit: int,
    openai_api_key,
):
    return {
        name: generate_agent_description(
            conversation_description, name, word_limit, openai_api_key
        )
        for name in participants
    }


def generate_system_message(name: str, description: str, conversation_description: str):
    return f"""{conversation_description}

    Dein Name ist {name}.

    Deine Beschreibung lautet wie folgt: {description}

    Dein Ziel ist es, deinen Gesprächspartner von deinem Standpunkt zu überzeugen.

    Du sollst mit deinen Werkzeugen nach Informationen suchen, um die Behauptungen deines Partners zu widerlegen.
    Nenne deine Quellen.

    Du darfst keine Fake-Zitate erzeugen.
    Zitiere KEINE Quellen, die du nicht selbst nachgeschlagen hast.

    Füge sonst nichts hinzu.
    Antworte auf Deutsch.

    Höre in dem Moment auf zu sprechen, in dem du aus deiner Sicht zu Ende gesprochen haben.
    """


def get_specified_topic(raw_topic, participants, word_limit, openai_api_key):
    topic_specifier_prompt = [
        SystemMessage(content="Du kannst Themen spezifischer gestalten."),
        HumanMessage(
            content=f"""{raw_topic}
            Du bist der Moderator.
            Bitte gestalte das Thema noch spezifischer.
            Bitte antworte mit der angegebenen Aufgabe in {word_limit} Wörtern oder weniger.
            Spreche direkt zu diesen Teilnehmern: {*participants,}.
            Füge sonst nichts hinzu.
            Antworte auf Deutsch."""
        ),
    ]

    return ChatOpenAI(openai_api_key=openai_api_key, temperature=1.0)(
        topic_specifier_prompt
    ).content


def select_next_speaker(step: int, agents: List[DialogueAgent]) -> int:
    idx = (step) % len(agents)
    return idx
