from __future__ import annotations

from pathlib import Path

from app.retrieval import Retriever
from app.schemas import BriefRequest, BriefResponse, ToolTrace
from app.tools import ToolRegistry, ToolResult, format_response_tool, make_outline_tool, safety_review_tool

DISCLAIMER = (
    "This assistant drafts source-grounded community content from a local sample corpus. "
    "It is not a scholar and should not be used for fatwas or final religious rulings."
)


class DawahAgent:
    def __init__(self, data_dir: Path):
        self.retriever = Retriever(data_dir)
        self.tools = ToolRegistry()
        self.tools.register("retrieve_sources", self._retrieve_sources)
        self.tools.register("build_outline", make_outline_tool)
        self.tools.register("format_response", format_response_tool)
        self.tools.register("safety_review", safety_review_tool)

    def list_sources(self):
        return self.retriever.list_sources()

    def run(self, request: BriefRequest) -> BriefResponse:
        trace: list[ToolTrace] = []

        retrieval = self.tools.run("retrieve_sources", request=request)
        citations = retrieval.value
        trace.append(retrieval.trace)

        outline = self.tools.run("build_outline", request=request, citations=citations)
        trace.append(outline.trace)

        formatted = self.tools.run("format_response", request=request, outline=outline.value)
        trace.append(formatted.trace)

        review = self.tools.run("safety_review", request=request, citations=citations)
        trace.append(review.trace)

        return BriefResponse(
            topic=request.topic,
            audience=request.audience,
            content_type=request.content_type,
            answer=formatted.value,
            citations=citations,
            review_checklist=review.value,
            tool_trace=trace,
            disclaimer=DISCLAIMER,
        )

    def _retrieve_sources(self, request: BriefRequest) -> ToolResult:
        query = " ".join([request.topic, request.audience, request.content_type, request.tone, *request.constraints])
        citations = self.retriever.search(query=query, limit=4)
        return ToolResult(
            value=citations,
            trace=ToolTrace(
                name="retrieve_sources",
                input_summary=query[:120],
                output_summary=f"Retrieved {len(citations)} citation candidates",
            ),
        )
