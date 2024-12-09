from fastapi import APIRouter

router = APIRouter(
    prefix="/drill-bot",
    tags=["drill-bot"],
    responses={404: {"description": "Not found"}},
)


@router.get("/nyi", description="Platzhalter")
def nyi():
    return {"output": "nyi"}
