# Verification record

Verified locally and on Google Cloud on 2026-08-25 using Python 3.12.13.

## Automated checks

- 45 tests passed.
- Combined measured coverage across the ADK app, FastAPI service, and deterministic package: 95%.
- Ruff lint passed.
- Ruff formatting check passed for 28 files.
- The real Google ADK definition imports successfully as app `revenue_sentinel`, agent `revenue_sentinel`, model `gemini-3.5-flash`, with two tools.

## HTTP proof

A local Uvicorn process served the FastAPI app on `127.0.0.1:8765`:

- `GET /healthz` → HTTP 200 and `status: ok`.
- `POST /api/demo` → HTTP 200, five audited opportunities: two review, one table, two reject.
- `GET /` → HTTP 200 and the Revenue Sentinel dashboard.

## Google Cloud proof

- Dedicated project: `blaz-revenue-sentinel-2026`.
- Cloud Run service: `revenue-sentinel` in `us-central1`.
- Active revision: `revenue-sentinel-00002-t5j`, serving 100% of traffic.
- Public URL: `https://revenue-sentinel-867717531848.us-central1.run.app`.
- `GET /api/health` returned HTTP 200 with `status: ok`.
- `POST /api/demo` returned five cases and USD 515 total planning value.
- `POST /api/agent/audit` returned HTTP 200 from Gemini 3.5 Flash and recorded the `audit_opportunity` tool call.
- The live proof response contained evidence digest `645e79ed492bb72b9bae5bcfbe93107bfd7a266174983b89ecae2525ee7c8352`.
- Firestore contains the matching digest-addressed audit document.
- Cloud Logging records the revision-2 agent request with HTTP 200 and 12.05-second latency.
- A three-region uptime check runs every 15 minutes against `/api/health` with a critical email alert policy.
- Cloud Run is capped at one instance and uses the dedicated `revenue-sentinel-runtime` service account.

## Demo proof

The five-case credential-free CLI completed successfully:

- verified Google contest route: review because entrant eligibility remains unknown;
- unverified/unprotected contract: review;
- 0.00016-USDT agent marketplace queue: table;
- expired contract: reject;
- invalid source/deadline: reject.

The hackathon channel cap is 1%, producing USD 500 expected value on the USD 50,000 maximum prize example. That is a conservative planning assumption, not a forecast or prize claim.

## Visual proof

`assets/architecture.png` was rendered from the source SVG and visually inspected at 3200×1800. All nodes, arrows, labels, boundaries, and the owner-gate footer are legible without clipping or overlap.

## Environment findings

- Google Cloud CLI is installed and authenticated to the project owner account.
- Cloud Build successfully built both deployed container revisions.
- The dedicated billing project has a USD 145 gross-spend alert budget for the credit period.

## Unverified external state

The following remain explicitly unverified and must not be claimed:

- Devpost registration, contest entry, public repository, demo-video upload, or submission;
- judging result, prize, user, customer, contract, sale, or revenue.
