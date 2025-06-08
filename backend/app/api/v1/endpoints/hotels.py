from fastapi import APIRouter

router = APIRouter()

@router.get("/hotels")
def get_hotels():
    """
    Retrieve hotel information.
    """

    return {"message": "Listing top available hotels.."}


