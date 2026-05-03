import sys
import os
import uuid
from datetime import datetime, timedelta

from bson import ObjectId
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import get_database

client = TestClient(app)


def make_user_payload():
    suffix = uuid.uuid4().hex[:8]
    return {
        "email": f"test_{suffix}@example.com",
        "username": f"testuser_{suffix}",
        "password": "password123",
        "phone_number": "+10000000000",
    }


def auth_headers():
    payload = make_user_payload()
    r = client.post("/api/v1/auth/signup", json=payload)
    assert r.status_code == 200
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, r.json()["user"]


# --- Root & health ---


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "message" in data
    assert data.get("docs") == "/docs"


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "healthy"


# --- Auth & users ---


def test_auth_and_user_flow():
    payload = make_user_payload()

    signup_response = client.post("/api/v1/auth/signup", json=payload)
    assert signup_response.status_code == 200
    signup_data = signup_response.json()
    assert "access_token" in signup_data
    assert signup_data["token_type"] == "bearer"
    assert signup_data["user"]["email"] == payload["email"]
    assert isinstance(signup_data["user"]["id"], str)

    token = signup_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["user"]["username"] == payload["username"]

    me_response = client.get("/api/v1/users/me", headers=headers)
    assert me_response.status_code == 200
    user_data = me_response.json()
    assert user_data["email"] == payload["email"]

    user_id = user_data["id"]
    user_response = client.get(f"/api/v1/users/{user_id}")
    assert user_response.status_code == 200
    assert user_response.json()["email"] == payload["email"]

    update_response = client.put(
        "/api/v1/users/me",
        headers=headers,
        json={"username": payload["username"] + "_updated"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["username"].endswith("_updated")

    deactivate_response = client.delete("/api/v1/users/me", headers=headers)
    assert deactivate_response.status_code == 204


def test_login_wrong_password():
    payload = make_user_payload()
    assert client.post("/api/v1/auth/signup", json=payload).status_code == 200
    r = client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": "wrong-password"},
    )
    assert r.status_code == 401


def test_users_me_without_token():
    r = client.get("/api/v1/users/me")
    assert r.status_code == 401


def test_users_me_invalid_token():
    r = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert r.status_code == 401


def test_get_user_invalid_id():
    r = client.get("/api/v1/users/not-a-valid-objectid")
    assert r.status_code == 404


def test_duplicate_signup_email():
    payload = make_user_payload()
    assert client.post("/api/v1/auth/signup", json=payload).status_code == 200
    r2 = client.post("/api/v1/auth/signup", json=payload)
    assert r2.status_code == 400
    assert "Email already registered" in r2.json()["detail"]


def test_duplicate_signup_username():
    p1 = make_user_payload()
    p2 = make_user_payload()
    p2["username"] = p1["username"]
    assert client.post("/api/v1/auth/signup", json=p1).status_code == 200
    r2 = client.post("/api/v1/auth/signup", json=p2)
    assert r2.status_code == 400
    assert "Username already taken" in r2.json()["detail"]


# --- Time capsules ---


def test_time_capsule_endpoints():
    payload = make_user_payload()

    signup_response = client.post("/api/v1/auth/signup", json=payload)
    assert signup_response.status_code == 200
    auth_data = signup_response.json()
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    future_date = (datetime.utcnow() + timedelta(days=1)).isoformat()

    capsule_response = client.post(
        "/api/v1/time-capsules",
        headers=headers,
        json={
            "title": "My Future Capsule",
            "content": "Secret message content",
            "content_type": "text",
            "open_date": future_date,
        },
    )
    assert capsule_response.status_code == 200
    capsule_data = capsule_response.json()
    assert capsule_data["title"] == "My Future Capsule"
    assert capsule_data["user_id"] == auth_data["user"]["id"]
    assert capsule_data["is_opened"] is False

    capsule_id = capsule_data["id"]

    list_response = client.get("/api/v1/time-capsules", headers=headers)
    assert list_response.status_code == 200
    assert any(item["id"] == capsule_id for item in list_response.json())

    pending_response = client.get("/api/v1/time-capsules/pending", headers=headers)
    assert pending_response.status_code == 200
    assert any(item["id"] == capsule_id for item in pending_response.json())

    opened_response = client.get("/api/v1/time-capsules/opened", headers=headers)
    assert opened_response.status_code == 200
    assert opened_response.json() == []

    capsule_detail = client.get(f"/api/v1/time-capsules/{capsule_id}", headers=headers)
    assert capsule_detail.status_code == 200
    assert capsule_detail.json()["id"] == capsule_id
    assert capsule_detail.json()["is_opened"] is False
    assert "user" in capsule_detail.json()

    update_capsule_response = client.put(
        f"/api/v1/time-capsules/{capsule_id}",
        headers=headers,
        json={"title": "Updated Capsule Title"},
    )
    assert update_capsule_response.status_code == 200
    assert update_capsule_response.json()["title"] == "Updated Capsule Title"

    open_response = client.post(f"/api/v1/time-capsules/{capsule_id}/open", headers=headers)
    assert open_response.status_code == 400
    assert "Cannot open capsule yet" in open_response.json()["detail"]

    db = get_database()
    db.time_capsules.update_one(
        {"_id": ObjectId(capsule_id)},
        {
            "$set": {
                "open_date": datetime.utcnow() - timedelta(hours=1),
                "updated_at": datetime.utcnow(),
            }
        },
    )

    check_ready_response = client.post("/api/v1/time-capsules/check-ready")
    assert check_ready_response.status_code == 200
    assert "Opened" in check_ready_response.json()["message"]

    opened_response_after = client.get("/api/v1/time-capsules/opened", headers=headers)
    assert opened_response_after.status_code == 200
    assert any(item["id"] == capsule_id for item in opened_response_after.json())
    opened_item = next(i for i in opened_response_after.json() if i["id"] == capsule_id)
    assert opened_item["content"] == "Secret message content"

    delete_fail_response = client.delete(f"/api/v1/time-capsules/{capsule_id}", headers=headers)
    assert delete_fail_response.status_code == 404


def test_create_capsule_open_date_in_past():
    headers, user = auth_headers()
    past = (datetime.utcnow() - timedelta(days=1)).isoformat()
    r = client.post(
        "/api/v1/time-capsules",
        headers=headers,
        json={
            "title": "Bad",
            "content": "x",
            "content_type": "text",
            "open_date": past,
        },
    )
    assert r.status_code == 400
    assert "future" in r.json()["detail"].lower()


def test_delete_unopened_capsule_success():
    headers, _ = auth_headers()
    future_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
    cr = client.post(
        "/api/v1/time-capsules",
        headers=headers,
        json={
            "title": "To delete",
            "content": "secret",
            "content_type": "text",
            "open_date": future_date,
        },
    )
    assert cr.status_code == 200
    cid = cr.json()["id"]
    dr = client.delete(f"/api/v1/time-capsules/{cid}", headers=headers)
    assert dr.status_code == 200
    assert dr.json().get("message")


def test_open_capsule_manually_when_due():
    headers, user = auth_headers()
    future_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
    cr = client.post(
        "/api/v1/time-capsules",
        headers=headers,
        json={
            "title": "Open me",
            "content": "plaintext body",
            "content_type": "text",
            "open_date": future_date,
        },
    )
    cid = cr.json()["id"]
    db = get_database()
    db.time_capsules.update_one(
        {"_id": ObjectId(cid)},
        {"$set": {"open_date": datetime.utcnow() - timedelta(minutes=1)}},
    )
    op = client.post(f"/api/v1/time-capsules/{cid}/open", headers=headers)
    assert op.status_code == 200
    body = op.json()
    assert body["is_opened"] is True
    assert body["content"] == "plaintext body"
    assert body["user"]["id"] == user["id"]


def test_capsule_wrong_owner_404():
    h1, _ = auth_headers()
    h2, u2 = auth_headers()
    future_date = (datetime.utcnow() + timedelta(days=2)).isoformat()
    cr = client.post(
        "/api/v1/time-capsules",
        headers=h1,
        json={
            "title": "A",
            "content": "c",
            "content_type": "text",
            "open_date": future_date,
        },
    )
    cid = cr.json()["id"]
    r = client.get(f"/api/v1/time-capsules/{cid}", headers=h2)
    assert r.status_code == 404


def test_capsule_invalid_id():
    headers, _ = auth_headers()
    r = client.get("/api/v1/time-capsules/not-valid-id", headers=headers)
    assert r.status_code == 404


def test_conversation_and_message_flow():
    headers1, user1 = auth_headers()
    payload = make_user_payload()
    signup_response = client.post("/api/v1/auth/signup", json=payload)
    assert signup_response.status_code == 200
    user2 = signup_response.json()["user"]
    headers2 = {"Authorization": f"Bearer {signup_response.json()['access_token']}"}

    conv_response = client.post(
        "/api/v1/conversations",
        headers=headers1,
        json={"title": "Hello Chat", "member_ids": [user2["id"]]},
    )
    assert conv_response.status_code == 200
    conv_data = conv_response.json()
    assert user1["id"] in conv_data["member_ids"]
    assert user2["id"] in conv_data["member_ids"]
    conversation_id = conv_data["id"]

    msg_response = client.post(
        "/api/v1/messages",
        headers=headers1,
        json={
            "conversation_id": conversation_id,
            "content": "Hello from user1",
            "content_type": "text",
        },
    )
    assert msg_response.status_code == 200
    msg_data = msg_response.json()
    assert msg_data["content"] == "Hello from user1"
    assert msg_data["sender_id"] == user1["id"]
    message_id = msg_data["id"]

    get_msg_response = client.get(f"/api/v1/messages/{message_id}", headers=headers2)
    assert get_msg_response.status_code == 200
    assert get_msg_response.json()["content"] == "Hello from user1"

    read_response = client.post(f"/api/v1/messages/{message_id}/read", headers=headers2)
    assert read_response.status_code == 200
    assert read_response.json()["is_read"] is True

    favorite_response = client.post(f"/api/v1/messages/{message_id}/favorite", headers=headers2)
    assert favorite_response.status_code == 200
    assert favorite_response.json()["is_favorite"] is True

    conversation_messages = client.get(
        f"/api/v1/messages/conversation/{conversation_id}",
        headers=headers2,
    )
    assert conversation_messages.status_code == 200
    assert any(message["id"] == message_id for message in conversation_messages.json())
