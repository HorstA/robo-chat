from typing import List, Literal, Sequence

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms.ollama import Ollama
from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    BaseMessage,
    FunctionMessage,
    HumanMessage,
)
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain_experimental.text_splitter import SemanticChunker

# ToDo das fliegt später wieder raus -> Poetry!!!
# from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import (
    ChatOpenAI,
    OpenAIEmbeddings,
    AzureChatOpenAI,
    AzureOpenAIEmbeddings,
)
from langchain_openai.llms import AzureOpenAI
from loguru import logger
from utils.AppSettings import AppSettings

# from langchain_nvidia_ai_endpoints import ChatNVIDIA


settings = AppSettings()


@logger.catch
def get_model(
    temperature: float = 0,
    use_ollama_json_format: bool = False,
    use_openai: bool = settings.getenv("USE_OPENAI", False),
    openai_chat_model: str = settings.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
):
    if use_openai:
        logger.debug("Using OPENAI...")
        return ChatOpenAI(model=openai_chat_model, temperature=temperature)
    elif settings.getenv("USE_GROQ", False):
        from langchain_groq import ChatGroq

        logger.debug("Using groq...")
        return ChatGroq(
            temperature=temperature,
            model=settings.getenv("GROQ_CHAT_MODEL", "llama3-70b-8192"),
        )
    elif settings.getenv("USE_AZURE", False):
        logger.debug("Using Azure (may not work)...")
        return AzureOpenAI(deployment_name="gpt-4o-mini", temperature=temperature)

    if use_ollama_json_format:
        return Ollama(
            base_url=settings.LLM_URL_SERVER,
            model=settings.LLM_MODEL,
            temperature=temperature,
            format="json",
        )
    else:
        return Ollama(
            base_url=settings.LLM_URL_SERVER,
            model=settings.LLM_MODEL,
            temperature=temperature,
        )


@logger.catch
def get_chatmodel(
    temperature: float = 0,
    use_ollama_json_format: bool = False,
    use_openai: bool = settings.getenv("USE_OPENAI", False),
    openai_chat_model: str = settings.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
    num_ctx=2048,
):
    if use_openai:
        logger.debug("Using OPENAI...")
        return ChatOpenAI(model=openai_chat_model, temperature=temperature)
    elif settings.getenv("USE_GROQ", False):
        from langchain_groq import ChatGroq

        logger.debug("Using groq...")
        return ChatGroq(
            temperature=temperature,
            model=settings.getenv("GROQ_CHAT_MODEL", "llama3-70b-8192"),
        )
    elif settings.getenv("USE_AZURE"):
        logger.debug("Using Azure...")
        return AzureChatOpenAI(
            temperature=temperature,
            azure_deployment=settings.getenv("AZURE_DEPLOYMENT"),
        )

    if use_ollama_json_format:
        return ChatOllama(
            base_url=settings.LLM_URL_SERVER,
            model=settings.LLM_MODEL,
            temperature=temperature,
            format="json",
            num_ctx=num_ctx,
        )
    else:
        return ChatOllama(
            base_url=settings.LLM_URL_SERVER,
            model=settings.LLM_MODEL,
            temperature=temperature,
            num_ctx=num_ctx,
        )


@logger.catch
def get_functionmodel(
    temperature: float = 0,
    use_openai: bool = settings.getenv("USE_OPENAI", False),
    openai_chat_model: str = settings.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
):
    if use_openai:
        logger.debug("Using OPENAI...")
        return ChatOpenAI(model=openai_chat_model, temperature=temperature)
    elif settings.getenv("USE_GROQ", False):
        from langchain_groq import ChatGroq

        logger.debug("Using groq...")
        return ChatGroq(
            temperature=temperature,
            model=settings.getenv("GROQ_CHAT_MODEL", "llama3-70b-8192"),
        )
    elif settings.getenv("USE_AZURE"):
        logger.debug("Using Azure...")
        return AzureChatOpenAI(
            temperature=temperature,
            azure_deployment=settings.getenv("AZURE_DEPLOYMENT"),
        )
    else:
        return OllamaFunctions(
            base_url=settings.LLM_URL_SERVER,
            model=settings.LLM_MODEL,
            temperature=temperature,
            format="json",
        )


@logger.catch(reraise=True)
def get_embeddingsmodel():
    # Note: OpenAIEmbeddings has different dimensions:
    if settings.getenv("USE_OPENAI_EMBEDDING", False):
        logger.debug("Using OpenAI text-embedding-3-small...")
        return OpenAIEmbeddings(model="text-embedding-3-small")
    elif settings.getenv("USE_AZURE_EMBEDDING", False):
        logger.debug("using Azure text-embedding-3-large...")
        return AzureOpenAIEmbeddings(model="text-embedding-3-large")

    logger.debug(f"Using OllamaEmbeddings {settings.LLM_EMBEDDINGMODEL}...")
    return OllamaEmbeddings(
        base_url=settings.LLM_URL_EMBEDDING_SERVER or settings.LLM_URL_SERVER,
        model=settings.LLM_EMBEDDINGMODEL,
    )


def get_splitter(
    splitter_type: Literal["recursive", "semantic"] = "recursive",
    chunk_size: int = settings.CHUNK_SIZE,
    chunk_overlap: int = settings.CHUNK_OVERLAP,
    separators: List[str] | None = ["\nArt. ", "\n(", "\n\n", "\n", " ", ""],
):
    if splitter_type == "recursive":
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
        )
    elif splitter_type == "semantic":
        # Semantic splitting hat bei ersten Tests mit dem BayBG kein besseres Resultat geliefert
        # dauert auch ca. 3 Minuten, aber die Teilung ist tatsächlich einigermaßen semantisch
        # breakpoint_threshold_type hat wenig Einfluss
        text_splitter = SemanticChunker(
            get_embeddingsmodel(), breakpoint_threshold_type="percentile"
        )
    return text_splitter


@logger.catch
def embed_text(text: str):
    embed_model = get_embeddingsmodel()
    embed_vector = embed_model.embed_query(text)
    return embed_vector


def get_last_message(messages: Sequence[AnyMessage]) -> AnyMessage | None:
    if messages:
        return messages[-1]
    return None


def get_last_ai_message(messages: Sequence[AnyMessage]) -> AIMessage | None:
    if messages is None:
        return None
    for m in messages[::-1]:
        if isinstance(m, AIMessage):
            return m
    return None


def get_last_ai_message_name(messages: Sequence[AnyMessage], name) -> AIMessage | None:
    if messages is None:
        return None
    for m in messages[::-1]:
        if isinstance(m, AIMessage) and m.name == name:
            return m
    return None


def get_last_human_message(messages: Sequence[AnyMessage]) -> HumanMessage | None:
    if messages is None:
        return None
    for m in messages[::-1]:
        if isinstance(m, HumanMessage):
            return m
    return None


def get_last_function_message(messages: Sequence[BaseMessage]) -> HumanMessage | None:
    if messages is None:
        return None
    for m in messages[::-1]:
        if isinstance(m, FunctionMessage):
            return m
    return None
