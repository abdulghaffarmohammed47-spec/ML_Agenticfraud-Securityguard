# AFSG — Agentic Fraud & Security Guard

**Detect. Explain. Investigate. Predict. Respond.**

AFSG is a research-oriented prototype for fraud-risk triage. It demonstrates how transaction signals can be combined into a transparent risk assessment, accompanied by evidence and an explanation, and routed for human review. The goal is not simply to return a score: it is to make the score inspectable and keep consequential decisions accountable.

> **Research/demo disclaimer:** This repository currently implements a deterministic, illustrative rule-based scoring baseline. It is not a trained or validated fraud-detection model, does not establish that a transaction is fraudulent, and must not be connected to real payment decisions. The score weights are demonstration choices, not empirically learned or calibrated values.

## Current prototype

- FastAPI REST API with interactive OpenAPI docs
- Input validation for transaction attributes
- Transparent weighted risk signals and evidence list
- Risk bands (`low`, `medium`, `high`) with next-step suggestions
- Case creation and retrieval
- Human review endpoint (`approve`, `decline`, or `escalate`) with reviewer notes
- Explicit guardrail: the scoring endpoint does not automatically block or decline a transaction
- Unit/API tests and Docker setup

## Architecture (prototype)

```text
Client / Demo UI
      |
      v
FastAPI API  ---> Input validation
      |                  |
      v                  v
Risk signal rules --> Evidence + weighted score
      |                  |
      v                  v
Case store (in-memory) --> Explanation / risk band
                           |
                           v
                    Human analyst review
```

The current case store is in-memory; cases disappear when the service restarts. PostgreSQL persistence, model training, SHAP explanations, RAG, bounded agents, authentication, and a production case-management UI are future extensions—not implemented features in this starter repository.

## Repository structure

```text
AFSG_Project/
├── app/
│   └── main.py              # FastAPI app, scoring, cases, human review
├── tests/
│   └── test_api.py         # API tests
├── data/                   # Place permitted sample data here (currently empty)
├── docs/                   # Project documentation (currently empty)
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.11+ (Python 3.12 recommended)
- Git
- Optional: Docker Desktop

## Run locally (Windows PowerShell / VS Code)

1. Download and extract this project ZIP.
2. Open the extracted `AFSG_Project` folder in VS Code.
3. Open Terminal → PowerShell and run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

If PowerShell blocks activation, run this once in the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Open:
- API: http://127.0.0.1:8000
- Swagger / interactive testing: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

Stop the server with `Ctrl+C`.

## Run with Docker

From the project root:

```bash
docker compose up --build
```

Then visit http://localhost:8000/docs. Stop and remove the container with:

```bash
docker compose down
```

## API quick start

### 1. Score a sample transaction

In Swagger, select `POST /transactions/score` → **Try it out**, and submit:

```json
{
  "transaction_id": "txn-demo-001",
  "amount": 2100,
  "currency": "USD",
  "account_age_days": 2,
  "transactions_last_hour": 9,
  "distance_from_usual_km": 850,
  "device_trusted": false,
  "billing_shipping_match": false,
  "international": true
}
```

The response includes `case_id`, `risk_score`, `risk_band`, `evidence`, `explanation`, `recommended_next_step`, and `decision_status`. Save the returned `case_id` for the next calls.

### 2. Retrieve a case

```http
GET /cases/{case_id}
```

### 3. List cases

```http
GET /cases
```

### 4. Record a human review

```http
POST /cases/{case_id}/review
Content-Type: application/json
```

```json
{
  "reviewer": "analyst-demo",
  "decision": "escalate",
  "notes": "Review identity and transaction context independently."
}
```

Allowed decisions: `approve`, `decline`, `escalate`. In a real system, this endpoint would require authentication, authorization, immutable audit logging, and policy controls.

## Illustrative scoring policy

| Signal | Demo weight |
|---|---:|
| Amount ≥ 1,500 | +20 |
| Account age < 7 days | +20 |
| 8 or more transactions in the last hour | +20 |
| Distance from usual location ≥ 500 km | +15 |
| Untrusted device | +10 |
| Billing/shipping mismatch | +10 |
| International transaction | +5 |

The score is capped at 100. Bands: `low` < 25, `medium` 25–49, `high` ≥ 50. These thresholds are arbitrary demonstration settings and are not calibrated to a dataset.

## Run tests

```bash
pytest -q
```

## Research roadmap

1. **Data and protocol:** Document data provenance, permissible use, label definition, leakage controls, and a reproducible temporal train/validation/test split (e.g., IEEE-CIS dataset, subject to its terms).
2. **Baseline modeling:** Train and compare suitable models such as Logistic Regression, Random Forest, and XGBoost; establish reproducible preprocessing.
3. **Evaluation:** Report PR-AUC (important under class imbalance), ROC-AUC, precision, recall, F1, calibration, false-positive rate, and inference latency. Include confidence intervals where feasible.
4. **Explainability:** Add SHAP-based feature attribution and clearly distinguish model attribution from causal evidence.
5. **Persistence and audit:** Replace in-memory cases with PostgreSQL; add access control, audit trail, retention, and secure secrets management.
6. **Investigation assistance:** Introduce retrieval-grounded summaries and bounded agents only with source citations, strict tool permissions, and human approval.
7. **Human-centered evaluation:** Measure analyst usefulness, review time, error rates, and fairness across appropriately governed groups.

Do not claim model performance until experiments have actually been run and reported.

## Safety, privacy, and responsible use

- A risk signal is an indicator for investigation, not proof of fraud.
- Keep a human accountable for adverse actions.
- Minimize personal data; use synthetic or approved data for development.
- Do not commit datasets, customer information, API keys, or secrets to GitHub.
- Before deployment, conduct security, privacy, bias/fairness, calibration, and operational reviews.

## GitHub: publish this project

### A. Create a repository on GitHub

1. Sign in at https://github.com
2. Click **+** → **New repository**.
3. Repository name: `AFSG-Agentic-Fraud-Security-Guard` (or your preferred name).
4. Description: `Explainable fraud-risk triage research prototype with evidence and human-review guardrails.`
5. Choose **Public** if this is intended for faculty/recruiters; otherwise choose **Private**.
6. **Do not** initialize with README, `.gitignore`, or license because this project already includes them.
7. Click **Create repository** and keep the page open to copy its URL.

### B. Push from VS Code terminal

Extract the ZIP, open the project folder, then run:

```bash
git init
git add .
git commit -m "Initial commit: AFSG research prototype"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/AFSG-Agentic-Fraud-Security-Guard.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username and use the actual repository URL. GitHub may prompt you to sign in through a browser. Do not enter your password into a source file or terminal command.

### C. Later updates

```bash
git status
git add .
git commit -m "Describe your changes"
git push
```

### D. Verify

Refresh your GitHub repository page. Confirm `app/`, `tests/`, `README.md`, `requirements.txt`, and configuration files are present. Check that `.env`, credentials, private data, and large datasets are not committed.

## License

No license has been selected yet. If you want others to reuse the code, add a license (for example, MIT) after confirming it fits your project and institution's requirements. Without a license, default copyright restrictions apply.

## Author

**Mohammed Abdul Ghaffar**  
AFSG — Agentic Fraud & Security Guard  
Research / academic prototype
