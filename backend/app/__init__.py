from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_router import main_router

app = FastAPI(
    title="RouteRishi API",
    description="An API for fetching travel-related "
    "information like flights, hotels, and more. ",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
        "http://localhost:3000",  # Alternative React dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# main router from the api module
app.include_router(main_router, prefix="/api")

@app.get("/")
def test_api():
    return {"message": "Helllo World!"}