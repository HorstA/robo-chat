from fastapi import APIRouter
from langserve import add_routes
from chains.supervisor.graph import supervisor
from langfuse.callback import CallbackHandler
from langchain_core.runnables.config import RunnableConfig


router = APIRouter(
    prefix="/supervisor",
    tags=["supervisor"],
    responses={404: {"description": "Not found"}},
)


config = RunnableConfig(callbacks=[CallbackHandler()])

add_routes(router, supervisor.with_config(config), path="/invoke")


@router.post("/invoke-test", name="invoke supervisor", description="Invoke Supervisor")
def invoke_supervisor():
    return {"output": "supervisor"}
