from fastapi import APIRouter

from app.api import predict

api_router = APIRouter()

api_router.include_router(
    predict.router,
    tags=["Prediction"]
)