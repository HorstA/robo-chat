from fastapi import APIRouter

router = APIRouter(
    prefix="/chat-room",
    tags=["chat-room"],
    responses={404: {"description": "Not found"}},
)


@router.get("/nyi", description="Platzhalter")
def nyi():
    return {"output": "nyi"}
