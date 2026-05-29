# SourceWise Dawah Agent

SourceWise Dawah Agent is a source-grounded planning assistant for masjid and MSA content. It retrieves from a small curated knowledge base, runs a multi-step tool workflow, and returns citation-backed outlines, captions, or study-circle plans with a review checklist.

The project is intentionally safe-by-default: it does not issue fatwas, it cites the local notes it used, and it includes human review steps before anything is published.

## Quickstart

Run a local example from the command line:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m app.cli --topic "welcoming new Muslim students" --audience "college MSA" --content-type study_circle_plan
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/docs`.

## Architecture

```mermaid
flowchart LR
    A["Brief request"] --> B["Retrieve sources tool"]
    B --> C["Build outline tool"]
    C --> D["Format response tool"]
    D --> E["Safety review tool"]
    E --> F["Citation-backed brief"]
```

## Workflow

- `retrieve_sources`: scores local text notes against the request.
- `build_outline`: turns the strongest chunks into a structured plan.
- `format_response`: shapes the plan for a khutbah outline, social caption, or study circle.
- `safety_review`: adds review checks for citations, tone, scope, and community fit.

The included workflow is deterministic so tests and local demos run without outside services. `.env.example` also includes an optional `OPENAI_API_KEY` for experimenting with a hosted formatting step later.

## API

```http
POST /api/briefs
Content-Type: application/json

{
  "topic": "welcoming new Muslim students",
  "audience": "college MSA",
  "content_type": "study_circle_plan",
  "tone": "warm and practical"
}
```

Useful routes:

- `GET /health`
- `GET /api/sources`
- `POST /api/briefs`

## Local Setup

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
uvicorn app.main:app --reload
```

## Docker

```bash
docker build -t sourcewise-dawah-agent .
docker run --rm -p 8000:8000 sourcewise-dawah-agent
```

## Deployment

Deploy the Docker image to Render, Fly.io, Railway, or any container host.

Environment variables:

- `SOURCEWISE_DATA_DIR`: optional path to plain-text source notes.
- `OPENAI_API_KEY`: optional future extension; not required for the included agent.

## Testing

```bash
pytest
```

## Roadmap

- Admin UI for uploading reviewed source notes.
- Vector database option with pgvector or Chroma.
- Optional model-backed formatter behind the deterministic planner.
- Feedback log for reviewers to mark weak citations or tone issues.
