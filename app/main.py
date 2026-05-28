from functools import lru_cache
import os
from pathlib import Path

from fastapi import FastAPI

from app.agent import DawahAgent
from app.schemas import BriefRequest, BriefResponse, SourceSummary

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "sources"


@lru_cache
def get_agent() -> DawahAgent:
    data_dir = Path(os.getenv("SOURCEWISE_DATA_DIR", DEFAULT_DATA_DIR))
    return DawahAgent(data_dir=data_dir)


app = FastAPI(
    title="SourceWise Dawah Agent",
    version="0.1.0",
    description="Source-grounded agentic AI assistant for masjid and MSA content planning.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/sources", response_model=list[SourceSummary])
def list_sources() -> list[SourceSummary]:
    return get_agent().list_sources()


@app.post("/api/briefs", response_model=BriefResponse)
def create_brief(request: BriefRequest) -> BriefResponse:
    return get_agent().run(request)
