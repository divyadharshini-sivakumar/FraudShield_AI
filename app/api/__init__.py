from fastapi import APIRouter
from app.api.predict import router as predict_router
from app.api.auth import router as auth_router

api_router = APIRouter()
api_router.include_router(
    auth_router,
    tags=["Authentication"],
)

api_router.include_router(
    predict_router,
    tags=["Prediction"],
)