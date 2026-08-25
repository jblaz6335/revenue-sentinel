$ErrorActionPreference = "Stop"

uv run ruff check .
uv run ruff format --check .
uv run pytest --cov=src/revenue_sentinel --cov=main --cov-report=term-missing
uv run revenue-sentinel fixtures/opportunities.json --pretty
uv run python -c "from app.agent import app, root_agent; print(app.name, root_agent.name, root_agent.model.model, len(root_agent.tools))"
