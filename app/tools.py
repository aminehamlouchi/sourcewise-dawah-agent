from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from app.schemas import BriefRequest, Citation, ToolTrace


@dataclass
class ToolResult:
    value: Any
    trace: ToolTrace


ToolFn = Callable[..., ToolResult]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolFn] = {}

    def register(self, name: str, fn: ToolFn) -> None:
        self._tools[name] = fn

    def run(self, name: str, **kwargs: Any) -> ToolResult:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name](**kwargs)


def make_outline_tool(request: BriefRequest, citations: list[Citation]) -> ToolResult:
    focus_points = [citation.heading for citation in citations[:3]]
    outline = {
        "opening": f"Begin with the community need behind '{request.topic}' for {request.audience}.",
        "focus_points": focus_points or ["Clarify the topic", "Connect to daily practice", "Invite one action"],
        "evidence_notes": [citation.excerpt for citation in citations[:3]],
        "call_to_action": "End with one realistic next step the audience can take this week.",
    }
    return ToolResult(
        value=outline,
        trace=ToolTrace(
            name="build_outline",
            input_summary=f"{request.content_type} for {request.audience}",
            output_summary=f"Created {len(outline['focus_points'])} focus points",
        ),
    )


def format_response_tool(request: BriefRequest, outline: dict[str, Any]) -> ToolResult:
    if request.content_type == "social_caption":
        answer = {
            "caption": (
                f"{request.topic.title()} starts with one sincere step. "
                f"For {request.audience}, connect the reminder to real service, steady character, "
                "and a practical action before the week ends."
            ),
            "bullets": outline["focus_points"],
            "hashtags": ["#MSA", "#Masjid", "#CommunityCare"],
        }
    elif request.content_type == "khutbah_outline":
        answer = {
            "title": request.topic.title(),
            "sections": [
                {"name": "Opening reminder", "notes": outline["opening"]},
                {"name": "Community application", "notes": "; ".join(outline["focus_points"])},
                {"name": "Action step", "notes": outline["call_to_action"]},
            ],
            "estimated_minutes": 12,
        }
    else:
        answer = {
            "title": f"Study circle: {request.topic.title()}",
            "agenda": [
                "Welcome and intention setting",
                *outline["focus_points"],
                "Pair discussion",
                outline["call_to_action"],
            ],
            "facilitator_notes": outline["evidence_notes"],
        }

    return ToolResult(
        value=answer,
        trace=ToolTrace(
            name="format_response",
            input_summary=f"Format as {request.content_type}",
            output_summary=f"Produced fields: {', '.join(answer.keys())}",
        ),
    )


def safety_review_tool(request: BriefRequest, citations: list[Citation]) -> ToolResult:
    checklist = [
        "Verify every religious claim against a trusted teacher or reviewed local source before publishing.",
        "Keep the language practical and avoid presenting this as a fatwa.",
        "Confirm the tone fits the audience and does not shame people who are learning.",
        "Check that every cited source is relevant to the final wording.",
    ]
    if not citations:
        checklist.insert(0, "Add reviewed sources before using this content publicly.")
    if request.constraints:
        checklist.append("Confirm the requested constraints are reflected without overstating the sources.")

    return ToolResult(
        value=checklist,
        trace=ToolTrace(
            name="safety_review",
            input_summary=f"{len(citations)} citations and {len(request.constraints)} constraints",
            output_summary=f"Returned {len(checklist)} review checks",
        ),
    )
