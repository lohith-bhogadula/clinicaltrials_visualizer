# ClinicalTrials.gov Query-to-Visualization Agent

An API-only backend that turns a natural-language question plus optional filters into a frontend-ready visualization specification. It queries the official ClinicalTrials.gov API v2 at request time and returns only data supported by retrieved records.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Then open `http://127.0.0.1:8000/` for the interactive dashboard, `http://127.0.0.1:8000/docs` for Swagger UI, or run `python run_examples.py` after the server starts. Run tests with `pytest -q`.

The frontend uses responsive, dependency-free SVG charts. It supports time-series, bar-chart, and sponsor–drug network responses, hover tooltips, example queries, record-level citations, loading/errors, and JSON download.

Container run: `docker build -t clinicaltrials-viz . && docker run -p 8000:8000 clinicaltrials-viz`.

## Request schema

`POST /v1/visualizations` accepts `query` (required, 3–500 characters) and optional `drug_name`, `condition`, `trial_phase` (`PHASE1`, `PHASE2`, `PHASE3`, `PHASE4`, `EARLY_PHASE1`, `NA`), `sponsor`, `country`, `start_year`, `end_year`, and `max_studies` (1–1000). Inputs are type- and range-validated.

## Response schema

The top-level response contains `visualization` and `meta`. Visualization contains `type` (`bar_chart`, `time_series`, or `network_graph`), `title`, `encoding`, and `data`. Each aggregate datum or graph edge has `citations`, with an NCT ID, API-backed supporting excerpt, and canonical study URL. `meta` provides source, applied filters, the deterministic interpretation, record count, and limitations.

## Design

The planner is deterministic and keyword-based: time language produces a yearly series; geographic/phase/distribution language produces a bar chart; relationship language produces a sponsor–drug graph. This prevents an LLM from silently inventing query parameters or chart values. Retrieval uses documented API v2 search parameters, then local exact filtering for year, phase, and country where needed. The public API can paginate beyond the cap; this implementation intentionally caps results to keep response cost and latency bounded, and reports that limitation.

## AI planner and MCP tool

By default the deterministic planner runs with no secret or AI dependency. To enable the optional AI planner, set `OPENAI_API_KEY`, `AI_PLANNER=openai`, and optionally `AI_MODEL`. The AI is constrained to return one of six chart intents and a confidence score. It cannot create filters, counts, source records, or citations; the API and deterministic aggregators remain the only factual path. If the model is unavailable or returns invalid JSON, the service safely falls back to the heuristic planner.

`mcp_server.py` is an optional stdio MCP server exposing `search_clinical_trials` as a tool for an MCP client. Run it separately from the web service in a dedicated environment: `pip install -r requirements-mcp.txt` then `python mcp_server.py`.

## Tradeoffs and next steps

Only the first API page is retrieved, though `max_studies` can be up to 1,000. The service retries transient API failures three times with exponential backoff, but a production version should also page until an explicit budget and add a shared cache. This submission chooses inspectable constrained planning over an opaque model-driven workflow.

## AI-tool disclosure

AI assistance was used to accelerate initial scaffolding and documentation. The final design, data model, retrieval/filtering behavior, citation model, and tests were reviewed and adapted deliberately. Verification includes unit tests and live calls to the official endpoint.
