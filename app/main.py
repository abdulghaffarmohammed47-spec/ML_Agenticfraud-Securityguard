"""AFSG - Agentic Fraud & Security Guard: transparent fraud-risk triage API.

This educational starter uses a deterministic illustrative scoring policy. It is
NOT a trained/validated fraud model and must not be used for real transactions.
"""
from typing import Any
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="AFSG | Agentic Fraud & Security Guard", version="0.1.0",
              description="Explainable fraud-risk triage demo with human review controls.")

CASES: dict[str, dict[str, Any]] = {}

class Transaction(BaseModel):
    transaction_id: str | None = None
    amount: float = Field(gt=0)
    currency: str = "USD"
    account_age_days: int = Field(ge=0)
    transactions_last_hour: int = Field(ge=0)
    distance_from_usual_km: float = Field(ge=0)
    device_trusted: bool = True
    billing_shipping_match: bool = True
    international: bool = False

class ReviewDecision(BaseModel):
    reviewer: str = Field(min_length=1)
    decision: str = Field(pattern="^(approve|decline|escalate)$")
    notes: str = ""

@app.get("/")
def root():
    return {"service": "AFSG", "message": "Detect. Explain. Investigate. Predict. Respond.",
            "docs": "/docs", "warning": "Demo heuristic only; not production fraud detection."}

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/transactions/score")
def score_transaction(tx: Transaction):
    """Create a transparent risk assessment and case; no automatic adverse action."""
    points = 0
    evidence = []
    if tx.amount >= 1500:
        points += 20; evidence.append({"signal": "high_amount", "points": 20, "observed": tx.amount})
    if tx.account_age_days < 7:
        points += 20; evidence.append({"signal": "new_account", "points": 20, "observed_days": tx.account_age_days})
    if tx.transactions_last_hour >= 8:
        points += 20; evidence.append({"signal": "velocity", "points": 20, "observed": tx.transactions_last_hour})
    if tx.distance_from_usual_km >= 500:
        points += 15; evidence.append({"signal": "location_deviation", "points": 15, "observed_km": tx.distance_from_usual_km})
    if not tx.device_trusted:
        points += 10; evidence.append({"signal": "untrusted_device", "points": 10})
    if not tx.billing_shipping_match:
        points += 10; evidence.append({"signal": "address_mismatch", "points": 10})
    if tx.international:
        points += 5; evidence.append({"signal": "international_transaction", "points": 5})
    risk_score = min(points, 100)
    band = "low" if risk_score < 25 else "medium" if risk_score < 50 else "high"
    case_id = str(uuid4())
    result = {
        "case_id": case_id,
        "transaction_id": tx.transaction_id or str(uuid4()),
        "risk_score": risk_score,
        "risk_band": band,
        "evidence": evidence,
        "explanation": ("No configured risk signals were triggered." if not evidence else
                        "Risk score is the sum of configured signal weights: " + ", ".join(x["signal"] for x in evidence) + "."),
        "recommended_next_step": "allow_review" if band == "low" else "manual_review",
        "decision_status": "pending_human_review" if band != "low" else "not_required_by_demo_policy",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "limitations": ["Illustrative rules, not a trained model", "Risk signals are not proof of fraud",
                       "No transaction is automatically blocked or declined"]
    }
    CASES[case_id] = result
    return result

@app.get("/cases")
def list_cases():
    return list(CASES.values())

@app.get("/cases/{case_id}")
def get_case(case_id: str):
    if case_id not in CASES: raise HTTPException(status_code=404, detail="Case not found")
    return CASES[case_id]

@app.post("/cases/{case_id}/review")
def review_case(case_id: str, review: ReviewDecision):
    if case_id not in CASES: raise HTTPException(status_code=404, detail="Case not found")
    case = CASES[case_id]
    case["human_review"] = {**review.model_dump(), "reviewed_at": datetime.now(timezone.utc).isoformat()}
    case["decision_status"] = "reviewed_by_human"
    return case
