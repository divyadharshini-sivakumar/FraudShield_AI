import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.db.session import Base, engine

# Import models so SQLAlchemy registers their tables.
from app.db.models import DetectionRecord


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="FraudShield AI API",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    api_router,
    prefix="/api",
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting FraudShield AI API")

    database_url = str(engine.url)

    db_backend = (
        "postgres"
        if "postgres" in database_url
        else "sqlite"
    )

    logger.info(
        "Using database backend: %s",
        db_backend,
    )

    Base.metadata.create_all(
        bind=engine,
    )

    logger.info(
        "Database tables created or verified"
    )


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(
        "Shutting down FraudShield AI API"
    )