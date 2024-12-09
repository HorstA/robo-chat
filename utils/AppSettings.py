import os
from dotenv import find_dotenv, load_dotenv
from typing_extensions import Annotated, Doc
from loguru import logger


class AppSettings:
    """
    `AppSetting` class, the one and only source to get your enviroment variables and predefined parameters.

    Will call os.getenv(), not (!) static, create an instance first.
    ### Example

    ```python
    from mylibs.classes.AppSettings import AppSettings

    settings = AppSettings()

    key = settings.API_KEY
    ```
    """

    true_values = [
        "true",
        "1",
        "t",
        "y",
        "yes",
        "ja",
        "ok",
    ]

    def __init__(self):
        # logger.info("Reading AppSettings...")
        load_dotenv(find_dotenv())  # load enviroment variables once
        self.API_USER = os.getenv("API_USER")
        self.API_PWD = os.getenv("API_PWD")

        self.SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
        self.SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

        self.CHROMADB_HOST = os.getenv("CHROMADB_HOST", "chromaserver")
        self.CHROMADB_PORT = int(os.getenv("CHROMADB_PORT", 8088))
        self.CHROMADB_COLLECTION = os.getenv("CHROMADB_COLLECTION", "rag")
        self.CHROMADB_QA_COLLECTION = os.getenv("CHROMADB_QA_COLLECTION", "qa")
        self.CHROMADB_API_KEY = os.getenv("CHROMADB_API_KEY", None)
        self.CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
        self.CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))

        self.PGVECTOR_USER = os.getenv("PGVECTOR_USER", "user")
        self.PGVECTOR_PASSWORD = os.getenv("PGVECTOR_PASSWORD", "pwd")
        self.PGVECTOR_HOST = os.getenv("PGVECTOR_HOST", "localhost")
        self.PGVECTOR_PORT = int(os.getenv("PGVECTOR_PORT", 5432))
        self.PGVECTOR_DB = os.getenv("PGVECTOR_DB", "db")
        self.PGVECTOR_COLLECTION = os.getenv("PGVECTOR_COLLECTION", "rag")
        self.PGVECTOR_QA_COLLECTION = os.getenv("PGVECTOR_QA_COLLECTION", "qa")

        self.MSSQL_USER = os.getenv("MSSQL_USER", "user")
        self.MSSQL_PASSWORD = os.getenv("MSSQL_PASSWORD", "pwd")
        self.MSSQL_HOST = os.getenv("MSSQL_HOST", "localhost")
        self.MSSQL_PORT = int(os.getenv("MSSQL_PORT", 5432))
        self.MSSQL_DB = os.getenv("MSSQL_DB", "db")

        self.LLM_URL_SERVER = os.getenv("LLM_URL_SERVER")
        self.LLM_URL_EMBEDDING_SERVER = os.getenv("LLM_URL_EMBEDDING_SERVER")
        self.LLM_MODEL = os.getenv("LLM_MODEL", "lff_api_llama31:70b_default")
        self.LLM_MODEL_LARGE = os.getenv("LLM_MODEL_LARGE", "lff_api_llama31:70b_large")
        self.LLM_EMBEDDINGMODEL = os.getenv("LLM_EMBEDDINGMODEL", "nomic-embed-text")
        self.LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1024"))
        self.LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
        self.LLM_LOG_FILE = os.getenv("LLM_LOG_FILE", "./data/log/llmlog.log")

        self.LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", None)
        self.LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "sk-...")
        self.LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "http://localhost:3000")

        self.LOG_FILE = os.getenv("LOG_FILE", "./data/log/apilog.log")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

        self.UNSTRUCTURED_API_URL = os.getenv(
            "UNSTRUCTURED_API_URL", "http://localhost:8089"
        )
        self.VECTORSTORE_DECAY_RATE = os.getenv("VECTORSTORE_DECAY_RATE", 0.08)

        self.fastapi_title = "LLM API"
        self.fastapi_version = "0.1"
        self.fastapi_description = "API server for LLM services"

    def getenv(self, key: str, default=None):
        return os.getenv(key, default)
