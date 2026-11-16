from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def sample():
    return {"transaction_id":"txn-demo-001", "amount":2100, "currency":"USD",
            "account_age_days":2, "transactions_last_hour":9,
            "distance_from_usual_km":850, "device_trusted":False,
            "billing_shipping_match":False, "international":True}

def test_health():
    assert client.get('/health').json()['status'] == 'ok'

def test_score_and_explain():
    response = client.post('/transactions/score', json=sample())
    assert response.status_code == 200
    body = response.json()
    assert body['risk_band'] == 'high'
    assert body['evidence']
    assert body['decision_status'] == 'pending_human_review'
    assert body['case_id']

def test_human_review():
    case = client.post('/transactions/score', json=sample()).json()
    reviewed = client.post(f"/cases/{case['case_id']}/review", json={
        "reviewer":"analyst-demo", "decision":"escalate", "notes":"Verify independently"
    })
    assert reviewed.status_code == 200
    assert reviewed.json()['decision_status'] == 'reviewed_by_human'


def test_unknown_case():
    assert client.get('/cases/not-a-case').status_code == 404
