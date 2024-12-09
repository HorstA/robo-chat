from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes

from app.routers import chat_room, drill_bot


app = FastAPI()


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


@app.get("/nyi", description="Platzhalter")
def nyi():
    return {"output": "nyi"}


app.include_router(chat_room.router)
app.include_router(drill_bot.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
