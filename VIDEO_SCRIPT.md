# Four-minute demo script

## 0:00-0:25 - The costly failure mode

“Revenue teams do not suffer from a lack of leads. They suffer from noisy leads: expired contracts, eligibility traps, unverified buyers, unclear budgets, and tiny tasks that cost more to inspect than they can ever pay. A normal chat agent can sound confident while skipping those gates.”

## 0:25-0:55 - Product

“Revenue Sentinel is an autonomous evidence gate built with Google ADK and Gemini 3.5 Flash. It turns opportunity data into a ranked, auditable action queue. Gemini handles orchestration and explanation; deterministic code owns facts that must not drift.”

## 0:55-1:40 - Live batch

“This credential-free fixture contains five deliberately different cases. The current Google hackathon has verified rules and prize evidence, but eligibility is not yet confirmed, so it stays in review. A queue of sixteen agent tasks is worth only 0.00016 USDT, so it is tabled. An expired contract and an invalid source are rejected. A high-budget contract without payment protection stays under review.”

“The system calculates bounded expected value, exposes every finding, and gives each result a SHA-256 evidence digest. It never calls a lead revenue.”

## 1:40-2:20 - Agent action

“The ADK agent has two tools: audit an opportunity and create an evidence brief. It cannot send a message, submit a form, spend funds, sign, deploy, or modify an account. Opportunity text is treated as untrusted data.”

“If I ask Gemini what to pursue, it must call the audit first. Unknown eligibility cannot become ready. Closed or invalid opportunities cannot be promoted by persuasive language.”

## 2:20-3:00 - Engineering proof

“The FastAPI service validates every request and exposes single and batch audits plus a deterministic demo. The test suite covers hard gates, sorting, digests, tamper detection, API validation, and persistence behavior. Local JSONL records form a hash chain.”

## 3:00-3:35 - Google Cloud proof

“The service runs on Cloud Run. Vertex AI supplies Gemini, and Firestore stores digest-addressed audit results. Here is the active Cloud Run revision, the live endpoint, the matching log entry, and the Firestore document.”

The preceding paragraph is now verified against revision `revenue-sentinel-00002-t5j`, the live Gemini call, the matching Firestore record, and Cloud logs.

## 3:35-3:55 - Value

“Revenue Sentinel removes the repetitive work of filtering and documenting opportunities while preserving the moments that actually require human authority. It helps autonomous agents move faster without inventing certainty, permission, or revenue.”
