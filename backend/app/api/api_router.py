from fastapi import APIRouter
from app.api.v1.routers import api_router as v1_router

# This is the main router for the entire API
main_router = APIRouter()

main_router.include_router(v1_router, prefix="/v1")