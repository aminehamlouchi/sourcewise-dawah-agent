from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.agent import DawahAgent
from app.main import DEFAULT_DATA_DIR
from app.schemas import BriefRequest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a source-grounded dawah content brief.")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--audience", default="general community")
    parser.add_argument("--content-type", default="study_circle_plan", choices=["khutbah_outline", "social_caption", "study_circle_plan"])
    parser.add_argument("--tone", default="warm and practical")
    parser.add_argument("--constraint", action="append", default=[])
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--json", action="store_true", help="Print raw JSON")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    request = BriefRequest(
        topic=args.topic,
        audience=args.audience,
        content_type=args.content_type,
        tone=args.tone,
        constraints=args.constraint,
    )
    agent = DawahAgent(data_dir=Path(args.data_dir))
    response = agent.run(request)
    if args.json:
        print(response.model_dump_json(indent=2))
        return

    print(f"# {response.answer.get('title', request.topic.title())}")
    print()
    print(response.disclaimer)
    print()
    print(json.dumps(response.answer, indent=2))
    print()
    print("Citations:")
    for citation in response.citations:
        print(f"- {citation.title} / {citation.heading}: {citation.excerpt}")
    print()
    print("Review checklist:")
    for item in response.review_checklist:
        print(f"- {item}")


if __name__ == "__main__":
    main()
