from fastapi import APIRouter

router = APIRouter()

@router.get("/flights")
def get_flights():
    """
    Retrieve flight information.
    """

    return {"message": "Listing top available flights.."}

# check: # https://serpapi.com/google-hotels-api
