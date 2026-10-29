"""
Test suite for Flask Web Platform, FastAPI Microservice, and full-stack API endpoints.
"""

import pytest
from app import app
import backend.app as backend_app
from admin.admin_manager import audit_platform_health

try:
    from fastapi.testclient import TestClient
    from backend.fastapi_app import app as fastapi_app
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    TestClient = None
    fastapi_app = None

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key-123'
    with app.test_client() as client:
        yield client

@pytest.fixture
def api_client():
    if not HAS_FASTAPI:
        pytest.skip("FastAPI not installed in this environment")
    return TestClient(fastapi_app)

def test_root_landing_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_login_page_renders(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data or b"Welcome" in response.data

def test_unauthenticated_dashboard_redirect(client):
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_unauthenticated_resources_redirect(client):
    response = client.get('/resources')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_unauthenticated_spinwheel_redirect(client):
    response = client.get('/spinwheel')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_api_sentiment_endpoint(client):
    response = client.post('/api/sentiment', json={"text": "I feel really stressed about my exams tomorrow"})
    assert response.status_code == 200
    data = response.get_json()
    assert "mood" in data
    assert "polarity" in data
    assert "shlok" in data
    assert "reframing" in data
    assert "affirmation" in data
    assert "context" in data

def test_api_health_endpoint(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"

def test_api_gita_verses_endpoint(client):
    response = client.get('/api/gita/verses')
    assert response.status_code == 200
    data = response.get_json()
    assert "verses" in data
    assert len(data["verses"]) > 0
    assert "sanskrit" in data["verses"][0]

def test_authenticated_routes(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'testuser'
        sess['role'] = 'student'
        sess['points'] = 100

    # Test dashboard rendering
    res_dash = client.get('/dashboard')
    assert res_dash.status_code == 200
    assert b"Reflection" in res_dash.data and b"Journal" in res_dash.data

    # Test resources rendering
    res_res = client.get('/resources')
    assert res_res.status_code == 200
    assert b"Resource Hub" in res_res.data or b"Cognitive Reframing" in res_res.data

    # Test spinwheel rendering
    res_spin = client.get('/spinwheel')
    assert res_spin.status_code == 200
    assert b"Spin Wheel" in res_spin.data

    # Test spinwheel post
    res_spin_post = client.post('/spinwheel', json={"index": 0})
    assert res_spin_post.status_code == 200
    spin_data = res_spin_post.get_json()
    assert "points_won" in spin_data
    assert "message" in spin_data
    assert "shlok" in spin_data

    # Test mini-goal completion
    res_goal = client.post('/api/complete-minigoal', json={"reward": 25, "goal_text": "Square Breathing"})
    assert res_goal.status_code == 200
    assert res_goal.get_json().get("success") is True

def test_admin_dashboard_portal(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'admin'
        sess['role'] = 'admin'

    res_admin = client.get('/admin/dashboard')
    assert res_admin.status_code == 200
    assert b"SARATHI ENTERPRISE ADMIN" in res_admin.data or b"Admin Console" in res_admin.data

def test_backend_modular_import():
    assert backend_app.app is not None

def test_admin_manager_audit():
    result = audit_platform_health()
    assert result is True

# --- FastAPI Test Suite ---
@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed in this environment")
def test_fastapi_health(api_client):
    response = api_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed in this environment")
def test_fastapi_analyze(api_client):
    response = api_client.post("/api/v1/analyze", json={"text": "I feel anxious about my upcoming exam."})
    assert response.status_code == 200
    data = response.json()
    assert "polarity" in data
    assert "context" in data
    assert "shlok" in data
    assert "reframing" in data
    assert "affirmation" in data

@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed in this environment")
def test_fastapi_chat(api_client):
    response = api_client.post("/api/v1/chat", json={"message": "I feel lonely and isolated."})
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "affirmation" in data
    assert "shlok" in data
    assert data["is_crisis"] is False

@pytest.mark.skipif(not HAS_FASTAPI, reason="FastAPI not installed in this environment")
def test_fastapi_chat_crisis_interception(api_client):
    response = api_client.post("/api/v1/chat", json={"message": "I want to kill myself."})
    assert response.status_code == 200
    data = response.json()
    assert data["is_crisis"] is True
    assert "Tele-MANAS" in data["reply"]
    assert "14416" in data["reply"]

def test_period_export_csv(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'rohan_student'
        sess['role'] = 'student'
        sess['gender'] = 'female'

    res = client.get('/api/period/export')
    assert res.status_code == 200
    assert "text/csv" in res.content_type
    assert b"timestamp,mood,symptoms,flow" in res.data

def test_forum_live_search(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'rohan_student'
        sess['role'] = 'student'

    res = client.get('/forum?q=anxiety')
    assert res.status_code == 200
    assert b"Peer Support Forum" in res.data


def test_dedicated_login_portals(client):
    res_student = client.get('/login/student')
    assert res_student.status_code == 200
    assert b"Student" in res_student.data or b"Welcome" in res_student.data

    res_counselor = client.get('/login/counselor')
    assert res_counselor.status_code == 200
    assert b"Counselor" in res_counselor.data

    res_admin = client.get('/login/admin')
    assert res_admin.status_code == 200
    assert b"Admin" in res_admin.data

    res_reg_counselor = client.get('/register/counselor')
    assert res_reg_counselor.status_code == 200
    assert b"Join Sarathi as a Counselor" in res_reg_counselor.data

def test_male_caregiver_period_access(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'aarav_male'
        sess['role'] = 'student'
        sess['gender'] = 'male'

    res = client.get('/period')
    assert res.status_code == 200
    assert b"Caregiver" in res.data or b"Ally" in res.data

def test_managed_profile_creation_and_switch(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'aarav_male'
        sess['role'] = 'student'

    res_add = client.post('/api/profile/add', data={
        "profile_name": "Ananya",
        "relationship": "Daughter",
        "gender": "Female",
        "age": "16",
        "notes": "Exam anxiety and cycle cramps"
    }, follow_redirects=False)
    assert res_add.status_code == 302

def test_counselor_clinical_permission_workflow(client):
    # 1. User grants permission
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'student_user'
        sess['role'] = 'student'

    res_grant = client.post('/api/permissions/grant', data={
        "counselor_id": "1",
        "allowed_until": "2026-12-31",
        "can_view_journal": "1",
        "can_view_screenings": "1",
        "can_view_wellness": "1",
        "notes": "Preparing for exam stress sessions"
    }, follow_redirects=False)
    assert res_grant.status_code == 302

    # 2. Counselor accesses permitted client history
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'counselor1'
        sess['role'] = 'counselor'

    res_client_view = client.get('/counselor/client/1')
    assert res_client_view.status_code == 200
    assert b"Clinical Review" in res_client_view.data or b"Consent Valid Until" in res_client_view.data
