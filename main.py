from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict, Field

from revenue_sentinel.demo import run_demo
from revenue_sentinel.service import OpportunityService


class OpportunityPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    opportunity_id: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=300)
    source_url: str = Field(min_length=1, max_length=2048)
    channel: str = Field(min_length=1, max_length=100)
    potential_value_usd: float = Field(ge=0, le=100_000_000)
    deadline_iso: str | None = None
    eligible: bool | None = None
    buyer_verified: bool | None = None
    payment_protected: bool | None = None
    budget_clear: bool = False
    scope_clear: bool = False
    public_evidence: list[str] = Field(default_factory=list, max_length=20)
    external_actions: list[str] = Field(default_factory=list, max_length=20)
    notes: str = Field(default="", max_length=5000)


class AuditBatch(BaseModel):
    opportunities: list[OpportunityPayload] = Field(min_length=1, max_length=100)


service = OpportunityService()
api = FastAPI(title="Revenue Sentinel", version="0.1.0")
app = api


@api.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "revenue-sentinel"}


@api.get("/api/health")
def api_health() -> dict[str, str]:
    return healthz()


@api.post("/api/audit")
def audit(payload: OpportunityPayload) -> dict[str, Any]:
    return service.audit_one(payload.model_dump())


@api.post("/api/audit/batch")
def audit_batch(payload: AuditBatch) -> dict[str, Any]:
    queue = service.audit_many([item.model_dump() for item in payload.opportunities])
    return {"count": len(queue), "queue": queue}


@api.post("/api/demo")
def demo() -> dict[str, Any]:
    fixture = Path(__file__).parent / "fixtures" / "opportunities.json"
    if not fixture.exists():
        raise HTTPException(status_code=500, detail="demo fixture unavailable")
    return run_demo(fixture)


@api.post("/api/agent/audit")
async def agent_audit(payload: OpportunityPayload) -> dict[str, Any]:
    from app.runtime import AgentQuotaExceeded, audit_with_agent

    try:
        return await audit_with_agent(payload.model_dump())
    except AgentQuotaExceeded as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Gemini agent invocation failed") from exc


@api.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Revenue Sentinel</title><style>
:root{color-scheme:dark;--ink:#eef7ff;--muted:#96aac0;--cyan:#5ee7f7;--mint:#8fffd1;--panel:#0b1b2b;--line:#1b3b50}
*{box-sizing:border-box}body{font-family:Inter,ui-sans-serif,system-ui,sans-serif;margin:0;background:radial-gradient(circle at 80% 0,#103650 0,#06111e 43%);color:var(--ink)}
main{max-width:1100px;margin:auto;padding:54px 22px 80px}.eyebrow{color:var(--cyan);text-transform:uppercase;letter-spacing:.16em;font-size:13px;font-weight:800}
.hero{font-size:clamp(50px,9vw,92px);line-height:.88;letter-spacing:-.06em;margin:20px 0}.sub{font-size:20px;color:#bed0df;max-width:790px;line-height:1.55}
.status{display:flex;gap:10px;flex-wrap:wrap;margin:28px 0}.pill{border:1px solid #26526b;background:#0a2032;border-radius:999px;padding:8px 12px;color:#cbeaf3;font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:14px;margin-top:36px}.card,.lab{background:linear-gradient(145deg,#0d2033,#091725);border:1px solid var(--line);border-radius:18px;padding:22px;box-shadow:0 18px 50px #0004}.card b{color:var(--cyan)}
.lab{margin-top:18px}.lab h2{margin-top:0}.actions{display:flex;gap:12px;flex-wrap:wrap}button,a.button{appearance:none;border:0;border-radius:12px;padding:13px 17px;background:var(--cyan);color:#021017;font-weight:800;cursor:pointer;text-decoration:none}button.secondary,a.secondary{background:#142d40;color:var(--ink);border:1px solid #28506a}button:disabled{opacity:.55;cursor:wait}
pre{white-space:pre-wrap;word-break:break-word;min-height:92px;background:#050e18;border:1px solid #17364a;border-radius:13px;padding:16px;color:#c9f7e5;line-height:1.45;overflow:auto}.fine{font-size:13px;color:var(--muted);line-height:1.5}code{color:var(--mint)}
</style></head><body><main><div class="eyebrow">Google ADK · Gemini 3.5 Flash · Cloud Run · Firestore</div>
<h1 class="hero">Revenue<br>Sentinel</h1><p class="sub">I built an autonomous evidence gate for revenue operations. It rejects dead or ineligible leads, quantifies expected value, surfaces missing proof, and produces an owner-ready action queue without inventing revenue or taking unsafe external action.</p>
<div class="status"><span class="pill">Live on Google Cloud</span><span class="pill">Deterministic policy core</span><span class="pill">Tamper-evident records</span><span class="pill">Owner-gated actions</span></div>
<section class="grid"><article class="card"><b>Evidence first</b><p>Sources, deadlines, eligibility, budget, scope, and payment protection become explicit findings.</p></article>
<article class="card"><b>Deterministic gate</b><p>Gemini cannot override closed, ineligible, unsafe, or dust-value outcomes.</p></article>
<article class="card"><b>Tamper evident</b><p>Every persisted audit gets a SHA-256 evidence digest stored in Firestore.</p></article>
<article class="card"><b>Action aware</b><p>Research and preparation can move forward while external writes remain explicit human gates.</p></article></section>
<section class="lab"><h2>Live proof lab</h2><p class="fine">Run the five-case local policy fixture, or invoke the bounded Google ADK agent. The live agent must call the deterministic audit tool before it can explain a decision.</p>
<div class="actions"><button id="demo">Run five-case audit</button><button class="secondary" id="agent">Run Gemini agent audit</button><a class="button secondary" href="/docs">Open API docs</a></div>
<pre id="output">Ready. Choose a proof run above.</pre><p class="fine">The public Gemini demo is capped at 30 calls per UTC hour to protect the project credit and judging availability.</p></section>
<script>
const output=document.querySelector('#output');
const sample={opportunity_id:'judge-demo',title:'Verified automation contract',source_url:'https://example.com/opportunity',channel:'Contract',potential_value_usd:2500,deadline_iso:'2099-01-01T00:00:00Z',eligible:true,buyer_verified:true,payment_protected:true,budget_clear:true,scope_clear:true,public_evidence:['https://example.com/opportunity','https://example.com/terms'],external_actions:['prepare proposal'],notes:'Synthetic judge demo'};
async function run(button,url,body){button.disabled=true;output.textContent='Running live proof...';try{const response=await fetch(url,{method:'POST',headers:body?{'content-type':'application/json'}:{},body:body?JSON.stringify(body):undefined});const data=await response.json();if(!response.ok)throw new Error(data.detail||'Request failed');output.textContent=JSON.stringify(data,null,2)}catch(error){output.textContent='Proof run failed: '+error.message}finally{button.disabled=false}}
document.querySelector('#demo').onclick=e=>run(e.currentTarget,'/api/demo');
document.querySelector('#agent').onclick=e=>run(e.currentTarget,'/api/agent/audit',sample);
</script></main></body></html>"""


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
