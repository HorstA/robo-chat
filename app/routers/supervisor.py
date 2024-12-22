from fastapi import APIRouter
from langserve import add_routes
from chains.supervisor.graph import supervisor
from langfuse.callback import CallbackHandler
from langchain_core.runnables.config import RunnableConfig
from utils.pinutils import Led

from app.globals import bots

router = APIRouter(
    prefix="/supervisor",
    tags=["supervisor"],
    responses={404: {"description": "Not found"}},
)


config = RunnableConfig(callbacks=[CallbackHandler()])

red_bot = Led("red")
yellow_bot = Led("yellow")
green_bot = Led("green")


add_routes(router, supervisor.with_config(config), path="/invoke")


@router.post("/invoke-test", name="invoke supervisor", description="Invoke Supervisor")
def invoke_supervisor():
    return {"output": "supervisor"}


# async def read_items(commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)]):


@router.get("/start-bots", name="start bots", description="Starts the dummy bots")
def start_bots():
    bots.leds[0].blink(1)
    bots.leds[1].blink(0.75)
    bots.leds[2].blink(0.5)

    return {"output": "started bots"}


@router.get("/stop-bots", name="stop bots", description="Stops the dummy bots")
def stop_bots():
    bots.leds[0].stop()
    bots.leds[1].stop()
    bots.leds[2].stop()

    return {"output": "stopped bots"}
