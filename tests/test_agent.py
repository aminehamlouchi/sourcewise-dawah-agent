from pathlib import Path

from app.agent import DawahAgent
from app.schemas import BriefRequest


def test_agent_returns_citations_and_review_checklist() -> None:
    agent = DawahAgent(Path("data/sources"))
    response = agent.run(
        BriefRequest(
            topic="welcoming new Muslim students",
            audience="college MSA",
            content_type="study_circle_plan",
        )
    )

    assert response.citations
    assert response.review_checklist
    assert len(response.tool_trace) == 4
    assert "not a scholar" in response.disclaimer
