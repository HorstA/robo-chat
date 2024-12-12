import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langfuse.callback import CallbackHandler
from langchain_core.runnables.config import RunnableConfig
from langserve import add_routes
from contextlib import asynccontextmanager
from app.routers import drill_bot, file, supervisor
from chains.rag.graph import graph as rag_graph, InputDict
from chains.chat.chain import chain as chat_chain
from chains.chat.graph import graph as chat_graph
from utils import AppSettings
from loguru import logger

settings = AppSettings.AppSettings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    ###  before the application starts ###
    os.makedirs("./data/log", exist_ok=True)
    os.makedirs("./data/upload", exist_ok=True)
    logger.add(
        settings.LOG_FILE,
        colorize=False,
        enqueue=True,
        level=os.getenv("LOGLEVEL", default="DEBUG"),
        rotation="1 MB",
    )
    logger.success(f"Starting server with loglevel: {settings.LOG_LEVEL}")
    yield

    ### after the application has finished ###
    logger.success("Server has shut down.")


app = FastAPI(
    title=settings.fastapi_title,
    version=settings.fastapi_version,
    description=settings.fastapi_description,
    lifespan=lifespan,
)

langfuse_handler = CallbackHandler()
config = None
# Todo: This method is blocking. It is discouraged to use it in production code.
try:
    langfuse_handler.auth_check()
    logger.success("Verbindung mit Langfuse hergestellt.")
    config = RunnableConfig(callbacks=[langfuse_handler])
except Exception as e:
    logger.error(
        "Die Authentifizierung mit Langfuse ist fehlgeschlagen. Sind die env-Variablen LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY und LANGFUSE_HOST gesetzt?"
    )
    logger.error(e)


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


@app.get("/nyi", description="Platzhalter")
def nyi():
    return {"output": "nyi"}


add_routes(
    app,
    chat_chain,
    path="/chat",
)

add_routes(
    app,
    chat_graph.with_config(config),
    path="/chat_graph",
)

add_routes(
    app,
    rag_graph.with_config(config),
    path="/rag",
    input_type=InputDict,
)

app.include_router(supervisor.router)
app.include_router(drill_bot.router)
app.include_router(file.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
