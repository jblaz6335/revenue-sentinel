# Devpost submission draft

## Project name

Revenue Sentinel

## Category

Taskmaster

## Tagline

An autonomous evidence gate that turns noisy revenue opportunities into a ranked, auditable action queue.

## One-line value proposition

Revenue Sentinel lets an agent research and prepare opportunities automatically without mistaking a lead for revenue, uncertainty for eligibility, or a plausible action for permission.

## Project URL

https://revenue-sentinel-867717531848.us-central1.run.app

## Repository

https://github.com/jblaz6335/revenue-sentinel

## Inspiration

The hardest part of autonomous revenue operations is not generating more text. It is repeatedly checking whether an opportunity is still open, whether the entrant is eligible, whether the buyer or sponsor and prize are real, whether payment is protected, whether scope and budget are clear, whether the expected value justifies the work, and which steps still require human authority.

During my real opportunity research, a seller-agent queue containing sixteen tasks turned out to be worth only 0.00016 USDT in total, while public job results routinely pointed to closed, unverified, or poorly bounded work. That is exactly the kind of messy multi-step chore an autonomous agent should handle, but only with a hard evidence boundary.

## What it does

Revenue Sentinel ingests one opportunity or a batch of up to 100 and produces a ranked queue with four possible outcomes:

- `ready`: verified, low-risk, clearly scoped preparation can proceed;
- `review`: a potentially valuable opportunity has unresolved evidence or authority gates;
- `table`: compensation is too small to justify attention;
- `reject`: the source, deadline, or eligibility fails a hard gate.

Each result includes evidence state, risk, bounded probability, expected value, findings, action gate, next step, timestamp, and a SHA-256 evidence digest. In deployed mode, Firestore stores results by digest. In local mode, an optional JSONL ledger creates a tamper-evident hash chain.

## How I built it

- Google ADK defines a Gemini 3.5 Flash agent with two plain-Python tools: deterministic opportunity audit and evidence-brief creation.
- A typed Python policy engine owns source, deadline, eligibility, evidence, payment, budget, scope, value, and action rules.
- FastAPI exposes health, single audit, batch audit, deterministic demo, and interactive API documentation.
- Cloud Run hosts the service; Vertex AI supplies Gemini; Firestore stores digest-addressed audit evidence.
- Pydantic rejects unknown fields and unsafe request shapes before they reach the engine.
- Forty-five tests cover hard gates, channel probability caps, sorting, digests, tamper detection, API validation, local and Firestore persistence, the live-agent boundary, and the real ADK agent definition, with 95% combined measured coverage.

## Google technology used

- Gemini 3.5 Flash
- Google Agent Development Kit (`google-adk`)
- Google Cloud Run
- Google Cloud Firestore
- Vertex AI authentication/configuration

## Key engineering choice

The generative model does not own the final decision. Gemini decides which tool to call and how to explain the result; deterministic code owns facts that must never drift. The model has no tool for messaging, submission, payment, signing, deployment, or account mutation.

## Challenges

My first implementation exposed a subtle but serious contradiction: unknown eligibility produced owner-review text while the categorical decision still said `ready`. The test suite caught it. I changed the state machine so eligibility must be explicitly true before any result can be ready.

My first value model also overestimated contest odds by treating a hackathon like a direct contract. I added channel-specific probability caps so high-prize competitions remain conservative rather than inflating pipeline value.

## Accomplishments

- A credential-free five-case demo that separates valuable review work from expired, invalid, unsafe, and dust-value routes.
- Deterministic, explainable gates that Gemini cannot override.
- A tamper-evident local ledger and digest-addressed cloud persistence design.
- Typed batch API, compact proof dashboard, Cloud Run configuration, architecture diagram, reproducible runbook, and automated tests.

The current verified count is 45 passing tests at 95% combined measured coverage; re-run `VERIFICATION.md` checks immediately before submission.

## What I learned

Autonomy becomes more useful when authority is explicit. Agents can do extensive research, validation, scoring, evidence preparation, and routing without acquiring implicit permission to spend, sign, submit, or message. Separating those concerns makes the agent both safer and faster because every unresolved gate is visible instead of buried in prose.

## What's next

- Add connectors that capture canonical opportunity pages into a normalized evidence envelope.
- Add signed snapshots and source-change detection.
- Add a human decision inbox with scoped approvals.
- Add Pub/Sub-driven background audits for deadline and source changes.
- Calibrate channel probabilities using observed historical conversion data rather than generic priors.

## Demo video

`[public YouTube or Vimeo URL, maximum four minutes]`

The final video must visibly prove the Cloud Run backend, ADK/Gemini invocation, Firestore record, architecture, deterministic gate, and test result. Do not claim live cloud behavior before those artifacts exist.

## Other data sources

The included fixture uses public-source URLs and synthetic examples. It contains no buyer data, credentials, personal data, or customer records. The demo's current Google contest facts should be rechecked immediately before recording.

## Findings and learnings

The most important finding is that a credible autonomous revenue agent needs a falsification layer more than it needs another copywriting layer. Closed deadlines, unknown eligibility, invalid sources, unprotected payments, ambiguous scope, and economically meaningless compensation should survive contact with a persuasive model as explicit structured state.

## Truth boundary

The repository and live proof establish the deterministic engine, API, ADK definition, fixture, tests, architecture, active Cloud Run revision, successful Gemini 3.5 Flash tool invocation, Firestore persistence, and Cloud logging. They do not claim Devpost submission, customers, revenue, judging results, or a prize.
