# Revenue Sentinel demo script

Target: 3 minutes 20 seconds to 3 minutes 45 seconds.

Voice: Kokoro ONNX, `af_heart`, speed `1.03`, normalized to minus 16 LUFS.

## 1. The problem

Most revenue tools try to find more leads. My problem was the opposite. I was losing time to expired posts, unknown eligibility, unverified buyers, vague budgets, and tiny tasks that cost more to inspect than they could ever pay. I built Revenue Sentinel as a solo developer to turn that noisy research into a clear, evidence-backed queue.

## 2. The workflow

Revenue Sentinel checks the source, deadline, eligibility, buyer, payment protection, budget, scope, and evidence before it recommends anything. Every opportunity becomes ready, review, table, or reject. Ready still requires owner approval for external action. Review means an important fact is missing. Table means the value is too small. Reject means a hard rule failed.

## 3. Live execution

This is the deployed service running on Google Cloud. I am starting with the five-case audit. The fixture includes a current contest, an unverified contract, a queue worth only a fraction of a cent, an expired contract, and an invalid source. The result is two reviews, one table, and two rejects. Each result includes risk, bounded expected value, findings, a next step, and a SHA-256 evidence digest.

## 4. Gemini with a hard boundary

Now I am running the live Gemini agent. Google ADK gives Gemini 3.5 Flash two tools: audit an opportunity and create an evidence brief. The agent must call the deterministic audit before it can explain a decision. It has no tool for sending messages, spending funds, signing, submitting, or changing an account. In this run, the verified synthetic contract is ready, but the action gate still says owner approval.

## 5. Architecture and cloud proof

I separated the system into clear layers. FastAPI on Cloud Run accepts typed input. Google ADK and Gemini choose the approved tool. The Python policy engine owns the rules that must never drift. Firestore stores each audit by its evidence digest. The active Cloud Run revision is revenue-sentinel-00002-t5j with one hundred percent of traffic. The live agent request returned HTTP 200, and the matching Firestore document was saved.

## 6. Reproducibility

The public repository includes the architecture, deployment script, fixture, runbook, and exact setup steps. Forty-five automated tests pass with ninety-five percent combined coverage. Ruff lint and formatting checks pass. The public demo needs no login, and the deterministic five-case run needs no model key. Judges can open the live URL, run both proofs, inspect the API docs, and reproduce the project locally.

## 7. Close

Revenue Sentinel does the repetitive work of checking, ranking, and documenting opportunities without pretending that a lead is revenue or that uncertainty is permission. I built it to move faster while keeping every important claim and action auditable. The live service and complete source are available at the links in this submission.
