import sys
import os
import uuid
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import SessionLocal
from app.models import TimeCapsule

client = TestClient(app)


def make_user_payload():
    suffix = uuid.uuid4().hex[:8]
    return {
        "email": f"test_{suffix}@example.com",
        "username": f"testuser_{suffix}",
        "password": "password123",
        "phone_number": "+10000000000"
    }


def test_auth_and_user_flow():
    payload = make_user_payload()

    # Signup
    signup_response = client.post("/api/v1/auth/signup", json=payload)
    assert signup_response.status_code == 200
    signup_data = signup_response.json()
    assert "access_token" in signup_data
    assert signup_data["token_type"] == "bearer"
    assert signup_data["user"]["email"] == payload["email"]

    token = signup_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]}
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["user"]["username"] == payload["username"]

    # Current user
    me_response = client.get("/api/v1/users/me", headers=headers)
    assert me_response.status_code == 200
    user_data = me_response.json()
    assert user_data["email"] == payload["email"]

    # Get user by ID
    user_id = user_data["id"]
    user_response = client.get(f"/api/v1/users/{user_id}")
    assert user_response.status_code == 200
    assert user_response.json()["email"] == payload["email"]

    # Update user
    update_response = client.put(
        "/api/v1/users/me",
        headers=headers,
        json={"username": payload["username"] + "_updated"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["username"].endswith("_updated")

    # Deactivate user
    deactivate_response = client.delete("/api/v1/users/me", headers=headers)
    assert deactivate_response.status_code == 204


def test_time_capsule_endpoints():
    payload = make_user_payload()

    signup_response = client.post("/api/v1/auth/signup", json=payload)
    assert signup_response.status_code == 200
    auth_data = signup_response.json()
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    future_date = (datetime.utcnow() + timedelta(days=1)).isoformat()

    # Create capsule
    capsule_response = client.post(
        "/api/v1/time-capsules",
        headers=headers,
        json={
            "title": "My Future Capsule",
            "content": "Secret message content",
            "content_type": "text",
            "open_date": future_date
        }
    )
    assert capsule_response.status_code == 200
    capsule_data = capsule_response.json()
    assert capsule_data["title"] == "My Future Capsule"
    assert capsule_data["user_id"] == auth_data["user"]["id"]
    assert capsule_data["is_opened"] is False

    capsule_id = capsule_data["id"]

    # Get my capsules
    list_response = client.get("/api/v1/time-capsules", headers=headers)
    assert list_response.status_code == 200
    assert any(item["id"] == capsule_id for item in list_response.json())

    # Get pending capsules
    pending_response = client.get("/api/v1/time-capsules/pending", headers=headers)
    assert pending_response.status_code == 200
    assert any(item["id"] == capsule_id for item in pending_response.json())

    # Get opened capsules (should be empty)
    opened_response = client.get("/api/v1/time-capsules/opened", headers=headers)
    assert opened_response.status_code == 200
    assert opened_response.json() == []

    # Get specific capsule
    capsule_detail = client.get(f"/api/v1/time-capsules/{capsule_id}", headers=headers)
    assert capsule_detail.status_code == 200
    assert capsule_detail.json()["id"] == capsule_id
    assert capsule_detail.json()["is_opened"] is False

    # Update capsule
    update_capsule_response = client.put(
        f"/api/v1/time-capsules/{capsule_id}",
        headers=headers,
        json={"title": "Updated Capsule Title"}
    )
    assert update_capsule_response.status_code == 200
    assert update_capsule_response.json()["title"] == "Updated Capsule Title"

    # Attempt to open capsule before open date
    open_response = client.post(f"/api/v1/time-capsules/{capsule_id}/open", headers=headers)
    assert open_response.status_code == 400
    assert "Cannot open capsule yet" in open_response.json()["detail"]

    # Set capsule open_date to past and test check-ready opening
    with SessionLocal() as db:
        capsule_record = db.query(TimeCapsule).filter(TimeCapsule.id == capsule_id).first()
        assert capsule_record is not None
        capsule_record.open_date = datetime.utcnow() - timedelta(hours=1)
        db.commit()

    check_ready_response = client.post("/api/v1/time-capsules/check-ready")
    assert check_ready_response.status_code == 200
    assert "Opened" in check_ready_response.json()["message"]

    # Verify opened capsules now contain the capsule
    opened_response_after = client.get("/api/v1/time-capsules/opened", headers=headers)
    assert opened_response_after.status_code == 200
    assert any(item["id"] == capsule_id for item in opened_response_after.json())

    # Delete opened capsule should fail
    delete_fail_response = client.delete(f"/api/v1/time-capsules/{capsule_id}", headers=headers)
    assert delete_fail_response.status_code == 404


def test_duplicate_signup_error():
    payload = make_user_payload()
    response_1 = client.post("/api/v1/auth/signup", json=payload)
    assert response_1.status_code == 200

    response_2 = client.post("/api/v1/auth/signup", json=payload)
    assert response_2.status_code == 400
    assert "Email already registered" in response_2.json()["detail"]


if __name__ == "__main__":
    print("Running API endpoint tests...")
    test_auth_and_user_flow()
    print("Auth and user flow tests passed")
    test_time_capsule_endpoints()
    print("Time capsule endpoint tests passed")
    test_duplicate_signup_error()
    print("Duplicate signup error test passed")
    print("All endpoint tests passed")
