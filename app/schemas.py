from typing import Any, Literal

from pydantic import BaseModel, Field

ContentType = Literal["khutbah_outline", "social_caption", "study_circle_plan"]


class BriefRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=160)
    audience: str = Field("general community", min_length=3, max_length=120)
    content_type: ContentType = "study_circle_plan"
    tone: str = Field("warm and practical", min_length=3, max_length=120)
    constraints: list[str] = Field(default_factory=list)


class Citation(BaseModel):
    source_id: str
    title: str
    path: str
    heading: str
    score: float
    excerpt: str


class ToolTrace(BaseModel):
    name: str
    input_summary: str
    output_summary: str


class BriefResponse(BaseModel):
    topic: str
    audience: str
    content_type: ContentType
    answer: dict[str, Any]
    citations: list[Citation]
    review_checklist: list[str]
    tool_trace: list[ToolTrace]
    disclaimer: str


class SourceSummary(BaseModel):
    source_id: str
    title: str
    tags: list[str]
    path: str
