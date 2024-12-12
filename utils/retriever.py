from loguru import logger
from utils import AppSettings, aiutils
from langchain_postgres.vectorstores import PGVector

settings = AppSettings.AppSettings()


@logger.catch(reraise=True)
def get_vectorstore(collection_name: str = settings.PGVECTOR_COLLECTION):
    # postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]
    connection = f"postgresql+psycopg://{settings.PGVECTOR_USER}:{settings.PGVECTOR_PASSWORD}@{settings.PGVECTOR_HOST}:{settings.PGVECTOR_PORT}/{settings.PGVECTOR_DB}"

    vectorstore = PGVector(
        embeddings=aiutils.get_embeddingsmodel(),
        collection_name=collection_name,
        connection=connection,
        use_jsonb=True,
    )
    return vectorstore


@logger.catch(reraise=True)
def get_retriever(
    search_kwargs=None, collection_name: str = settings.PGVECTOR_COLLECTION
):
    vectorstore = get_vectorstore(collection_name)

    if search_kwargs:
        retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
    else:
        retriever = vectorstore.as_retriever()

    return retriever
