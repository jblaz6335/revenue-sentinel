# Demo runbook

Target length: 3 minutes 35 seconds. Keep the recording unedited if required by the final rules review.

## 1. Establish the problem - 25 seconds

Show the dashboard. Explain that autonomous revenue agents can waste time on closed, ineligible, unsafe, or dust-value work and can turn uncertain leads into false revenue claims.

## 2. Show the five-case batch - 55 seconds

Run:

```powershell
uv run revenue-sentinel fixtures/opportunities.json --pretty
```

Highlight:

- the Google contest remains `review` until owner eligibility is confirmed;
- the 0.00016 USDT marketplace queue is tabled;
- the expired contract and invalid source are rejected;
- the unprotected, unverified contract stays under review.

## 3. Prove the deterministic boundary - 50 seconds

Open `src/revenue_sentinel/engine.py`. Show the hard-reject, dust, eligibility, and ready conditions. Explain that Gemini cannot override these decisions because the ADK agent only receives audit and brief tools.

Run the tests:

```powershell
uv run pytest
uv run ruff check .
```

## 4. Show the agent and architecture - 45 seconds

Open `app/agent.py` and `assets/architecture.svg`. Point out Gemini 3.5 Flash, Google ADK, the Cloud Run API, Firestore evidence store, and the owner gate around external writes.

## 5. Prove Google Cloud deployment - 45 seconds

Show, in one continuous sequence:

1. the Cloud Run service and revision;
2. the public or authenticated `.run.app` endpoint;
3. `POST /api/demo` returning five results;
4. an ADK/Gemini invocation;
5. the corresponding Firestore record;
6. Cloud logs showing the request.

Every listed cloud item was verified on August 25, 2026. Show the evidence in one continuous recording.

## 6. Close - 15 seconds

“Revenue Sentinel lets an agent move fast on research and preparation without confusing a lead with revenue or an uncertain fact with permission.”
