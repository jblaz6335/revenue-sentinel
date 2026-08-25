# Submission checklist

## Eligibility and ownership - owner review

- [x] Entrant is above the age of majority and resides outside excluded jurisdictions.
- [x] Entrant is not otherwise ineligible under the official rules.
- [x] Submit as an individual/hobbyist and sole developer.
- [x] Confirm the entrant owns or is authorized to submit every project component.
- [x] Join the contest using the correct Devpost account (`jblaz6335`).
- [x] Review and accept the binding official rules personally.

## Google Cloud - owner/account action

- [x] Use dedicated project `blaz-revenue-sentinel-2026` and confirm billing responsibility.
- [x] Claim the USD 150 participant credit.
- [x] Create the least-privilege `revenue-sentinel-runtime` service account.
- [x] Enable a gross-spend budget and keep maximum instances at one.
- [x] Deploy to Cloud Run.
- [x] Verify active revision `revenue-sentinel-00002-t5j` and the `.run.app` endpoint.
- [x] Verify one real ADK/Gemini 3.5 Flash invocation.
- [x] Verify one matching Firestore audit record and Cloud log entry.

## Public artifacts - owner/account action

- [x] Review the clean source archive.
- [x] Publish the sanitized repository at `https://github.com/jblaz6335/revenue-sentinel`.
- [x] Ensure spin-up instructions reproduce the current verified build.
- [x] Record an approximately four-minute demo.
- [x] Upload the video publicly or as permitted by final rules.
- [x] Add the verified repository, deployment, and video URLs to `SUBMISSION.md`.

## Final technical verification

- [x] `uv sync --python 3.12 --extra dev`
- [x] `uv run pytest --cov=app --cov=src/revenue_sentinel --cov=main --cov-report=term`
- [x] `uv run ruff check .`
- [x] `uv run ruff format --check .`
- [x] `uv run revenue-sentinel fixtures/opportunities.json --pretty`
- [x] HTTP health, demo, dashboard, and API docs verified.
- [ ] Docker build and container health verified where Docker is available.
- [ ] Clean archive extraction passes the same checks.

## Devpost submission

- [x] Draft created as `Revenue Sentinel` under Devpost submission `1153677`.
- [x] Category: Taskmaster.
- [x] Submitter type and country saved as Individual / United States.
- [x] Description covers inspiration, features, technology, challenges, accomplishments, learnings, and next steps in first-person solo-developer voice.
- [x] Live Cloud Run URL and public GitHub repository saved.
- [x] Project thumbnail and architecture gallery image uploaded with captions.
- [x] Architecture diagram attached in the judge-only requirements.
- [x] Google SDKs, Cloud services, Gemini 3.5 Flash, start date, and reproducible testing instructions saved.
- [x] Demo visibly proves the backend runs on Google Cloud.
- [x] Add the public demo video URL to the required Video demo link field.
- [x] All claims match `VERIFICATION.md`.
- [x] Submit before August 31, 2026 at 5:00 p.m. PT.
- [x] Save the final submission URL and confirmation evidence.

## Optional bonus actions

- [ ] Decide whether to publish a qualifying technical article.
- [ ] Decide whether to publish a qualifying social post with `#AllThingsAgenticHackathon`.
- [ ] Keep any optional public claim inside the verified boundary.
