from fastapi import FastAPI
from app.api.api_router import main_router

app = FastAPI(
    title="Trava API",
    description="An API for fetching travel-related "
    "information like flights, hotels, and more. ",
    version="1.0.0"
)

# main router from t
# he api module
app.include_router(main_router, prefix="/api")

@app.get("/")
def test_api():
    return {"message": "Helllo World!"}